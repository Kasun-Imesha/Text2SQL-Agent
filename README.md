# Text2SQL Agent

A multi-agent system that converts natural language queries into SQL and executes them against a database, displaying results with visualizations.

## What is This?

This project implements an intelligent database assistant that:
- Accepts plain English questions about your database
- Automatically generates appropriate SQL queries
- Executes queries and retrieves results
- Displays results as formatted tables and charts
- Provides optional debug traces of the agent reasoning

The system uses multiple specialized AI agents working together:
- **Retriever Agent**: Searches for relevant database schemas based on user queries
- **SQL Generator Agent**: Creates SQL queries from natural language
- **SQL Validator Agent**: Ensures SQL syntax correctness
- **SQL Executor Agent**: Runs the SQL and retrieves results

## Setup

### Prerequisites
- Python 3.10+
- OpenAI API key

### Installation

1. **Clone or download the project**
   ```bash
   cd DB-Retriever-Agent
   ```

2. **Create a virtual environment (recommended)**
   ```bash
   python -m venv venv
   venv\Scripts\activate  # On Windows
   source venv/bin/activate  # On macOS/Linux
   ```

3. **Install dependencies**
   ```bash
   pip install -r requitements.txt
   ```

4. **Set up environment variables**
   Create a `.env` file in the project root:
   ```
   OPENAI_API_KEY=your_openai_api_key_here
   ```

5. **Build the SQL database (if needed)**
   ```bash
   python misc/build_sqlite_db.py
   ```

5. **Build the Schema database**
   ```bash
   python misc/build_vector_db.py
   ```

## Usage

### Running the Web Interface

Start the Streamlit application:
```bash
streamlit run app.py
```

The app will open in your browser at `http://localhost:8501`

1. Enter a natural language question about your data in the input field
2. Click "Ask" or press Enter
3. The system will:
   - Query the database schema
   - Generate an SQL query
   - Validate and execute the query
   - Display results as a table or chart
4. View the debug trace to see agent reasoning (optional)

### Example Queries
- "How many orders did we receive last month?"
- "Which products have the highest sales?"
- "Show me the top 5 customers by revenue"
- "What's the average order value?"

## Project Structure

```
DB-Retriever-Agent/
├── app.py                 # Main Streamlit web app
├── agent_group.py         # Test Agent orchestration logic
├── prompts.py             # Agent system prompts
├── utils.py               # Utility functions (OpenAI client setup)
├── requitements.txt       # Python dependencies
│
├── agents/                # Individual agent implementations
│   ├── retriever_agent.py        # Schema retrieval
│   ├── sql_generator_agent.py    # SQL generation
│   ├── sql_validator_agent.py    # SQL validation
│   └── sql_executor_agent.py     # Query execution
│   
│
├── tools/                 # Database tools
│   ├── query_db.py              # Vector DB search for schemas
│   ├── database_sqlite.py       # SQLite execution
│   └── database_sqlalchemy.py   # SQLAlchemy execution
│
├── data/                  # Data files for database initialization
│   ├── test_db_schema_creation.sql  # SQL DB schemas
│   ├── test_db_vector_schema_info.csv  # SQL schema info to store in vector db
│   ├── customers.csv
│   ├── orders.csv
│   ├── products.csv
│   ├── suppliers.csv
│   └── order_details.csv
│
├── static/                # Frontend assets
│   └── styles.css
└── misc/                  # Utility scripts
    ├── build_sqlite_db.py       # Create SQLite database
    └── build_vector_db.py       # Create vector embeddings
```

## Configuration

### Database Connection
The system supports both SQLite and SQLAlchemy-based retrievals (`tools/database_sqlite.py`, `tools/database_sqlalchemy.py`). They are used in the executor agent (`agents\sql_executor_agent.py`).

### Vector Database
Chroma is used to store and search database schema embeddings for semantic matching. The vector database is initialized in `vector_db/`.

## Troubleshooting

**Issue: "OPENAI_API_KEY not found"**
- Ensure you've created a `.env` file with your API key

**Issue: Database not found**
- Run `python misc/build_sqlite_db.py` to initialize the test database

**Issue: Module not found errors**
- Reinstall dependencies: `pip install -r requitements.txt`
- Ensure you're in the correct virtual environment

## Notes

- The project uses AutoGen-v0.4 agents for orchestration
- LangChain is used for LLM interactions and embeddings
- Chroma provides vector database capabilities for semantic search
- Results are displayed using Streamlit with pandas DataFrames
