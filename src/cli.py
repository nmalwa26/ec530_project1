from __future__ import annotations

from src.csv_loader import load_csv
from src.schema_manager import (
    build_schema_object,
    generate_create_table_sql,
    get_existing_schemas,
    decide_table_action,
)
from src.sqlite_manager import (
    connect_db,
    create_table,
    insert_rows,
    list_tables,
)
from src.query_service import process_query


def show_menu() -> None:
    """
    Display the available CLI actions.
    """
    print("\n=== LLM SQL System ===")
    print("1. Load CSV")
    print("2. Run SQL query")
    print("3. Ask natural-language question")
    print("4. List tables")
    print("5. Exit")


def handle_load_csv(conn) -> None:
    """
    Handle the CSV ingestion workflow.
    """
    file_path = input("Enter CSV file path: ").strip()

    try:
        csv_data = load_csv(file_path)

        incoming_schema = build_schema_object(
            csv_data["table_name"],
            csv_data["columns"],
        )

        existing_schemas = get_existing_schemas(conn)
        decision = decide_table_action(incoming_schema, existing_schemas)

        if decision["action"] == "create":
            create_sql = generate_create_table_sql(incoming_schema)
            create_table(conn, create_sql)
            insert_rows(conn, decision["table_name"], csv_data["rows"])

            print(
                f"Created table '{decision['table_name']}' "
                f"and inserted {csv_data['row_count']} row(s)."
            )

        elif decision["action"] == "append":
            insert_rows(conn, decision["table_name"], csv_data["rows"])

            print(
                f"Appended {csv_data['row_count']} row(s) "
                f"to table '{decision['table_name']}'."
            )

        elif decision["action"] == "conflict":
            print(f"Schema conflict detected for table '{decision['table_name']}'.")
            print("Options: overwrite, rename, skip")

            choice = input("Choose an option: ").strip().lower()

            if choice == "skip":
                print("Skipped CSV import.")
                return

            elif choice == "overwrite":
                print("Overwrite option not implemented yet.")
                return

            elif choice == "rename":
                new_table_name = input("Enter new table name: ").strip()

                renamed_schema = build_schema_object(
                    new_table_name,
                    csv_data["columns"],
                )
                create_sql = generate_create_table_sql(renamed_schema)
                create_table(conn, create_sql)
                insert_rows(conn, new_table_name, csv_data["rows"])

                print(
                    f"Created table '{new_table_name}' "
                    f"and inserted {csv_data['row_count']} row(s)."
                )
                return

            else:
                print("Invalid choice. Skipping CSV import.")
                return

        else:
            print(f"Unknown schema decision: {decision['action']}")

    except Exception as e:
        print(f"Error loading CSV: {e}")


def handle_sql_query(conn) -> None:
    """
    Handle a raw SQL query entered by the user.
    """
    sql = input("Enter SQL query: ").strip()

    result = process_query(sql, conn, input_mode="sql")

    if result["success"]:
        print(result["formatted_result"])
    else:
        print(result["message"])
        for error in result["errors"]:
            print(f"- {error}")


def handle_natural_language_query(conn) -> None:
    """
    Handle a natural-language query entered by the user.
    """
    user_query = input("Ask a question: ").strip()

    result = process_query(user_query, conn, input_mode="natural_language")

    if result["success"]:
        print(f"Generated SQL: {result['generated_sql']}")
        print(result["formatted_result"])
    else:
        print(result["message"])
        if result.get("generated_sql"):
            print(f"Generated SQL: {result['generated_sql']}")
        for error in result["errors"]:
            print(f"- {error}")


def handle_list_tables(conn) -> None:
    """
    Display all tables currently in the database.
    """
    tables = list_tables(conn)

    if not tables:
        print("No tables found.")
        return

    print("Tables:")
    for table in tables:
        print(f"- {table}")


def run_cli(db_path: str = "app.db") -> None:
    """
    Start the CLI application.
    """
    conn = connect_db(db_path)

    print("Welcome to the LLM SQL System.")

    while True:
        show_menu()
        choice = input("Select an option: ").strip()

        if choice == "1":
            handle_load_csv(conn)

        elif choice == "2":
            handle_sql_query(conn)

        elif choice == "3":
            handle_natural_language_query(conn)

        elif choice == "4":
            handle_list_tables(conn)

        elif choice == "5":
            print("Goodbye!")
            conn.close()
            break

        else:
            print("Invalid option. Please choose 1-5.")