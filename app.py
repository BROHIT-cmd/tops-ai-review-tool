
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
# ✅ CLEAN UI
# -----------------------------------
st.markdown("""
<style>
.stApp { background-color: white; color: black; }
.header { display: flex; justify-content: flex-end; }
.score-box {
    background-color: #f3f4f6;
    padding: 12px;
    border-radius: 6px;
    text-align: center;
    font-size: 20px;
    font-weight: bold;
}
.comment-box {
    background-color: #f9fafb;
    padding: 8px;
    margin-bottom: 6px;
    border-left: 4px solid red;
}
</style>
""", unsafe_allow_html=True)

# -----------------------------------
# ✅ HEADER
# -----------------------------------
st.markdown('<div class="header">', unsafe_allow_html=True)
try:
    st.image("logo.png", width=200)
except:
    pass
st.markdown('</div>', unsafe_allow_html=True)

# -----------------------------------
# ✅ TABS (MULTI PAGE)
# -----------------------------------
tab1, tab2 = st.tabs(["🔍 Drawing Review Tool", "📐 Template Drawing"])

# ===================================
# ✅ TAB 1 → MAIN TOOL
# ===================================
with tab1:

    st.title("AI Assisted TOPS Drawing review Tool")

    st.caption(
        "Tool Description - This tool automates the validation of TOPS pumping station drawings by analyzing uploaded PDF files against predefined engineering checklists. It helps identify missing or incomplete design elements, provides a compliance score, and generates structured review comments along with downloadable reports. The aim is to support engineers in improving design quality, reducing manual effort, and ensuring consistency across project reviews."
    )

    st.markdown("### Please upload TOPS PS drawing PDF")

    uploaded_files = st.file_uploader(
        "Upload PDF files",
        type="pdf",
        accept_multiple_files=True
    )

    def create_pdf(comments, score):
        buffer = io.BytesIO()
        c = canvas.Canvas(buffer, pagesize=letter)

        c.drawString(30, 750, "AI Drawing Review Report")
        c.drawString(30, 730, f"Score: {score}/100")

        y = 700
        for comment in comments:
            c.drawString(40, y, comment)
            y -= 15

        c.save()
        buffer.seek(0)
        return buffer

    if uploaded_files:

        for file in uploaded_files:

            st.markdown("---")
            st.subheader(f"📄 Reviewing: {file.name}")

            reader = PdfReader(file)
            st.write(f"Total Pages: {len(reader.pages)}")

            full_text = ""

            for i, page in enumerate(reader.pages):
                page_text = page.extract_text()

                if page_text:
                    st.write(f"✅ Page {i+1}")
                    full_text += " " + page_text
                else:
                    st.warning(f"⚠️ Page {i+1} has no readable text")

            full_text = full_text.lower()

            st.success("✅ Drawing Loaded")

            comments = []
            score = 100

            def check_rule(keyword, message, penalty=3):
                if keyword not in full_text:
                    comments.append(message)
                    return penalty
                return 0

            if st.button(f"🚀 Run Review - {file.name}"):

                try:
                    base_path = os.path.dirname(__file__)
                    path = os.path.join(base_path, "Checklist.txt")

                    with open(path, "r", encoding="utf-8") as f:
                        rules = f.readlines()

                    for rule in rules:
                        rule = rule.strip().lower()
                        if rule and not rule.startswith("#"):
                            score -= check_rule(rule, f"⚠️ {rule} missing")

                except:
                    st.error("❌ Checklist not found")

                score = max(score, 0)

                st.markdown(f"""
                <div class="score-box">Score: {score}/100</div>
                """, unsafe_allow_html=True)

                if score >= 90:
                    st.success("✅ Excellent")
                elif score >= 70:
                    st.warning("⚠️ Needs Improvement")
                else:
                    st.error("❌ Major Issues")

                st.subheader("📋 Issues")

                if comments:
                    for c in comments:
                        st.markdown(f'<div class="comment-box">{c}</div>', unsafe_allow_html=True)
                else:
                    st.success("✅ No issues")

                base_name = file.name.replace(".pdf", "")

                report_text = "\n".join(comments)

                st.download_button(
                    f"📥 TXT - {file.name}",
                    data=report_text,
                    file_name=f"{base_name}_report.txt"
                )

                pdf = create_pdf(comments, score)

                st.download_button(
                    f"📄 PDF - {file.name}",
                    data=pdf,
                    file_name=f"{base_name}_report.pdf"
                )

# ===================================
# ✅ TAB 2 → TOPS PS DRAWING TEMPLATE IMAGE
# ===================================
with tab2:

    st.title("TOPS PS DRAWING TEMPLATE IMAGE")

    st.caption(
        "This template drawing represents a standard layout of a TOPS Pumping Station (PS). It serves as a reference for key design components, layout arrangement, and essential elements that should be included in engineering drawings. Users can compare their drawings against this template to ensure completeness, consistency, and compliance with project and standard requirements"
    )
    st.markdown("### Reference Template")

    try:
        st.image("TOPS PS Drawing Template.png", use_container_width=True)
    except:
        st.warning("⚠️ Template image (tops.png) not found")

# -----------------------------------
# ✅ FOOTER
# -----------------------------------
st.markdown("---")
st.caption("AI-assisted tool | Final validation by design engineer required")
