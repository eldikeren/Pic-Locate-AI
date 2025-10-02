"""
Fix embedding dimensions with memory-efficient approach
"""

from supabase import create_client

def fix_embedding_memory_issue():
    """Provide memory-efficient solution for embedding dimension fix"""
    try:
        supabase = create_client(
            "https://gezmablgrepoaamtizts.supabase.co",
            "eyJhbGciOiJIUzI1NiIsInR5cCI6IkpXVCJ9.eyJpc3MiOiJzdXBhYmFzZSIsInJlZiI6Imdlem1hYmxncmVwb2FhbXRpenRzIiwicm9sZSI6ImFub24iLCJpYXQiOjE3NTkxNzg2MzMsImV4cCI6MjA3NDc1NDYzM30.lJjaubEzeET8OwcHWJ_x_pOAXd8Bc1yDbpdvKianLM0"
        )
        
        print("Fixing embedding dimensions with memory-efficient approach...")
        print("=" * 60)
        print("The memory error occurs because changing vector dimensions requires")
        print("reprocessing all existing data. Here's a memory-efficient solution:")
        print()
        print("SOLUTION 1: Increase maintenance_work_mem (Recommended)")
        print("1. Go to: https://supabase.com/dashboard/project/gezmablgrepoaamtizts")
        print("2. Click on 'Settings' -> 'Database'")
        print("3. Find 'maintenance_work_mem' and increase it to 64MB or 128MB")
        print("4. Then run the SQL commands")
        print()
        print("SOLUTION 2: Alternative - Create new table (If memory increase fails)")
        print("Run this SQL instead:")
        print()
        print("-- Create new table with correct dimensions")
        print("CREATE TABLE image_captions_new (")
        print("    image_id uuid PRIMARY KEY REFERENCES images(id) ON DELETE CASCADE,")
        print("    caption_en text,")
        print("    caption_he text,")
        print("    facts jsonb,")
        print("    embed_en vector(1536),")
        print("    embed_he vector(1536)")
        print(");")
        print()
        print("-- Copy data from old table")
        print("INSERT INTO image_captions_new (image_id, caption_en, caption_he, facts, embed_en, embed_he)")
        print("SELECT image_id, caption_en, caption_he, facts, embed_en, embed_he")
        print("FROM image_captions;")
        print()
        print("-- Drop old table and rename new one")
        print("DROP TABLE image_captions;")
        print("ALTER TABLE image_captions_new RENAME TO image_captions;")
        print()
        print("-- Create indexes")
        print("CREATE INDEX image_captions_embed_en_idx ON image_captions")
        print("USING ivfflat (embed_en vector_cosine_ops) WITH (lists = 100);")
        print()
        print("CREATE INDEX image_captions_embed_he_idx ON image_captions")
        print("USING ivfflat (embed_he vector_cosine_ops) WITH (lists = 100);")
        print()
        print("Try Solution 1 first (increase memory), then Solution 2 if needed.")
        
    except Exception as e:
        print(f"Error: {e}")

if __name__ == "__main__":
    fix_embedding_memory_issue()
