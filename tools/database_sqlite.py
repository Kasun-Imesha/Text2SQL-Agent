import os
from dotenv import load_dotenv
load_dotenv()

import sqlite3
from typing import List, Any, Dict


# def execute_sql(query: str) -> List[Any]:
#     conn = sqlite3.connect(os.getenv("DB_NAME"))
#     cursor = conn.cursor()
    
#     try:
#         cursor.execute(query)
#         results = cursor.fetchall()
        
#         return results
#     except Exception as e:
#         return str(e)
#     finally:
#         conn.close()


def execute_sql(query: str) -> Dict[str, Any]:
    conn = sqlite3.connect(os.getenv("DB_NAME"))
    cursor = conn.cursor()
    
    try:
        cursor.execute(query)
        results = cursor.fetchall()
        
        # Extract column names before connection closes
        columns = [desc[0] for desc in cursor.description] if cursor.description else []
        
        return {
            "columns": columns,
            "rows": [list(row) for row in results],
            "row_count": len(results)
        }
    except Exception as e:
        return {"error": str(e), "columns": [], "rows": [], "row_count": 0}
    finally:
        conn.close()


if __name__ == "__main__":
    cmds = [
        "SELECT COUNT(*) FROM customers;",
        """
        SELECT country, COUNT(*) AS customer_count
        FROM customers
        GROUP BY country
        ORDER BY customer_count DESC
        LIMIT 1;
        """
    ]
    
    for cmd in cmds:
        print(execute_sql(cmd))
    