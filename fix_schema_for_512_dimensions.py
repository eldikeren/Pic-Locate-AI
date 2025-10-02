"""
Fix the V4 schema to use 512 dimensions to match V3 data
"""

def fix_schema_for_512_dimensions():
    """Provide SQL to fix the schema for 512 dimensions"""
    print("Fixing V4 schema for 512 dimensions (to match V3 data)")
    print("=" * 60)
    print("The V3 data has 512-dimensional embeddings, but we created")
    print("the V4 schema expecting 1536 dimensions. Let's fix this.")
    print()
    print("Run this SQL in Supabase SQL Editor:")
    print()
    print("-- Step 1: Drop the existing table")
    print("DROP TABLE IF EXISTS image_captions CASCADE;")
    print()
    print("-- Step 2: Recreate with 512 dimensions (matching V3 data)")
    print("CREATE TABLE image_captions (")
    print("    image_id uuid PRIMARY KEY REFERENCES images(id) ON DELETE CASCADE,")
    print("    caption_en text,")
    print("    caption_he text,")
    print("    facts jsonb,")
    print("    embed_en vector(512),")
    print("    embed_he vector(512)")
    print(");")
    print()
    print("-- Step 3: Create indexes")
    print("CREATE INDEX image_captions_embed_en_idx ON image_captions")
    print("USING ivfflat (embed_en vector_cosine_ops) WITH (lists = 100);")
    print()
    print("CREATE INDEX image_captions_embed_he_idx ON image_captions")
    print("USING ivfflat (embed_he vector_cosine_ops) WITH (lists = 100);")
    print()
    print("This will create the correct schema for 512-dimensional embeddings")
    print("that match your existing V3 data. After this, the migration will work!")

if __name__ == "__main__":
    fix_schema_for_512_dimensions()
