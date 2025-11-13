from typing import Any

from pydantic import ValidationError

from task.tools.users.base import BaseUserServiceTool
from task.tools.users.models.user_info import UserUpdate


class UpdateUserTool(BaseUserServiceTool):

    @property
    def name(self) -> str:
        return "update_user"

    @property
    def description(self) -> str:
        return "Updates attributes for an existing User by ID"

    @property
    def input_schema(self) -> dict[str, Any]:
        return {
            "type": "object",
            "properties": {
                "id": {
                    "type": "number",
                    "description": "User ID"
                },
                "new_attributes": UserUpdate.model_json_schema()
            },
            "required": ["id"]
        }

    def execute(self, arguments: dict[str, Any]) -> str:
        try:
            user_id = arguments.get("id", 0)
            new_attributes = arguments.get("new_attributes", None)
            if user_id and new_attributes:
                validated_model = UserUpdate.model_validate(new_attributes)
                return self._user_client.update_user(user_id, validated_model)
            else:
                return f"User ID is empty, cannot proceed with User Delete operation"
        except ValidationError as validation_e:
            return f"Invalid User attributes for creating a new User. Details: {str(validation_e)}"
        except Exception as e:
            return f"Error while updating user: {str(e)}"

