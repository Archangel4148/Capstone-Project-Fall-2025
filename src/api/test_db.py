from database_service import DatabaseService

def main():

    print("Running database test...")

    # 2. Create table
    DatabaseService.create_table(
        "students",
        {
            "id": "SERIAL PRIMARY KEY",
            "name": "TEXT",
            "grade": "INTEGER",
            "on_probation": "BOOLEAN",
        }
    )
    print("Created table (or verified it exists).")

    # 3. Insert demo row
    DatabaseService.insert(
        "students",
        {
            "name": "Simon Edmunds",
            "grade": 95,
            "on_probation": False,
        }
    )
    print("Inserted row.")

    # 4. Select
    rows = DatabaseService.select("students", ["id", "name", "grade", "on_probation"], None)
    print("All rows:")
    for row in rows:
        print(row)

    # 5. Update
    DatabaseService.update(
        "students",
        {"on_probation": True},
        [("name", "=", "Simon Edmunds")]
    )
    print("Updated rows.")

    # 6. Select again
    rows = DatabaseService.select("students", ["name", "on_probation"], None)
    print("Rows after update:")
    for row in rows:
        print(row)

    # 7. Delete
    DatabaseService.delete("students", [("name", "=", "Simon Edmunds")])
    print("Deleted row.")

    # 8. Final check
    rows = DatabaseService.select("students", None, None)
    print("Final rows:")
    print(rows)

if __name__ == "__main__":
    main()
