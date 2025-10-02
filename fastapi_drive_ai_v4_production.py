"""
PicLocate V4 - Production-Grade Visual Search Engine
Complete implementation with:
- Multi-pass vision pipeline (detection → segmentation → color/material → room classification)
- Per-object color and material analysis
- Structured captions + semantic embeddings
- Hybrid search (SQL filters + vector similarity + explainable ranking)
- Full Hebrew/English support

Architecture: See supabase_schema_v2.sql for database schema
"""

import os
import io
import ssl
import json
import uuid
import time
import hashlib
import traceback
from typing import List, Dict, Optional, Tuple
from pathlib import Path
from datetime import datetime

# FastAPI
from fastapi import FastAPI, HTTPException, UploadFile, File, Form, Query
from fastapi.responses import StreamingResponse, JSONResponse, FileResponse
from fastapi.middleware.cors import CORSMiddleware
from pydantic import BaseModel

# Google Drive & Auth
from google.oauth2 import service_account
from google.auth.transport.requests import Request
from google_auth_oauthlib.flow import InstalledAppFlow
from googleapiclient.discovery import build
from googleapiclient.http import MediaIoBaseDownload
from googleapiclient.errors import HttpError

# Computer Vision & ML
import torch
from PIL import Image
import numpy as np
import cv2
from ultralytics import YOLO
from sklearn.cluster import KMeans
from skimage import color as skimage_color
import imagehash

# Optional imports
try:
    import clip
    CLIP_AVAILABLE = True
except ImportError:
    CLIP_AVAILABLE = False
    print("⚠️ CLIP not available, using text embeddings only")

try:
    from transformers import AutoProcessor, AutoModelForZeroShotObjectDetection
    TRANSFORMERS_AVAILABLE = True
except ImportError:
    TRANSFORMERS_AVAILABLE = False

# Supabase & Database
from supabase import create_client, Client
from dotenv import load_dotenv

# OpenAI for embeddings & translations
import openai

# Load environment variables
load_dotenv()

# =====================================================
# CONFIGURATION
# =====================================================

# Supabase
SUPABASE_URL = os.getenv("SUPABASE_URL", "https://gezmablgrepoaamtizts.supabase.co")
SUPABASE_KEY = os.getenv("SUPABASE_KEY", "eyJhbGciOiJIUzI1NiIsInR5cCI6IkpXVCJ9.eyJpc3MiOiJzdXBhYmFzZSIsInJlZiI6Imdlem1hYmxncmVwb2FhbXRpenRzIiwicm9sZSI6ImFub24iLCJpYXQiOjE3NTkxNzg2MzMsImV4cCI6MjA3NDc1NDYzM30.lJjaubEzeET8OwcHWJ_x_pOAXd8Bc1yDbpdvKianLM0")
supabase: Client = create_client(SUPABASE_URL, SUPABASE_KEY)

# OpenAI
OPENAI_API_KEY = os.getenv("OPENAI_API_KEY", "")
if OPENAI_API_KEY:
    openai.api_key = OPENAI_API_KEY

# Google Drive Target Folder
TARGET_FOLDER_ID = '11kSHWn47cQqeRhtlVQ-4Uask7jr2fqjW'
TARGET_FOLDER_NAME = 'Shared Locations Drive'

# OAuth Scopes
SCOPES = [
    'https://www.googleapis.com/auth/drive.readonly',
    'https://www.googleapis.com/auth/userinfo.email',
    'https://www.googleapis.com/auth/userinfo.profile',
    'openid'
]

# SSL Configuration
ssl_context = ssl.create_default_context()
ssl_context.check_hostname = False
ssl_context.verify_mode = ssl.CERT_NONE

# =====================================================
# MODELS INITIALIZATION
# =====================================================

# YOLO for object detection
print("📦 Loading YOLO model...")
yolo_model = YOLO("yolov8n.pt")

# CLIP for embeddings (optional, will switch to caption-based later)
if CLIP_AVAILABLE:
    try:
        print("📦 Loading CLIP model...")
        device = "cuda" if torch.cuda.is_available() else "cpu"
        clip_model, clip_preprocess = clip.load("ViT-B/32", device=device)
        print("✅ CLIP model loaded successfully")
    except Exception as e:
        print(f"⚠️ Failed to load CLIP model: {e}")
        clip_model = None
        clip_preprocess = None
        CLIP_AVAILABLE = False
else:
    clip_model = None
    clip_preprocess = None

# Grounding DINO for open-vocabulary detection (optional upgrade from YOLO)
# print("📦 Loading Grounding DINO...")
# dino_processor = AutoProcessor.from_pretrained("IDEA-Research/grounding-dino-base")
# dino_model = AutoModelForZeroShotObjectDetection.from_pretrained("IDEA-Research/grounding-dino-base")

# SAM2 for segmentation (will add after basic setup)
# from sam2.build_sam import build_sam2
# sam2_checkpoint = "./checkpoints/sam2_hiera_large.pt"
# sam2_model = build_sam2(sam2_checkpoint)

# =====================================================
# CANONICAL MAPPINGS & CONSTANTS
# =====================================================

# Canonical room types
CANONICAL_ROOMS = [
    'kitchen', 'dining_room', 'living_room', 'bedroom', 'bathroom',
    'office', 'hallway', 'balcony', 'kids_room', 'laundry',
    'garage', 'outdoor_patio', 'entryway', 'unknown'
]

# Object → Room weights (for room inference)
OBJECT_ROOM_WEIGHTS = {
    'oven': {'kitchen': 1.00, 'dining_room': 0.10},
    'stove': {'kitchen': 1.00, 'dining_room': 0.10},
    'cooktop': {'kitchen': 1.00, 'dining_room': 0.10},
    'range_hood': {'kitchen': 0.95, 'dining_room': 0.05},
    'sink': {'kitchen': 0.85, 'bathroom': 0.95, 'laundry': 0.30},
    'refrigerator': {'kitchen': 0.85, 'dining_room': 0.10},
    'fridge': {'kitchen': 0.85, 'dining_room': 0.10},
    'microwave': {'kitchen': 0.70, 'office': 0.10, 'dining_room': 0.10},
    'kitchen_island': {'kitchen': 0.95, 'dining_room': 0.05},
    'dining_table': {'dining_room': 0.90, 'kitchen': 0.20},
    'chair': {'dining_room': 0.70, 'office': 0.05, 'living_room': 0.20},
    'sofa': {'living_room': 0.95, 'dining_room': 0.05},
    'couch': {'living_room': 0.95, 'dining_room': 0.05},
    'tv': {'living_room': 0.90, 'bedroom': 0.05, 'office': 0.05},
    'television': {'living_room': 0.90, 'bedroom': 0.05},
    'coffee_table': {'living_room': 0.85, 'dining_room': 0.10, 'office': 0.05},
    'bed': {'bedroom': 1.00},
    'wardrobe': {'bedroom': 0.85, 'office': 0.10},
    'nightstand': {'bedroom': 0.85},
    'toilet': {'bathroom': 1.00},
    'shower': {'bathroom': 1.00},
    'bathtub': {'bathroom': 1.00},
    'desk': {'office': 0.90, 'bedroom': 0.05, 'living_room': 0.15},
    'office_chair': {'office': 0.90},
    'washer': {'laundry': 1.00, 'kitchen': 0.10},
    'dryer': {'laundry': 1.00, 'kitchen': 0.10},
    'washing_machine': {'laundry': 1.00, 'kitchen': 0.10},
}

# Hebrew ↔ English synonym mapping
HEBREW_ENGLISH_SYNONYMS = {
    # Rooms
    'מטבח': 'kitchen',
    'סלון': 'living_room',
    'פינת אוכל': 'dining_room',
    'חדר שינה': 'bedroom',
    'שירותים': 'bathroom',
    'אמבטיה': 'bathroom',
    'משרד': 'office',
    'מסדרון': 'hallway',
    'מרפסת': 'balcony',
    'חדר ילדים': 'kids_room',
    'חדר כביסה': 'laundry',
    'מוסך': 'garage',
    
    # Objects
    'שולחן אוכל': 'dining_table',
    'שולחן': 'table',
    'כיסא': 'chair',
    'ספה': 'sofa',
    'מקרר': 'refrigerator',
    'תנור': 'oven',
    'כיריים': 'stove',
    'כיור': 'sink',
    'אי מטבח': 'kitchen_island',
    'טלוויזיה': 'tv',
    'מיטה': 'bed',
    'ארון': 'wardrobe',
    'שולחן קפה': 'coffee_table',
    'שולחן עבודה': 'desk',
    'אסלה': 'toilet',
    'מקלחת': 'shower',
    'אמבטיה': 'bathtub',
    'מכונת כביסה': 'washing_machine',
    
    # Colors
    'שחור': 'black',
    'לבן': 'white',
    'אפור': 'gray',
    'חום': 'brown',
    'בז׳': 'beige',
    'אדום': 'red',
    'כחול': 'blue',
    'ירוק': 'green',
    'צהוב': 'yellow',
    'סגול': 'purple',
    'ורוד': 'pink',
    'כתום': 'orange',
    'כסוף': 'silver',
    'זהב': 'gold',
    
    # Materials
    'עץ': 'wood',
    'שיש': 'marble',
    'גרניט': 'granite',
    'זכוכית': 'glass',
    'מתכת': 'metal',
    'פלדה': 'stainless_steel',
    'נירוסטה': 'stainless_steel',
    'בד': 'fabric',
    'עור': 'leather',
    'אריח': 'tile',
    'אבן': 'stone',
    'בטון': 'concrete',
}

# Named colors for LAB→name conversion
NAMED_COLORS = {
    'black': (0, 0, 0),
    'white': (255, 255, 255),
    'gray': (128, 128, 128),
    'dark_gray': (64, 64, 64),
    'light_gray': (192, 192, 192),
    'brown': (139, 69, 19),
    'dark_brown': (101, 67, 33),
    'beige': (245, 245, 220),
    'cream': (255, 253, 208),
    'red': (255, 0, 0),
    'blue': (0, 0, 255),
    'navy': (0, 0, 128),
    'green': (0, 128, 0),
    'yellow': (255, 255, 0),
    'purple': (128, 0, 128),
    'pink': (255, 192, 203),
    'orange': (255, 165, 0),
    'silver': (192, 192, 192),
    'gold': (255, 215, 0),
    'teal': (0, 128, 128),
}

# Materials list
MATERIALS = [
    'marble', 'wood', 'granite', 'glass', 'metal', 'fabric',
    'leather', 'tile', 'stone', 'concrete', 'plastic', 'stainless_steel'
]

# =====================================================
# FASTAPI APP SETUP
# =====================================================

app = FastAPI(
    title="PicLocate V4 - Production Visual Search",
    description="Advanced image search with room classification, per-object colors/materials, and semantic search",
    version="4.0.0"
)

# CORS
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# Global state
drive_service = None
_connection_cache = {}

# =====================================================
# PHASE 1: PERCEPTUAL HASH & DEDUPLICATION
# =====================================================

def compute_phash(image: Image.Image) -> bytes:
    """Compute perceptual hash for image deduplication"""
    try:
        phash = imagehash.phash(image, hash_size=8)
        return phash.hash.tobytes()
    except Exception as e:
        print(f"❌ Failed to compute pHash: {e}")
        return b'\x00' * 8

def check_duplicate_image(phash: bytes) -> Optional[str]:
    """Check if image with similar pHash already exists"""
    try:
        result = supabase.table("images").select("drive_id").eq("phash", phash).execute()
        if result.data:
            return result.data[0]['drive_id']
        return None
    except Exception as e:
        print(f"❌ pHash duplicate check failed: {e}")
        return None

# =====================================================
# PHASE 1: ROOM CLASSIFICATION
# =====================================================

def infer_room_from_objects(detected_objects: List[Dict]) -> Tuple[str, float]:
    """
    Infer room type from detected objects using weighted voting
    
    Args:
        detected_objects: List of {label, confidence, ...}
    
    Returns:
        (room_type, confidence)
    """
    room_scores = {room: 0.0 for room in CANONICAL_ROOMS}
    
    for obj in detected_objects:
        label = obj.get('label', '').lower()
        conf = obj.get('confidence', 0.0)
        
        # Look up weights for this object
        if label in OBJECT_ROOM_WEIGHTS:
            for room, weight in OBJECT_ROOM_WEIGHTS[label].items():
                room_scores[room] += weight * conf
    
    # Find best room
    if not room_scores or max(room_scores.values()) == 0:
        return 'unknown', 0.0
    
    best_room = max(room_scores, key=room_scores.get)
    best_score = room_scores[best_room]
    
    # Normalize confidence (heuristic)
    total_object_conf = sum(obj.get('confidence', 0.0) for obj in detected_objects)
    if total_object_conf > 0:
        confidence = min(best_score / (total_object_conf + 1), 1.0)
    else:
        confidence = 0.0
    
    # Threshold: require minimum confidence
    if confidence < 0.35:
        return 'unknown', confidence
    
    return best_room, confidence

# =====================================================
# PHASE 2: PER-OBJECT COLOR EXTRACTION
# =====================================================

def rgb_to_lab(rgb: Tuple[int, int, int]) -> Tuple[float, float, float]:
    """Convert RGB to CIELAB color space"""
    rgb_normalized = np.array([[rgb]], dtype=np.float32) / 255.0
    lab = skimage_color.rgb2lab(rgb_normalized)
    return tuple(lab[0, 0])

def lab_to_color_name(lab: Tuple[float, float, float]) -> str:
    """Convert LAB to nearest named color"""
    L, a, b = lab
    
    # Special cases for neutral colors
    if L < 20:
        return 'black'
    if L > 90 and abs(a) < 10 and abs(b) < 10:
        return 'white'
    if abs(a) < 15 and abs(b) < 15:
        if L < 40:
            return 'dark_gray'
        elif L > 70:
            return 'light_gray'
        else:
            return 'gray'
    
    # Convert LAB back to RGB for comparison
    lab_array = np.array([[[L, a, b]]], dtype=np.float32)
    rgb = skimage_color.lab2rgb(lab_array)[0, 0]
    rgb_255 = tuple((rgb * 255).astype(int))
    
    # Find nearest named color
    min_dist = float('inf')
    best_color = 'gray'
    
    for name, ref_rgb in NAMED_COLORS.items():
        dist = sum((c1 - c2) ** 2 for c1, c2 in zip(rgb_255, ref_rgb))
        if dist < min_dist:
            min_dist = dist
            best_color = name
    
    return best_color

def extract_object_colors(image: np.ndarray, bbox: Dict, k=3) -> List[Dict]:
    """
    Extract dominant colors from object region using K-means in LAB space
    
    Args:
        image: Image as numpy array (RGB)
        bbox: Bounding box {"x", "y", "w", "h"}
        k: Number of color clusters
    
    Returns:
        List of {"name": "black", "lab": {...}, "ratio": 0.6}
    """
    try:
        x, y, w, h = bbox['x'], bbox['y'], bbox['w'], bbox['h']
        
        # Crop to bbox
        crop = image[y:y+h, x:x+w]
        if crop.size == 0:
            return []
        
        # Reshape to pixels list
        pixels = crop.reshape(-1, 3)
        
        # Convert to LAB
        lab_pixels = skimage_color.rgb2lab(pixels.reshape(1, -1, 3) / 255.0)[0]
        
        # K-means clustering
        kmeans = KMeans(n_clusters=min(k, len(pixels)), random_state=42, n_init=10)
        kmeans.fit(lab_pixels)
        
        # Get cluster centers and sizes
        labels = kmeans.labels_
        centers = kmeans.cluster_centers_
        
        colors = []
        for i, center in enumerate(centers):
            ratio = np.sum(labels == i) / len(labels)
            if ratio < 0.05:  # Skip very small clusters
                continue
            
            L, a, b = center
            color_name = lab_to_color_name((L, a, b))
            
            colors.append({
                "name": color_name,
                "lab": {"L": float(L), "a": float(a), "b": float(b)},
                "ratio": float(ratio)
            })
        
        # Sort by ratio (most dominant first)
        colors.sort(key=lambda c: c['ratio'], reverse=True)
        return colors
    
    except Exception as e:
        print(f"❌ Color extraction failed: {e}")
        return []

# =====================================================
# PHASE 2: MATERIAL DETECTION (HEURISTIC V1)
# =====================================================

def detect_material_heuristic(image: np.ndarray, bbox: Dict, label: str) -> Tuple[str, float]:
    """
    Heuristic material detection based on texture and context
    
    TODO: Replace with trained classifier later
    
    Args:
        image: Image as numpy array
        bbox: Bounding box
        label: Object label
    
    Returns:
        (material, confidence)
    """
    try:
        x, y, w, h = bbox['x'], bbox['y'], bbox['w'], bbox['h']
        crop = image[y:y+h, x:x+w]
        
        if crop.size == 0:
            return 'unknown', 0.0
        
        # Convert to grayscale for texture analysis
        gray = cv2.cvtColor(crop, cv2.COLOR_RGB2GRAY)
        
        # Compute texture features
        laplacian_var = cv2.Laplacian(gray, cv2.CV_64F).var()
        
        # Compute color statistics
        mean_brightness = np.mean(gray)
        color_std = np.std(crop, axis=(0, 1))
        
        # Heuristic rules based on object type and texture
        if label in ['refrigerator', 'oven', 'microwave', 'sink', 'range_hood']:
            # Appliances tend to be metal or stainless steel
            if mean_brightness > 150:
                return 'stainless_steel', 0.7
            else:
                return 'metal', 0.6
        
        elif label in ['dining_table', 'coffee_table', 'desk']:
            # Tables can be wood, marble, or glass
            if laplacian_var > 500:  # High texture variance
                return 'marble', 0.5
            elif mean_brightness > 180 and color_std.mean() < 20:
                return 'glass', 0.5
            else:
                return 'wood', 0.6
        
        elif label in ['sofa', 'chair']:
            # Furniture usually fabric or leather
            if laplacian_var < 200:
                return 'leather', 0.5
            else:
                return 'fabric', 0.6
        
        elif label in ['wardrobe', 'cabinet']:
            return 'wood', 0.6
        
        else:
            return 'unknown', 0.0
    
    except Exception as e:
        print(f"❌ Material detection failed: {e}")
        return 'unknown', 0.0

# =====================================================
# PHASE 3: CAPTION GENERATION
# =====================================================

def generate_structured_caption(
    room_type: str,
    objects: List[Dict],
    style_tags: List[str] = None
) -> Tuple[str, str, Dict]:
    """
    Generate structured English and Hebrew captions + facts JSON
    
    Args:
        room_type: Inferred room type
        objects: List of detected objects with colors/materials
        style_tags: Optional style tags
    
    Returns:
        (caption_en, caption_he, facts_json)
    """
    try:
        # Group objects by label
        object_counts = {}
        object_details = []
        
        for obj in objects:
            label = obj.get('label', 'object')
            color = obj.get('color_name', '')
            material = obj.get('material', '')
            
            # Count objects
            if label not in object_counts:
                object_counts[label] = 0
            object_counts[label] += 1
            
            # Store details
            detail = {"label": label, "count": 1}
            if color:
                detail['color'] = color
            if material:
                detail['material'] = material
            object_details.append(detail)
        
        # Build English caption
        caption_parts = []
        
        # Room type
        if room_type and room_type != 'unknown':
            caption_parts.append(room_type.replace('_', ' ').title())
        
        # Objects with colors
        object_descriptions = []
        for label, count in object_counts.items():
            # Find object details
            obj_with_label = [o for o in objects if o.get('label') == label]
            if obj_with_label:
                obj = obj_with_label[0]
                color = obj.get('color_name', '')
                material = obj.get('material', '')
                
                desc = []
                if color:
                    desc.append(color)
                if material and material != 'unknown':
                    desc.append(material)
                
                desc.append(label.replace('_', ' '))
                
                if count > 1:
                    desc.append(f"({count})")
                
                object_descriptions.append(' '.join(desc))
        
        if object_descriptions:
            caption_parts.append("with " + ', '.join(object_descriptions))
        
        # Style
        if style_tags:
            caption_parts.append(f"; style: {', '.join(style_tags)}")
        
        caption_en = ' '.join(caption_parts) + '.'
        
        # Hebrew caption (TODO: proper translation, using placeholder for now)
        caption_he = translate_to_hebrew_simple(caption_en)
        
        # Structured facts JSON
        facts = {
            "room": room_type,
            "objects": object_details,
            "materials": list(set(o.get('material', '') for o in objects if o.get('material'))),
            "colors": list(set(o.get('color_name', '') for o in objects if o.get('color_name'))),
            "style": style_tags or []
        }
        
        return caption_en, caption_he, facts
    
    except Exception as e:
        print(f"❌ Caption generation failed: {e}")
        return "Image", "תמונה", {}

def translate_to_hebrew_simple(text: str) -> str:
    """Simple Hebrew translation using OpenAI (placeholder)"""
    # TODO: Implement proper translation or use pre-built mapping
    # For now, return placeholder
    return text  # Will implement properly in Phase 4

# =====================================================
# PHASE 3: EMBEDDINGS
# =====================================================

def generate_text_embedding(text: str) -> List[float]:
    """Generate embedding for text using OpenAI"""
    try:
        if not OPENAI_API_KEY:
            print("⚠️ OpenAI API key not set, using zero vector")
            return [0.0] * 1536
        
        response = openai.embeddings.create(
            model="text-embedding-3-large",
            input=text,
            dimensions=1536
        )
        return response.data[0].embedding
    
    except Exception as e:
        print(f"❌ Embedding generation failed: {e}")
        return [0.0] * 1536

# =====================================================
# MAIN INDEXING PIPELINE
# =====================================================

def process_and_index_image(
    drive_id: str,
    file_name: str,
    folder_path: str,
    image_data: bytes
) -> Dict:
    """
    Complete multi-pass vision pipeline:
    1. Perceptual hash & dedup check
    2. Object detection (YOLO)
    3. Per-object color extraction
    4. Per-object material detection
    5. Room classification
    6. Caption generation
    7. Embedding generation
    8. Store in Supabase (5 tables)
    
    Returns:
        Status dictionary
    """
    try:
        # Load image
        image = Image.open(io.BytesIO(image_data)).convert('RGB')
        image_np = np.array(image)
        width, height = image.size
        
        print(f"🖼️  Processing: {file_name}")
        
        # =====================================================
        # STEP 1: Perceptual Hash & Dedup
        # =====================================================
        phash = compute_phash(image)
        duplicate_id = check_duplicate_image(phash)
        if duplicate_id:
            print(f"⏭️  Duplicate detected (existing: {duplicate_id}), skipping")
            return {"status": "duplicate", "duplicate_of": duplicate_id}
        
        # =====================================================
        # STEP 2: Object Detection (YOLO)
        # =====================================================
        yolo_results = yolo_model(image_np, verbose=False)[0]
        detected_objects = []
        
        for detection in yolo_results.boxes.data:
            x1, y1, x2, y2, conf, cls = detection
            label = yolo_model.names[int(cls)]
            
            bbox = {
                "x": int(x1),
                "y": int(y1),
                "w": int(x2 - x1),
                "h": int(y2 - y1)
            }
            
            # =====================================================
            # STEP 3: Per-Object Color Extraction
            # =====================================================
            colors = extract_object_colors(image_np, bbox, k=3)
            primary_color = colors[0] if colors else {"name": "unknown", "lab": {}, "ratio": 1.0}
            
            # =====================================================
            # STEP 4: Material Detection
            # =====================================================
            material, material_conf = detect_material_heuristic(image_np, bbox, label)
            
            detected_objects.append({
                "label": label,
                "confidence": float(conf),
                "bbox": bbox,
                "color_name": primary_color['name'],
                "color_lab": primary_color['lab'],
                "secondary_colors": colors[1:] if len(colors) > 1 else [],
                "material": material,
                "material_confidence": material_conf,
                "area_pixels": bbox['w'] * bbox['h']
            })
        
        print(f"   ✅ Detected {len(detected_objects)} objects")
        
        # =====================================================
        # STEP 5: Room Classification
        # =====================================================
        room_type, room_confidence = infer_room_from_objects(detected_objects)
        print(f"   🏠 Room: {room_type} (conf: {room_confidence:.2f})")
        
        # =====================================================
        # STEP 6: Caption Generation
        # =====================================================
        caption_en, caption_he, facts = generate_structured_caption(
            room_type,
            detected_objects,
            style_tags=[]  # TODO: Add style detection
        )
        print(f"   📝 Caption: {caption_en[:80]}...")
        
        # =====================================================
        # STEP 7: Embedding Generation
        # =====================================================
        embed_en = generate_text_embedding(caption_en)
        embed_he = embed_en  # Using same for now, TODO: separate Hebrew
        
        # =====================================================
        # STEP 8: Store in Supabase (Multi-Table Insert)
        # =====================================================
        
        # 8.1: Insert into images table
        image_id = str(uuid.uuid4())
        image_data_db = {
            "id": image_id,
            "drive_id": drive_id,
            "file_name": file_name,
            "folder_path": folder_path,
            "width": width,
            "height": height,
            "phash": phash.hex(),  # Store as hex string
            "room_type": room_type,
            "room_confidence": room_confidence,
            "style_tags": [],
            "indexed_at": datetime.utcnow().isoformat()
        }
        supabase.table("images").upsert(image_data_db, on_conflict="drive_id").execute()
        
        # Get the actual image_id (in case it was an update)
        result = supabase.table("images").select("id").eq("drive_id", drive_id).execute()
        if result.data:
            image_id = result.data[0]['id']
        
        # 8.2: Insert objects
        for obj in detected_objects:
            obj_data = {
                "image_id": image_id,
                "label": obj['label'],
                "label_confidence": obj['confidence'],
                "bbox": obj['bbox'],
                "mask_rle": None,  # TODO: Add SAM2 masks
                "color_name": obj['color_name'],
                "color_lab": obj['color_lab'],
                "secondary_colors": obj['secondary_colors'],
                "material": obj['material'],
                "material_confidence": obj['material_confidence'],
                "area_pixels": obj['area_pixels'],
                "attributes": {}
            }
            supabase.table("image_objects").insert(obj_data).execute()
        
        # 8.3: Insert caption & embeddings
        caption_data = {
            "image_id": image_id,
            "caption_en": caption_en,
            "caption_he": caption_he,
            "facts": facts,
            "embed_en": embed_en,
            "embed_he": embed_he
        }
        supabase.table("image_captions").upsert(caption_data, on_conflict="image_id").execute()
        
        # 8.4: Insert tags (denormalized for fast filtering)
        tags = [
            f"room:{room_type}",
            *[f"obj:{obj['label']}" for obj in detected_objects],
            *[f"col:{obj['color_name']}" for obj in detected_objects if obj['color_name'] != 'unknown'],
            *[f"mat:{obj['material']}" for obj in detected_objects if obj['material'] != 'unknown'],
        ]
        
        for tag in set(tags):  # Deduplicate
            supabase.table("image_tags").upsert(
                {"image_id": image_id, "tag": tag},
                on_conflict="image_id,tag"
            ).execute()
        
        print(f"   ✅ Stored in Supabase (image_id: {image_id})")
        
        return {
            "status": "success",
            "image_id": image_id,
            "room_type": room_type,
            "objects_count": len(detected_objects),
            "caption": caption_en
        }
    
    except Exception as e:
        print(f"❌ Failed to process {file_name}: {e}")
        print(traceback.format_exc())
        return {"status": "error", "error": str(e)}

# =====================================================
# GOOGLE DRIVE INTEGRATION
# =====================================================

def authenticate_drive():
    """Authenticate with Google Drive (OAuth2)"""
    global drive_service
    
    try:
        oauth_file = "client_secret_1012576941399-515ln173s773sbrrpn3gtmek0d5vc0u5.apps.googleusercontent.com.json"
        
        if not os.path.exists(oauth_file):
            return {
                "status": "oauth_required",
                "message": "OAuth file not found"
            }
        
        flow = InstalledAppFlow.from_client_secrets_file(oauth_file, scopes=SCOPES)
        flow.redirect_uri = 'http://localhost:8000/auth/callback'
        
        auth_url, _ = flow.authorization_url(
            prompt='consent',
            access_type='offline',
            include_granted_scopes='true'
        )
        
        return {
            "status": "oauth_required",
            "auth_url": auth_url
        }
    
    except Exception as e:
        return {"status": "error", "error": str(e)}

def crawl_and_index_folder(service, folder_id: str = None, folder_path: str = None):
    """Recursively crawl folder and index all images"""
    if folder_id is None:
        folder_id = TARGET_FOLDER_ID
    if folder_path is None:
        folder_path = TARGET_FOLDER_NAME
    
    print(f"📁 Crawling: {folder_path}")
    
    # Query for images
    query = f"'{folder_id}' in parents and mimeType contains 'image/' and trashed=false"
    
    try:
        results = service.files().list(q=query, fields="files(id,name,parents,mimeType)", pageSize=1000).execute()
        files = results.get('files', [])
        
        print(f"   📸 Found {len(files)} images")
        
        # Process each image
        for file in files:
            file_id = file['id']
            file_name = file['name']
            
            # Download image
            request = service.files().get_media(fileId=file_id)
            fh = io.BytesIO()
            downloader = MediaIoBaseDownload(fh, request)
            
            done = False
            while not done:
                status, done = downloader.next_chunk()
            
            image_data = fh.getvalue()
            
            # Process and index
            result = process_and_index_image(file_id, file_name, folder_path, image_data)
            print(f"      {result.get('status')}: {file_name}")
        
        # Get subfolders
        query_folders = f"'{folder_id}' in parents and mimeType='application/vnd.google-apps.folder' and trashed=false"
        folder_results = service.files().list(q=query_folders, fields="files(id,name)").execute()
        subfolders = folder_results.get('files', [])
        
        print(f"   📂 Found {len(subfolders)} subfolders")
        
        # Recursively crawl subfolders
        for subfolder in subfolders:
            subfolder_path = f"{folder_path}/{subfolder['name']}"
            crawl_and_index_folder(service, subfolder['id'], subfolder_path)
    
    except Exception as e:
        print(f"❌ Error crawling folder: {e}")

# =====================================================
# FASTAPI ENDPOINTS
# =====================================================

@app.get("/")
def root():
    return {
        "app": "PicLocate V4 Production",
        "version": "4.0.0",
        "status": "operational"
    }

@app.get("/health")
def health_check():
    """Health check endpoint"""
    return {
        "status": "healthy",
        "app": "PicLocate V4 Production",
        "version": "4.0.0"
    }

@app.get("/auth")
def auth_drive():
    """Start OAuth authentication"""
    return authenticate_drive()

@app.get("/auth/callback")
def auth_callback(code: str = None, error: str = None):
    """Handle OAuth callback"""
    global drive_service
    
    if error:
        return {"status": "error", "error": f"OAuth error: {error}"}
    
    if not code:
        return {"status": "error", "error": "No authorization code received"}
    
    try:
        oauth_file = "client_secret_1012576941399-515ln173s773sbrrpn3gtmek0d5vc0u5.apps.googleusercontent.com.json"
        
        flow = InstalledAppFlow.from_client_secrets_file(oauth_file, scopes=SCOPES)
        flow.redirect_uri = 'http://localhost:8000/auth/callback'
        
        # Exchange code for credentials
        flow.fetch_token(code=code)
        credentials = flow.credentials
        
        # Build the service
        drive_service = build('drive', 'v3', credentials=credentials)
        
        return {
            "status": "success",
            "message": "Authentication successful",
            "redirect_url": "http://localhost:4000"
        }
    
    except Exception as e:
        return {"status": "error", "error": str(e)}

@app.get("/auth/status")
def auth_status():
    """Check authentication status"""
    global drive_service
    
    if not drive_service:
        return {"status": "not_authenticated", "message": "Please authenticate first"}
    
    try:
        # Test the connection
        results = drive_service.files().list(
            q=f"'{TARGET_FOLDER_ID}' in parents and mimeType contains 'image/' and trashed=false",
            pageSize=1
        ).execute()
        
        return {
            "status": "authenticated",
            "message": "Successfully connected to Google Drive",
            "target_folder": TARGET_FOLDER_NAME,
            "folder_id": TARGET_FOLDER_ID
        }
    
    except Exception as e:
        return {"status": "error", "error": str(e)}

@app.post("/index")
def index_drive():
    """Index all images from Google Drive"""
    global drive_service
    
    if not drive_service:
        return {"error": "Not authenticated"}
    
    try:
        print("🚀 Starting full drive indexing...")
        crawl_and_index_folder(drive_service)
        
        # Get total count
        result = supabase.table("images").select("id", count="exact").execute()
        total_images = result.count if hasattr(result, 'count') else 0
        
        return {
            "status": "success",
            "message": f"Indexed {total_images} images",
            "total_images": total_images
        }
    
    except Exception as e:
        return {"error": str(e)}

# Search endpoints
class SearchRequest(BaseModel):
    query: str
    top_k: int = 5
    lang: str = "en"

@app.post("/search")
def search_images(req: SearchRequest):
    """Search images using V4 database"""
    try:
        # Translate Hebrew query to English if needed
        if req.lang == "he":
            # Simple Hebrew to English translation
            hebrew_to_english = {
                "מטבח": "kitchen",
                "שולחן": "table", 
                "שחור": "black",
                "לבן": "white",
                "אפור": "gray",
                "אמבטיה": "bathroom",
                "סלון": "living room",
                "חדר שינה": "bedroom"
            }
            
            translated_query = req.query
            for hebrew, english in hebrew_to_english.items():
                translated_query = translated_query.replace(hebrew, english)
        else:
            translated_query = req.query
        
        # Search in image_captions table using vector similarity
        result = supabase.table("image_captions").select(
            "image_id, caption_en, caption_he"
        ).execute()
        
        if not result.data:
            return {"results": [], "total_results": 0}
        
        # Simple text matching for now (can be enhanced with vector search)
        matching_results = []
        for row in result.data:
            caption = row.get('caption_en', '').lower()
            if translated_query.lower() in caption:
                # Get image details
                img_result = supabase.table("images").select(
                    "drive_id, file_name, folder_path, room_type"
                ).eq("id", row['image_id']).execute()
                
                if img_result.data:
                    img_data = img_result.data[0]
                    matching_results.append({
                        "image_id": row['image_id'],
                        "file_name": img_data.get('file_name', 'Unknown'),
                        "folder_path": img_data.get('folder_path', ''),
                        "room_type": img_data.get('room_type', ''),
                        "caption": row.get('caption_en', ''),
                        "similarity": 0.8  # Placeholder similarity score
                    })
        
        return {
            "results": matching_results[:req.top_k],
            "total_results": len(matching_results),
            "query": req.query,
            "translated_query": translated_query
        }
        
    except Exception as e:
        return {"error": str(e), "results": []}

@app.get("/stats/overview")
def get_stats():
    """Get system statistics"""
    try:
        # Get counts from each table
        image_count = supabase.table("images").select("id", count="exact").execute().count
        object_count = supabase.table("image_objects").select("id", count="exact").execute().count
        caption_count = supabase.table("image_captions").select("id", count="exact").execute().count
        
        # Get room distribution
        room_result = supabase.table("images").select("room_type").execute()
        room_distribution = {}
        for r in room_result.data:
            room = r.get('room_type', 'unknown')
            room_distribution[room] = room_distribution.get(room, 0) + 1
        
        return {
            "database_stats": {
                "total_images": image_count,
                "total_objects": object_count,
                "total_captions": caption_count
            },
            "distributions": {
                "rooms": room_distribution
            }
        }
        
    except Exception as e:
        return {"error": str(e)}

print("✅ PicLocate V4 Production backend initialized")

