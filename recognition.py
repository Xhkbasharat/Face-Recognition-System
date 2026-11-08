from dataclasses import dataclass

from face_engine import FaceEngine


@dataclass
class Match:

    person_key: str | None

    display_name: str

    score: float

    accepted: bool


class FaceMatcher:

    def __init__(
        self,
        engine,
        database,
        threshold=0.48
    ):

        self.engine = engine

        self.database = database

        self.threshold = threshold


    # Identify a detected face
    def identify(self, face):

        query_embedding = self.engine.embedding(face)

        stored_faces = self.database.all_embeddings()

        if not stored_faces:

            return Match(
                None,
                "Unknown",
                -1.0,
                False
            )

        best_matches = {}

        # Compare with registered embeddings
        for key, name, stored_embedding in stored_faces:

            score = self.engine.cosine_similarity(
                query_embedding,
                stored_embedding
            )

            if (
                key not in best_matches
                or score > best_matches[key][0]
            ):

                best_matches[key] = (
                    score,
                    name
                )

        # Find best matching identity
        best_key, (best_score, best_name) = max(
            best_matches.items(),
            key=lambda item: item[1][0]
        )

        # Apply recognition threshold
        if best_score >= self.threshold:

            return Match(
                best_key,
                best_name,
                best_score,
                True
            )

        return Match(
            None,
            "Unknown",
            best_score,
            False
        )
