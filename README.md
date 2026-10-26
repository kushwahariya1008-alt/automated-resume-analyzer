# Automated Resume Analyzer for Job Portals

A beginner-friendly student prototype built with Python and Streamlit.

## Features
- Upload text-based PDF, DOCX, or TXT resumes.
- Extract resume text.
- Detect email and phone-like text.
- Detect skills from a predefined list.
- Compare user-entered required skills with the resume.
- Display a transparent skill-match percentage and missing skills.
- Download a short text summary.

## Run locally
1. Install Python 3.10 or newer.
2. Open a terminal in this folder.
3. Create and activate a virtual environment (optional but recommended).
4. Install packages: `pip install -r requirements.txt`
5. Start the app: `streamlit run app.py`

## Deployment
Push `app.py` and `requirements.txt` to a GitHub repository, then create a Streamlit Community Cloud app using that repository and `app.py` as the entry point. Follow the hosting service's current instructions.

## Limitations
This is a prototype using rule-based text matching. It does not include custom-trained NER, semantic vector embeddings, a database, OCR for scanned documents, or production-grade security. The skill score is not a hiring recommendation. Review results manually and use anonymized sample resumes for testing.

## Privacy
Do not upload personal resumes without permission. Do not commit real resumes or personal data to GitHub.
