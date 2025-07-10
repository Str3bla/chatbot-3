# zoho_api.py - Zoho Recruit API Module with Automatic Token Refresh
import requests
import re
import os
from typing import Optional, Dict, Any

# =============================================================================
# ZOHO RECRUIT API CREDENTIALS - FROM ENVIRONMENT VARIABLES
# =============================================================================
ZOHO_CLIENT_ID = os.getenv('ZOHO_CLIENT_ID', '1000.AL6419HX3THLR4U73ZGWVMPGPTITNX')
ZOHO_CLIENT_SECRET = os.getenv('ZOHO_CLIENT_SECRET', '361cf827b2cb1e0903843319f0eb7856e3d6fdaac6')
ZOHO_REFRESH_TOKEN = os.getenv('ZOHO_REFRESH_TOKEN')
ZOHO_ACCESS_TOKEN = os.getenv('ZOHO_ACCESS_TOKEN')  # Optional - will refresh if needed
ZOHO_BASE_URL = "https://recruit.zoho.com/recruit/v2"
ZOHO_ACCOUNTS_URL = "https://accounts.zoho.com"

# Validate that required environment variables are set
if not ZOHO_REFRESH_TOKEN:
    raise ValueError("ZOHO_REFRESH_TOKEN environment variable is required but not set")

# Global variable to store current access token in memory
_current_access_token = ZOHO_ACCESS_TOKEN

# =============================================================================
# AUTOMATIC TOKEN REFRESH FUNCTIONS
# =============================================================================

def get_fresh_access_token() -> Optional[str]:
    """
    Get a fresh access token using the refresh token
    
    Returns:
        Fresh access token or None if failed
    """
    global _current_access_token
    
    token_url = f"{ZOHO_ACCOUNTS_URL}/oauth/v2/token"
    
    payload = {
        'grant_type': 'refresh_token',
        'client_id': ZOHO_CLIENT_ID,
        'client_secret': ZOHO_CLIENT_SECRET,
        'refresh_token': ZOHO_REFRESH_TOKEN
    }
    
    try:
        response = requests.post(token_url, data=payload)
        if response.status_code == 200:
            token_data = response.json()
            fresh_token = token_data.get('access_token')
            if fresh_token:
                _current_access_token = fresh_token  # Cache in memory
                return fresh_token
        
        print(f"Token refresh failed: {response.status_code} - {response.text}")
        return None
        
    except Exception as e:
        print(f"Token refresh error: {str(e)}")
        return None

def get_valid_access_token() -> Optional[str]:
    """
    Get a valid access token, refreshing if necessary
    
    Returns:
        Valid access token or None if unable to get one
    """
    global _current_access_token
    
    # If we don't have a token, get a fresh one
    if not _current_access_token:
        return get_fresh_access_token()
    
    # Return the current token (will be validated by actual API call)
    return _current_access_token

def make_zoho_api_request(url: str, headers: Dict[str, str] = None, retry_on_401: bool = True) -> Optional[Dict[Any, Any]]:
    """
    Make a Zoho API request with automatic token refresh on 401 errors
    
    Args:
        url: Full API URL to call
        headers: Additional headers (auth header will be added automatically)
        retry_on_401: Whether to retry with fresh token on 401 error
        
    Returns:
        API response JSON or error dict
    """
    access_token = get_valid_access_token()
    if not access_token:
        return {
            "error": True,
            "message": "Unable to get valid access token"
        }
    
    # Prepare headers
    api_headers = {
        'Authorization': f'Zoho-oauthtoken {access_token}',
        'Content-Type': 'application/json'
    }
    if headers:
        api_headers.update(headers)
    
    try:
        response = requests.get(url, headers=api_headers)
        
        # If 401 and we haven't retried yet, refresh token and try again
        if response.status_code == 401 and retry_on_401:
            print("Access token expired, refreshing...")
            fresh_token = get_fresh_access_token()
            if fresh# zoho_api.py - Zoho Recruit API Module
import requests
import re
import os
from typing import Optional, Dict, Any

# =============================================================================
# ZOHO RECRUIT API CREDENTIALS - FROM ENVIRONMENT VARIABLES
# =============================================================================
ZOHO_CLIENT_ID = "1000.AL6419HX3THLR4U73ZGWVMPGPTITNX"
ZOHO_CLIENT_SECRET = "361cf827b2cb1e0903843319f0eb7856e3d6fdaac6" 
ZOHO_ACCESS_TOKEN = os.getenv('ZOHO_ACCESS_TOKEN')
ZOHO_BASE_URL = "https://recruit.zoho.com/recruit/v2"

# Validate that required environment variables are set
if not ZOHO_ACCESS_TOKEN:
    raise ValueError("ZOHO_ACCESS_TOKEN environment variable is required but not set")

# =============================================================================
# SIMPLE TOKEN REFRESH FUNCTION
# =============================================================================

def get_fresh_access_token_from_refresh(refresh_token: str) -> Optional[Dict[str, Any]]:
    """
    Get fresh access token using refresh token - exactly like the working curl command
    
    Args:
        refresh_token: The refresh token from user input
        
    Returns:
        Dict with new tokens or error info
    """
    token_url = "https://accounts.zoho.com/oauth/v2/token"
    
    payload = {
        'grant_type': 'authorization_code',  # Using same as working curl
        'client_id': ZOHO_CLIENT_ID,
        'client_secret': ZOHO_CLIENT_SECRET,
        'redirect_uri': 'http://localhost',
        'code': refresh_token
    }
    
    try:
        response = requests.post(token_url, data=payload)
        
        if response.status_code == 200:
            token_data = response.json()
            return {
                "success": True,
                "access_token": token_data.get('access_token'),
                "refresh_token": token_data.get('refresh_token'),
                "expires_in": token_data.get('expires_in', 3600),
                "raw_response": token_data
            }
        else:
            return {
                "success": False,
                "error": f"HTTP {response.status_code}",
                "message": response.text
            }
            
    except Exception as e:
        return {
            "success": False,
            "error": "Request failed",
            "message": str(e)
        }

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
