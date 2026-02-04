from collections.abc import Generator
from typing import Any

import requests

from dify_plugin import Tool
from dify_plugin.entities.tool import ToolInvokeMessage


class ExaAnswerTool(Tool):
    def _invoke(self, tool_parameters: dict[str, Any]) -> Generator[ToolInvokeMessage, None, None]:
        api_key = self.runtime.credentials["exa_api_key"]
        query = tool_parameters.get("query", "")
        if not query:
            raise ValueError("Query is required")

        text = tool_parameters.get("text", False)
        model = tool_parameters.get("model", "exa")

        payload: dict[str, Any] = {
            "query": query,
            "model": model,
        }

        if text:
            payload["contents"] = {"text": True}

        headers = {
            "x-api-key": api_key,
            "Content-Type": "application/json",
        }

        response = requests.post("https://api.exa.ai/answer", json=payload, headers=headers)
        response.raise_for_status()
        result_data = response.json()

        yield self.create_json_message(result_data)
        yield self.create_text_message(self._format_results(result_data, query))

    def _format_results(self, data: dict, query: str) -> str:
        answer = data.get("answer", "No answer generated.")
        sources = data.get("results", [])

        lines = [f"## Exa Answer\n", f"**Question:** {query}\n", f"**Answer:**\n{answer}\n"]

        if sources:
            lines.append(f"\n### Sources ({len(sources)})\n")
            for i, s in enumerate(sources, 1):
                title = s.get("title", "Untitled")
                url = s.get("url", "")
                lines.append(f"{i}. [{title}]({url})")

                if s.get("publishedDate"):
                    lines.append(f"   Published: {s['publishedDate']}")

                if s.get("text"):
                    text = s["text"][:300] + "..." if len(s.get("text", "")) > 300 else s.get("text", "")
                    lines.append(f"   ```\n   {text}\n   ```")

            lines.append("")

        return "\n".join(lines)
