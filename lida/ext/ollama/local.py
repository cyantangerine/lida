import logging
import os
from dataclasses import asdict
from typing import Dict, Union, List

import httpx
from llmx import TextGenerator, TextGenerationConfig, TextGenerationResponse, Message
from llmx.utils import get_models_maxtoken_dict, num_tokens_from_messages, cache_request


class LocalTextGenerator(TextGenerator):
    def __init__(
            self,
            api_key: str = os.environ.get("OPENAI_API_KEY", None),
            provider: str = "ollama",
            organization: str = None,
            api_base: str = None,
            api_version: str = None,
            model: str = None,
            models: Dict = None,
    ):
        super().__init__(provider=provider)
        self.provider = provider.lower()

        # Handle different providers
        self._init_ollama_client(api_base, model)
        self.model_max_token_dict = get_models_maxtoken_dict(models)

    def _init_ollama_client(self, api_base, model):
        """Initialize Ollama client"""
        self.api_base = api_base or os.environ.get("OLLAMA_BASE_URL", "http://localhost:11434")
        self.model_name = model or "gemma3:1b"
        # Create HTTP client for Ollama
        self.client = httpx.Client(base_url=self.api_base, timeout=300.0, proxies={"http://": None})

        # Test connection
        try:
            response = self.client.get("/api/tags")
            if response.status_code == 200:
                logging.info("Successfully connected to Ollama API")
            else:
                logging.warning(f"Ollama API returned status {response.status_code}")
        except Exception as e:
            logging.error(f"Failed to connect to Ollama API: {str(e)}")


    def generate(
            self,
            messages: Union[List[dict], str],
            config: TextGenerationConfig = TextGenerationConfig(),
            **kwargs,
    ) -> TextGenerationResponse:
        use_cache = config.use_cache
        model = self.model_name
        prompt_tokens = num_tokens_from_messages(messages)
        max_tokens = max(
            self.model_max_token_dict.get(
                model, 4096) - prompt_tokens - 10, 200
        )

        # if self.provider == "ollama":
        return self._generate_ollama(messages, config, model, use_cache, max_tokens)
        # else:
        #     return self._generate_openai(messages, config, model, use_cache, max_tokens)

    def _generate_ollama(self, messages, config, model, use_cache, max_tokens):
        """Generate text using Ollama API"""
        # Convert messages to Ollama format
        prompt = self._convert_messages_to_prompt(messages)

        ollama_config = {
            "model": model,
            "prompt": prompt,
            "stream": False,
            # "options": {
            #     "temperature": config.temperature,
            #     "top_p": config.top_p,
            #     "frequency_penalty": config.frequency_penalty,
            #     "presence_penalty": config.presence_penalty,
            #     "num_predict": max_tokens,
            # }
        }

        cache_key_params = ollama_config.copy()
        cache_key_params["messages"] = messages

        if use_cache:
            response = cache_request(cache=self.cache, params=cache_key_params)
            if response:
                return TextGenerationResponse(**response)

        try:
            # Make request to Ollama API
            response = self.client.post("/api/generate", json=ollama_config)
            logging.info(f"Ollama response: {response.text}")
            response.raise_for_status()

            result = response.json()
            # logging.info(f"Ollama response: {result}")

            # Convert Ollama response to expected format
            text_response = [Message(role="assistant", content=result.get("response", ""))]

            response_obj = TextGenerationResponse(
                text=text_response,
                logprobs=[],
                config=ollama_config,
                # usage={"prompt_tokens": prompt_tokens, "completion_tokens": len(result.get("response", "")), "total_tokens": prompt_tokens + len(result.get("response", ""))}
            )

            if use_cache:
                cache_request(
                    cache=self.cache, params=cache_key_params, values=asdict(response_obj)
                )

            return response_obj

        except Exception as e:
            logging.error(f"Error calling Ollama API: {str(e)}")
            raise

    def _convert_messages_to_prompt(self, messages):
        """Convert chat messages to a single prompt for Ollama"""
        if isinstance(messages, str):
            return messages

        prompt_parts = []
        for msg in messages:
            if isinstance(msg, dict):
                role = msg.get("role", "")
                content = msg.get("content", "")
                if role == "system":
                    prompt_parts.append(f"System: {content}")
                elif role == "user":
                    prompt_parts.append(f"User: {content}")
                elif role == "assistant":
                    prompt_parts.append(f"Assistant: {content}")
            else:
                prompt_parts.append(str(msg))

        return "\n".join(prompt_parts) + "\nAssistant:"

    def count_tokens(self, text) -> int:
        return num_tokens_from_messages(text)
