import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).parent.parent))

from autogen_agentchat.agents import AssistantAgent

from utils import get_model_client
from tools.query_db import query_db
from prompts import retriever_agent_prompt


def get_retriever_agent():
    retriever_agent = AssistantAgent(
        "retriever",
        model_client=get_model_client(),
        system_message=retriever_agent_prompt,
        tools=[query_db],
    )
    
    return retriever_agent


if __name__ == "__main__":
    import asyncio
    retriever_agent = get_retriever_agent()
    res = asyncio.run(retriever_agent.run(task="Which country has the most customers?"))
    print(res)
    