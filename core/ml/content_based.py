"""
Content-Based Filtering — "Similar Movies"

Finds movies with similar characteristics (synopsis, genres, actors).

How it works:
1. Each movie's text profile = synopsis + genres (repeated for weight) + top actors
2. TF-IDF converts these text profiles into numeric vectors
   (rare/distinctive words get high scores, common words get low scores)
3. Cosine similarity between vectors = how similar two movies are
   (1.0 = identical profile, 0.0 = nothing in common)

Genres are repeated 3x so they weigh more than random word overlaps in the synopsis.
This prevents a thriller from matching a comedy just because both mention "family".
"""

import pickle
from pathlib import Path
from sklearn.metrics.pairwise import cosine_similarity

MODELS_DIR = Path(__file__).parent.parent.parent / "models"


class ContentBasedModel:
    def __init__(self):
        self.tfidf_matrix = None
        self.tmdb_ids = None
        self.tmdb_id_to_idx = None

    def load(self):
        """Load pre-trained TF-IDF matrix and ID mappings from disk."""
        with open(MODELS_DIR / "cb_tfidf_matrix.pkl", "rb") as f:
            self.tfidf_matrix = pickle.load(f)
        with open(MODELS_DIR / "cb_tmdb_ids.pkl", "rb") as f:
            self.tmdb_ids = pickle.load(f)

        self.tmdb_id_to_idx = {tid: i for i, tid in enumerate(self.tmdb_ids)}

    def get_similar(self, tmdb_id, n=5):
        """
        Find the N most similar movies to a given movie.

        Returns a list of dicts: [{"tmdb_id": int, "score": float}, ...]
        Returns empty list if the movie is not in our corpus.
        """
        if self.tfidf_matrix is None:
            return []

        if tmdb_id not in self.tmdb_id_to_idx:
            return []

        idx = self.tmdb_id_to_idx[tmdb_id]
        sim_scores = cosine_similarity(
            self.tfidf_matrix[idx : idx + 1], self.tfidf_matrix
        )[0]

        # Top N, excluding the movie itself
        top_indices = sim_scores.argsort()[::-1][1 : n + 1]

        return [
            {"tmdb_id": self.tmdb_ids[i], "score": round(float(sim_scores[i]), 4)}
            for i in top_indices
        ]
