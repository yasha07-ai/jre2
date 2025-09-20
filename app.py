import streamlit as st
from src.helper import extract_text_from_pdf, ask_openai, validate_resume
from src.job_api import fetch_naukri_jobs

st.set_page_config(page_title="Job Recommender", layout="wide")
st.title("📄AI Job Recommendation Engine")
st.markdown("Upload your resume and get job recommendations based on your skills and experience from Naukri.")

uploaded_file = st.file_uploader("Upload your resume (PDF)", type=["pdf"])

if uploaded_file:
    with st.spinner("Extracting text from your resume..."):
        resume_text = extract_text_from_pdf(uploaded_file)
    
    with st.spinner("Validating resume format..."):
        is_valid_resume = validate_resume(resume_text)
    
    if not is_valid_resume:
        st.error("❌ This doesn't appear to be a valid resume. Please upload a proper resume with sections like experience, skills, education, or contact information.")
        st.stop()

    with st.spinner("Summarizing your resume..."):
        summary = ask_openai(f"If this is a valid resume, summarize it highlighting the skills, education, and experience. If this is not a resume or lacks proper resume content, respond with 'NOT A VALID RESUME': \n\n{resume_text}", max_tokens=500)
        
        if "NOT A VALID RESUME" in summary.upper():
            st.error("❌ This document does not contain valid resume information.")
            st.stop()

    
    with st.spinner("Finding skill Gaps..."):
        gaps = ask_openai(f"If this is a valid resume, analyze it and highlight missing skills, certifications, and experiences needed for better job opportunities. If this is not a resume, respond with 'NOT A VALID RESUME': \n\n{resume_text}", max_tokens=400)
        
        if "NOT A VALID RESUME" in gaps.upper():
            st.error("❌ This document does not contain valid resume information.")
            st.stop()

    with st.spinner("Creating Future Roadmap..."):
        roadmap = ask_openai(f"If this is a valid resume, suggest a future roadmap to improve this person's career prospects (Skills to learn, certifications needed, industry exposure). If this is not a resume, respond with 'NOT A VALID RESUME': \n\n{resume_text}", max_tokens=400)
        
        if "NOT A VALID RESUME" in roadmap.upper():
            st.error("❌ This document does not contain valid resume information.")
            st.stop()
    
    # Display nicely formatted results
    st.markdown("---")
    st.header("📑 Resume Summary")
    st.markdown(f"<div style='background-color: #000000; padding: 15px; border-radius: 10px; font-size:16px; color:white;'>{summary}</div>", unsafe_allow_html=True)

    st.markdown("---")
    st.header("🛠️ Skill Gaps & Missing Areas")
    st.markdown(f"<div style='background-color: #000000; padding: 15px; border-radius: 10px; font-size:16px; color:white;'>{gaps}</div>", unsafe_allow_html=True)

    st.markdown("---")
    st.header("🚀 Future Roadmap & Preparation Strategy")
    st.markdown(f"<div style='background-color: #000000; padding: 15px; border-radius: 10px; font-size:16px; color:white;'>{roadmap}</div>", unsafe_allow_html=True)

    st.success("✅ Analysis Completed Successfully!")


    if st.button("🔎Get Job Recommendations"):
        with st.spinner("Fetching job recommendations..."):
            keywords = ask_openai(
                f"Based on this resume summary, suggest the best job titles and keywords for searching jobs. Give a comma-separated list only, no explanation.\n\nSummary: {summary}",
                max_tokens=100
            )

            search_keywords_clean = keywords.replace("\n", "").strip()

        st.success(f"Extracted Job Keywords: {search_keywords_clean}")

        with st.spinner("Fetching jobs from Naukri..."):
            naukri_jobs = fetch_naukri_jobs(search_keywords_clean, rows=60)

        st.markdown("---")
        st.header("💼 Top Naukri Jobs (India)")

        if naukri_jobs:
            for job in naukri_jobs:
                st.markdown(f"**{job.get('title', 'N/A')}** at *{job.get('companyName', 'N/A')}*")
                st.markdown(f"- 📍 {job.get('location', 'N/A')}")
                
                # Handle URL properly - check for valid URL
                job_url = job.get('jdURL') or job.get('url') or job.get('jobUrl')
                if job_url and job_url != 'None' and job_url.startswith('http'):
                    st.markdown(f"- 🔗 [View Job]({job_url})")
                else:
                    st.markdown("- 🔗 Job URL not available")
                st.markdown("---")
        else:
            st.warning("No Naukri jobs found.")