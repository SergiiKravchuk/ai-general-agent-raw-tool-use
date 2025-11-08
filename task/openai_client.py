import json
from typing import Any

import requests

from task.models.message import Message
from task.models.role import Role
from task.tools.base import BaseTool


class OpenAIClient:

    def __init__(self, model: str, api_key: str, tools: list[BaseTool] | None = None):
        if not api_key:
            raise ValueError("API KEY is empty")
        self._api_key = api_key
        self._endpoint = "https://api.openai.com/v1/chat/completions"
        self._model = model
        self._tools = {tool.name: tool for tool in tools}
        self._tool_schemas = [tool.openai_schema for tool in tools]

    def get_completion(self, messages: list[Message], print_request: bool = True) -> Message:
        response = requests.post(url=self._endpoint, headers=self._headers(), json=self._payload(messages))

        if response.status_code == 200:
            data = response.json()
            choices = data.get("choices", [])
            if choices:
                choice = choices[0]
                message_data = choice.get("message", {})
                content = message_data.get("content")
                tool_calls = message_data.get("tool_calls")

                model_response = Message(role=Role.AI, content=content, tool_calls=tool_calls)
                finish_reason = choice.get("finish_reason", "")

                match finish_reason:
                    case "tool_calls":
                        messages.append(model_response)  # TODO: double check this mutability
                        tool_results = self._process_tool_calls(tool_calls)
                        messages.extend(tool_results)
                        return self.get_completion(messages=messages)
                    case "stop":
                        messages.append(model_response)  # TODO: double check this mutability
                        return model_response
                    case _:
                        raise ValueError(f"Unknown Finish Reason or Finish Reason was not provided: '{finish_reason}'")
            raise ValueError("Choice was not provided in the model response")
        else:
            raise Exception(f"HTTP {response.status_code}: {response.text}")

    def _payload(self, messages: list[Message]):
        return {
            "model": self._model,
            "messages": [msg.to_dict() for msg in messages],
            "tools": self._tool_schemas
        }

    def _headers(self):
        return {
            "Authorization": f"Bearer {self._api_key}",
            "Content-Type": "application/json"
        }

    def _process_tool_calls(self, tool_calls: list[dict[str, Any]]) -> list[Message]:
        """Process tool calls and add results to messages."""
        tool_messages = []
        for tool_call in tool_calls:
            tool_call_id = tool_call["id"]
            function = tool_call["function"]
            function_name = function["name"]
            function_args = json.loads(function["arguments"])

            tool_result = self._call_tool(function_name, function_args)

            tool_result_message = Message(
                role=Role.TOOL,
                tool_call_id=tool_call_id,
                name=function_name,
                content=tool_result
            )

            tool_messages.append(tool_result_message)

            print(f"FUNCTION '{function_name}'\n{tool_result}\n{'-' * 50}")
        return tool_messages

    def _call_tool(self, tool_name: str, arguments: dict[str, Any]) -> str:
        tool = self._tools.get(tool_name, None)

        if tool:
            return tool.execute(arguments)
        else:
            return f"Unknown tool: {tool_name}"
