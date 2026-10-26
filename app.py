import re
from io import BytesIO
from pathlib import Path

import pdfplumber
import streamlit as st
from docx import Document

st.set_page_config(page_title="Automated Resume Analyzer", page_icon="📄", layout="wide")

SKILL_BANK = [
    "python", "sql", "excel", "power bi", "tableau", "machine learning",
    "statistics", "data analysis", "data visualization", "pandas", "numpy",
    "scikit-learn", "deep learning", "natural language processing", "nlp",
    "java", "c++", "c", "javascript", "html", "css", "react", "git",
    "communication", "project management", " problem solving", "aws", "azure",
    "mysql", "postgresql", "mongodb", "r programming", "data cleaning"
]

def extract_text(uploaded_file):
    """Extract text from PDF, DOCX, or TXT files."""
    filename = uploaded_file.name.lower()
    raw = uploaded_file.getvalue()
    if filename.endswith(".pdf"):
        pages = []
        with pdfplumber.open(BytesIO(raw)) as pdf:
            for page in pdf.pages:
                pages.append(page.extract_text() or "")
        return "\n".join(pages)
    if filename.endswith(".docx"):
        doc = Document(BytesIO(raw))
        paragraphs = [p.text for p in doc.paragraphs if p.text.strip()]
        for table in doc.tables:
            for row in table.rows:
                paragraphs.append(" | ".join(cell.text for cell in row.cells))
        return "\n".join(paragraphs)
    if filename.endswith(".txt"):
        return raw.decode("utf-8", errors="ignore")
    raise ValueError("Unsupported file type. Please upload a PDF, DOCX, or TXT file.")

def find_email(text):
    match = re.search(r"[A-Za-z0-9._%+-]+@[A-Za-z0-9.-]+\.[A-Za-z]{2,}", text)
    return match.group(0) if match else "Not found"

def find_phone(text):
    match = re.search(r"(?<!\d)(?:\+?\d[\d\s().-]{8,}\d)(?!\d)", text)
    if not match:
        return "Not found"
    digits = re.sub(r"\D", "", match.group(0))
    return match.group(0).strip() if 10 <= len(digits) <= 15 else "Not found"

def find_skills(text):
    lower = text.lower()
    found = []
    for skill in SKILL_BANK:
        clean = skill.strip()
        if clean and re.search(r"(?<!\w)" + re.escape(clean) + r"(?!\w)", lower):
            found.append(clean.title() if clean not in {"sql", "nlp", "html", "css", "aws", "azure"} else clean.upper())
    return sorted(set(found), key=str.lower)

def extract_experience_years(text):
    patterns = [
        r"(\d+(?:\.\d+)?)\s*\+?\s*years?\s+(?:of\s+)?experience",
        r"experience\s*[:\-]?\s*(\d+(?:\.\d+)?)\s*\+?\s*years?"
    ]
    lower = text.lower()
    for pattern in patterns:
        match = re.search(pattern, lower)
        if match:
            try:
                return float(match.group(1))
            except ValueError:
                pass
    return None

def calculate_match(resume_skills, required_skills, resume_text, job_text):
    required = [s.strip() for s in required_skills.split(",") if s.strip()]
    if required:
        matched = [s for s in required if s.lower() in resume_text.lower()]
        missing = [s for s in required if s.lower() not in resume_text.lower()]
        skill_score = round(100 * len(matched) / len(required))
    else:
        matched, missing, skill_score = [], [], 0

    # Simple transparent prototype score: skill match is the only scored factor.
    # Experience/education are shown separately and are not guessed.
    return required, matched, missing, skill_score

st.title("📄 Automated Resume Analyzer for Job Portals")
st.write("Upload a resume and compare its skills with a job description. This is a student prototype, not an automated hiring decision system.")
st.info("Supported formats: text-based PDF, DOCX, and TXT. Scanned-image PDFs may need OCR and might not extract correctly.")

left, right = st.columns(2)
with left:
    resume_file = st.file_uploader("1. Upload candidate resume", type=["pdf", "docx", "txt"])
with right:
    job_title = st.text_input("2. Job title", placeholder="e.g., Junior Data Analyst")
    job_description = st.text_area(
        "3. Paste the job description",
        placeholder="Describe the role, required skills, education, and experience...",
        height=180
    )
    required_skills = st.text_input(
        "Required skills (comma-separated)",
        placeholder="Python, SQL, Excel, Power BI"
    )

if st.button("Analyze Resume", type="primary", use_container_width=True):
    if not resume_file:
        st.error("Please upload a resume first.")
    elif not job_description.strip():
        st.error("Please enter a job description.")
    elif not required_skills.strip():
        st.error("Please enter at least one required skill, separated by commas.")
    else:
        try:
            resume_text = extract_text(resume_file)
            if not resume_text.strip():
                st.error("No readable text was found. Try a text-based PDF, DOCX, or TXT file.")
            else:
                skills = find_skills(resume_text)
                email = find_email(resume_text)
                phone = find_phone(resume_text)
                years = extract_experience_years(resume_text)
                required, matched, missing, score = calculate_match(
                    skills, required_skills, resume_text, job_description
                )

                st.subheader("Analysis Results")
                c1, c2, c3 = st.columns(3)
                c1.metric("Skill match", f"{score}%")
                c2.metric("Required skills matched", f"{len(matched)} / {len(required)}")
                c3.metric("Extracted skills detected", str(len(skills)))

                st.progress(score / 100)
                st.caption("Score is calculated from the required skills found in the resume. It is not a prediction of job performance.")

                result_left, result_right = st.columns(2)
                with result_left:
                    st.markdown("#### Extracted contact details")
                    st.write("**Email:**", email)
                    st.write("**Phone:**", phone)
                    st.write("**Experience stated:**", f"{years:g} years" if years is not None else "Not confidently detected")
                    st.markdown("#### Skills detected")
                    st.write(", ".join(skills) if skills else "No skills from the built-in list were detected.")
                with result_right:
                    st.markdown("#### Matched required skills")
                    st.success(", ".join(matched) if matched else "No required skills matched.")
                    st.markdown("#### Missing required skills")
                    st.warning(", ".join(missing) if missing else "No missing required skills.")
                    st.markdown("#### Job")
                    st.write(job_title or "Not specified")

                with st.expander("View extracted resume text"):
                    st.text(resume_text[:15000])
                    if len(resume_text) > 15000:
                        st.caption("Only the first 15,000 characters are shown.")

                st.download_button(
                    "Download analysis summary",
                    data=(
                        f"Automated Resume Analyzer\\nJob title: {job_title or 'Not specified'}\\n"
                        f"Skill match: {score}%\\nMatched skills: {', '.join(matched)}\\n"
                        f"Missing skills: {', '.join(missing)}\\nEmail: {email}\\nPhone: {phone}\\n"
                    ),
                    file_name="resume_analysis_summary.txt",
                    mime="text/plain"
                )
                st.warning("Privacy note: Do not upload real candidates' personal data without permission. Use sample or anonymized resumes for testing.")
        except Exception as exc:
            st.error(f"Could not analyze this file: {exc}")

with st.expander("How this prototype works"):
    st.markdown("""
    1. Reads text from a PDF, DOCX, or TXT resume.
    2. Detects email and phone-like text using regular expressions.
    3. Looks for skills in a predefined skill list.
    4. Compares the required skills entered by the user against the resume text.
    5. Calculates a transparent skill-match percentage.

    **Current limitations:** The prototype does not train a custom NER model, use transformer embeddings, verify education, or calculate a validated hiring score. Scanned PDFs may require OCR. A human must review the result.
    """)
