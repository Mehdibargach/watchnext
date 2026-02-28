"""
Collaborative Filtering — "Viewers Also Liked"

Finds movies liked by viewers with similar taste, using SVD latent factors.

How it works:
1. We have a giant table: 162K users × 62K movies × ratings (1-5 stars)
2. SVD (Singular Value Decomposition) decomposes this table into hidden patterns
3. Each movie gets a vector of 100 "taste factors" — not based on its content,
   but on HOW USERS RATE IT
4. Movies with similar taste-factor vectors = movies liked by the same type of people
5. Cosine similarity between vectors = how similarly two movies are perceived by users

Key difference from content-based:
- Content-based says "these movies have similar synopses/genres/actors"
- Collaborative says "the same type of people tend to like both these movies"
  (even if the movies look nothing alike on paper)
"""

import pickle
from pathlib import Path
from sklearn.metrics.pairwise import cosine_similarity

MODELS_DIR = Path(__file__).parent.parent.parent / "models"


class CollaborativeModel:
    def __init__(self):
        self.item_factors = None
        self.movie_to_idx = None
        self.idx_to_movie = None
        self.ml_to_tmdb = None
        self.tmdb_to_ml = None

    def load(self):
        """Load pre-trained SVD item factors and ID mappings from disk."""
        with open(MODELS_DIR / "cf_item_factors.pkl", "rb") as f:
            self.item_factors = pickle.load(f)
        with open(MODELS_DIR / "cf_movie_to_idx.pkl", "rb") as f:
            self.movie_to_idx = pickle.load(f)
        with open(MODELS_DIR / "cf_idx_to_movie.pkl", "rb") as f:
            self.idx_to_movie = pickle.load(f)
        with open(MODELS_DIR / "ml_to_tmdb.pkl", "rb") as f:
            self.ml_to_tmdb = pickle.load(f)
        with open(MODELS_DIR / "tmdb_to_ml.pkl", "rb") as f:
            self.tmdb_to_ml = pickle.load(f)

    def get_also_liked(self, tmdb_id, n=5):
        """
        Find movies that viewers with similar taste also liked.

        Returns a list of dicts: [{"tmdb_id": int, "score": float}, ...]
        Returns empty list if the movie is not in MovieLens.
        """
        if self.item_factors is None:
            return []

        # Convert TMDB ID to MovieLens ID
        ml_id = self.tmdb_to_ml.get(tmdb_id)
        if ml_id is None or ml_id not in self.movie_to_idx:
            return []

        idx = self.movie_to_idx[ml_id]
        movie_vec = self.item_factors[idx].reshape(1, -1)

        sims = cosine_similarity(movie_vec, self.item_factors)[0]

        # Top N, excluding the movie itself
        top_indices = sims.argsort()[::-1][1 : n + 1]

        results = []
        for i in top_indices:
            rec_ml_id = self.idx_to_movie[i]
            rec_tmdb_id = self.ml_to_tmdb.get(rec_ml_id)
            if rec_tmdb_id:
                results.append({
                    "tmdb_id": rec_tmdb_id,
                    "score": round(float(sims[i]), 4),
                })
        return results
