from pathlib import Path
import sqlite3
import sys
import os

import pytest

# Add the src folder to sys.path
sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), "..", "src")))

from api.database_service import DatabaseService

tmp_path = Path(__file__).parent.resolve()

@pytest.fixture(scope="session", autouse=True)
def temp_db():
    # Create a temporary database file
    db_file = tmp_path / "test.db"
    original_path = DatabaseService.DB_PATH
    DatabaseService.DB_PATH = str(db_file)
    DatabaseService.initialize()

    yield DatabaseService  # pass to tests if needed

    # Make sure everything is disconnected, then delete the temporary DB
    DatabaseService.close_all_connections()
    try:
        db_file.unlink()
    except PermissionError:
        print(f"Could not delete {db_file} – it may still be in use.")
    DatabaseService.DB_PATH = original_path
