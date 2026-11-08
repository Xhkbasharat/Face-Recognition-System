import cv2
import numpy as np

from insightface.app import FaceAnalysis


class FaceEngine:

    def __init__(
        self,
        model_name="buffalo_l",
        detection_size=(640, 640)
    ):

        self.app = FaceAnalysis(
            name=model_name,
            providers=["CPUExecutionProvider"]
        )

        self.app.prepare(
            ctx_id=0,
            det_size=detection_size
        )


    # Detect faces in an image
    def detect(self, frame):

        faces = self.app.get(frame)

        # Sort faces by size
        faces = sorted(
            faces,
            key=lambda face:
            (face.bbox[2] - face.bbox[0]) *
            (face.bbox[3] - face.bbox[1]),
            reverse=True
        )

        return faces


    # Extract normalized face embedding
    @staticmethod
    def embedding(face):

        vector = np.asarray(
            face.embedding,
            dtype=np.float32
        )

        norm = np.linalg.norm(vector)

        if norm == 0:
            raise ValueError("Invalid face embedding")

        return vector / norm


    # Calculate cosine similarity
    @staticmethod
    def cosine_similarity(vector1, vector2):

        vector1 = np.asarray(
            vector1,
            dtype=np.float32
        )

        vector2 = np.asarray(
            vector2,
            dtype=np.float32
        )

        denominator = (
            np.linalg.norm(vector1) *
            np.linalg.norm(vector2)
        )

        if denominator == 0:
            return -1.0

        similarity = np.dot(
            vector1,
            vector2
        ) / denominator

        return float(similarity)


    # Draw face detection rectangle
    @staticmethod
    def draw_box(
        frame,
        face,
        label,
        color=(40, 200, 40)
    ):

        x1, y1, x2, y2 = map(
            int,
            face.bbox
        )

        cv2.rectangle(
            frame,
            (x1, y1),
            (x2, y2),
            color,
            2
        )

        cv2.putText(
            frame,
            label,
            (x1, max(25, y1 - 10)),
            cv2.FONT_HERSHEY_SIMPLEX,
            0.65,
            color,
            2,
            cv2.LINE_AA
              )
