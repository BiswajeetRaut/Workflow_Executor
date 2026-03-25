from __future__ import annotations

import json
from typing import Any, Dict

from groq import Groq

from run.agents.base import ProviderAgent


class LLMAgent(ProviderAgent):
    def __init__(self):
        self.client = Groq()

    def execute(self, prompt: str, context: Dict[str, Any]) -> Dict[str, Any]:
        response = self.client.chat.completions.create(
            model="openai/gpt-oss-120b",
            temperature=0,
            messages=[
                {
                    "role": "system",
                    "content": "Transform context. Return compact JSON object only.",
                },
                {
                    "role": "user",
                    "content": f"Prompt:\n{prompt}\n\nContext:\n{json.dumps(context, ensure_ascii=False)}",
                },
            ],
        )

        content = response.choices[0].message.content.strip()
        try:
            return json.loads(content)
        except json.JSONDecodeError:
            # Keep pipeline resilient for testing when model adds prose around JSON.
            start = content.find("{")
            end = content.rfind("}")
            if start != -1 and end != -1 and end > start:
                return json.loads(content[start : end + 1])
            return {"llm_raw_output": content}
