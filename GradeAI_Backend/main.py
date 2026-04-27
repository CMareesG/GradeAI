from fastapi import FastAPI, UploadFile, File, Form
from fastapi.middleware.cors import CORSMiddleware
import os

from services.pdf_service import convert_pdf_to_images
from services.ocr_service import extract_text_from_image
from services.splitter_service import split_answers
from services.rag_service import build_rag_data, load_answer_keys
from services.evaluation_service import evaluate_answer
from services.embedding_service import compute_similarity

app = FastAPI()

# ---------------- CORS ----------------
app.add_middleware(
    CORSMiddleware,
    allow_origins=["http://localhost:3000"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

POPPLER_PATH = "C:/Users/ASUS/Downloads/Release-25.12.0-0/poppler-25.12.0/Library/bin"
DATA_PATH = "data"


def normalize_score(score):
    integer_part = int(score)
    decimal_part = score - integer_part

    if decimal_part < 0.25:
        return integer_part
    elif decimal_part < 0.75:
        return integer_part + 0.5
    else:
        return integer_part + 1


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


# ---------------- MAIN API ----------------
@app.post("/evaluate")
async def evaluate(
    file: UploadFile = File(...),
    subject: str = Form(...),
    test: str = Form(...)
):
    file_bytes = await file.read()

    # PDF → Images
    images = convert_pdf_to_images(file_bytes, POPPLER_PATH)

    # OCR
    full_text = ""
    for img in images:
        full_text += extract_text_from_image(img) + "\n"

    # Split answers
    student_answers = split_answers(full_text)

    # Load answer keys
    answer_key_path = os.path.join(DATA_PATH, subject, test)
    answer_keys = load_answer_keys(answer_key_path)

    # Build RAG mapping
    rag_data = build_rag_data(student_answers, answer_keys)

    results = []
    total_score = 0
    max_total = 0

    for q_id, data in rag_data.items():

        if "error" in data:
            continue

        try:
            result = evaluate_answer(q_id, data)

            relevance_score = compute_similarity(
                data["student_answer"],
                data["question"]
            )

            if relevance_score < 0.3:
                result["score"] = 0
                result["feedback"] = "Answer does not match the question"
                result["embedding_similarity"] = 0
                result["final_score"] = 0

                results.append(result)
                max_total += result["max_score"]
                continue

            similarity = compute_similarity(
                data["student_answer"],
                data["correct_answer"]
            )

            embedding_score = similarity * data["max_score"]

            final_score = (
                0.7 * result["score"] +
                0.3 * embedding_score
            )

            final_score = normalize_score(final_score)

            # Update result
            result["embedding_similarity"] = round(similarity, 3)
            result["final_score"] = final_score
            result["score"] = final_score

            results.append(result)
            total_score += final_score
            max_total += result["max_score"]

        except Exception as e:
            results.append({
                "question_id": q_id,
                "score": 0,
                "max_score": data["max_score"],
                "feedback": f"Error: {str(e)}"
            })
            max_total += data["max_score"]

    total_score = normalize_score(total_score)

    grade = calculate_grade(total_score, max_total)

    return {
        "total_score": total_score,
        "max_score": max_total,
        "percentage": round((total_score / max_total) * 100, 2) if max_total else 0,
        "grade": grade,
        "results": results
    }


# ---------------- GET TESTS ----------------
@app.get("/tests/{subject}")
def get_tests(subject: str):
    path = os.path.join(DATA_PATH, subject)

    if not os.path.exists(path):
        return []

    return [f for f in os.listdir(path) if f.endswith(".json")]


# ---------------- GET SUBJECTS ----------------
@app.get("/subjects")
def get_subjects():
    return [
        f for f in os.listdir(DATA_PATH)
        if os.path.isdir(os.path.join(DATA_PATH, f))
    ]