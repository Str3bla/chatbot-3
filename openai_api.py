# openai_api.py - OpenAI API Module for Job Embeddings
import openai
import os
from typing import List, Optional, Dict, Any
import random

# =============================================================================
# OPENAI API CREDENTIALS - FROM ENVIRONMENT VARIABLES
# =============================================================================
OPENAI_API_KEY = os.getenv('OPENAI_API_KEY')
EMBEDDING_MODEL = "text-embedding-3-small"

# Validate that required environment variables are set
if not OPENAI_API_KEY:
    raise ValueError("OPENAI_API_KEY environment variable is required but not set")

# =============================================================================
# OPENAI API FUNCTIONS
# =============================================================================

def prepare_embedding_text(similarity_data: Dict[str, Any]) -> str:
    """
    Prepare job data for embedding using Option B approach:
    Combine title + description + key metadata for richer embeddings
    
    Args:
        similarity_data: Job data from get_job_for_similarity()
        
    Returns:
        Combined text ready for embedding
    """
    title = similarity_data.get('title', '')
    description = similarity_data.get('clean_description', '')
    metadata = similarity_data.get('metadata', {})
    
    # Build rich text for embedding
    embedding_text_parts = []
    
    # Add job title
    if title:
        embedding_text_parts.append(f"Job Title: {title}")
    
    # Add main job description
    if description:
        embedding_text_parts.append(f"Job Description: {description}")
    
    # Add key metadata
    if metadata.get('experience_required'):
        embedding_text_parts.append(f"Experience Required: {metadata['experience_required']}")
    
    if metadata.get('salary'):
        embedding_text_parts.append(f"Salary: ${metadata['salary']}")
    
    if metadata.get('remote'):
        embedding_text_parts.append("Remote Work: Available" if metadata['remote'] else "Remote Work: Not Available")
    
    if metadata.get('client'):
        embedding_text_parts.append(f"Client: {metadata['client']}")
    
    # Join all parts with double newlines
    final_text = "\n\n".join(embedding_text_parts)
    
    return final_text

def embed_job_description(job_text: str) -> Optional[List[float]]:
    """
    Create embedding vector for job description using OpenAI
    
    Args:
        job_text: Prepared job text for embedding
        
    Returns:
        List of floats (1536 dimensions) or None if failed
    """
    try:
        # Set the API key
        openai.api_key = OPENAI_API_KEY
        
        # Create embedding
        response = openai.embeddings.create(
            model=EMBEDDING_MODEL,
            input=job_text,
            encoding_format="float"
        )
        
        # Extract the embedding vector
        embedding = response.data[0].embedding
        
        return embedding
        
    except Exception as e:
        # Simple error handling - just return None and error message
        print(f"OpenAI API Error: {str(e)}")
        return None

def embed_job_with_metadata(similarity_data: Dict[str, Any]) -> Optional[Dict[str, Any]]:
    """
    Complete embedding process: prepare text + embed + add metadata
    
    Args:
        similarity_data: Job data from get_job_for_similarity()
        
    Returns:
        Dict with embedding vector and metadata ready for Pinecone storage
    """
    # Prepare text for embedding
    embedding_text = prepare_embedding_text(similarity_data)
    
    # Create embedding
    embedding_vector = embed_job_description(embedding_text)
    
    if not embedding_vector:
        return None
    
    # Generate random time to fill for POC
    time_to_fill = random.randint(20, 80)
    
    # Prepare complete data structure
    embedding_data = {
        "vector": embedding_vector,
        "metadata": {
            "zoho_job_id": similarity_data.get('job_id', ''),
            "requisition_number": similarity_data.get('requisition_number', ''),
            "job_title": similarity_data.get('title', ''),
            "time_to_fill": time_to_fill,
            "salary": similarity_data.get('metadata', {}).get('salary', ''),
            "client": similarity_data.get('metadata', {}).get('client', ''),
            "remote": similarity_data.get('metadata', {}).get('remote', False),
            "experience_required": similarity_data.get('metadata', {}).get('experience_required', ''),
            "status": similarity_data.get('metadata', {}).get('status', ''),
            "embedding_text": embedding_text[:500] + "..." if len(embedding_text) > 500 else embedding_text  # Store sample of embedded text
        }
    }
    
    return embedding_data

def test_openai_connection() -> bool:
    """
    Simple test to verify OpenAI API connection works
    
    Returns:
        True if connection successful, False otherwise
    """
    try:
        openai.api_key = OPENAI_API_KEY
        
        # Test with simple text
        response = openai.embeddings.create(
            model=EMBEDDING_MODEL,
            input="Test connection to OpenAI API",
            encoding_format="float"
        )
        
        return len(response.data) > 0 and len(response.data[0].embedding) == 1536
        
    except Exception as e:
        print(f"OpenAI connection test failed: {str(e)}")
        return False
