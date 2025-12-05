import re
import sqlite3

QUERY_PLACEHOLDER = "?"  # This is defined by SQLite


class DatabaseService:
    @classmethod
    def connect(cls) -> sqlite3.Connection:
        """Connects to the database, returning the connection object"""
        return sqlite3.connect("nudgy_database.db")

    @classmethod
    def initialize(cls):
        cls.create_table(
            "calendar",
            {
                "calendar_item_id": "INTEGER PRIMARY KEY",
                "datetime": "TEXT",
                "event_name": "TEXT",
                "event_description": "TEXT",
                "duration": "INTEGER",
                "include_to_do_task": "INTEGER",
                "has_reminder": "INTEGER",
            }
        )
        cls.create_table(
            "screen_time",
            {
                "application_path": "TEXT",
                "query_timestamp": "INTEGER",
            }
        )
        cls.create_table(
            "to_do_list",
            {
                "task_id": "INTEGER PRIMARY KEY",
                "description": "TEXT",
                "due_date": "TEXT",
                "include_calendar_item": "INTEGER",
            }
        )
        cls.create_table(
            "timer",
            {
                "name": "TEXT",
                "duration": "INTEGER",
                "is_main_timer": "BOOL"
            }
        )
        cls.create_table(
            "event_map",
            {
                "event_id": "INTEGER",
                "to_do_item_id": "INTEGER",
                "calendar_item_id": "INTEGER",
            }
        )


    @classmethod
    def execute(cls, query: str, parameters: list | tuple = None) -> list | None:
        """
        Executes an SQL query on the database, returning any results from the database

        query:
            The SQL query to be executed, with placeholders
        parameters:
            The parameters to be used in the query (replaces the placeholders)

        Example:
            DatabaseService.execute("INSERT INTO students (name, grade) VALUES (?, ?)", ["Simon Edmunds", 95])
        """
        with cls.connect() as connection:
            cursor = connection.execute(query, parameters or [])

            if cursor.description:
                return cursor.fetchall()

            return None

    @classmethod
    def create_table(cls, table_name: str, columns: dict, force: bool = False) -> list | None:
        """
        Creates a table named {table_name} with the given columns.

        columns:
            holds column names and data types
            Example:
                {
                    "id": "INTEGER PRIMARY KEY",
                    "name": "TEXT",
                    "age": "INTEGER",
                    "gpa": "REAL"
                }
        force:
            When False, suppresses exist errors (only creates the new table if it doesn't exist).

        Example:
        DatabaseService.create_table(
            "students",
            {
                "id": "INTEGER PRIMARY KEY",
                "name": "TEXT",
                "grade": "TEXT",
                "academic_level": "TEXT",
            }
        )
        """
        validate_table_name(table_name)
        validate_cols(columns)

        if not columns:
            raise ValueError("No columns provided for table creation")

        column_definitions = ", ".join(f"{column} {data_type}" for column, data_type in columns.items())
        if_not_exists_section = "IF NOT EXISTS" if not force else ""

        query = f"CREATE TABLE {if_not_exists_section} {table_name} ({column_definitions})"

        return cls.execute(query)

    @classmethod
    def insert(cls, table_name: str, values: dict) -> list | None:
        """
        Inserts a row into table {table_name} with column values {values}
        (Values should be structured like  {column_name}: {data_to_be_stored})
        Example:
        DatabaseService.insert("students", {"name": "Simon Edmunds", "grade": 41, "on_probation": "False"})
        """
        validate_table_name(table_name)
        validate_cols(list(values.keys()))

        keys = ", ".join(values.keys())
        placeholders = ", ".join([QUERY_PLACEHOLDER] * len(values))

        query = f"INSERT INTO {table_name} ({keys}) VALUES ({placeholders})"
        parameters = list(values.values())

        return cls.execute(query, parameters)

    @classmethod
    def update(cls, table_name: str, values: dict, conditions: list[tuple] | None) -> list | None:
        """
        Updates values in table {table_name} for rows that meet all conditions.

        conditions:
            Structured like [(key, conditional_operator, value)]
            If None or empty, selects all rows (*)

        Example:
        DatabaseService.update(
            "students",
            {"on_probation": "True"},
            [("name", "=", "Simon Edmunds"), ("grade", "<=", 50)]
        )
        (Updates "on_probation" to "True" for all matching rows.)
        """
        validate_table_name(table_name)
        validate_cols(list(values.keys()))
        validate_conditions(conditions)

        if not values:
            raise ValueError("No values provided for update")

        set_strings = []
        set_params = []
        for key, value in values.items():
            set_strings.append(f"{key} = {QUERY_PLACEHOLDER}")
            set_params.append(value)

        set_command = ", ".join(set_strings)

        condition_suffix, condition_params = build_condition_suffix(conditions)
        query = f"UPDATE {table_name} SET {set_command}{condition_suffix}"

        parameters = set_params + condition_params

        return cls.execute(query, parameters)

    @classmethod
    def select(cls, table_name: str, columns: list[str] | None, conditions: list[tuple] | None) -> list | None:
        """
        Selects data from table {table_name}.

        columns:
            A list of column names to retrieve.
            If None or empty, selects all columns (*).

        conditions:
            A list of tuples: (key, operator, value)
            All conditions are AND-ed together.
            If None or empty, selects all rows (*)

        Example:
        DatabaseService.select(
            "students",
            ["name", "grade"],
            [("academic_level", "=", "senior")]
        )

        This method returns a list of all rows. Each row is represented as a tuple of values for each selected column
        """
        validate_table_name(table_name)
        validate_cols(columns)

        columns = ", ".join(columns) if columns else "*"

        condition_suffix, parameters = build_condition_suffix(conditions)
        query = f"SELECT {columns} FROM {table_name}{condition_suffix}"

        return cls.execute(query, parameters)

    @classmethod
    def delete(cls, table_name: str, conditions: list[tuple] | None) -> list | None:
        """
        Deletes rows from {table_name} where all conditions are met.

        conditions:
            Structured like [(key, conditional_operator, value)]
            ** WARNING: If conditions is None, deletes ALL rows!

        Example:
        DatabaseService.delete(
            "students",
            [("graduated", "=", True)]
        )
        (Deletes all rows where 'graduated' is True.)
        """
        validate_table_name(table_name)
        validate_conditions(conditions)

        condition_suffix, parameters = build_condition_suffix(conditions)
        query = f"DELETE FROM {table_name}{condition_suffix}"

        return cls.execute(query, parameters)


def build_condition_suffix(conditions: list[tuple]) -> tuple[str, list]:
    """
    Builds an SQL-style suffix for conditions in a query, returning the parameters along with a suffix of the form:
    ' WHERE {condition1} AND {condition2} AND {condition3}'
    """
    parameters = []
    if conditions:
        condition_strings = []
        for key, operator, value in conditions:
            condition_strings.append(f"{key} {operator} {QUERY_PLACEHOLDER}")
            parameters.append(value)

        return " WHERE " + " AND ".join(condition_strings), parameters
    else:
        return "", []

def validate_table_name(table_name: str) -> None:
    """
    If table_name is invalid, throws a ValueError.
    Valid is considered to be alphanumeric, including underscores.
    """

    if re.fullmatch("^([0-9A-Za-z_])*$", table_name) is None:
        raise ValueError("Invalid query")

def validate_cols(cols: list[str]) -> None:
    """
    If any column is invalid, throws a ValueError. If cols is None, then returns.
    Valid is considered to be alphanumeric, including underscores.
    """

    if cols is None:
        return

    for c in cols:
        if re.fullmatch("^([0-9A-Za-z_])*$", c) is None:
            raise ValueError("Invalid query")

def validate_conditions(conditions: list[tuple]) -> None:
    """
    If any column is invalid, throws a ValueError. If conditions is None, then returns.
    Valid is considered to be alphanumeric, including underscores.
    """

    if conditions is None:
        return

    for c in conditions:
        column = c[0]
        operator = c[1]

        if re.fullmatch("^([0-9A-Za-z_])*$", column) is None or not operator in ("=", ">", "<", ">=", "<=", "<>"):
            raise ValueError("Invalid query")
