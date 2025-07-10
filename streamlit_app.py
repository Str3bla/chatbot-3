# streamlit_app.py - Main Streamlit Application
import streamlit as st
import pandas as pd

# Import our custom API modules
from zoho_api import fetch_job_data, extract_job_info, get_job_for_similarity, get_fresh_access_token_from_refresh
from openai_api import embed_job_with_metadata, prepare_embedding_text, test_openai_connection

# =============================================================================
# STREAMLIT APP - ZOHO API TESTING WITH TOKEN REFRESH
# =============================================================================

st.title("🎯 Zoho API Test - Interactive Job Lookup")
st.write("Test Zoho API calls with automatic token refresh helper")

# =============================================================================
# TOKEN REFRESH HELPER SECTION - AT THE TOP
# =============================================================================
st.markdown("---")
st.subheader("🔄 Token Refresh Helper")
st.write("Use this section to get a fresh access token when the current one expires")

# Input for refresh token (authorization code)
refresh_token_input = st.text_input(
    "Enter Authorization Code from Zoho:",
    placeholder="1000.abc123def456...",
    help="Get this from Zoho Self Client 'Generate Code' (10-minute expiry)"
)

if st.button("🔄 Get Fresh Access Token") and refresh_token_input:
    with st.spinner("Getting fresh access token..."):
        token_result = get_fresh_access_token_from_refresh(refresh_token_input)
        
        if token_result.get("success"):
            st.success("✅ Fresh access token obtained!")
            
            # Show the new access token prominently
            new_access_token = token_result["access_token"]
            st.subheader("📋 Copy This Access Token:")
            st.code(new_access_token, language='text')
            
            st.info("👆 **Copy this token and update your Streamlit Cloud secrets with it!**")
            
            # Show additional info
            col1, col2 = st.columns(2)
            with col1:
                st.write(f"**Expires in:** {token_result.get('expires_in', 'Unknown')} seconds")
            with col2:
                if token_result.get("refresh_token"):
                    st.write("**New refresh token also provided**")
            
            # Instructions
            st.markdown("""
            **How to update your Streamlit secrets:**
            1. Go to your Streamlit Cloud app settings
            2. Click "Secrets" tab
            3. Replace the ZOHO_ACCESS_TOKEN value with the token above
            4. Save and wait ~1 minute for app to restart
            """)
            
        else:
            st.error("❌ Failed to get fresh access token")
            st.error(f"**Error:** {token_result.get('error', 'Unknown error')}")
            if token_result.get('message'):
                st.error(f"**Details:** {token_result['message']}")

st.markdown("---")

# =============================================================================
# USER INPUT SECTION
# =============================================================================
st.subheader("📋 Job Lookup")

# Freeform text input for Job ID
job_id_input = st.text_input(
    "Enter Zoho Job Opening ID:",
    value="821313000000528968",  # Default to working ID
    placeholder="e.g., 821313000000528968",
    help="Enter the internal Zoho Job Opening ID (long numeric string)"
)

# Display current input
if job_id_input:
    st.info(f"**Testing Job ID:** {job_id_input}")

st.markdown("---")

# =============================================================================
# API TEST BUTTONS
# =============================================================================
col1, col2, col3 = st.columns(3)

with col1:
    test_zoho = st.button("🔧 Test Zoho API Call", type="primary")

with col2:
    test_openai = st.button("🧠 Test OpenAI API Call", type="secondary")

with col3:
    test_full = st.button("🎯 Test Full Pipeline", disabled=True, help="Coming soon - after Pinecone integration")

st.markdown("---")

# =============================================================================
# ZOHO API TEST
# =============================================================================
if test_zoho and job_id_input:
    with st.spinner(f"Testing Zoho API call for Job ID: {job_id_input}..."):
        
        # Call the Zoho API using our imported function
        data = fetch_job_data(job_id_input)
        
        if data and not data.get("error"):
            st.success("✅ Zoho API call successful!")
            
            # Show raw response (collapsed by default)
            with st.expander("📊 Raw Zoho API Response", expanded=False):
                st.json(data)
            
            # Extract and display job info using our imported function
            job_info = extract_job_info(data)
            if job_info:
                st.subheader("🎯 Job Information from Zoho")
                
                # Create clean display table
                display_data = [
                    {"Field": "Job ID", "Value": job_info['job_id']},
                    {"Field": "Requisition Number", "Value": job_info['requisition_number']},
                    {"Field": "Job Title", "Value": job_info['job_title']},
                    {"Field": "Posting Title", "Value": job_info['posting_title']},
                    {"Field": "Salary", "Value": f"{job_info['currency']}{job_info['salary']}" if job_info['salary'] else "Not specified"},
                    {"Field": "Status", "Value": job_info['status']},
                    {"Field": "Remote Job", "Value": "Yes" if job_info['remote_job'] else "No"},
                    {"Field": "Experience Required", "Value": job_info['work_experience']},
                    {"Field": "Client", "Value": job_info['client_name']},
                    {"Field": "Account Manager", "Value": job_info['account_manager']},
                ]
                
                df = pd.DataFrame(display_data)
                st.dataframe(df, use_container_width=True, hide_index=True)
                
                # Show job description
                if job_info['job_description']:
                    st.subheader("📄 Job Description from Zoho")
                    st.text_area(
                        "Raw Description (with HTML):", 
                        job_info['job_description'][:500] + "..." if len(job_info['job_description']) > 500 else job_info['job_description'], 
                        height=200, 
                        disabled=True
                    )
        else:
            st.error("❌ Zoho API call failed")
            if data and data.get("message"):
                st.error(f"Error: {data['message']}")

# =============================================================================
# OPENAI API TEST  
# =============================================================================
if test_openai and job_id_input:
    with st.spinner(f"Testing OpenAI API call for Job ID: {job_id_input}..."):
        
        # First, get job data from Zoho
        similarity_data = get_job_for_similarity(job_id_input)
        
        if similarity_data:
            st.success("✅ Job data retrieved from Zoho!")
            
            # Show what we'll embed
            st.subheader("🧠 OpenAI API Test")
            st.write(f"**Job ID:** {similarity_data['job_id']}")
            st.write(f"**Title:** {similarity_data['title']}")
            
            # Prepare text for embedding
            embedding_text = prepare_embedding_text(similarity_data)
            
            # Show prepared text
            st.subheader("📝 Text Prepared for OpenAI Embedding")
            st.text_area(
                "Combined text (title + description + metadata):",
                embedding_text[:800] + "..." if len(embedding_text) > 800 else embedding_text,
                height=200,
                disabled=True
            )
            
            # Show character count
            char_count = len(embedding_text)
            st.info(f"📏 **Character Count:** {char_count:,} characters")
            
            # Test OpenAI connection first
            if test_openai_connection():
                st.success("✅ OpenAI API connection successful!")
                
                # Now create the actual embedding
                embedding_result = embed_job_with_metadata(similarity_data)
                
                if embedding_result:
                    st.success("✅ Job embedding created successfully!")
                    
                    # Show embedding results
                    st.subheader("🎯 Embedding Results")
                    
                    # Embedding vector info
                    vector_length = len(embedding_result['vector'])
                    st.write(f"**Vector Dimensions:** {vector_length}")
                    st.write(f"**Model Used:** text-embedding-3-small")
                    
                    # Show first few dimensions as sample
                    sample_vector = embedding_result['vector'][:10]
                    st.write(f"**Sample Vector (first 10 dimensions):** {[round(x, 4) for x in sample_vector]}")
                    
                    # Show metadata that will be stored with vector
                    st.subheader("📊 Metadata for Vector Storage")
                    metadata_display = []
                    for key, value in embedding_result['metadata'].items():
                        if key != 'embedding_text':  # Skip the long text field
                            metadata_display.append({"Field": key, "Value": str(value)})
                    
                    metadata_df = pd.DataFrame(metadata_display)
                    st.dataframe(metadata_df, use_container_width=True, hide_index=True)
                    
                    # Success message
                    st.success(f"🎉 **Ready for Pinecone!** Vector with {vector_length} dimensions and metadata prepared.")
                    
                else:
                    st.error("❌ Failed to create embedding")
                    
            else:
                st.error("❌ OpenAI API connection failed - check API key")
                
        else:
            st.error("❌ Failed to get job data from Zoho")

# =============================================================================
# FULL PIPELINE TEST (Placeholder)
# =============================================================================
if test_full:
    st.info("🚧 **Full Pipeline Test** - Coming after Pinecone integration!")

# =============================================================================
# HELP SECTION
# =============================================================================
st.markdown("---")
st.subheader("💡 How to Use")

st.markdown("""
**Step 1:** Enter a Zoho Job Opening ID in the text box above

**Step 2:** Choose your test type:
- **Basic API Call:** Tests raw API connection and shows all job data
- **Similarity Analysis:** Prepares data specifically for embedding/vectorization

**Step 3:** Review the results and job description data

**Next Steps:** Once this works, we can build the OpenAI embedding and Pinecone integration!
""")

st.info("💡 This modular approach separates API logic from UI, making it easy to reuse the Zoho functions in other scripts.")
