"""
Setup V4 Schema in Supabase
"""

from supabase import create_client

def setup_v4_schema():
    """Create V4 schema tables"""
    try:
        supabase = create_client(
            "https://gezmablgrepoaamtizts.supabase.co",
            "eyJhbGciOiJIUzI1NiIsInR5cCI6IkpXVCJ9.eyJpc3MiOiJzdXBhYmFzZSIsInJlZiI6Imdlem1hYmxncmVwb2FhbXRpenRzIiwicm9sZSI6ImFub24iLCJpYXQiOjE3NTkxNzg2MzMsImV4cCI6MjA3NDc1NDYzM30.lJjaubEzeET8OwcHWJ_x_pOAXd8Bc1yDbpdvKianLM0"
        )
        
        print("Setting up V4 schema...")
        
        # Test if tables exist by trying to query them
        tables_to_check = ['images', 'image_objects', 'image_room_scores', 'image_captions', 'image_tags']
        
        for table in tables_to_check:
            try:
                result = supabase.table(table).select('*').limit(1).execute()
                print(f"Table '{table}' exists")
            except Exception as e:
                print(f"Table '{table}' does not exist: {e}")
        
        print("\n" + "="*60)
        print("V4 SCHEMA SETUP REQUIRED")
        print("="*60)
        print()
        print("The V4 schema tables need to be created in Supabase.")
        print("Please follow these steps:")
        print()
        print("1. Go to: https://supabase.com/dashboard/project/gezmablgrepoaamtizts")
        print("2. Click on 'SQL Editor' in the left sidebar")
        print("3. Copy and paste the contents of 'supabase_schema_v2.sql'")
        print("4. Click 'Run' to execute the schema creation")
        print()
        print("This will create the following tables:")
        print("- images (main image records)")
        print("- image_objects (detected objects with colors/materials)")
        print("- image_room_scores (room classification scores)")
        print("- image_captions (structured captions and embeddings)")
        print("- image_tags (searchable tags)")
        print()
        print("After creating the schema, restart the V4 backend to use the new tables.")
        
    except Exception as e:
        print(f"Error: {e}")

if __name__ == "__main__":
    setup_v4_schema()
