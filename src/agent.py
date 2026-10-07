import os
import sys
import json
from dotenv import load_dotenv
from groq import Groq

from src.tools import TOOLS_MAP, TOOL_DEFINITIONS
from src.database import close_database
from src.logger import logging
from src.exception import MyCustomException

load_dotenv()

GROQ_API_KEY = os.getenv("GROQ_API_KEY")

if not GROQ_API_KEY:
    logging.error("GROQ_API_KEY environment variable is missing.")
    raise ValueError("GROQ_API_KEY is not set in environment variables.")

groq_client = Groq(api_key=GROQ_API_KEY)

def run_agent(user_prompt: str) -> str:
    try:
        logging.info(f"Received user query: '{user_prompt}'")

        messages = [
            {
                "role": "system",
                "content": (
                    "You are a helpful Personal Finance Assistant. "
                    "You answer user questions strictly by using tools. "
                    "Rule 1: Never guess or invent facts—only use information returned by tools[cite: 3, 4]. "
                    "Rule 2: If a tool returns no data or an error, state clearly that the information could not be found[cite: 3, 4]. "
                    "Rule 3: If no available tool can answer the user's question, admit it directly without inventing an answer[cite: 3]."
                )
            },
            {"role": "user", "content": user_prompt}
        ]

        loop_count = 0
        max_loops = 5  
        while loop_count < max_loops:
            loop_count += 1
            logging.info(f"Starting agent loop iteration {loop_count}...")

            response = groq_client.chat.completions.create(
                model="qwen/qwen3.8-27b",
                messages=messages,
                tools=TOOL_DEFINITIONS,
                temperature=0.1
            )

            response_message = response.choices[0].message
            
            assistant_msg = {
                "role": "assistant",
                "content": response_message.content or ""
            }
            
            if response_message.tool_calls:
                assistant_msg["tool_calls"] = [
                    {
                        "id": tool_call.id,
                        "type": "function",
                        "function": {
                            "name": tool_call.function.name,
                            "arguments": tool_call.function.arguments
                        }
                    }
                    for tool_call in response_message.tool_calls
                ]

            messages.append(assistant_msg)
            if not response_message.tool_calls:
                logging.info("Agent generated final answer.")
                return response_message.content
            for tool_call in response_message.tool_calls:
                function_name = tool_call.function.name
                call_id = tool_call.id
                raw_args = tool_call.function.arguments

                logging.info(f"Executing requested tool: '{function_name}'")

                function_args = {}
                if raw_args and raw_args.strip():
                    try:
                        function_args = json.loads(raw_args)
                    except json.JSONDecodeError as json_err:
                        logging.error(f"Failed to parse arguments for {function_name}: {json_err}")
                if function_name in TOOLS_MAP:
                    try:
                        tool_output = TOOLS_MAP[function_name](function_args)
                    except Exception as exec_err:
                        logging.error(f"Execution error inside tool {function_name}: {exec_err}")
                        tool_output = json.dumps({"status": "error", "message": str(exec_err)})
                else:
                    logging.warning(f"Requested tool '{function_name}' does not exist.")
                    tool_output = json.dumps({"status": "error", "message": f"Tool '{function_name}' is not supported."})

                messages.append({
                    "role": "tool",
                    "tool_call_id": call_id,
                    "content": tool_output
                })

        logging.warning("Exceeded maximum tool interaction loops[cite: 3].")
        return "Sorry, I could not complete your request within the maximum allowed steps."

    except Exception as e:
        logging.error(f"Error in run_agent execution: {str(e)}")
        raise MyCustomException(e, sys)
    finally:
        close_database()