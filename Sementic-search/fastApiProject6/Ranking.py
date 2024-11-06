import numpy as np


def get_ranked_answers(query_embedding, answers):
    """
    Function to rank answers based on their cosine similarity to the query embedding.

    Parameters:
    - query_embedding: A numpy array representing the query embedding.
    - answers: A list of dictionaries where each dictionary contains an 'embedding' field
               along with the answer's content, chapter, and number.

    Returns:
    - A list of dictionaries where each dictionary contains the score (as a float)
      and the corresponding answer data, sorted by score in descending order.
    """

    # Function to compute cosine similarity
    def cosine_similarity(embedding1, embedding2):
        return np.dot(embedding1, embedding2) / (np.linalg.norm(embedding1) * np.linalg.norm(embedding2))

    results = []

    for answer in answers:
        score = cosine_similarity(query_embedding, answer['embedding'])
        results.append({
            "score": float(score),
            "data": {
                "content": answer["content"],
                "chapter": answer["chapter"],
                "number": answer["number"]
            }
        })

    sorted_results = sorted(results, key=lambda x: x['score'], reverse=True)

    return sorted_results
