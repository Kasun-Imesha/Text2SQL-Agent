import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).parent.parent))

from autogen_agentchat.agents import AssistantAgent

from utils import get_model_client
from prompts import sql_generator_agent_prompt


def get_sql_generator_agent():
    sql_generator_agent = AssistantAgent(
        "sql_generator",
        model_client=get_model_client(),
        system_message=sql_generator_agent_prompt,
    )
    
    return sql_generator_agent
