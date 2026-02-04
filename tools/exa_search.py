from collections.abc import Generator
from typing import Any

import requests

from dify_plugin import Tool
from dify_plugin.entities.tool import ToolInvokeMessage


class ExaSearchTool(Tool):
    def _invoke(self, tool_parameters: dict[str, Any]) -> Generator[ToolInvokeMessage, None, None]:
        api_key = self.runtime.credentials["exa_api_key"]
        query = tool_parameters.get("query", "")
        if not query:
            raise ValueError("Search query is required")

        search_type = tool_parameters.get("search_type", "auto")
        num_results = int(tool_parameters.get("num_results", 10))
        include_domains = tool_parameters.get("include_domains", "")
        exclude_domains = tool_parameters.get("exclude_domains", "")
        start_published_date = tool_parameters.get("start_published_date", "")
        end_published_date = tool_parameters.get("end_published_date", "")
        use_autoprompt = tool_parameters.get("use_autoprompt", True)
        text_contents = tool_parameters.get("text_contents", False)
        highlights = tool_parameters.get("highlights", False)
        summary = tool_parameters.get("summary", False)
        max_age_hours = tool_parameters.get("max_age_hours")
        include_text = tool_parameters.get("include_text")
        exclude_text = tool_parameters.get("exclude_text")
        category = tool_parameters.get("category")
        subpages = tool_parameters.get("subpages")

        include_domains_list = [d.strip() for d in include_domains.split(",") if d.strip()] if include_domains else []
        exclude_domains_list = [d.strip() for d in exclude_domains.split(",") if d.strip()] if exclude_domains else []

        payload: dict[str, Any] = {
            "query": query,
            "numResults": num_results,
            "useAutoprompt": use_autoprompt,
        }

        if search_type and search_type != "auto":
            payload["type"] = search_type
        if include_domains_list:
            payload["includeDomains"] = include_domains_list
        if exclude_domains_list:
            payload["excludeDomains"] = exclude_domains_list
        if start_published_date:
            payload["startPublishedDate"] = start_published_date
        if end_published_date:
            payload["endPublishedDate"] = end_published_date
        if category:
            payload["category"] = category
        if include_text:
            payload["includeText"] = [include_text]
        if exclude_text:
            payload["excludeText"] = [exclude_text]

        contents = {}
        if text_contents:
            contents["text"] = True
        if highlights:
            contents["highlights"] = True
        if summary:
            contents["summary"] = True
        if max_age_hours is not None:
            contents["maxAgeHours"] = int(max_age_hours)
        if subpages is not None:
            contents["subpages"] = int(subpages)
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
        lines = [f"## Exa Search Results\n", f"**Query:** {query}\n", f"**Results:** {len(results)}\n"]

        for i, r in enumerate(results, 1):
            title = r.get("title", "Untitled")
            url = r.get("url", "")
            lines.append(f"### {i}. [{title}]({url})\n")

            if r.get("publishedDate"):
                lines.append(f"**Published:** {r['publishedDate']}")
            if r.get("author"):
                lines.append(f"**Author:** {r['author']}")
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
