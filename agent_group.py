import asyncio
from autogen_agentchat.ui import Console
from autogen_agentchat.teams import RoundRobinGroupChat
from autogen_agentchat.conditions import TextMentionTermination

from agents import get_sql_generator_agent, get_retriever_agent, get_sql_executor_agent, get_sql_validator_agent

async def main():
    retriever_agent = get_retriever_agent()
    sql_generator_agent = get_sql_generator_agent()
    sql_validator_agent = get_sql_validator_agent()
    sql_executor_agent = get_sql_executor_agent()
    
    termination = TextMentionTermination("DONE")
    
    group_chat = RoundRobinGroupChat(
        participants=[retriever_agent, sql_generator_agent, sql_validator_agent, sql_executor_agent],
        termination_condition=termination,
        max_turns=4,
    )
    
    stream = group_chat.run_stream(
        # task="How many different customers are there?",
        # task="Which country has the most customers?",
        # task="What is the total freight cost per customer?",
        # task="Top 5 best selling products",
        task="Total revenue by product category",
    )
    
    await Console(stream)

if __name__ == "__main__":
    asyncio.run(main())
    
    