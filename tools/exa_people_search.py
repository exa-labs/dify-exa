from collections.abc import Generator
from typing import Any

import requests

from dify_plugin import Tool
from dify_plugin.entities.tool import ToolInvokeMessage


class ExaPeopleSearchTool(Tool):
    def _invoke(self, tool_parameters: dict[str, Any]) -> Generator[ToolInvokeMessage, None, None]:
        api_key = self.runtime.credentials["exa_api_key"]
        query = tool_parameters.get("query", "")
        if not query:
            raise ValueError("Search query is required")

        num_results = int(tool_parameters.get("num_results", 10))
        include_domains = tool_parameters.get("include_domains", "")
        text_contents = tool_parameters.get("text_contents", False)
        highlights = tool_parameters.get("highlights", False)
        summary = tool_parameters.get("summary", False)
        livecrawl = tool_parameters.get("livecrawl")

        include_domains_list = [d.strip() for d in include_domains.split(",") if d.strip()] if include_domains else []

        payload: dict[str, Any] = {
            "query": query,
            "category": "people",
            "numResults": num_results,
        }

        if include_domains_list:
            payload["includeDomains"] = include_domains_list
        if livecrawl:
            payload["livecrawl"] = livecrawl

        contents = {}
        if text_contents:
            contents["text"] = True
        if highlights:
            contents["highlights"] = True
        if summary:
            contents["summary"] = True
        if contents:
            payload["contents"] = contents

        headers = {
            "x-api-key": api_key,
            "Content-Type": "application/json",
        }

        response = requests.post("https://api.exa.ai/search", json=payload, headers=headers)
        response.raise_for_status()
        result_data = response.json()

        yield self.create_json_message(result_data)
        yield self.create_text_message(self._format_results(result_data, query))

    def _format_results(self, data: dict, query: str) -> str:
        results = data.get("results", [])
        lines = [f"## Exa People Search Results\n", f"**Query:** {query}\n", f"**Results:** {len(results)}\n"]

        for i, r in enumerate(results, 1):
            title = r.get("title", "Untitled")
            url = r.get("url", "")
            lines.append(f"### {i}. [{title}]({url})\n")

            if "score" in r:
                lines.append(f"**Score:** {r['score']:.4f}")

            if r.get("summary"):
                lines.append(f"\n**Summary:** {r['summary']}\n")

            if r.get("highlights"):
                lines.append("\n**Highlights:**")
                for h in r["highlights"]:
                    lines.append(f"> {h}")

            if r.get("text"):
                text = r["text"][:500] + "..." if len(r.get("text", "")) > 500 else r.get("text", "")
                lines.append(f"\n```\n{text}\n```")

            lines.append("---\n")

        return "\n".join(lines)
