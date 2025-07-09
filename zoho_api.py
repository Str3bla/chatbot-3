# zoho_api.py - Zoho Recruit API Module
import requests
import re
from typing import Optional, Dict, Any

# =============================================================================
# ZOHO RECRUIT API CREDENTIALS
# =============================================================================
ZOHO_ACCESS_TOKEN = "1000.bee988d6f88dee9a6d5c642d3784b8e3.7bbdcbd5fce82e85d75862beaf5ecba5"
ZOHO_BASE_URL = "https://recruit.zoho.com/recruit/v2"

# =============================================================================
# ZOHO API FUNCTIONS
# =============================================================================

def fetch_job_data(job_id: str) -> Optional[Dict[Any, Any]]:
    """
    Fetch job data from Zoho Recruit API
    
    Args:
        job_id: The Zoho job opening ID (e.g., "821313000000528968")
        
    Returns:
        Dict containing job data or None if failed
    """
    url = f"{ZOHO_BASE_URL}/JobOpenings/{job_id}"
    headers = {
        'Authorization': f'Zoho-oauthtoken {ZOHO_ACCESS_TOKEN}',
        'Content-Type': 'application/json'
    }
    
    try:
        response = requests.get(url, headers=headers)
        if response.status_code == 200:
            return response.json()
        else:
            return {
                "error": True,
                "status_code": response.status_code,
                "message": f"API Error: {response.status_code}"
            }
    except Exception as e:
        return {
            "error": True,
            "message": f"Request failed: {str(e)}"
        }

def extract_job_info(job_data: Dict[Any, Any]) -> Optional[Dict[str, Any]]:
    """
    Extract clean job information from Zoho API response
    
    Args:
        job_data: Raw API response from fetch_job_data()
        
    Returns:
        Dict with cleaned job information or None if no data
    """
    if not job_data or job_data.get("error"):
        return None
        
    if 'data' not in job_data or len(job_data['data']) == 0:
        return None
    
    job_info = job_data['data'][0]
    
    # Extract key fields with defaults
    cleaned_info = {
        'job_id': job_info.get('id', ''),
        'requisition_number': job_info.get('Job_Opening_ID', ''),
        'job_title': job_info.get('Job_Opening_Name', ''),
        'posting_title': job_info.get('Posting_Title', ''),
        'job_description': job_info.get('Job_Description', ''),
        'salary': job_info.get('Salary', ''),
        'currency': job_info.get('$currency_symbol', ''),
        'status': job_info.get('Job_Opening_Status', ''),
        'remote_job': job_info.get('Remote_Job', False),
        'date_opened': job_info.get('Date_Opened', ''),
        'target_date': job_info.get('Target_Date', ''),
        'work_experience': job_info.get('Work_Experience', ''),
        'number_of_positions': job_info.get('Number_of_Positions', ''),
        'client_name': job_info.get('Client_Name', {}).get('name', '') if job_info.get('Client_Name') else '',
        'account_manager': job_info.get('Account_Manager', {}).get('name', '') if job_info.get('Account_Manager') else ''
    }
    
    return cleaned_info

def clean_job_description(job_description: str) -> str:
    """
    Clean HTML tags and formatting from job description
    
    Args:
        job_description: Raw job description with HTML
        
    Returns:
        Cleaned plain text job description
    """
    if not job_description:
        return ""
    
    # Remove HTML tags
    clean_text = re.sub(r'<[^>]+>', '', job_description)
    
    # Clean up extra whitespace and newlines
    clean_text = re.sub(r'\s+', ' ', clean_text)
    clean_text = clean_text.strip()
    
    return clean_text

def get_job_for_similarity(job_id: str) -> Optional[Dict[str, str]]:
    """
    Get job data specifically formatted for similarity analysis
    
    Args:
        job_id: The Zoho job opening ID
        
    Returns:
        Dict with job info ready for embedding/similarity analysis
    """
    # Fetch raw data
    raw_data = fetch_job_data(job_id)
    if not raw_data or raw_data.get("error"):
        return None
    
    # Extract and clean
    job_info = extract_job_info(raw_data)
    if not job_info:
        return None
    
    # Format for similarity analysis
    similarity_data = {
        'job_id': job_info['job_id'],
        'requisition_number': job_info['requisition_number'], 
        'title': job_info['job_title'],
        'clean_description': clean_job_description(job_info['job_description']),
        'raw_description': job_info['job_description'],
        'metadata': {
            'salary': job_info['salary'],
            'status': job_info['status'],
            'remote': job_info['remote_job'],
            'experience_required': job_info['work_experience'],
            'client': job_info['client_name']
        }
    }
    
    return similarity_data
