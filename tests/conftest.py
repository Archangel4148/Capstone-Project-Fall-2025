import sys
import os
from unittest.mock import MagicMock, patch

import pytest

# Add the src folder to sys.path (fixes import issues with pytest)
sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), "..", "src")))


@pytest.fixture()
def temp_db(tmp_path_factory):
    # Create a temporary database file
    from api.database_service import DatabaseService
    db_dir = tmp_path_factory.mktemp("db")
    db_file = db_dir / "test.db"
    original_path = DatabaseService.DB_PATH
    DatabaseService.DB_PATH = str(db_file)
    DatabaseService.initialize()

    yield DatabaseService  # pass to tests if needed

    # Make sure everything is disconnected, then delete the temporary DB
    DatabaseService.close_all_connections()
    try:
        db_file.unlink()
    except PermissionError:
        raise ValueError(f"Could not delete {db_file}, it may still be in use.")
    DatabaseService.DB_PATH = original_path

@pytest.fixture(autouse=True)
def mock_notifications():
    """Automatically mock notifypy.Notify so real notifications aren't sent in tests."""
    with patch("notifications.Notify", autospec=True) as mock_notify_cls:
        mock_notify_instance = MagicMock()
        mock_notify_cls.return_value = mock_notify_instance
        yield mock_notify_instance