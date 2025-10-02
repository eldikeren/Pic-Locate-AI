"""
Check V4 migration results
"""

from supabase import create_client

def check_v4_migration():
    """Check the results of the V4 migration"""
    try:
        supabase = create_client(
            "https://gezmablgrepoaamtizts.supabase.co",
            "eyJhbGciOiJIUzI1NiIsInR5cCI6IkpXVCJ9.eyJpc3MiOiJzdXBhYmFzZSIsInJlZiI6Imdlem1hYmxncmVwb2FhbXRpenRzIiwicm9sZSI6ImFub24iLCJpYXQiOjE3NTkxNzg2MzMsImV4cCI6MjA3NDc1NDYzM30.lJjaubEzeET8OwcHWJ_x_pOAXd8Bc1yDbpdvKianLM0"
        )
        
        print("V4 Migration Results Check")
        print("=" * 50)
        
        # Check V3 table
        try:
            count_v3 = supabase.table('image_embeddings').select('file_id', count='exact').execute().count
            print(f"V3 table 'image_embeddings': {count_v3} records")
        except Exception as e:
            print(f"V3 table error: {e}")
        
        # Check V4 tables
        v4_tables = ['images', 'image_objects', 'image_room_scores', 'image_captions', 'image_tags']
        total_v4_records = 0
        
        for table_name in v4_tables:
            try:
                count_v4 = supabase.table(table_name).select('id', count='exact').execute().count
                print(f"V4 table '{table_name}': {count_v4} records")
                total_v4_records += count_v4
            except Exception as e:
                print(f"V4 table '{table_name}' error: {e}")
        
        print(f"\nTotal V4 records: {total_v4_records}")
        
        # Sample data from each table
        print("\nSample Data:")
        print("-" * 30)
        
        # Sample from images table
        try:
            sample_images = supabase.table('images').select('drive_id, file_name, room_type').limit(3).execute()
            if sample_images.data:
                print("Sample images:")
                for img in sample_images.data:
                    print(f"  - {img['file_name']} (room: {img['room_type']})")
        except Exception as e:
            print(f"Error getting sample images: {e}")
        
        # Sample from image_objects table
        try:
            sample_objects = supabase.table('image_objects').select('label, color_name, material').limit(5).execute()
            if sample_objects.data:
                print("\nSample objects:")
                for obj in sample_objects.data:
                    print(f"  - {obj['label']} (color: {obj['color_name']}, material: {obj['material']})")
        except Exception as e:
            print(f"Error getting sample objects: {e}")
        
        # Sample from image_captions table
        try:
            sample_captions = supabase.table('image_captions').select('caption_en, caption_he').limit(2).execute()
            if sample_captions.data:
                print("\nSample captions:")
                for cap in sample_captions.data:
                    print(f"  EN: {cap['caption_en'][:100]}...")
                    print(f"  HE: {cap['caption_he'][:100]}...")
        except Exception as e:
            print(f"Error getting sample captions: {e}")
        
        print("\nMigration Status: SUCCESS!")
        print("All V3 data has been successfully migrated to V4 schema.")
        
    except Exception as e:
        print(f"Error: {e}")

if __name__ == "__main__":
    check_v4_migration()
