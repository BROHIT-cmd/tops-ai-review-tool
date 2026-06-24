import streamlit as st
from pypdf import PdfReader
from reportlab.lib.pagesizes import letter
from reportlab.pdfgen import canvas
import io
import os

# -----------------------------------
# ✅ PAGE CONFIG
# -----------------------------------
st.set_page_config(page_title="AI Assisted TOPS Drawing review Tool", layout="wide")

# -----------------------------------
# ✅ CLEAN WHITE UI
# -----------------------------------
st.markdown("""
<style>
.stApp { background-color: white; color: black; }
.header { display: flex; justify-content: flex-end; margin-bottom: 10px; }
.score-box {
    background-color: #f3f4f6;
    padding: 6px;
    border-radius: 6px;
    text-align: center;
    font-size: 30px;
    font-weight: bold;
}
.comment-box {
    background-color: #f9fafb;
    padding: 8px;
    margin-bottom: 3px;
    border-left: 2px solid #dc2626;
}
.stButton button {
    background-color: #1F6FEB;
    color: white;
    border-radius: 6px;
}
.stDownloadButton button {
    background-color: #2da44e;
    color: white;
}
</style>
""", unsafe_allow_html=True)

# -----------------------------------
# ✅ HEADER
# -----------------------------------
st.markdown('<div class="header">', unsafe_allow_html=True)
try:
    st.image("logo.png", width=200, height=180)
except:
    pass
st.markdown('</div>', unsafe_allow_html=True)

# -----------------------------------
# ✅ TITLE
# -----------------------------------
st.title("AI Assisted TOPS Drawing review Tool")

st.caption(
    "Tool Description - This tool automates the validation of TOPS pumping station drawings by analyzing uploaded PDF files against predefined engineering checklists. It helps identify missing or incomplete design elements, provides a compliance score, and generates structured review comments along with downloadable reports. The aim is to support engineers in improving design quality, reducing manual effort, and ensuring consistency across project reviews."
)

# -----------------------------------
# ✅ FILE UPLOAD (MULTI PDF)
# -----------------------------------
st.markdown("### Please upload TOPS PS drawings PDF")

uploaded_files = st.file_uploader(
    "Upload PDF files",
    type="pdf",
    accept_multiple_files=True
)

# -----------------------------------
# ✅ PDF REPORT FUNCTION
# -----------------------------------
def create_pdf(comments, score):
    buffer = io.BytesIO()
    c = canvas.Canvas(buffer, pagesize=letter)

    c.drawString(100, 750, "AI Drawing Review Report")
    c.drawString(100, 730, f"Score: {score}/100")

    y = 700
    for comment in comments:
        c.drawString(40, y, comment)
        y -= 15

    c.save()
    buffer.seek(0)
    return buffer

# -----------------------------------
# ✅ MAIN LOGIC
# -----------------------------------
if uploaded_files:

    full_text = ""

    for file in uploaded_files:
        st.subheader(f"📄 Processing: {file.name}")

        reader = PdfReader(file)
        st.write(f"Total Pages: {len(reader.pages)}")

        # ✅ MULTI-PAGE LOOP
        for i, page in enumerate(reader.pages):
            page_text = page.extract_text()

            if page_text:
                st.write(f"✅ Page {i+1}")
                full_text += " " + page_text
            else:
                st.warning(f"⚠️ Page {i+1} has no readable text")

    full_text = full_text.lower()

    st.success("✅ All PDFs loaded successfully")

    # ✅ Prepare variables
    comments = []
    score = 100

    # ✅ RULE FUNCTION
    def check_rule(keyword, message, penalty=3):
        if keyword not in full_text:
            comments.append(message)
            return penalty
        return 0

    # ✅ RUN REVIEW BUTTON
    if st.button("🚀 Run Review"):

        try:
            base_path = os.path.dirname(__file__)
            checklist_path = os.path.join(base_path, "Checklist.txt")

            with open(checklist_path, "r", encoding="utf-8") as file:
                rules = file.readlines()

            for rule in rules:
                rule = rule.strip().lower()
                if rule and not rule.startswith("#"):
                    score -= check_rule(rule, f"⚠️ {rule} missing")

        except:
            st.error("❌ Checklist file not found")

        score = max(score, 0)

        # ✅ SCORE
        st.markdown(f"""
        <div class="score-box">Score: {score}/100</div>
        """, unsafe_allow_html=True)

        # ✅ STATUS
        if score >= 90:
            st.success("✅ Excellent Design")
        elif score >= 70:
            st.warning("⚠️ Needs Improvement")
        else:
            st.error("❌ Major Issues Found")

        # ✅ COMMENTS
        st.subheader("📋 Issues Found")

        if comments:
            for c in comments:
                st.markdown(f'<div class="comment-box">{c}</div>', unsafe_allow_html=True)
        else:
            st.success("✅ No issues found")

        # ✅ TXT DOWNLOAD
        report_text = "\n".join(comments)
        st.download_button(
            "📥 Download TXT",
            data=report_text,
            file_name="report.txt"
        )

        # ✅ PDF DOWNLOAD
        pdf = create_pdf(comments, score)
        st.download_button(
            "📄 Download PDF",
            data=pdf,
            file_name="report.pdf"
        )

# -----------------------------------
# ✅ FOOTER
# -----------------------------------
st.markdown("---")
st.caption("AI-assisted tool | Final review by design engineer required")
