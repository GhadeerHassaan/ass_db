import oracledb

def get_connection():
    print("=== Oracle Metadata Explorer ===")
    username = input("Enter username: ")
    password = input("Enter password: ")
    host = input("Enter host (default localhost): ") or "localhost"
    port = input("Enter port (default 1521): ") or "1521"
    service_name = input("Enter service name: ")

    dsn = f"{host}:{port}/{service_name}"
    try:
        connection = oracledb.connect(user=username, password=password, dsn=dsn)
        print("Connected successfully!\n")
        return connection
    except oracledb.DatabaseError as e:
        print("Error connecting to database:", e)
        return None

def list_objects(cursor, object_type):
    queries = {
        "Tables": "SELECT table_name FROM user_tables ORDER BY table_name",
        "Views": "SELECT view_name FROM user_views ORDER BY view_name",
        "Sequences": "SELECT sequence_name FROM user_sequences ORDER BY sequence_name",
        "Users": "SELECT username FROM all_users ORDER BY username"
    }

    cursor.execute(queries[object_type])
    results = cursor.fetchall()
    if not results:
        print(f"No {object_type.lower()} found.\n")
        return []

    print(f"\nAvailable {object_type}:")
    for idx, row in enumerate(results, start=1):
        print(f"{idx}. {row[0]}")
    return [row[0] for row in results]

def show_table_metadata(cursor, table_name):
    while True:
        print(f"\nChoose what to view about {table_name}:")
        print("1. Columns")
        print("2. Constraints")
        print("3. Indexes")
        print("4. Back to main menu")
        choice = input("Enter option number: ")

        if choice == "1":
            cursor.execute(f"""
                SELECT column_name, data_type, data_length, nullable
                FROM user_tab_columns
                WHERE table_name = '{table_name.upper()}'
                ORDER BY column_id
            """)
            columns = cursor.fetchall()
            print("\nColumns:")
            for col in columns:
                print(f"{col[0]} | {col[1]}({col[2]}) | Nullable: {col[3]}")

        elif choice == "2":
            cursor.execute(f"""
                SELECT constraint_name, constraint_type, status
                FROM user_constraints
                WHERE table_name = '{table_name.upper()}'
                ORDER BY constraint_name
            """)
            constraints = cursor.fetchall()
            print("\nConstraints:")
            for con in constraints:
                print(f"{con[0]} | Type: {con[1]} | Status: {con[2]}")

        elif choice == "3":
            cursor.execute(f"""
                SELECT index_name, uniqueness
                FROM user_indexes
                WHERE table_name = '{table_name.upper()}'
                ORDER BY index_name
            """)
            indexes = cursor.fetchall()
            print("\nIndexes:")
            for idx_row in indexes:
                print(f"{idx_row[0]} | Unique: {idx_row[1]}")

        elif choice == "4":
            break
        else:
            print("Invalid option. Try again.")

def main():
    connection = get_connection()
    if not connection:
        return

    cursor = connection.cursor()

    while True:
        print("\nSelect the object type you want to view:")
        print("1. Tables")
        print("2. Views")
        print("3. Sequences")
        print("4. Users")
        print("5. Exit")

        option = input("Enter option number: ")

        if option == "1":
            objects = list_objects(cursor, "Tables")
            if objects:
                selection = int(input("Select a table number: "))
                if 1 <= selection <= len(objects):
                    table_name = objects[selection - 1]
                    print(f"\nYou selected: {table_name}")
                    show_table_metadata(cursor, table_name)

        elif option == "2":
            list_objects(cursor, "Views")

        elif option == "3":
            list_objects(cursor, "Sequences")

        elif option == "4":
            list_objects(cursor, "Users")

        elif option == "5":
            print("Exiting...")
            break

        else:
            print("Invalid option. Please try again.")

    cursor.close()
    connection.close()

if __name__ == "__main__":
    main()
