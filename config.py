from pathlib import Path

BASE_DIR = Path(__file__).resolve().parent

DATA_DIR = BASE_DIR / "data"

DB_PATH = DATA_DIR / "faces.sqlite3"

MODEL_NAME = "buffalo_l"

MATCH_THRESHOLD = 0.48

DETECTION_SIZE = (640, 640)

CAMERA_INDEX = 0

FRAME_RESIZE_WIDTH = 960
