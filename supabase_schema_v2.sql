-- PicLocate Production Schema V2
-- Complete schema for production-grade image search with room classification, 
-- per-object colors/materials, and semantic search

-- Drop existing tables if migrating (be careful in production!)
-- DROP TABLE IF EXISTS image_tags CASCADE;
-- DROP TABLE IF EXISTS image_captions CASCADE;
-- DROP TABLE IF EXISTS image_room_scores CASCADE;
-- DROP TABLE IF EXISTS image_objects CASCADE;
-- DROP TABLE IF EXISTS images CASCADE;

-- Enable required extensions
CREATE EXTENSION IF NOT EXISTS vector;
CREATE EXTENSION IF NOT EXISTS pg_trgm;

-- =====================================================
-- 1. IMAGES TABLE (main image metadata)
-- =====================================================
CREATE TABLE IF NOT EXISTS images (
  id UUID PRIMARY KEY DEFAULT gen_random_uuid(),
  drive_id TEXT UNIQUE NOT NULL,              -- Google Drive file ID
  file_name TEXT NOT NULL,
  folder_path TEXT,
  width INTEGER,
  height INTEGER,
  phash BYTEA,                                -- Perceptual hash for deduplication (8 bytes)
  created_at TIMESTAMPTZ DEFAULT NOW(),
  captured_at TIMESTAMPTZ,                    -- EXIF datetime if present
  room_type TEXT,                             -- Resolved: 'kitchen','living_room','bedroom','bathroom','dining_room','office','hallway','balcony','kids_room','laundry','garage','outdoor_patio','entryway','unknown'
  room_confidence FLOAT,                      -- Confidence score 0-1
  style_tags TEXT[],                          -- ['modern','rustic','minimalist','traditional']
  indexed_at TIMESTAMPTZ DEFAULT NOW()
);

-- Indexes for images table
CREATE INDEX IF NOT EXISTS idx_images_room_type ON images(room_type);
CREATE INDEX IF NOT EXISTS idx_images_folder_path ON images(folder_path);
CREATE INDEX IF NOT EXISTS idx_images_phash ON images(phash);
CREATE INDEX IF NOT EXISTS idx_images_drive_id ON images(drive_id);

-- =====================================================
-- 2. IMAGE_OBJECTS TABLE (detected objects per image)
-- =====================================================
CREATE TABLE IF NOT EXISTS image_objects (
  id UUID PRIMARY KEY DEFAULT gen_random_uuid(),
  image_id UUID REFERENCES images(id) ON DELETE CASCADE,
  label TEXT NOT NULL,                        -- Canonical: 'dining_table','sofa','refrigerator','oven','sink','bed','toilet','shower','bathtub','wardrobe','desk','tv','coffee_table','kitchen_island','stove','range_hood','microwave','chair','washer','dryer'
  label_confidence FLOAT,                     -- Detection confidence 0-1
  bbox JSONB,                                 -- Bounding box: {"x":10,"y":20,"w":100,"h":80}
  mask_rle JSONB,                            -- RLE compressed mask or mask URL
  color_name TEXT,                            -- Primary color: 'black','white','gray','brown','beige','red','blue','green','yellow','purple','pink','orange','silver','gold','cream','navy','teal'
  color_lab JSONB,                           -- LAB color space: {"L":50,"a":10,"b":-5}
  secondary_colors JSONB,                    -- Array of additional colors: [{"name":"gray","lab":{...},"ratio":0.3}]
  material TEXT,                              -- 'marble','wood','granite','glass','metal','fabric','leather','tile','stone','concrete','plastic','stainless_steel'
  material_confidence FLOAT,
  attributes JSONB,                           -- Extra attributes: {"is_island":true,"door_count":2,"drawer_count":4}
  area_pixels INTEGER,                        -- Mask area in pixels
  created_at TIMESTAMPTZ DEFAULT NOW()
);

-- Indexes for image_objects
CREATE INDEX IF NOT EXISTS idx_objects_image_id ON image_objects(image_id);
CREATE INDEX IF NOT EXISTS idx_objects_label ON image_objects(label);
CREATE INDEX IF NOT EXISTS idx_objects_material ON image_objects(material);
CREATE INDEX IF NOT EXISTS idx_objects_color_name ON image_objects(color_name);
CREATE INDEX IF NOT EXISTS idx_objects_label_color ON image_objects(label, color_name);
CREATE INDEX IF NOT EXISTS idx_objects_label_material ON image_objects(label, material);

-- =====================================================
-- 3. IMAGE_ROOM_SCORES (scene classifier probabilities)
-- =====================================================
CREATE TABLE IF NOT EXISTS image_room_scores (
  image_id UUID REFERENCES images(id) ON DELETE CASCADE,
  room TEXT NOT NULL,                         -- 'kitchen','living_room','bedroom','bathroom','dining_room','office','hallway','balcony','kids_room','laundry','garage','outdoor_patio','entryway'
  score FLOAT NOT NULL,                       -- Probability 0-1
  PRIMARY KEY (image_id, room)
);

CREATE INDEX IF NOT EXISTS idx_room_scores_image_id ON image_room_scores(image_id);

-- =====================================================
-- 4. IMAGE_CAPTIONS (structured captions + embeddings)
-- =====================================================
CREATE TABLE IF NOT EXISTS image_captions (
  image_id UUID PRIMARY KEY REFERENCES images(id) ON DELETE CASCADE,
  caption_en TEXT NOT NULL,                   -- English structured caption
  caption_he TEXT,                            -- Hebrew structured caption (optional)
  facts JSONB,                                -- Structured facts: {"room":"kitchen","objects":[{"label":"dining_table","color":"black","count":1}],"materials":["marble","wood"],"style":"modern"}
  embed_en VECTOR(1536),                      -- OpenAI text-embedding-3-large or similar
  embed_he VECTOR(1536),                      -- Hebrew embedding (optional, or translate HE→EN)
  created_at TIMESTAMPTZ DEFAULT NOW()
);

-- Vector similarity indexes (IVFFLAT for speed)
CREATE INDEX IF NOT EXISTS idx_captions_embed_en ON image_captions 
  USING ivfflat (embed_en vector_cosine_ops) WITH (lists = 100);

CREATE INDEX IF NOT EXISTS idx_captions_embed_he ON image_captions 
  USING ivfflat (embed_he vector_cosine_ops) WITH (lists = 100);

-- GIN index for JSONB facts filtering
CREATE INDEX IF NOT EXISTS idx_captions_facts ON image_captions USING gin(facts);

-- =====================================================
-- 5. IMAGE_TAGS (denormalized tags for fast filtering)
-- =====================================================
CREATE TABLE IF NOT EXISTS image_tags (
  image_id UUID REFERENCES images(id) ON DELETE CASCADE,
  tag TEXT NOT NULL,                          -- Format: 'room:kitchen', 'obj:dining_table', 'col:black', 'mat:marble', 'style:modern'
  PRIMARY KEY (image_id, tag)
);

-- Indexes for fast tag lookups
CREATE INDEX IF NOT EXISTS idx_tags_tag ON image_tags(tag);
CREATE INDEX IF NOT EXISTS idx_tags_image_id ON image_tags(image_id);

-- =====================================================
-- HELPER VIEWS (optional, for analytics)
-- =====================================================

-- View: Image summary with object counts
CREATE OR REPLACE VIEW image_summary AS
SELECT 
  i.id,
  i.drive_id,
  i.file_name,
  i.folder_path,
  i.room_type,
  i.room_confidence,
  COUNT(DISTINCT o.id) as object_count,
  ARRAY_AGG(DISTINCT o.label) FILTER (WHERE o.label IS NOT NULL) as detected_objects,
  ARRAY_AGG(DISTINCT o.material) FILTER (WHERE o.material IS NOT NULL) as materials,
  ARRAY_AGG(DISTINCT o.color_name) FILTER (WHERE o.color_name IS NOT NULL) as colors,
  c.caption_en
FROM images i
LEFT JOIN image_objects o ON o.image_id = i.id
LEFT JOIN image_captions c ON c.image_id = i.id
GROUP BY i.id, c.caption_en;

-- =====================================================
-- SAMPLE QUERIES (for testing)
-- =====================================================

-- Find kitchens with black dining tables and marble
-- SELECT i.*, c.caption_en
-- FROM images i
-- JOIN image_objects o1 ON o1.image_id = i.id
-- JOIN image_objects o2 ON o2.image_id = i.id
-- JOIN image_captions c ON c.image_id = i.id
-- WHERE i.room_type = 'kitchen'
--   AND o1.label = 'dining_table' AND o1.color_name = 'black'
--   AND o2.material = 'marble'
-- ORDER BY i.room_confidence DESC;

-- Vector search with filters
-- SELECT i.*, (1 - (c.embed_en <=> $1::vector)) as similarity
-- FROM images i
-- JOIN image_captions c ON c.image_id = i.id
-- WHERE i.room_type = 'kitchen'
--   AND EXISTS (
--     SELECT 1 FROM image_objects o 
--     WHERE o.image_id = i.id 
--     AND o.label = 'dining_table' 
--     AND o.color_name = 'black'
--   )
-- ORDER BY similarity DESC
-- LIMIT 20;

-- =====================================================
-- MAINTENANCE
-- =====================================================

-- Run after bulk inserts
-- VACUUM ANALYZE images;
-- VACUUM ANALYZE image_objects;
-- VACUUM ANALYZE image_captions;
-- VACUUM ANALYZE image_tags;

-- Reindex periodically for vector indexes
-- REINDEX INDEX idx_captions_embed_en;
-- REINDEX INDEX idx_captions_embed_he;

