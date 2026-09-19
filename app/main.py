import argparse
import os
import sys
import json

from openai import OpenAI

API_KEY = os.getenv("OPENROUTER_API_KEY")
BASE_URL = os.getenv("OPENROUTER_BASE_URL", default="https://openrouter.ai/api/v1")

AVAILABLE_TOOLS_SCHEMA = [
    {
        "type": "function",
        "function": {
            "name": "Read",
            "description": "Read and return the contents of a file",
            "parameters": {
                "type": "object",
                "properties": {
                    "file_path": {
                        "type": "string",
                        "description": "The path to the file to read",
                    }
                },
                "required": ["file_path"],
            },
        },
    },
    {
        "type": "function",
        "function": {
            "name": "Write",
            "description": "Write content to a file",
            "parameters": {
                "type": "object",
                "properties": {
                    "file_path": {
                        "type": "string",
                        "description": "The path of the file to write to",
                    },
                    "content": {
                        "type": "string",
                        "description": "The content to write to the file",
                    },
                },
                "required": ["file_path", "content"],
            },
        },
    },
]

def execute_tool(tool_call):
    available_tools = {
            "Read" : read_file,
            "Write": write_file
        }

    tool_name = tool_call.function.name

    if tool_name not in available_tools:
        return f"Error: Tool '{tool_name}' is not recognized."

    try:
        tool_args = json.loads(tool_call.function.arguments)
        tool_function = available_tools[tool_name]
        
        # Ensure the result is always cast to a string for the API
        return str(tool_function(**tool_args))
        
    except json.JSONDecodeError:
        return "Error: Failed to parse tool arguments from the LLM."
       



def read_file(file_path: str):
    try:
        with open(file_path) as f:
            return f.read()
    except FileNotFoundError:
        return f"Error: The file at {file_path} was not found."
    except Exception as e:
        return f"Error reading file: {e}"


def write_file(file_path:str,content:str):

    try:
        with open(file_path,"w") as f:
            f.write(content)
            return "File written successfully."
    except Exception as e:
        return f"Error writing file: {e}"


def main():
    p = argparse.ArgumentParser()
    p.add_argument("-p", required=True)
    args = p.parse_args()

    if not API_KEY:
        raise RuntimeError("OPENROUTER_API_KEY is not set")

    client = OpenAI(api_key=API_KEY, base_url=BASE_URL)
    
    messages=[{"role": "user", "content": args.p}]

    while True:

        chat = client.chat.completions.create(
        model="anthropic/claude-haiku-4.5",
        messages = messages,
        tools=AVAILABLE_TOOLS_SCHEMA,
    )
        
        
        if not chat.choices or len(chat.choices) == 0:
            raise RuntimeError("no choices in response")

        response_message = chat.choices[0].message
        messages.append(response_message)

        if not response_message.tool_calls:
            print(response_message.content)
            break

        for tool_call in response_message.tool_calls:
            result = execute_tool(tool_call)

            messages.append({
                "role": "tool" ,
                "tool_call_id": tool_call.id,
                "content":str(result)
            })

    # You can use print statements as follows for debugging, they'll be visible when running tests.
    print("Logs from your program will appear here!", file=sys.stderr)    


if __name__ == "__main__":
    main()
