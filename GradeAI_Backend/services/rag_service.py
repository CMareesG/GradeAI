import json

def load_answer_keys(file_path):
    """
    Load answer key dynamically based on subject/test
    """
    with open(file_path, "r") as f:
        return json.load(f)


def get_answer_key(q_id, answer_keys):
    """
    Retrieve answer key for given question ID
    """
    return answer_keys.get(q_id)


def build_rag_data(student_answers, answer_keys):
    """
    Combine student answers with answer key
    """
    rag_data = {}

    for q_id, student_ans in student_answers.items():
        answer_data = get_answer_key(q_id, answer_keys)

        if answer_data:
            rag_data[q_id] = {
                "question": answer_data["question"],
                "correct_answer": answer_data["answer"],
                "keywords": answer_data.get("keywords", []),
                "max_score": answer_data["max_score"],
                "student_answer": student_ans
            }
        else:
            rag_data[q_id] = {
                "student_answer": student_ans,
                "error": f"Answer key not found for {q_id}"
            }

    return rag_data