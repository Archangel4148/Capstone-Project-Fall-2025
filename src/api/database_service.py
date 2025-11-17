QUERY_PLACEHOLDER = "?"  # This will depend on the database we use


class DatabaseService:
    DB_PATH = None  # Path to the database (this might have to change, idk how APIs work lol)

    @classmethod
    def connect(cls):
        """Connect to the database, returning the connection object"""
        raise NotImplementedError()

    @classmethod
    def execute(cls, query: str, parameters: list | tuple = None):
        """
        Executes an SQL query on the database, returning any results from the database

        query:
            The SQL query to be executed, with placeholders
        parameters:
            The parameters to be used in the query (replaces the placeholders)

        Example:
            DatabaseService.execute("INSERT INTO students (name, grade) VALUES (?, ?)", ["Simon Edmunds", 95])
        """
        raise NotImplementedError()

    @classmethod
    def create_table(cls, table_name: str, columns: dict, if_not_exists: bool = True):
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
        if_not_exists:
            When True, suppresses exist errors (only creates the new table if it doesn't exist).

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
        if not columns:
            raise ValueError("No columns provided for table creation")

        # Build the column definitions from the provided column data
        column_definitions = ", ".join(f"{column} {data_type}" for column, data_type in columns.items())

        if_not_exists_section = "IF NOT EXISTS" if if_not_exists else ""

        # Build the full query
        query = f"CREATE TABLE {if_not_exists_section} {table_name} ({column_definitions})"

        # Execute the query, returning the result
        return cls.execute(query)

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

        # Execute the query, returning the result
        return cls.execute(query, parameters)

    @classmethod
    def update(cls, table_name: str, values: dict, conditions: list[tuple] | None):
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

        if not values:
            raise ValueError("No values provided for update")

        # Build the SET query
        set_strings = []
        parameters = []
        for key, value in values.items():
            # Build the SET strings (using parameters for values)
            set_strings.append(f"{key} = {QUERY_PLACEHOLDER}")
            parameters.append(value)

        # Combine the set strings into a single clause
        set_command = ", ".join(set_strings)

        # Base query
        query = f"UPDATE {table_name} SET {set_command}"

        # Conditions
        if conditions:
            condition_strings = []
            for key, operator, value in conditions:
                # Add the condition to be checked (using placeholders for values)
                condition_strings.append(f"{key} {operator} {QUERY_PLACEHOLDER}")
                # Add the value to the query parameters
                parameters.append(value)

            # Add the conditions to the query
            query += " WHERE " + " AND ".join(condition_strings)

        # Execute the query, returning the result
        return cls.execute(query, parameters)

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
            If None or empty, selects all rows (*)

        Example:
        DatabaseService.select(
            "students",
            ["name", "grade"],
            [("academic_level", "=", "senior")]
        )
        (Returns name and grade for all seniors.)
        """

        # Build the list of columns (or use wildcard if None or empty)
        columns = ", ".join(columns) if columns else "*"

        # Build the base query and prepare for parameters
        query = f"SELECT {columns} FROM {table_name}"
        parameters = []

        # Conditions
        if conditions:
            condition_strings = []
            for key, operator, value in conditions:
                # Add the condition to be checked (using placeholders for values)
                condition_strings.append(f"{key} {operator} {QUERY_PLACEHOLDER}")
                # Add the value to the query parameters
                parameters.append(value)

            # Add the conditions to the query
            query += " WHERE " + " AND ".join(condition_strings)

        # Execute the query, returning the result
        return cls.execute(query, parameters)

    @classmethod
    def delete(cls, table_name: str, conditions: list[tuple] | None):
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

        # Base query
        query = f"DELETE FROM {table_name}"
        parameters = []

        # Conditions
        if conditions:
            condition_strings = []
            for key, operator, value in conditions:
                # Add the condition to be checked (using placeholders for values)
                condition_strings.append(f"{key} {operator} {QUERY_PLACEHOLDER}")
                # Add the value to the query parameters
                parameters.append(value)

            # Add the conditions to the query
            query += " WHERE " + " AND ".join(condition_strings)

        # Execute the query, returning the result
        return cls.execute(query, parameters)