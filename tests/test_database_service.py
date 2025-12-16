import sqlite3
import pytest
from pathlib import Path
from api.database_service import DatabaseService, build_condition_suffix, validate_table_name, validate_cols, validate_conditions

@pytest.fixture(autouse=True)
def reset_db(tmp_path):
    # Clear everything so the DB is clean for testing
    DatabaseService.DB_PATH = tmp_path / "test.db"
    DatabaseService.close_all_connections()

def test_connect_and_close():
    # Test connection and closing updates connection list
    conn = DatabaseService.connect()
    assert isinstance(conn, sqlite3.Connection)
    assert conn in DatabaseService._connections

    DatabaseService.close_all_connections()
    assert DatabaseService._connections == []

def test_create_table_and_insert_select():
    # Test table creation, insert, and select
    DatabaseService.create_table("students", {"id": "INTEGER", "name": "TEXT"})
    DatabaseService.insert("students", {"id": 1, "name": "Alice"})
    DatabaseService.insert("students", {"id": 2, "name": "Bob"})

    rows = DatabaseService.select("students", None, None)
    assert len(rows) == 2
    assert (1, "Alice") in rows
    assert (2, "Bob") in rows

    rows_name_only = DatabaseService.select("students", ["name"], None)
    assert rows_name_only == [("Alice",), ("Bob",)]

def test_update_and_delete():
    # Test update and delete
    DatabaseService.create_table("students", {"id": "INTEGER", "name": "TEXT"})
    DatabaseService.insert("students", {"id": 1, "name": "Alice"})
    DatabaseService.insert("students", {"id": 2, "name": "Bob"})

    DatabaseService.update("students", {"name": "Alice2"}, [("id", "=", 1)])
    rows = DatabaseService.select("students", None, None)
    assert (1, "Alice2") in rows
    assert (2, "Bob") in rows

    # Delete a row
    DatabaseService.delete("students", [("id", "=", 2)])
    rows = DatabaseService.select("students", None, None)
    assert rows == [(1, "Alice2")]

    # Delete all rows
    DatabaseService.delete("students", None)
    rows = DatabaseService.select("students", None, None)
    assert rows == []

def test_build_condition_suffix():
    # Check that the condition suffixes are correct
    suffix, params = build_condition_suffix([("id", "=", 1), ("name", "=", "Alice")])
    assert suffix == " WHERE id = ? AND name = ?".replace("?", "?")  # just syntax match
    assert params == [1, "Alice"]

    suffix, params = build_condition_suffix(None)
    assert suffix == ""
    assert params == []

def test_validation_functions():
    # valid names
    validate_table_name("valid_name_1")
    validate_cols(["a", "b1", "c_2"])
    validate_conditions([("col", "=", 1)])

    # invalid table
    with pytest.raises(ValueError):
        validate_table_name("invalid-name!")

    # invalid column
    with pytest.raises(ValueError):
        validate_cols(["good", "bad-name"])

    # invalid conditions
    with pytest.raises(ValueError):
        validate_conditions([("bad-column", "=", 1)])
    with pytest.raises(ValueError):
        validate_conditions([("col", "?!", 1)])

def test_close_all_connections_exception():
    # Test that close_all_connections handles errors in connections
    class BadConnection:
        def close(self):
            raise RuntimeError("fail")

    DatabaseService._connections = [BadConnection()]
    # Should not raise, should just pass
    DatabaseService.close_all_connections()
    assert DatabaseService._connections == []

def test_create_table_no_columns():
    # Test that create_table raises an error if no columns are provided
    with pytest.raises(ValueError, match="No columns provided for table creation"):
        DatabaseService.create_table("students", {})

def test_update_no_values():
    # Test that update raises an error if no values are provided
    with pytest.raises(ValueError, match="No values provided for update"):
        DatabaseService.update("students", {}, [("id", "=", 1)])