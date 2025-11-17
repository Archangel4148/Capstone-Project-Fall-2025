QUERY_PLACEHOLDER = "?"  # This will depend on the database we use


class DatabaseService:
    DB_PATH = None  # Path to the database (this might have to change, idk how APIs work lol)

    # TODO: I'm assuming we need some kind of setup() or connect() function to sync with the database

    @classmethod
    def insert(cls, table_name: str, values: dict):
        """
        Inserts a row into table {table_name} with column values {values}
        (Values should be structured like  {column_name}: {data_to_be_stored})
        Example:
        DatabaseService.insert("students", {"name": "Simon Edmunds", "grade": 41, "on_probation": "False"})
        """
        # Comma-separated list of column names
        keys = ", ".join(values.keys())

        # Comma-separated list of placeholders (places for values to be applied once the query is evaluated)
        placeholders = ", ".join([QUERY_PLACEHOLDER] * len(values))

        # Build the SQL query to insert the row (using placeholders to prevent SQL injection)
        query = f"INSERT INTO {table_name} ({keys}) VALUES ({placeholders})"

        # Get the actual provided values
        parameters = list(values.values())

        # TODO: Finish this, actually apply the values the placeholders and send the query to the DB (Once we pick a DB)

    @classmethod
    def update(cls, table_name: str, values: dict, conditions: list[tuple]):
        """
        Updates values in table {table_name} for rows that meet all conditions.

        Conditions are structured like:
            [(key, conditional_operator, value)]

        Example:
        DatabaseService.update(
            "students",
            {"on_probation": "True"},
            [("name", "=", "Simon Edmunds"), ("grade", "<=", 50)]
        )
        (Updates "on_probation" to "True" for all matching rows.)
        """
        raise NotImplementedError()

    @classmethod
    def select(cls, table_name: str, columns: list[str] | None, conditions: list[tuple] | None):
        """
        Selects data from table {table_name}.

        columns:
            A list of column names to retrieve.
            If None or empty, selects all columns (*).

        conditions:
            A list of tuples: (key, operator, value)
            All conditions are AND-ed together.

        Example:
        DatabaseService.select(
            "students",
            ["name", "grade"],
            [("academic_level", "=", "senior")]
        )
        (Returns name and grade for all seniors.)
        """
        raise NotImplementedError()

    @classmethod
    def delete(cls, table_name: str, conditions: list[tuple]):
        """
        Deletes rows from {table_name} where all conditions are met.

        Conditions are structured like:
            [(key, conditional_operator, value)]

        Example:
        DatabaseService.delete(
            "students",
            [("graduated", "=", True)]
        )
        (Deletes all rows where 'graduated' is True.)
        """
        raise NotImplementedError()
