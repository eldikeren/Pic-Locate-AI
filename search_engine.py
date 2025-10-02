"""
Phase 4: Advanced Search Engine
- Query parsing (Hebrew/English)
- SQL filtering + Vector similarity
- Weighted ranking with explainability
"""

import re
from typing import List, Dict, Tuple, Optional
from dataclasses import dataclass
import numpy as np

# Hebrew synonyms (imported from main)
from fastapi_drive_ai_v4_production import HEBREW_ENGLISH_SYNONYMS, generate_text_embedding, supabase

@dataclass
class SearchConstraints:
    """Parsed search constraints"""
    room: Optional[str] = None
    objects: List[Dict[str, str]] = None  # [{"label": "dining_table", "color": "black", "material": "marble"}]
    colors: List[str] = None
    materials: List[str] = None
    style: List[str] = None
    min_count: Dict[str, int] = None  # {"dining_table": 1, "chair": 4}
    free_text: str = ""  # Residual text for semantic search
    
    def __post_init__(self):
        if self.objects is None:
            self.objects = []
        if self.colors is None:
            self.colors = []
        if self.materials is None:
            self.materials = []
        if self.style is None:
            self.style = []
        if self.min_count is None:
            self.min_count = {}

class QueryParser:
    """Parse Hebrew/English queries into structured constraints"""
    
    def __init__(self):
        self.he_to_en = HEBREW_ENGLISH_SYNONYMS
        # Reverse mapping
        self.en_to_he = {v: k for k, v in self.he_to_en.items()}
    
    def translate_hebrew_to_english(self, text: str) -> str:
        """Translate Hebrew words to English using synonym map"""
        words = text.split()
        translated = []
        
        for word in words:
            # Remove punctuation
            clean_word = re.sub(r'[^\w\s]', '', word)
            
            if clean_word in self.he_to_en:
                translated.append(self.he_to_en[clean_word])
            else:
                translated.append(word)
        
        return ' '.join(translated)
    
    def detect_language(self, text: str) -> str:
        """Detect if text is Hebrew or English"""
        # Simple heuristic: check for Hebrew characters
        hebrew_chars = re.findall(r'[\u0590-\u05FF]', text)
        return 'hebrew' if len(hebrew_chars) > len(text) * 0.3 else 'english'
    
    def extract_room(self, text: str) -> Optional[str]:
        """Extract room type from query"""
        text_lower = text.lower()
        
        # Try direct match
        room_keywords = [
            'kitchen', 'living room', 'bedroom', 'bathroom', 'dining room',
            'office', 'hallway', 'balcony', 'kids room', 'laundry'
        ]
        
        for room in room_keywords:
            if room in text_lower or room.replace(' ', '_') in text_lower:
                return room.replace(' ', '_')
        
        return None
    
    def extract_objects_with_attributes(self, text: str) -> List[Dict[str, str]]:
        """
        Extract objects with their colors and materials
        
        Examples:
            "black dining table" → [{"label": "dining_table", "color": "black"}]
            "marble countertop" → [{"label": "countertop", "material": "marble"}]
            "purple marble table" → [{"label": "table", "color": "purple", "material": "marble"}]
        """
        text_lower = text.lower()
        objects = []
        
        # Known objects
        object_keywords = [
            'dining_table', 'table', 'chair', 'sofa', 'couch', 'refrigerator', 'fridge',
            'oven', 'stove', 'sink', 'kitchen_island', 'island', 'tv', 'television',
            'bed', 'wardrobe', 'coffee_table', 'desk', 'toilet', 'shower', 'bathtub'
        ]
        
        # Known colors
        color_keywords = [
            'black', 'white', 'gray', 'brown', 'beige', 'red', 'blue', 'green',
            'yellow', 'purple', 'pink', 'orange', 'silver', 'gold'
        ]
        
        # Known materials
        material_keywords = [
            'marble', 'wood', 'granite', 'glass', 'metal', 'stainless_steel',
            'fabric', 'leather', 'tile', 'stone', 'concrete'
        ]
        
        # Find objects and their attributes
        for obj in object_keywords:
            if obj in text_lower:
                obj_info = {"label": obj}
                
                # Look for color before object
                words = text_lower.split()
                obj_index = next((i for i, word in enumerate(words) if obj in word), None)
                
                if obj_index is not None and obj_index > 0:
                    # Check previous word for color
                    prev_word = words[obj_index - 1]
                    if prev_word in color_keywords:
                        obj_info['color'] = prev_word
                    
                    # Check for material
                    if obj_index > 1:
                        prev_prev_word = words[obj_index - 2]
                        if prev_prev_word in material_keywords:
                            obj_info['material'] = prev_prev_word
                    
                    # Or material might be right before object
                    if prev_word in material_keywords:
                        obj_info['material'] = prev_word
                
                objects.append(obj_info)
        
        return objects
    
    def extract_counts(self, text: str, objects: List[Dict]) -> Dict[str, int]:
        """Extract object count requirements (e.g., '6 chairs')"""
        counts = {}
        
        for obj_info in objects:
            label = obj_info['label']
            
            # Look for number before object
            pattern = r'(\d+)\s+' + re.escape(label)
            match = re.search(pattern, text.lower())
            
            if match:
                counts[label] = int(match.group(1))
        
        return counts
    
    def parse(self, query: str) -> SearchConstraints:
        """
        Parse query into structured constraints
        
        Example:
            "מטבח עם שולחן שחור ושיש סגול" →
            SearchConstraints(
                room="kitchen",
                objects=[{"label": "dining_table", "color": "black", "material": "marble"}],
                colors=["black", "purple"],
                materials=["marble"],
                ...
            )
        """
        # Detect language and translate if Hebrew
        lang = self.detect_language(query)
        if lang == 'hebrew':
            query_en = self.translate_hebrew_to_english(query)
        else:
            query_en = query
        
        print(f"🔍 Parsing query: {query}")
        if lang == 'hebrew':
            print(f"   → Translated: {query_en}")
        
        # Extract constraints
        room = self.extract_room(query_en)
        objects = self.extract_objects_with_attributes(query_en)
        counts = self.extract_counts(query_en, objects)
        
        # Extract standalone colors and materials
        colors = list(set(obj.get('color') for obj in objects if obj.get('color')))
        materials = list(set(obj.get('material') for obj in objects if obj.get('material')))
        
        # Residual free text (for semantic search)
        free_text = query_en
        
        constraints = SearchConstraints(
            room=room,
            objects=objects,
            colors=colors,
            materials=materials,
            style=[],  # TODO: Extract style keywords
            min_count=counts,
            free_text=free_text
        )
        
        print(f"   ✅ Parsed: room={room}, objects={len(objects)}, colors={colors}, materials={materials}")
        
        return constraints

class HybridSearchEngine:
    """
    Hybrid search: SQL filters + Vector similarity + Weighted ranking
    """
    
    def __init__(self):
        self.parser = QueryParser()
        
        # Ranking weights
        self.w_semantic = 0.55
        self.w_room = 0.15
        self.w_object = 0.20
        self.w_material = 0.10
    
    def build_sql_filter(self, constraints: SearchConstraints) -> Tuple[str, List]:
        """
        Build SQL WHERE clause from constraints
        
        Returns:
            (where_clause, params)
        """
        conditions = []
        params = []
        
        # Room filter
        if constraints.room:
            conditions.append("i.room_type = %s")
            params.append(constraints.room)
        
        # Object filters (with colors and materials)
        for i, obj_info in enumerate(constraints.objects):
            label = obj_info['label']
            
            obj_condition = f"""
            EXISTS (
                SELECT 1 FROM image_objects o{i}
                WHERE o{i}.image_id = i.id
                AND o{i}.label = %s
            """
            params.append(label)
            
            # Add color constraint
            if obj_info.get('color'):
                obj_condition += f" AND o{i}.color_name = %s"
                params.append(obj_info['color'])
            
            # Add material constraint
            if obj_info.get('material'):
                obj_condition += f" AND o{i}.material = %s"
                params.append(obj_info['material'])
            
            obj_condition += ")"
            conditions.append(obj_condition)
        
        # Standalone material filter (any object with this material)
        standalone_materials = [m for m in constraints.materials 
                                if not any(obj.get('material') == m for obj in constraints.objects)]
        for material in standalone_materials:
            conditions.append("""
            EXISTS (
                SELECT 1 FROM image_objects om
                WHERE om.image_id = i.id AND om.material = %s
            )
            """)
            params.append(material)
        
        where_clause = " AND ".join(conditions) if conditions else "1=1"
        
        return where_clause, params
    
    def search(
        self,
        query: str,
        top_k: int = 20,
        explain: bool = True
    ) -> List[Dict]:
        """
        Execute hybrid search
        
        Steps:
        1. Parse query into constraints
        2. SQL filter (fast)
        3. Vector similarity re-rank
        4. Weighted scoring
        5. Explainability
        
        Returns:
            List of results with scores and explanations
        """
        try:
            # Step 1: Parse query
            constraints = self.parser.parse(query)
            
            # Step 2: Generate query embedding
            query_embed = generate_text_embedding(constraints.free_text)
            
            # Step 3: SQL filtering
            where_clause, params = self.build_sql_filter(constraints)
            
            # Build full query (Supabase RPC or raw SQL via PostgREST)
            # For simplicity, using Supabase Python client with filters
            
            query_builder = supabase.table("images").select("""
                id, drive_id, file_name, folder_path, room_type, room_confidence,
                image_captions(caption_en, embed_en)
            """)
            
            # Apply filters
            if constraints.room:
                query_builder = query_builder.eq("room_type", constraints.room)
            
            # Execute
            result = query_builder.execute()
            
            if not result.data:
                return []
            
            # Step 4: Compute similarity scores
            candidates = []
            for row in result.data:
                image_id = row['id']
                caption_data = row.get('image_captions', [{}])[0] if row.get('image_captions') else {}
                embed_en = caption_data.get('embed_en', [])
                
                if not embed_en:
                    continue
                
                # Cosine similarity
                embed_np = np.array(embed_en)
                query_np = np.array(query_embed)
                
                similarity = np.dot(embed_np, query_np) / (
                    np.linalg.norm(embed_np) * np.linalg.norm(query_np) + 1e-8
                )
                
                candidates.append({
                    "image_id": image_id,
                    "drive_id": row['drive_id'],
                    "file_name": row['file_name'],
                    "folder_path": row['folder_path'],
                    "room_type": row['room_type'],
                    "room_confidence": row['room_confidence'],
                    "caption": caption_data.get('caption_en', ''),
                    "semantic_score": float(similarity)
                })
            
            # Step 5: Get object details for candidates
            for candidate in candidates:
                # Fetch objects
                obj_result = supabase.table("image_objects").select("*").eq(
                    "image_id", candidate['image_id']
                ).execute()
                
                candidate['objects'] = obj_result.data if obj_result.data else []
                
                # Compute object match score
                matched_objects = 0
                total_obj_conf = 0
                
                for obj in candidate['objects']:
                    for constraint_obj in constraints.objects:
                        if obj['label'] == constraint_obj['label']:
                            # Check color match
                            color_match = (
                                not constraint_obj.get('color') or 
                                obj.get('color_name') == constraint_obj.get('color')
                            )
                            # Check material match
                            material_match = (
                                not constraint_obj.get('material') or
                                obj.get('material') == constraint_obj.get('material')
                            )
                            
                            if color_match and material_match:
                                matched_objects += 1
                                total_obj_conf += obj.get('label_confidence', 0)
                
                candidate['object_match_count'] = matched_objects
                candidate['object_score'] = (
                    total_obj_conf / len(constraints.objects) 
                    if constraints.objects else 0
                )
                
                # Material score
                matched_materials = sum(
                    1 for obj in candidate['objects']
                    if obj.get('material') in constraints.materials
                )
                candidate['material_score'] = (
                    matched_materials / len(constraints.materials)
                    if constraints.materials else 0
                )
            
            # Step 6: Weighted final score
            for candidate in candidates:
                final_score = (
                    self.w_semantic * candidate['semantic_score'] +
                    self.w_room * (candidate.get('room_confidence', 0) or 0) +
                    self.w_object * candidate['object_score'] +
                    self.w_material * candidate['material_score']
                )
                
                candidate['final_score'] = final_score
                
                # Explainability
                if explain:
                    candidate['explanation'] = {
                        "semantic_contribution": self.w_semantic * candidate['semantic_score'],
                        "room_contribution": self.w_room * (candidate.get('room_confidence', 0) or 0),
                        "object_contribution": self.w_object * candidate['object_score'],
                        "material_contribution": self.w_material * candidate['material_score'],
                        "matched_constraints": {
                            "room": candidate['room_type'] == constraints.room if constraints.room else None,
                            "objects": candidate['object_match_count'],
                            "materials": matched_materials if constraints.materials else 0
                        }
                    }
            
            # Step 7: Sort and return top-k
            candidates.sort(key=lambda x: x['final_score'], reverse=True)
            
            return candidates[:top_k]
        
        except Exception as e:
            print(f"❌ Search failed: {e}")
            import traceback
            print(traceback.format_exc())
            return []

# Singleton instance
search_engine = HybridSearchEngine()

def search_images(query: str, top_k: int = 20) -> List[Dict]:
    """Main search interface"""
    return search_engine.search(query, top_k=top_k, explain=True)

