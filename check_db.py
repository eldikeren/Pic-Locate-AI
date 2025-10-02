"""
Check database status
"""

from supabase import create_client

def check_database():
    try:
        supabase = create_client(
            "https://gezmablgrepoaamtizts.supabase.co",
            "eyJhbGciOiJIUzI1NiIsInR5cCI6IkpXVCJ9.eyJpc3MiOiJzdXBhYmFzZSIsInJlZiI6Imdlem1hYmxncmVwb2FhbXRpenRzIiwicm9sZSI6ImFub24iLCJpYXQiOjE3NTkxNzg2MzMsImV4cCI6MjA3NDc1NDYzM30.lJjaubEzeET8OwcHWJ_x_pOAXd8Bc1yDbpdvKianLM0"
        )
        
        # Check image_embeddings table
        result = supabase.table('image_embeddings').select('*').limit(1).execute()
        
        if result.data:
            print("Database Status: ACTIVE")
            print("Sample record keys:", list(result.data[0].keys()))
            
            # Count total records
            count_result = supabase.table('image_embeddings').select('file_id', count='exact').execute()
            total_count = count_result.count if hasattr(count_result, 'count') else len(count_result.data)
            print(f"Total images indexed: {total_count}")
            
        else:
            print("Database Status: EMPTY")
            print("No images indexed yet")
            
    except Exception as e:
        print(f"Database Error: {e}")

if __name__ == "__main__":
    check_database()
