import sys
import os

# Add the project root to sys.path to resolve imports
sys.path.append(os.path.abspath(os.path.join(os.path.dirname(__file__), '../..')))

from agents.vocabulary_agent.config import settings
from agents.vocabulary_agent.services.llm_service import LLMService

def test_llm():
    print(f"Testing LLM with model: {settings.LLM_MODEL}")
    print(f"Base URL: {settings.OPENAI_BASE_URL}")
    print(f"API Key: {settings.OPENAI_API_KEY[:4]}***")

    try:
        service = LLMService()
        response = service.client.chat.completions.create(
            model=settings.LLM_MODEL,
            messages=[
                {"role": "user", "content": "Hello, are you GLM?"}
            ]
        )
        print("Response:", response.choices[0].message.content)
        print("LLM Connection Successful!")
    except Exception as e:
        print(f"Error: {e}")

if __name__ == "__main__":
    test_llm()
