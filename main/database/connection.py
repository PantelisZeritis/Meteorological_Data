import os
import psycopg2
from psycopg2.extensions import connection, cursor
from dotenv import load_dotenv, find_dotenv

# Το find_dotenv() ψάχνει δυναμικά στο directory tree για να βρει το .env
load_dotenv(find_dotenv())

class DBConnection:
    def __init__(self):
        self.connection = None
        self.cursor = None

    def connect(self) -> dict:
        try:
            self.connection = psycopg2.connect(
                dbname = os.getenv("PG_DB"),
                user = os.getenv("PG_USER"),
                password = os.getenv("PG_PASS"),
                host = os.getenv("PG_HOST"),
                port = os.getenv("PG_PORT")
            )

            self.cursor = self.connection.cursor()
            return {"success": "ok"}
        except Exception as error:
            # Τυπώνουμε το πραγματικό σφάλμα στο terminal για να μην ψάχνουμε στα τυφλά
            print(f"PostgreSQL Connection Error: {error}")
            return {"error": str(error)}

    def get_connection(self) -> connection | None:
        return None if self.connection is None else self.connection

    def get_cursor(self) -> cursor | None:
        return None if self.cursor is None else self.cursor

    def close(self) -> None:
        if self.cursor is None or self.connection is None:
            print("Error: Tried to close a non-existent database connection")
            return

        self.cursor.close()
        self.connection.close()