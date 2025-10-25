import asyncio
import ollama
from ollama import AsyncClient
import logging
from typing import List, Dict, Any

logger = logging.getLogger(__name__)

async def run_chat(messages: List[Dict[str, str]], model: str = "gemma3:4b", url: str = "http://localhost:11434", timeout: int = 30):
    client = AsyncClient(host=url, timeout=timeout)
    full_response = ""

    try:
        async for part in await client.chat(
            model=model,
            messages=messages,
            stream=True
        ):
            content_chunk = part.get("message", {}).get("content", "")
            full_response += content_chunk
            print(content_chunk, end="", flush=True)
        print("\n\n✅ Full response:\n" + full_response.strip())
        return full_response

    except Exception as exc:
        logger.error(f"Ollama chat failed with model {model} at {url}. Exception: {exc}", exc_info=True)
        raise RuntimeError(f"Ollama chat failed with model {model} at {url}. See logs for details.") from exc

def health_check(url: str = "http://localhost:11434", timeout: int = 5) -> bool:
    """Check if the Ollama endpoint is healthy."""
    try:
        client = ollama.Client(host=url, timeout=timeout)
        client.list()
        return True
    except Exception as e:
        logger.warning(f"Health check failed: {e}")
        return False

def list_models(url: str = "http://localhost:11434", timeout: int = 30) -> list[dict[str, any]]:
    """List available models from the Ollama endpoint."""
    try:
        client = ollama.Client(host=url, timeout=timeout)
        models = client.list()
        logger.info(f"Models response: {models}")
        model_list = models.get('models', [])
        if not model_list:
            logger.warning("No models found in the response.")
            return []
        
        result = []
        for model in model_list:
            logger.info(f"Processing model: {model}")
            if 'model' in model:
                result.append({
                    'name': model['model'],
                    'size': model.get('size', 'N/A'),
                    'modified_at': model.get('modified_at', 'N/A')
                })
            else:
                logger.warning(f"Model entry does not have a 'model' key: {model}")
        return result
    except Exception as e:
        logger.error(f"Failed to list models: {e}")
        return []