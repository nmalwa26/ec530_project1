# LLM-Powered SQL Query System

## Overview 
This project implements a modular system that allows users to load CSV data into a SQLite database and query that data using either raw SQL or natural language. Natural-language queries are converted into SQL using a Large Language Model (LLM), and all queries are validated before execution to ensure safety and correctness. The system is designed with a strong emphasis on separation of concerns, where each module handles a specific responsibility within the overall workflow.

## Modules 
### CSV Loader
This project implements a modular system that allows users to load CSV data into a SQLite database and query that data using either raw SQL or natural language. Natural-language queries are converted into SQL using a Large Language Model (LLM), and all queries are validated before execution to ensure safety and correctness. The system is designed with a strong emphasis on separation of concerns, where each module handles a specific responsibility within the overall workflow.

### Schema Manager 
The Schema Manager is responsible for understanding and managing the structure of the database. It retrieves existing table schemas using SQLite’s PRAGMA table_info() command and represents schemas in a structured format. It also compares incoming CSV schemas with existing database schemas to determine whether a table should be created, appended to, or flagged as a conflict. Additionally, it provides schema information to other modules such as the Query Service and LLM Adapter. Testing for this module ensures that schema extraction is correct, schema comparisons behave as expected, and the correct decisions are made in different scenarios.

### SQLite Manager
The Schema Manager is responsible for understanding and managing the structure of the database. It retrieves existing table schemas using SQLite’s PRAGMA table_info() command and represents schemas in a structured format. It also compares incoming CSV schemas with existing database schemas to determine whether a table should be created, appended to, or flagged as a conflict. Additionally, it provides schema information to other modules such as the Query Service and LLM Adapter. Testing for this module ensures that schema extraction is correct, schema comparisons behave as expected, and the correct decisions are made in different scenarios.

### SQL Validator 
The SQLite Manager handles all direct interactions with the database. It establishes connections to the SQLite database, creates tables dynamically based on schema definitions, inserts rows using parameterized queries, and executes SELECT queries. It also provides functionality to list tables and retrieve schema metadata. The tests for this module verify that tables are created correctly, data is inserted and retrieved accurately, and query execution returns results in the expected format.

### LLM Adapter
The SQL Validator plays a critical role in ensuring database safety. It enforces strict rules by allowing only SELECT queries and rejecting any queries that attempt to modify the database, such as INSERT, UPDATE, DELETE, or DROP. It also checks that all referenced tables and columns exist in the database schema and prevents execution of multiple SQL statements in a single query. The validator includes logic to handle joins, aggregate functions, and aliases at a basic level. Testing focuses on confirming that valid queries pass and invalid queries are correctly rejected, including cases involving unknown tables, unknown columns, and unsafe SQL patterns.

### Query Service
The LLM Adapter is responsible for converting natural-language queries into SQL statements. It constructs prompts that include schema context, sends these prompts to the OpenAI API, and extracts SQL from the model’s response. Importantly, the output of the LLM is treated as untrusted input and must be validated before execution. The tests for this module verify correct prompt construction and SQL extraction, while API calls are mocked to ensure tests remain deterministic and do not depend on external services.

### CLI Interface
The Query Service acts as the central orchestrator of the system. It routes queries based on their type: raw SQL queries are sent directly to the SQL Validator and then to the database, while natural-language queries are first processed by the LLM Adapter, then validated, and finally executed. The Query Service also formats query results into a readable output for the user. Testing for this module ensures that both SQL and natural-language query flows function correctly, including handling validation failures and formatting results properly.

## Design Decisions
The system was designed with modularity in mind, but beyond that, each module was implemented in a way that emphasizes simplicity, testability, and robustness. The goal was not only to separate responsibilities, but to ensure that each component could be independently reasoned about and validated.

The CSV Loader was implemented to return structured data rather than directly interacting with the database. Instead of inserting data itself, it outputs a clean representation of table name, columns, and rows. This design makes the module reusable and easy to test, since its behavior is purely deterministic and independent of external systems like SQLite. Additionally, type inference was kept simple and mapped directly to SQLite types to avoid unnecessary complexity while still supporting realistic datasets.

The CSV Loader was implemented to return structured data rather than directly interacting with the database. Instead of inserting data itself, it outputs a clean representation of table name, columns, and rows. This design makes the module reusable and easy to test, since its behavior is purely deterministic and independent of external systems like SQLite. Additionally, type inference was kept simple and mapped directly to SQLite types to avoid unnecessary complexity while still supporting realistic datasets.

The Schema Manager was implemented as a logic layer that understands database structure without executing queries. Instead of tightly coupling schema decisions with database operations, it returns structured decisions such as create, append, or conflict. This allows other modules, like the CLI, to decide how to act on those outcomes. This separation makes the system more flexible and easier to extend, while also allowing the schema logic to be tested independently of the database.

The SQLite Manager was implemented as the only module responsible for direct database interaction. All SQL execution, table creation, and data insertion are centralized here. This design ensures that database access is controlled and predictable. Parameterized queries were used for inserts to avoid SQL injection and ensure safe handling of data. By isolating all database logic in one place, it becomes easier to debug, test, and modify database-related functionality without affecting other parts of the system.

The SQL Validator was implemented using lightweight parsing rather than a full SQL parser. The goal was to enforce key safety constraints without introducing unnecessary complexity. Regular expressions were used to extract tables and columns, and additional logic was added to handle common SQL patterns such as joins, aggregate functions, and aliases. The validator was designed to fail safely, rejecting any query that does not clearly meet the rules. This approach prioritizes security and simplicity over completeness, which is appropriate for the scope of the project.

The LLM Adapter was implemented with a clear separation between prompt construction, API interaction, and SQL extraction. The API call is isolated in a single function, which makes it easy to mock during testing and prevents external dependencies from affecting test results. The prompt was designed to be schema-aware and to enforce strict output formatting, ensuring that the model returns only SQL. Additionally, the adapter includes logic to clean and extract SQL from potentially messy model outputs, making the system more robust to variations in LLM responses.

The Query Service was implemented as the central orchestration layer that connects all other modules. Instead of embedding logic directly, it delegates responsibilities to the validator, LLM adapter, and database manager. It was designed to support multiple input modes (sql and natural_language) through a single interface, making it easy to extend. The service also standardizes output into a consistent structure, which simplifies both CLI integration and testing.

Finally, the CLI Interface was implemented as a thin wrapper around the system’s functionality. It does not contain business logic, but instead calls into the appropriate modules based on user input. This design ensures that the CLI remains simple and focused on interaction, while all core logic remains in testable modules. This also makes it easy to replace the CLI with another interface in the future, such as a web application, without changing the underlying system.

Overall, the implementation emphasizes clear boundaries between components, minimal coupling, and strong validation of inputs, especially those generated by the LLM.

## Summary 
Finally, the CLI was designed as the final layer of the system and is responsible only for user interaction. By keeping business logic out of the CLI, the system remains modular and can easily be extended in the future, for example by replacing the CLI with a web interface.
