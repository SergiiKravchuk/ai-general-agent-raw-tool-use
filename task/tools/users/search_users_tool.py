from typing import Any

from task.tools.users.base import BaseUserServiceTool


class SearchUsersTool(BaseUserServiceTool):

    @property
    def name(self) -> str:
        return "search_users"

    @property
    def description(self) -> str:
        return "Searches for existing Users by attributes"

    @property
    def input_schema(self) -> dict[str, Any]:
        return {
            "type": "object",
            "properties": {
                "name": {
                    "type": "string",
                    "description": "Name attribute of a User"
                },
                "surname": {
                    "type": "string",
                    "description": "Surname attribute of a User"
                },
                "email": {
                    "type": "string",
                    "description": "Email attribute of a User"
                },
                "gender": {
                    "type": "string",
                    "description": "Gender attribute of a User"
                }
            }
        }

    def execute(self, arguments: dict[str, Any]) -> str:
        try:
            return self._user_client.search_users(**arguments)
        except Exception as e:
            return f"Error while searching for a user: {str(e)}"
