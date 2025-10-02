"""
Fix embedding dimensions in V4 schema to accept 1536 dimensions (not 512)
"""

from supabase import create_client

def fix_embedding_dimensions():
    """Update V4 schema to accept 1536-dimensional embeddings"""
    try:
        supabase = create_client(
            "https://gezmablgrepoaamtizts.supabase.co",
            "eyJhbGciOiJIUzI1NiIsInR5cCI6IkpXVCJ9.eyJpc3MiOiJzdXBhYmFzZSIsInJlZiI6Imdlem1hYmxncmVwb2FhbXRpenRzIiwicm9sZSI6ImFub24iLCJpYXQiOjE3NTkxNzg2MzMsImV4cCI6MjA3NDc1NDYzM30.lJjaubEzeET8OwcHWJ_x_pOAXd8Bc1yDbpdvKianLM0"
        )
        
        print("Fixing embedding dimensions in V4 schema...")
        print("=" * 60)
        print("The V4 schema expects 512 dimensions but V3 data has 1536 dimensions.")
        print("We need to update the schema to accept 1536 dimensions.")
        print()
        print("SOLUTION:")
        print("1. Go to: https://supabase.com/dashboard/project/gezmablgrepoaamtizts")
        print("2. Click on 'SQL Editor' in the left sidebar")
        print("3. Run this SQL command:")
        print()
        print("-- Update image_captions table to accept 1536 dimensions")
        print("ALTER TABLE image_captions")
        print("ALTER COLUMN embed_en TYPE vector(1536);")
        print()
        print("ALTER TABLE image_captions")
        print("ALTER COLUMN embed_he TYPE vector(1536);")
        print()
        print("-- Recreate the vector indexes")
        print("DROP INDEX IF EXISTS image_captions_embed_en_idx;")
        print("DROP INDEX IF EXISTS image_captions_embed_he_idx;")
        print()
        print("CREATE INDEX image_captions_embed_en_idx ON image_captions")
        print("USING ivfflat (embed_en vector_cosine_ops)")
        print("WITH (lists = 100);")
        print()
        print("CREATE INDEX image_captions_embed_he_idx ON image_captions")
        print("USING ivfflat (embed_he vector_cosine_ops)")
        print("WITH (lists = 100);")
        print()
        print("After running this SQL, the migration will work!")
        
    except Exception as e:
        print(f"Error: {e}")

if __name__ == "__main__":
    fix_embedding_dimensions()
