from typing import Any

import requests

from task.tools.base import BaseTool


class WebSearchTool(BaseTool):

    def __init__(self, api_key: str):
        self.__api_key = api_key
        self.__endpoint = "https://api.openai.com/v1/chat/completions"

    # Sample of tool config:
    # {
    #     "type": "function",
    #     "function": {
    #         "name": "web_search_tool",
    #         "description": "Tool for WEB searching.",
    #         "parameters": {
    #             "type": "object",
    #             "properties": {
    #                 "request": {
    #                     "type": "string",
    #                     "description": "The search query or question to search for on the web"
    #                 }
    #             },
    #             "required": [
    #                 "request"
    #             ]
    #         }
    #     }
    # }

    @property
    def name(self) -> str:
        return "web_search_tool"

    @property
    def description(self) -> str:
        return "Searches for additional public information about Users on the Web"

    @property
    def input_schema(self) -> dict[str, Any]:
        return {
            "type": "object",
            "properties": {
                "request": {
                    "type": "string",
                    "description": "The search query or question to search for on the Web"
                }
            },
            "required": ["request"]
        }

    @staticmethod
    def _payload(arguments: dict[str, Any]):
        return {
            "model": "gpt-4o-search-preview",
            "messages": [
                {"role": "user", "content": str(arguments["request"])}
            ],
            "web_search_options": {
                "search_context_size": "low"
            }
        }

    def _headers(self):
        return {
            "Authorization": f"Bearer {self.__api_key}",
            "Content-Type": "application/json"
        }

    def execute(self, arguments: dict[str, Any]) -> str:
        response = requests.post(url=self.__endpoint, headers=self._headers(), json=self._payload(arguments))
        if response.status_code == 200:
            data = response.json()
            choices = data.get("choices", [])
            if choices:
                return choices[0].get("message", {}).get("content")
            raise ValueError("Choice was not provided in the model response")
        else:
            raise Exception(f"HTTP {response.status_code}: {response.text}")
