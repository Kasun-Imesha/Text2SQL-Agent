import os
from dotenv import load_dotenv
load_dotenv()

from typing import List, Any
from sqlalchemy import Engine, text, create_engine


engine = create_engine(f"sqlite:///{os.getenv('DB_NAME')}")

# def execute_sql(query: str) -> List[Any]:
#     try:
#         with engine.connect() as conn:
#             results = conn.execute(text(query)).fetchall()
#             return results
#     except Exception as e:
#         return str(e)

def execute_sql(query: str) -> dict:
    try:
        with engine.connect() as conn:
            result_proxy = conn.execute(text(query))
            rows = result_proxy.fetchall()

            # SQLAlchemy exposes column names via .keys()
            columns = list(result_proxy.keys())

            return {
                "columns": columns,
                "rows": [list(row) for row in rows],
                "row_count": len(rows),
            }
    except Exception as e:
        return {"error": str(e), "columns": [], "rows": [], "row_count": 0}
    
    
if __name__ == "__main__":
    cmds = [
        "SELECT COUNT(*) FROM customers;"
    ]
    
    for cmd in cmds:
        print(execute_sql(cmd))
    