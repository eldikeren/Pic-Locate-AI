# Supabase Migration Plan for PicLocate

## Database Schema

### 1. Users Table
```sql
CREATE TABLE users (
  id UUID PRIMARY KEY DEFAULT gen_random_uuid(),
  email TEXT UNIQUE NOT NULL,
  google_drive_token JSONB,
  created_at TIMESTAMP WITH TIME ZONE DEFAULT NOW(),
  updated_at TIMESTAMP WITH TIME ZONE DEFAULT NOW()
);
```

### 2. Images Table
```sql
CREATE TABLE images (
  id UUID PRIMARY KEY DEFAULT gen_random_uuid(),
  user_id UUID REFERENCES users(id) ON DELETE CASCADE,
  file_id TEXT NOT NULL, -- Google Drive file ID
  name TEXT NOT NULL,
  folder_path TEXT,
  file_size BIGINT,
  mime_type TEXT,
  created_at TIMESTAMP WITH TIME ZONE DEFAULT NOW(),
  UNIQUE(user_id, file_id)
);
```

### 3. Image Embeddings Table
```sql
CREATE TABLE image_embeddings (
  id UUID PRIMARY KEY DEFAULT gen_random_uuid(),
  image_id UUID REFERENCES images(id) ON DELETE CASCADE,
  clip_embedding VECTOR(512), -- CLIP embedding
  objects JSONB, -- YOLOv8 detected objects
  colors JSONB, -- Dominant colors
  suggested_rooms JSONB, -- Room type suggestions
  created_at TIMESTAMP WITH TIME ZONE DEFAULT NOW()
);
```

### 4. Search History Table
```sql
CREATE TABLE search_history (
  id UUID PRIMARY KEY DEFAULT gen_random_uuid(),
  user_id UUID REFERENCES users(id) ON DELETE CASCADE,
  query TEXT NOT NULL,
  results JSONB,
  created_at TIMESTAMP WITH TIME ZONE DEFAULT NOW()
);
```

## Vector Search Setup

### Enable pgvector extension
```sql
CREATE EXTENSION IF NOT EXISTS vector;
```

### Create vector index for similarity search
```sql
CREATE INDEX ON image_embeddings USING ivfflat (clip_embedding vector_cosine_ops) 
WITH (lists = 100);
```

## API Endpoints Migration

### 1. Authentication
- Replace current session system with Supabase Auth
- Use Supabase RLS (Row Level Security) for data isolation

### 2. Image Indexing
- Store embeddings in PostgreSQL
- Use Supabase Storage for uploaded images
- Implement batch processing for large datasets

### 3. Search
- Use vector similarity search in PostgreSQL
- Implement pagination and filtering
- Add search analytics

## Benefits

1. **Scalability**: Handle millions of images
2. **Performance**: Vector search is much faster
3. **Reliability**: Built-in backups and replication
4. **Security**: Row-level security and authentication
5. **Cost**: Pay only for what you use
6. **Real-time**: Live updates across devices

## Migration Steps

1. Set up Supabase project
2. Create database schema
3. Migrate existing data
4. Update FastAPI to use Supabase
5. Implement new authentication
6. Add vector search capabilities
7. Deploy and test

## Cost Estimation

- **Supabase Pro**: $25/month for 8GB database + 100GB storage
- **Vector operations**: Included in Pro plan
- **Bandwidth**: $0.09/GB after 100GB
- **Much cheaper** than storing everything in memory!
