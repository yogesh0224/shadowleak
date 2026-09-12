from functools import lru_cache


@lru_cache(maxsize=1)
def get_semantic_backend():
    from sentence_transformers import SentenceTransformer, util

    return SentenceTransformer("all-MiniLM-L6-v2"), util


def semantic_similarity(secret_fact: str, output_text: str, threshold: float = 0.65):
    if not secret_fact or not output_text:
        return 0.0, False

    model, util = get_semantic_backend()
    emb1 = model.encode(secret_fact, convert_to_tensor=True)
    emb2 = model.encode(output_text, convert_to_tensor=True)

    score = float(util.cos_sim(emb1, emb2)[0][0])

    return score, score >= threshold
