# LLM-Powered SQL Query System

## Overview 
### This project implements a modular system that allows users to load CSV data into a SQLite database and query that data using either raw SQL or natural language. Natural-language queries are converted into SQL using a Large Language Model (LLM), and all queries are validated before execution to ensure safety and correctness. The system is designed with a strong emphasis on separation of concerns, where each module handles a specific responsibility within the overall workflow.

## CSV Loader
### This project implements a modular system that allows users to load CSV data into a SQLite database and query that data using either raw SQL or natural language. Natural-language queries are converted into SQL using a Large Language Model (LLM), and all queries are validated before execution to ensure safety and correctness. The system is designed with a strong emphasis on separation of concerns, where each module handles a specific responsibility within the overall workflow.

## Schema Manager 
### The Schema Manager is responsible for understanding and managing the structure of the database. It retrieves existing table schemas using SQLite’s PRAGMA table_info() command and represents schemas in a structured format. It also compares incoming CSV schemas with existing database schemas to determine whether a table should be created, appended to, or flagged as a conflict. Additionally, it provides schema information to other modules such as the Query Service and LLM Adapter. Testing for this module ensures that schema extraction is correct, schema comparisons behave as expected, and the correct decisions are made in different scenarios.

## SQLite Manager
### The Schema Manager is responsible for understanding and managing the structure of the database. It retrieves existing table schemas using SQLite’s PRAGMA table_info() command and represents schemas in a structured format. It also compares incoming CSV schemas with existing database schemas to determine whether a table should be created, appended to, or flagged as a conflict. Additionally, it provides schema information to other modules such as the Query Service and LLM Adapter. Testing for this module ensures that schema extraction is correct, schema comparisons behave as expected, and the correct decisions are made in different scenarios.

