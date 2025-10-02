"""
Two-Stage Hybrid Search Engine for PicLocate
Stage A: Fast candidate retrieval (SQL + vector search)
Stage B: VLM verification with final AI verdict
"""

import asyncio
import json
import time
from typing import List, Dict, Any, Optional, Tuple
from dataclasses import dataclass
import openai
from supabase import create_client
import hashlib
from concurrent.futures import ThreadPoolExecutor
import aiohttp

@dataclass
class CandidateImage:
    """Candidate image from Stage A retrieval"""
    id: str
    file_name: str
    folder_path: str
    room_type: str
    room_confidence: float
    sem_score: float
    signed_url: str

@dataclass
class VLMVerdict:
    """VLM verification result"""
    image_id: str
    matches: bool
    confidence: float
    room: str
    evidence: Dict[str, Any]
    notes: str

@dataclass
class FinalResult:
    """Final search result with AI verdict"""
    image_id: str
    file_name: str
    folder_path: str
    vlm_confidence: float
    retrieval_score: float
    final_score: float
    room: str
    evidence: Dict[str, Any]
    match_reasons: List[str]
    ai_notes: str

class HybridSearchEngine:
    """Two-stage hybrid search engine with VLM final verdict"""
    
    def __init__(self, openai_api_key: str, supabase_client):
        self.openai_client = openai.OpenAI(api_key=openai_api_key)
        self.supabase = supabase_client
        self.vlm_model = "gpt-4o-mini"  # Cost-effective VLM
        self.cache = {}  # Simple in-memory cache for VLM results
        
        # Configuration
        self.TOP_K = 120  # Candidates from Stage A
        self.BATCH_SIZE = 12  # Images per VLM call
        self.CUTOFF = 0.72  # VLM confidence threshold
        self.FINAL_LIMIT = 24  # Final results to return
        
        # VLM System Prompt
        self.SYSTEM_PROMPT = """You are a careful visual verifier. For each image, decide if it satisfies the user's request using only what is visible. Be strict: if uncertain, say it does NOT match. Output only JSON by the schema.

Schema:
{
  "verdicts": [
    {
      "image_id": "string",
      "matches": true/false,
      "confidence": 0.0-1.0,
      "room": "kitchen|dining_room|living_room|bedroom|bathroom|office|unknown",
      "evidence": {
        "objects": [{"name": "string", "present": true/false}],
        "colors_on_objects": [{"object": "string", "color": "string"}],
        "materials_on_objects": [{"object": "string", "material": "string", "color": "string", "confidence": 0.0-1.0}],
        "room_features": ["string"]
      },
      "notes": "string - why this matches/does not match"
    }
  ]
}"""
    
    async def search(self, query: str, lang: str = "en", limit: int = 24) -> List[FinalResult]:
        """
        Main search function implementing two-stage pipeline
        
        Args:
            query: Natural language search query
            lang: Language (he|en)
            limit: Maximum results to return
            
        Returns:
            List of FinalResult objects with AI verdicts
        """
        print(f"🔍 Hybrid Search: '{query}' (lang: {lang})")
        start_time = time.time()
        
        # Normalize query (Hebrew → English)
        query_en = await self._normalize_query(query, lang)
        print(f"📝 Normalized query: '{query_en}'")
        
        # Stage A: Fast candidate retrieval
        print("🚀 Stage A: Fast candidate retrieval...")
        candidates = await self._stage_a_retrieval(query_en, self.TOP_K)
        print(f"✅ Retrieved {len(candidates)} candidates")
        
        if not candidates:
            return []
        
        # Stage B: VLM verification
        print("🤖 Stage B: VLM verification...")
        verdicts = await self._stage_b_vlm_verification(query_en, candidates)
        print(f"✅ VLM verified {len(verdicts)} images")
        
        # Filter and rank results
        print("📊 Ranking and filtering...")
        final_results = self._rank_and_filter(verdicts, candidates, limit)
        print(f"✅ Final results: {len(final_results)}")
        
        processing_time = time.time() - start_time
        print(f"⏱️ Total processing time: {processing_time:.2f}s")
        
        return final_results
    
    async def _normalize_query(self, query: str, lang: str) -> str:
        """Normalize query (Hebrew → English translation)"""
        if lang == "he":
            # Simple Hebrew → English mapping for common terms
            he_to_en = {
                "מטבח": "kitchen",
                "סלון": "living room", 
                "חדר שינה": "bedroom",
                "שירותים": "bathroom",
                "אמבטיה": "bathroom",
                "פינת אוכל": "dining room",
                "שולחן": "table",
                "כיסא": "chair",
                "ספה": "sofa",
                "מיטה": "bed",
                "כיור": "sink",
                "מקרר": "refrigerator",
                "תנור": "oven",
                "שחור": "black",
                "לבן": "white",
                "אפור": "gray",
                "חום": "brown",
                "כחול": "blue",
                "ירוק": "green",
                "אדום": "red",
                "שיש": "marble",
                "עץ": "wood",
                "מתכת": "metal"
            }
            
            query_en = query
            for he, en in he_to_en.items():
                query_en = query_en.replace(he, en)
            return query_en
        
        return query
    
    async def _stage_a_retrieval(self, query_en: str, top_k: int) -> List[CandidateImage]:
        """Stage A: Fast candidate retrieval using SQL + vector search"""
        try:
            # Parse query for exact filters
            room_filter = self._extract_room_filter(query_en)
            
            # Get query embedding
            query_embedding = await self._get_query_embedding(query_en)
            
            # Build SQL query
            sql_query = """
            WITH filtered AS (
                SELECT i.id, i.file_name, i.folder_path, i.room_type, i.room_confidence
                FROM images i
                WHERE ($1::text IS NULL OR i.room_type = $1)
            )
            SELECT f.id, f.file_name, f.folder_path, f.room_type, f.room_confidence,
                   (1 - (c.embed_en <=> $2::vector)) as sem_score
            FROM filtered f
            JOIN image_captions c ON c.image_id = f.id
            ORDER BY sem_score DESC
            LIMIT $3;
            """
            
            # Execute query
            result = self.supabase.rpc('execute_sql', {
                'query': sql_query,
                'params': [room_filter, query_embedding, top_k]
            }).execute()
            
            if not result.data:
                return []
            
            # Convert to CandidateImage objects and get signed URLs
            candidates = []
            for row in result.data:
                signed_url = await self._get_signed_url(row['id'])
                if signed_url:
                    candidate = CandidateImage(
                        id=row['id'],
                        file_name=row['file_name'],
                        folder_path=row['folder_path'],
                        room_type=row['room_type'],
                        room_confidence=row['room_confidence'],
                        sem_score=row['sem_score'],
                        signed_url=signed_url
                    )
                    candidates.append(candidate)
            
            return candidates
            
        except Exception as e:
            print(f"Error in Stage A retrieval: {e}")
            return []
    
    async def _stage_b_vlm_verification(self, query_en: str, candidates: List[CandidateImage]) -> List[VLMVerdict]:
        """Stage B: VLM verification with batch processing"""
        verdicts = []
        
        # Process in batches
        for i in range(0, len(candidates), self.BATCH_SIZE):
            batch = candidates[i:i + self.BATCH_SIZE]
            batch_verdicts = await self._verify_batch(query_en, batch)
            verdicts.extend(batch_verdicts)
        
        return verdicts
    
    async def _verify_batch(self, query_en: str, batch: List[CandidateImage]) -> List[VLMVerdict]:
        """Verify a batch of images with VLM"""
        try:
            # Check cache first
            cache_key = self._get_cache_key(query_en, batch)
            if cache_key in self.cache:
                print(f"📋 Cache hit for batch of {len(batch)} images")
                return self.cache[cache_key]
            
            # Prepare VLM request
            messages = [
                {"role": "system", "content": self.SYSTEM_PROMPT},
                {
                    "role": "user",
                    "content": [
                        {"type": "text", "text": f"Query: {query_en}\nReturn an array 'verdicts' following the schema."},
                        *self._prepare_image_content(batch)
                    ]
                }
            ]
            
            # Call VLM
            response = await asyncio.to_thread(
                self.openai_client.chat.completions.create,
                model=self.vlm_model,
                temperature=0,
                response_format={"type": "json_object"},
                messages=messages
            )
            
            # Parse response
            json_response = json.loads(response.choices[0].message.content)
            verdicts = []
            
            for verdict_data in json_response.get('verdicts', []):
                verdict = VLMVerdict(
                    image_id=verdict_data['image_id'],
                    matches=verdict_data['matches'],
                    confidence=verdict_data['confidence'],
                    room=verdict_data['room'],
                    evidence=verdict_data['evidence'],
                    notes=verdict_data['notes']
                )
                verdicts.append(verdict)
            
            # Cache results
            self.cache[cache_key] = verdicts
            
            return verdicts
            
        except Exception as e:
            print(f"Error in VLM verification: {e}")
            return []
    
    def _prepare_image_content(self, batch: List[CandidateImage]) -> List[Dict]:
        """Prepare image content for VLM request"""
        content = []
        for candidate in batch:
            content.extend([
                {"type": "text", "text": f"ImageID: {candidate.id}"},
                {"type": "image_url", "image_url": {"url": candidate.signed_url}}
            ])
        return content
    
    def _rank_and_filter(self, verdicts: List[VLMVerdict], candidates: List[CandidateImage], limit: int) -> List[FinalResult]:
        """Rank and filter results based on VLM verdicts"""
        # Create lookup for candidates
        candidate_lookup = {c.id: c for c in candidates}
        
        # Filter by VLM verdict and confidence
        filtered_verdicts = [
            v for v in verdicts 
            if v.matches and v.confidence >= self.CUTOFF
        ]
        
        # Calculate final scores and create results
        results = []
        for verdict in filtered_verdicts:
            candidate = candidate_lookup.get(verdict.image_id)
            if not candidate:
                continue
            
            # Blend VLM confidence with retrieval score
            final_score = 0.75 * verdict.confidence + 0.25 * candidate.sem_score
            
            # Extract match reasons
            match_reasons = self._extract_match_reasons(verdict.evidence)
            
            result = FinalResult(
                image_id=verdict.image_id,
                file_name=candidate.file_name,
                folder_path=candidate.folder_path,
                vlm_confidence=verdict.confidence,
                retrieval_score=candidate.sem_score,
                final_score=final_score,
                room=verdict.room,
                evidence=verdict.evidence,
                match_reasons=match_reasons,
                ai_notes=verdict.notes
            )
            results.append(result)
        
        # Sort by final score
        results.sort(key=lambda x: x.final_score, reverse=True)
        return results[:limit]
    
    def _extract_match_reasons(self, evidence: Dict[str, Any]) -> List[str]:
        """Extract human-readable match reasons from evidence"""
        reasons = []
        
        # Room
        if evidence.get('room_features'):
            reasons.append(f"Room: {', '.join(evidence['room_features'])}")
        
        # Objects
        objects = evidence.get('objects', [])
        present_objects = [obj['name'] for obj in objects if obj.get('present')]
        if present_objects:
            reasons.append(f"Objects: {', '.join(present_objects)}")
        
        # Colors
        colors = evidence.get('colors_on_objects', [])
        if colors:
            color_desc = [f"{c['object']}={c['color']}" for c in colors]
            reasons.append(f"Colors: {', '.join(color_desc)}")
        
        # Materials
        materials = evidence.get('materials_on_objects', [])
        if materials:
            material_desc = [f"{m['object']}={m['material']}" for m in materials]
            reasons.append(f"Materials: {', '.join(material_desc)}")
        
        return reasons
    
    async def _get_query_embedding(self, query: str) -> List[float]:
        """Get embedding for query using OpenAI"""
        try:
            response = await asyncio.to_thread(
                self.openai_client.embeddings.create,
                model="text-embedding-3-small",
                input=query
            )
            return response.data[0].embedding
        except Exception as e:
            print(f"Error getting query embedding: {e}")
            return []
    
    async def _get_signed_url(self, image_id: str) -> Optional[str]:
        """Get signed URL for image from Google Drive"""
        try:
            # This would integrate with your Google Drive API
            # For now, return a placeholder
            return f"https://drive.google.com/uc?id={image_id}"
        except Exception as e:
            print(f"Error getting signed URL: {e}")
            return None
    
    def _extract_room_filter(self, query: str) -> Optional[str]:
        """Extract room type filter from query"""
        room_mapping = {
            'kitchen': 'kitchen',
            'dining room': 'dining_room',
            'living room': 'living_room',
            'bedroom': 'bedroom',
            'bathroom': 'bathroom',
            'office': 'office'
        }
        
        query_lower = query.lower()
        for room_name, room_type in room_mapping.items():
            if room_name in query_lower:
                return room_type
        
        return None
    
    def _get_cache_key(self, query: str, batch: List[CandidateImage]) -> str:
        """Generate cache key for VLM results"""
        image_ids = sorted([c.id for c in batch])
        content = f"{query}:{':'.join(image_ids)}"
        return hashlib.md5(content.encode()).hexdigest()

# Example usage
async def test_hybrid_search():
    """Test the hybrid search engine"""
    print("Testing Hybrid Search Engine...")
    
    # This would be initialized with actual API keys and Supabase client
    # search_engine = HybridSearchEngine(openai_api_key="your-key", supabase_client=supabase)
    
    test_queries = [
        "kitchen with black table",
        "bathroom with marble countertop", 
        "living room with large sofa",
        "מטבח עם שולחן שחור"  # Hebrew
    ]
    
    for query in test_queries:
        print(f"\nQuery: {query}")
        # results = await search_engine.search(query)
        # print(f"Found {len(results)} results")
        # if results:
        #     top_result = results[0]
        #     print(f"Top result: {top_result.file_name}")
        #     print(f"VLM confidence: {top_result.vlm_confidence:.2f}")
        #     print(f"Match reasons: {top_result.match_reasons}")

if __name__ == "__main__":
    asyncio.run(test_hybrid_search())
