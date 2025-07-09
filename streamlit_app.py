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
        
        # Get job data formatted for similarity using our imported function
        similarity_data = get_job_for_similarity(job_id_input)
        
        if similarity_data:
            st.success("✅ Job data ready for OpenAI embedding!")
            
            st.subheader("🧠 OpenAI API Test")
            
            # Show what we'll embed
            st.write(f"**Job ID:** {similarity_data['job_id']}")
            st.write(f"**Title:** {similarity_data['title']}")
            
            # Show clean description that will be embedded
            st.subheader("📝 Text to Embed")
            embed_text = similarity_data['clean_description'][:1000]  # Truncate for display
            st.text_area(
                "This text will be sent to OpenAI for embedding:",
                embed_text + "..." if len(similarity_data['clean_description']) > 1000 else embed_text,
                height=200,
                disabled=True
            )
            
            # Character count
            char_count = len(similarity_data['clean_description'])
            st.info(f"📏 **Character Count:** {char_count:,} characters")
            
            # Placeholder for actual OpenAI call (coming next)
            st.warning("🚧 **OpenAI API integration coming next!** Currently showing prepared data only.")
            
        else:
            st.error("❌ Failed to prepare job data for OpenAI embedding")

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
