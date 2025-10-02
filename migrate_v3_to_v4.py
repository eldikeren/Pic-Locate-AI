"""
Migrate data from V3 image_embeddings table to V4 schema tables
"""

from supabase import create_client
import json
from datetime import datetime

def migrate_v3_to_v4():
    """Migrate existing V3 data to V4 schema"""
    try:
        supabase = create_client(
            "https://gezmablgrepoaamtizts.supabase.co",
            "eyJhbGciOiJIUzI1NiIsInR5cCI6IkpXVCJ9.eyJpc3MiOiJzdXBhYmFzZSIsInJlZiI6Imdlem1hYmxncmVwb2FhbXRpenRzIiwicm9sZSI6ImFub24iLCJpYXQiOjE3NTkxNzg2MzMsImV4cCI6MjA3NDc1NDYzM30.lJjaubEzeET8OwcHWJ_x_pOAXd8Bc1yDbpdvKianLM0"
        )
        
        print("Starting V3 to V4 migration...")
        print("=" * 60)
        
        # Get all V3 records
        print("Fetching V3 data...")
        v3_result = supabase.table('image_embeddings').select('*').execute()
        v3_records = v3_result.data
        
        print(f"Found {len(v3_records)} records in V3 table")
        
        if not v3_records:
            print("No V3 records to migrate")
            return
        
        migrated_count = 0
        error_count = 0
        
        for i, record in enumerate(v3_records):
            try:
                file_name = record['file_name']
                # Handle Unicode characters safely
                try:
                    print(f"Migrating {i+1}/{len(v3_records)}: {file_name}")
                except UnicodeEncodeError:
                    print(f"Migrating {i+1}/{len(v3_records)}: [Unicode filename]")
                
                # 1. Insert into images table
                image_data = {
                    "drive_id": record['file_id'],
                    "file_name": record['file_name'],
                    "folder_path": record.get('folder', ''),
                    "width": None,  # Not available in V3
                    "height": None,  # Not available in V3
                    "phash": None,  # Not available in V3
                    "room_type": record.get('room_type', 'unknown'),
                    "room_confidence": 0.5,  # Default confidence
                    "style_tags": [],
                    "indexed_at": record.get('created_at', datetime.utcnow().isoformat())
                }
                
                # Upsert image record
                supabase.table("images").upsert(image_data, on_conflict="drive_id").execute()
                
                # Get the image_id
                result = supabase.table("images").select("id").eq("drive_id", record['file_id']).execute()
                if result.data:
                    image_id = result.data[0]['id']
                else:
                    print(f"  Error: Could not get image_id for {record['file_name']}")
                    error_count += 1
                    continue
                
                # 2. Insert objects (if available)
                objects = record.get('objects', [])
                if objects and isinstance(objects, list):
                    for obj in objects:
                        if isinstance(obj, dict):
                            obj_data = {
                                "image_id": image_id,
                                "label": obj.get('label', 'unknown'),
                                "label_confidence": obj.get('confidence', 0.5),
                                "bbox": obj.get('bbox', {}),
                                "mask_rle": None,
                                "color_name": obj.get('color_name', 'unknown'),
                                "color_lab": obj.get('color_lab', {}),
                                "secondary_colors": [],
                                "material": obj.get('material', 'unknown'),
                                "material_confidence": 0.5,
                                "area_pixels": 0,
                                "attributes": {}
                            }
                            supabase.table("image_objects").insert(obj_data).execute()
                
                # 3. Insert caption & embedding
                caption_data = {
                    "image_id": image_id,
                    "caption_en": f"Image with {len(objects)} objects",
                    "caption_he": f"תמונה עם {len(objects)} אובייקטים",
                    "facts": {
                        "room": record.get('room_type', 'unknown'),
                        "objects": objects,
                        "materials": [],
                        "colors": record.get('colors', []),
                        "style": []
                    },
                    "embed_en": record.get('embedding', []),
                    "embed_he": record.get('embedding', [])  # Use same embedding for now
                }
                supabase.table("image_captions").upsert(caption_data, on_conflict="image_id").execute()
                
                # 4. Insert tags
                tags = [f"room:{record.get('room_type', 'unknown')}"]
                if objects:
                    for obj in objects:
                        if isinstance(obj, dict):
                            tags.append(f"obj:{obj.get('label', 'unknown')}")
                            if obj.get('color_name'):
                                tags.append(f"col:{obj['color_name']}")
                
                for tag in set(tags):
                    supabase.table("image_tags").upsert(
                        {"image_id": image_id, "tag": tag},
                        on_conflict="image_id,tag"
                    ).execute()
                
                migrated_count += 1
                
            except Exception as e:
                print(f"  Error migrating {record['file_name']}: {e}")
                error_count += 1
        
        print("=" * 60)
        print("MIGRATION COMPLETE")
        print("=" * 60)
        print(f"Successfully migrated: {migrated_count} records")
        print(f"Errors: {error_count} records")
        print()
        print("V4 schema tables now contain:")
        print("- images: Main image records")
        print("- image_objects: Detected objects")
        print("- image_captions: Captions and embeddings")
        print("- image_tags: Searchable tags")
        
    except Exception as e:
        print(f"Migration error: {e}")

if __name__ == "__main__":
    migrate_v3_to_v4()
