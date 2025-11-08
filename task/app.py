import os

from task.openai_client import OpenAIClient
from task.models.conversation import Conversation
from task.models.message import Message
from task.models.role import Role
from task.prompts import SYSTEM_PROMPT
from task.tools.base import BaseTool
from task.tools.users.create_user_tool import CreateUserTool
from task.tools.users.delete_user_tool import DeleteUserTool
from task.tools.users.get_user_by_id_tool import GetUserByIdTool
from task.tools.users.search_users_tool import SearchUsersTool
from task.tools.users.update_user_tool import UpdateUserTool
from task.tools.users.user_client import UserClient
from task.tools.web_search import WebSearchTool

OPENAI_API_KEY = os.getenv('OPENAI_API_KEY')

def print_tool_summary(available_tools: list[BaseTool]):
    import json
    for index, tool in enumerate(available_tools):
        # print(f"Tool {index+1}:\nDescription:{tool.description}\nSchema:\n{json.dumps(tool.input_schema, indent=4)}")
        print(f"Tool {index+1}:\nName: {tool.name}\nDescription: {tool.description}")
        print("\n", end="")

def user_service_tool_factory(user_client: UserClient):
    return [
        GetUserByIdTool(user_client),
        SearchUsersTool(user_client),
        CreateUserTool(user_client),
        UpdateUserTool(user_client),
        DeleteUserTool(user_client)
    ]


def openai_tool_factory(api_key: str):
    return [
        WebSearchTool(api_key),
    ]


def agent_factory(model: str):
    user_client = UserClient()
    available_tools = [*user_service_tool_factory(user_client), *openai_tool_factory(OPENAI_API_KEY)]

    match model:
        case "gpt-4o" | "gpt-4o-search-preview":
            return OpenAIClient(model=model, api_key=OPENAI_API_KEY, tools=available_tools)
        case _: raise Exception(f"Cannot create agent client for unsupported model={model}")


def print_message(message: Message):
    print(f"{message.role.value.upper()} > {message.content}")


def main():
    agent_client = agent_factory("gpt-4o")

    search_user_tool_query = 'Who is Carrie Rhodes?'
    websearch_user_tool_query = 'I would like to add a new user but before that please find some info about them, the name is Andrej Karpathy.'
    get_user_tool_query = 'Do we have a User with ID 303?'
    create_user_tool_query_valid = 'Create a new user with name Andrej Karpathy, email andrej.karpathy@bestai.com. He likes making videos about Generative AI and how they are built.'
    create_user_tool_query_complete = """
    Create a new test user, all data is generated and not real.
    New user's name is Amanda Grace Johnson, born on April 15, 1992, living at 1245 Apt 7B, Sunset Boulevard, Los Angeles, United States.
    Her email is amanda.johnson@example.com, phone number +1-310-555-0734, and gender is female. Add a short bio: “Marketing professional with over 8 years of experience in digital media and brand strategy. Passionate about travel, yoga, and photography.”
    Use the following credit card details: number 4532 7810 4567 2389, CVV 417, expiration date 09/28.
    """
    create_user_tool_query_invalid = 'Create a new User with name Don Family.'
    delete_user_tool_complex_query = 'Delete a user entry with the name Carrie Rhodes'
    update_user_tool_query = "Update email to 'carrie.rhodes.bus@busnow.com' for user with the name Carrie Rhodes"

    user_queries = [
        search_user_tool_query,
        get_user_tool_query,
        create_user_tool_query_valid,
        create_user_tool_query_invalid,
        create_user_tool_query_complete,
        delete_user_tool_complex_query,
        update_user_tool_query,
        websearch_user_tool_query
    ]

    messages = [
        Message(Role.SYSTEM, SYSTEM_PROMPT)
    ]

    for query in user_queries:
        user_message = Message(Role.USER, query)
        print_message(user_message)
        response = agent_client.get_completion([*messages, user_message])
        print_message(response)


main()

#TODO:
# Implement it with Anthropic orchestration model
# https://docs.claude.com/en/docs/agents-and-tools/tool-use/overview#single-tool-example