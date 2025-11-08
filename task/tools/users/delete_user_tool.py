from typing import Any

from task.tools.users.base import BaseUserServiceTool


class DeleteUserTool(BaseUserServiceTool):

    @property
    def name(self) -> str:
        return "delete_users"

    @property
    def description(self) -> str:
        return "Deletes an existing User by ID"

    @property
    def input_schema(self) -> dict[str, Any]:
        return {
            "type": "object",
            "properties": {
                "id": {
                    "type": "number",
                    "description": "User ID"
                }
            },
            "required": ["id"]
        }

    def execute(self, arguments: dict[str, Any]) -> str:
        try:
            user_id = arguments.get("id", 0)
            if user_id:
                return self._user_client.delete_user(user_id)
            else:
                return f"User ID is empty, cannot proceed with User Delete operation"
        except Exception as e:
            return f"Error while deleting a new user: {str(e)}"
