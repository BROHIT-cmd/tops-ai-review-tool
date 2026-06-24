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
# ✅ SIMPLE CLEAN WHITE STYLE
# -----------------------------------
st.markdown("""
<style>

/* ✅ Background */
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

/* ✅ Main container */
.main-card {
    border: 1px solid #ddd;
    border-radius: 10px;
    padding: 25px;
    background-color: #fafafa;
}

/* ✅ Reduce upload box height */
.stFileUploader > div {
    padding-top: 8px;
    padding-bottom: 8px;
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

/* ✅ Comments */
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
    st.image("logo.png", width=180)
except:
    pass
st.markdown('</div>', unsafe_allow_html=True)

# -----------------------------------
# ✅ TITLE
# -----------------------------------
st.title("TOPS PS Drawing Review Tool")

# -----------------------------------
# ✅ MAIN CARD
# -----------------------------------
st.markdown('<div class="main-card">', unsafe_allow_html=True)

# -----------------------------------
# ✅ CLEAN UPLOAD SECTION
# -----------------------------------
st.markdown("### Please upload TOPS PS drawing PDF")

uploaded_file = None

uploaded_file = st.file_uploader(
    "",
    type="pdf",
    label_visibility="collapsed"
)

st.markdown("""
<style>

/* ✅ Make upload area transparent */
[data-testid="stFileUploaderDropzone"] {
    background: transparent;
    border: none;
}

/* ✅ Remove border */
[data-testid="stFileUploader"] {
    border: none;
}

</style>
""", unsafe_allow_html=True)


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
        extracted = page.extract_text()
        if extracted:
            text += extracted

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
        with open("Checklist.txt", "r", encoding="utf-8") as f:
            rules = f.readlines()

        for rule in rules:
            rule = rule.strip().lower()
            if rule and not rule.startswith("#"):
                score -= check_rule(rule, f"⚠️ {rule} missing")

    except:
        st.error("❌ Checklist file not found")

    if st.button("🚀 Run Review"):

        score = max(score, 0)

        # ✅ Score display
        st.markdown(f"""
        <div class="score-box">Score: {score}/100</div>
        """, unsafe_allow_html=True)

        # ✅ Status
        if score >= 85:
            st.success("✅ Excellent Design")
        elif score >= 70:
            st.warning("⚠️ Needs Improvement")
        else:
            st.error("❌ Major Issues Found")

        # ✅ Comments
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