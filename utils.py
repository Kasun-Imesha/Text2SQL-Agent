from dotenv import load_dotenv
load_dotenv()

from autogen_ext.models.openai import OpenAIChatCompletionClient


def get_model_client(model="gpt-4.1", temperature=0, seed=42, max_tokens=200):
    model_client = OpenAIChatCompletionClient(
        model=model,
        temperature=temperature,
        max_tokens=max_tokens,
        seed=seed,
    )
    
    return model_client