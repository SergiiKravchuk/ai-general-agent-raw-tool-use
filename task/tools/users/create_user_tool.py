from typing import Any

from pydantic import ValidationError

from task.tools.users.base import BaseUserServiceTool
from task.tools.users.models.user_info import UserCreate


class CreateUserTool(BaseUserServiceTool):

    @property
    def name(self) -> str:
        return "add_user"

    @property
    def description(self) -> str:
        return "Creates a new User with given user attributes"

    @property
    def input_schema(self) -> dict[str, Any]:
        return UserCreate.model_json_schema()

    def execute(self, arguments: dict[str, Any]) -> str:
        try:
            validated_model = UserCreate.model_validate(arguments)
            return self._user_client.add_user(validated_model)
        except ValidationError as validation_e:
            return f"Invalid User attributes for creating a new User. Details: {str(validation_e)}"
        except Exception as e:
            return f"Error while creating a new user: {str(e)}"
