import streamlit as st
from pypdf import PdfReader
from reportlab.lib.pagesizes import letter
from reportlab.pdfgen import canvas
import io

# -----------------------------------
# ✅ PAGE CONFIG
# -----------------------------------
st.set_page_config(page_title="AI Drawing Review", layout="wide")

# -----------------------------------
# ✅ CLEAN WHITE STYLE + BORDER
# -----------------------------------
st.markdown("""
<style>

/* ✅ White background */
.stApp {
    background-color: white;
    color: black;
}

/* ✅ Top-right logo */
.header {
    display: flex;
    justify-content: flex-end;
    margin-bottom: 10px;
}

/* ✅ MAIN BORDER BOX */
.main-card {
    border: 1px solid #d1d5db;
    border-radius: 12px;
    padding: 30px;
    background-color: #ffffff;
    margin-top: 15px;
    box-shadow: 0 4px 10px rgba(0,0,0,0.05);
}

/* ✅ Reduce upload spacing */
.stFileUploader > div {
    padding-top: 6px;
    padding-bottom: 6px;
}

/* ✅ Buttons */
.stButton button {
    background-color: #1F6FEB;
    color: white;
    border-radius: 6px;
    padding: 8px;
    font-weight: bold;
}

/* ✅ Download buttons */
.stDownloadButton button {
    background-color: #2da44e;
    color: white;
    border-radius: 6px;
}

/* ✅ Score box */
.score-box {
    background-color: #f3f4f6;
    padding: 12px;
    border-radius: 6px;
    text-align: center;
    font-size: 20px;
    font-weight: bold;
    margin-top: 10px;
}

/* ✅ Comment box */
.comment-box {
    background-color: #f9fafb;
    padding: 8px;
    margin-bottom: 6px;
    border-left: 4px solid #dc2626;
    border-radius: 4px;
}

</style>
""", unsafe_allow_html=True)

# -----------------------------------
# ✅ HEADER (LOGO RIGHT)
# -----------------------------------
st.markdown('<div class="header">', unsafe_allow_html=True)
try:
    st.image("logo.png", width=160)
except:
    pass
st.markdown('</div>', unsafe_allow_html=True)

# -----------------------------------
# ✅ TITLE + DESCRIPTION
# -----------------------------------
st.title("AI-Assisted TOPS Drawing Validation System")

st.caption(
    "Validates TOPS pumping station drawings using checklist-based rules and generates review comments with scoring."
)

# -----------------------------------
# ✅ MAIN CARD START
# -----------------------------------
st.markdown('<div class="main-card">', unsafe_allow_html=True)

# -----------------------------------
# ✅ UPLOAD SECTION
# -----------------------------------
st.markdown("### Please upload TOPS PS drawing PDF")

uploaded_file = st.file_uploader(
    "Upload PDF file",
    type="pdf"
)

# -----------------------------------
# ✅ PDF REPORT FUNCTION
# -----------------------------------
def create_pdf(comments, score):
    buffer = io.BytesIO()
    c = canvas.Canvas(buffer, pagesize=letter)

    c.drawString(30, 750, "AI Drawing Review Report")
    c.drawString(30, 730, f"Score: {score}/100")

    y = 700
    for comment in comments:
        c.drawString(30, y, comment)
        y -= 15

    c.save()
    buffer.seek(0)
    return buffer

# -----------------------------------
# ✅ MAIN LOGIC
# -----------------------------------
if uploaded_file is not None:

    reader = PdfReader(uploaded_file)
    text = ""

    for page in reader.pages:
        page_text = page.extract_text()
        if page_text:
            text += page_text

    text = text.lower()

    st.success("✅ Drawing Loaded Successfully")

    comments = []
    score = 100

    def check_rule(keyword, message, penalty=3):
        if keyword not in text:
            comments.append(message)
            return penalty
        return 0

    try:
        with open("Checklist.txt", "r", encoding="utf-8") as file:
            rules = file.readlines()

        for rule in rules:
            rule = rule.strip().lower()
            if rule and not rule.startswith("#"):
                score -= check_rule(rule, f"⚠️ {rule} missing")

    except:
        st.error("❌ Checklist file not found")

    if st.button("🚀 Run Review"):

        score = max(score, 0)

        # ✅ SCORE DISPLAY
        st.markdown(f"""
        <div class="score-box">Score: {score}/100</div>
        """, unsafe_allow_html=True)

        # ✅ STATUS
        if score >= 85:
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
# ✅ CLOSE CARD
# -----------------------------------
st.markdown('</div>', unsafe_allow_html=True)

# -----------------------------------
# ✅ FOOTER
# -----------------------------------
st.markdown("---")
st.caption("AI-assisted tool | Final validation by design engineer required")
