from config import genai
from sklearn.metrics.pairwise import cosine_similarity


def get_embedding(text):
    response = genai.embed_content(
        model="models/gemini-embedding-001",
        content=text
    )
    return response["embedding"]


def compute_similarity(text1, text2):
    vec1 = get_embedding(text1)
    vec2 = get_embedding(text2)

    return cosine_similarity([vec1], [vec2])[0][0]