import streamlit as st
import os
import json

from services.pdf_service import convert_pdf_to_images
from services.ocr_service import extract_text_from_image
from services.splitter_service import split_answers
from services.rag_service import build_rag_data, load_answer_keys
from services.evaluation_service import evaluate_answer

# ---------------- CONFIG ----------------
POPPLER_PATH = r"C:/Users/maree/Downloads/Release-25.12.0-0/poppler-25.12.0/Library/bin"
DATA_PATH = "data"

st.set_page_config(page_title="Evaluation System", layout="wide")

# ---------------- STYLE ----------------
st.markdown("""
<style>

.block-container {
    padding: 2rem 3rem;
}

.title {
    font-size: 32px;
    font-weight: 700;
    margin-bottom: 5px;
}

.subtitle {
    font-size: 14px;
    color: rgba(180,180,180,0.8);
    margin-bottom: 25px;
}

.card {
    padding: 18px;
    border-radius: 10px;
    border: 1px solid rgba(255,255,255,0.08);
    background: rgba(255,255,255,0.03);
    margin-bottom: 15px;
}

.score-box {
    padding: 15px;
    border-radius: 10px;
    border: 1px solid rgba(255,255,255,0.1);
    text-align: center;
    font-size: 18px;
    font-weight: 600;
}

.section {
    margin-top: 25px;
    margin-bottom: 10px;
    font-weight: 600;
    font-size: 20px;
}

button {
    height: 100px !important;
    font-size: 18px !important;
    border-radius: 12px !important;
}

</style>
""", unsafe_allow_html=True)

# ---------------- GRADE FUNCTION ----------------
def calculate_grade(total_score, max_total):

    if max_total == 0:
        return "F"

    percentage = (total_score / max_total) * 100

    if percentage >= 85:
        return "A"
    elif percentage >= 65:
        return "B"
    elif percentage >= 45:
        return "C"
    else:
        return "F"

# ---------------- SESSION ----------------
if "page" not in st.session_state:
    st.session_state.page = "subjects"

# =====================================================
# ---------------- SUBJECT PAGE ----------------
# =====================================================
def show_subject_page():

    st.markdown("<div class='title'>Answer Sheet Evaluation</div>", unsafe_allow_html=True)
    st.markdown("<div class='subtitle'>Select a subject to begin</div>", unsafe_allow_html=True)

    subjects = os.listdir(DATA_PATH)
    cols = st.columns(3)

    for i, subject in enumerate(subjects):
        with cols[i % 3]:

            if st.button(
                subject.upper(),
                key=f"subject_{i}",
                use_container_width=True
            ):
                st.session_state.selected_subject = subject
                st.session_state.page = "evaluation"
                st.rerun()

# =====================================================
# ---------------- EVALUATION PAGE ----------------
# =====================================================
def show_evaluation_page():

    subject = st.session_state.get("selected_subject")

    if not subject:
        st.session_state.page = "subjects"
        st.rerun()

    if st.button("Back"):
        st.session_state.page = "subjects"
        st.rerun()

    st.markdown(f"<div class='title'>{subject.upper()} Evaluation</div>", unsafe_allow_html=True)
    st.markdown("<div class='subtitle'>Upload and evaluate handwritten answer sheets</div>", unsafe_allow_html=True)

    # ---------- LOAD TEST ----------
    tests = os.listdir(os.path.join(DATA_PATH, subject))
    display_tests = [t.replace(".json", "").replace("_", " ").title() for t in tests]
    test_mapping = dict(zip(display_tests, tests))

    selected_display = st.selectbox("Select Test", display_tests)
    selected_test = test_mapping[selected_display]

    file_path = os.path.join(DATA_PATH, subject, selected_test)

    uploaded_file = st.file_uploader("Upload Answer Sheet (PDF)", type=["pdf"])

    if uploaded_file:

        st.success("File received. Processing...")

        # Convert PDF
        with st.spinner("Reading document..."):
            images = convert_pdf_to_images(uploaded_file, POPPLER_PATH)

        st.write(f"{len(images)} pages detected")

        # Extract text
        full_text = ""
        progress = st.progress(0)

        with st.spinner("Extracting content..."):
            for i, img in enumerate(images):
                full_text += extract_text_from_image(img) + "\n"
                progress.progress((i + 1) / len(images))

        if not full_text.strip():
            st.error("No text extracted")
            return

        # Structure answers
        with st.spinner("Understanding answers..."):
            student_answers = split_answers(full_text)

        if not student_answers:
            st.error("Could not detect answers")
            return

        # Load keys
        answer_keys = load_answer_keys(file_path)

        # Build RAG
        with st.spinner("Preparing evaluation..."):
            rag_data = build_rag_data(student_answers, answer_keys)

        # Evaluate
        results = []
        total_score = 0
        max_total = 0

        with st.spinner("Evaluating responses..."):
            for q_id, data in rag_data.items():
                if "error" not in data:
                    try:
                        result = evaluate_answer(q_id, data)
                    except Exception as e:
                        result = {
                            "question_id": q_id,
                            "score": 0,
                            "max_score": data["max_score"],
                            "feedback": str(e),
                            "matched_keywords": [],
                            "missing_keywords": data["keywords"]
                        }

                    results.append(result)
                    total_score += result["score"]
                    max_total += result["max_score"]

        st.success("Evaluation completed")

        # ---------- GRADE ----------
        grade = calculate_grade(total_score, max_total)

        # ---------- SUMMARY ----------
        st.markdown("<div class='section'>Summary</div>", unsafe_allow_html=True)

        col1, col2, col3, col4 = st.columns(4)

        col1.markdown(f"<div class='score-box'>{total_score}<br><span style='font-size:12px;'>Total Score</span></div>", unsafe_allow_html=True)

        col2.markdown(f"<div class='score-box'>{max_total}<br><span style='font-size:12px;'>Maximum</span></div>", unsafe_allow_html=True)

        percentage = round((total_score / max_total) * 100, 2) if max_total else 0

        col3.markdown(f"<div class='score-box'>{percentage}%<br><span style='font-size:12px;'>Percentage</span></div>", unsafe_allow_html=True)

        col4.markdown(f"<div class='score-box'>{grade}<br><span style='font-size:12px;'>Grade</span></div>", unsafe_allow_html=True)

        # ---------- RESULTS ----------
        st.markdown("<div class='section'>Detailed Evaluation</div>", unsafe_allow_html=True)

        for r in results:

            st.markdown("<div class='card'>", unsafe_allow_html=True)

            col1, col2 = st.columns([1, 4])

            with col1:
                st.markdown(f"""
                <div class='score-box'>
                    {r['question_id']}<br>
                    <span style="font-size:14px;">{r['score']} / {r['max_score']}</span>
                </div>
                """, unsafe_allow_html=True)

            with col2:
                st.markdown("**Feedback**")
                st.write(r["feedback"])

                if r.get("missing_keywords"):
                    st.markdown(f"""
                    <div style="
                        margin-top:8px;
                        padding:10px;
                        border-radius:6px;
                        border:1px solid rgba(255,80,80,0.3);
                    ">
                    Missing: {", ".join(r["missing_keywords"])}
                    </div>
                    """, unsafe_allow_html=True)

                if r.get("matched_keywords"):
                    st.markdown(f"""
                    <div style="
                        margin-top:6px;
                        padding:10px;
                        border-radius:6px;
                        border:1px solid rgba(80,255,120,0.3);
                    ">
                    Covered: {", ".join(r["matched_keywords"])}
                    </div>
                    """, unsafe_allow_html=True)

            st.markdown("</div>", unsafe_allow_html=True)

