from groq import Groq
import json
import os
from typing import Dict, Any
from run.agents.base import ProviderAgent


class LLMAgent(ProviderAgent):
    def __init__(self):
        self.client = Groq(api_key=os.getenv("GROQ_API_KEY"))

    def execute(self, prompt: str, context: Dict[str, Any]) -> Dict[str, Any]:
        response = self.client.chat.completions.create(
            model="openai/gpt-oss-120b",
            temperature=0,
            messages=[
                {"role": "system", "content": "Transform context. Return JSON only."},
                {"role": "user", "content": f"{prompt}\n\nContext:\n{json.dumps(context)}"},
            ],
        )
        return json.loads(response.choices[0].message.content)
