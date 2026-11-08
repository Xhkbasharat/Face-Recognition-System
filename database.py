import sqlite3
from pathlib import Path
import numpy as np


class FaceDatabase:

    def __init__(self, db_path):

        Path(db_path).parent.mkdir(
            parents=True,
            exist_ok=True
        )

        self.db_path = str(db_path)

        self.create_database()


    def connect(self):

        return sqlite3.connect(self.db_path)


    def create_database(self):

        with self.connect() as conn:

            conn.execute("""
                CREATE TABLE IF NOT EXISTS people (

                    id INTEGER PRIMARY KEY AUTOINCREMENT,

                    person_key TEXT UNIQUE NOT NULL,

                    display_name TEXT NOT NULL,

                    created_at TEXT DEFAULT CURRENT_TIMESTAMP,

                    consent_confirmed INTEGER NOT NULL
                )
            """)

            conn.execute("""
                CREATE TABLE IF NOT EXISTS embeddings (

                    id INTEGER PRIMARY KEY AUTOINCREMENT,

                    person_id INTEGER NOT NULL,

                    vector BLOB NOT NULL,

                    dimension INTEGER NOT NULL,

                    created_at TEXT DEFAULT CURRENT_TIMESTAMP,

                    FOREIGN KEY(person_id)
                    REFERENCES people(id)
                    ON DELETE CASCADE
                )
            """)


    def add_person(self, person_key, display_name, vectors):

        vectors = [
            np.asarray(v, dtype=np.float32).reshape(-1)
            for v in vectors
        ]

        if not vectors:
            raise ValueError("No face embeddings provided.")

        with self.connect() as conn:

            conn.execute("PRAGMA foreign_keys = ON")

            cursor = conn.execute("""
                INSERT INTO people
                (person_key, display_name, consent_confirmed)
                VALUES (?, ?, 1)
            """, (person_key, display_name))

            person_id = cursor.lastrowid

            conn.executemany("""
                INSERT INTO embeddings
                (person_id, vector, dimension)
                VALUES (?, ?, ?)
            """, [
                (person_id, v.tobytes(), v.size)
                for v in vectors
            ])

        return person_id


    def all_embeddings(self):

        with self.connect() as conn:

            rows = conn.execute("""
                SELECT
                    p.person_key,
                    p.display_name,
                    e.vector,
                    e.dimension

                FROM embeddings e

                JOIN people p
                ON p.id = e.person_id
            """).fetchall()

        results = []

        for key, name, blob, dimension in rows:

            vector = np.frombuffer(
                blob,
                dtype=np.float32,
                count=dimension
            ).copy()

            results.append((key, name, vector))

        return results


    def delete_person(self, person_key):

        with self.connect() as conn:

            conn.execute("PRAGMA foreign_keys = ON")

            cursor = conn.execute("""
                DELETE FROM people
                WHERE person_key = ?
            """, (person_key,))

            return cursor.rowcount > 0


    def list_people(self):

        with self.connect() as conn:

            return conn.execute("""
                SELECT
                    person_key,
                    display_name,
                    created_at

                FROM people

                ORDER BY display_name
            """).fetchall()
