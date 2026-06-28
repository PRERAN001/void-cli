import os

import requests
from dotenv import load_dotenv

load_dotenv()


class LLMClient:
    def __init__(self, model="nvidia/nemotron-3.5-content-safety:free"):
        self.api_key = os.getenv("OPENROUTER_API_KEY")
        self.model = model
        self.url = "https://openrouter.ai/api/v1/chat/completions"

    def chat(self, messages, tools=None, tool_choice="auto", temperature=0.3):
        if not self.api_key:
            raise ValueError("OPENROUTER_API_KEY not found in .env")

        payload = {
            "model": self.model,
            "messages": messages,
            "temperature": temperature,
        }

        if tools:
            payload["tools"] = tools
            payload["tool_choice"] = tool_choice

        response = requests.post(
            self.url,
            headers={
                "Authorization": f"Bearer {self.api_key}",
                "Content-Type": "application/json",
            },
            json=payload,
            timeout=180,
        )
        response.raise_for_status()

        data = response.json()
        return data["choices"][0]["message"]

    def generate(self, prompt, system_prompt=None, temperature=0.3):
        messages = []

        if system_prompt:
            messages.append({
                "role": "system",
                "content": system_prompt,
            })

        messages.append({
            "role": "user",
            "content": prompt,
        })

        message = self.chat(
            messages=messages,
            temperature=temperature,
        )
        return message.get("content", "")
