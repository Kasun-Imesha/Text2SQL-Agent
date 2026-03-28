import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).parent.parent))

from autogen_agentchat.agents import AssistantAgent

from utils import get_model_client
from prompts import sql_executor_agent_prompt
from tools import execute_sql_sqlite, execute_sql_sqlalchemy


def get_sql_executor_agent():
    sql_executor_agent = AssistantAgent(
        "sql_executor",
        model_client=get_model_client(),
        system_message=sql_executor_agent_prompt,
        tools=[execute_sql_sqlite],
        # tools=[execute_sql_sqlalchemy],
    )
    
    return sql_executor_agent


if __name__ =="__main__":
    import asyncio
    from autogen_core import CancellationToken
    from autogen_agentchat.messages import TextMessage, BaseTextChatMessage
    
    sql_executor_agent = get_sql_executor_agent()
    # res = asyncio.run(sql_executor_agent.run(
    #     task="""
    #     SELECT country, COUNT(*) AS customer_count
    #     FROM customers
    #     GROUP BY country
    #     ORDER BY customer_count DESC
    #     LIMIT 1;
    #     """
    # ))
    res = asyncio.run(sql_executor_agent.on_messages(
        [TextMessage(
            content="""
            SELECT country, COUNT(*) AS customer_count
            FROM customers
            GROUP BY country
            ORDER BY customer_count DESC
            LIMIT 1;
            """,
            source="user"
        )],
        cancellation_token=CancellationToken(),
    ))
    print(res.chat_message.content)
    print("---" * 20)
    print(res.inner_messages)
    