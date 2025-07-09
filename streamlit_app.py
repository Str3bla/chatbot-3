# streamlit_app.py - Main Streamlit Application
import streamlit as st
import pandas as pd

# Import our custom Zoho API module
from zoho_api import fetch_job_data, extract_job_info, get_job_for_similarity

# =============================================================================
# STREAMLIT APP - ZOHO API TESTING WITH USER INPUT
# =============================================================================

st.title("🎯 Zoho API Test - Interactive Job Lookup")
st.write("Test Zoho API calls with any Job Opening ID")

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
col1, col2 = st.columns(2)

with col1:
    test_basic = st.button("🧪 Test Basic API Call", type="primary")

with col2:
    test_similarity = st.button("🎯 Test for Similarity Analysis", type="secondary")

st.markdown("---")

# =============================================================================
# BASIC API TEST
# =============================================================================
if test_basic and job_id_input:
    with st.spinner(f"Testing API call for Job ID: {job_id_input}..."):
        
        # Call the Zoho API using our imported function
        data = fetch_job_data(job_id_input)
        
        if data and not data.get("error"):
            st.success("✅ API call successful!")
            
            # Show raw response (collapsed by default)
            with st.expander("📊 Raw API Response", expanded=False):
                st.json(data)
            
            # Extract and display job info using our imported function
            job_info = extract_job_info(data)
            if job_info:
                st.subheader("🎯 Job Information")
                
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
                    {"Field": "Date Opened", "Value": job_info['date_opened']},
                    {"Field": "Target Date", "Value": job_info['target_date']},
                ]
                
                df = pd.DataFrame(display_data)
                st.dataframe(df, use_container_width=True, hide_index=True)
                
                # Show job description
                if job_info['job_description']:
                    st.subheader("📄 Job Description")
                    st.text_area(
                        "Raw Description (with HTML):", 
                        job_info['job_description'][:500] + "..." if len(job_info['job_description']) > 500 else job_info['job_description'], 
                        height=200, 
                        disabled=True
                    )
        else:
            st.error("❌ API call failed")
            if data and data.get("message"):
                st.error(f"Error: {data['message']}")

# =============================================================================
# SIMILARITY-READY TEST
# =============================================================================
if test_similarity and job_id_input:
    with st.spinner(f"Preparing job data for similarity analysis..."):
        
        # Get job data formatted for similarity using our imported function
        similarity_data = get_job_for_similarity(job_id_input)
        
        if similarity_data:
            st.success("✅ Job data ready for similarity analysis!")
            
            st.subheader("🎯 Similarity-Ready Data")
            
            # Show key fields
            st.write(f"**Job ID:** {similarity_data['job_id']}")
            st.write(f"**Requisition:** {similarity_data['requisition_number']}")
            st.write(f"**Title:** {similarity_data['title']}")
            
            # Show clean description
            st.subheader("📝 Cleaned Job Description")
            st.text_area(
                "Ready for embedding/vectorization:",
                similarity_data['clean_description'][:800] + "..." if len(similarity_data['clean_description']) > 800 else similarity_data['clean_description'],
                height=300,
                disabled=True
            )
            
            # Show metadata
            st.subheader("📊 Metadata for Analysis")
            metadata_df = pd.DataFrame([
                {"Field": "Salary", "Value": similarity_data['metadata']['salary']},
                {"Field": "Status", "Value": similarity_data['metadata']['status']},
                {"Field": "Remote", "Value": similarity_data['metadata']['remote']},
                {"Field": "Experience", "Value": similarity_data['metadata']['experience_required']},
                {"Field": "Client", "Value": similarity_data['metadata']['client']},
            ])
            st.dataframe(metadata_df, use_container_width=True, hide_index=True)
            
            # Character count for embedding
            char_count = len(similarity_data['clean_description'])
            st.info(f"📏 **Character Count:** {char_count:,} characters (ready for OpenAI embedding)")
            
        else:
            st.error("❌ Failed to prepare job data for similarity analysis")

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
