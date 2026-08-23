import os
import sys
import subprocess
import json
from openai import OpenAI

# 1. Setup OpenRouter Client
API_KEY = os.environ.get("OPENROUTER_API_KEY", "")
if not API_KEY:
    print("❌ OpenRouter API Key is missing! Please set OPENROUTER_API_KEY.")
    exit(1)

client = OpenAI(
    base_url="https://openrouter.ai/api/v1",
    api_key=API_KEY,
)

MODEL_ID = "meta-llama/llama-3.3-70b-instruct"

# 2. Define the Bash Tool
def execute_bash_command(command):
    try:
        result = subprocess.run(command, shell=True, capture_output=True, text=True, timeout=30)
        output = result.stdout
        if result.stderr:
            output += f"\nError Output:\n{result.stderr}"
        if not output.strip():
            output = "Command executed successfully with no output."
        return output
    except Exception as e:
        return f"Failed to execute command: {str(e)}"

tools = [
    {
        "type": "function",
        "function": {
            "name": "execute_bash_command",
            "description": "Execute a bash command. Use this to read files, run scripts, list directories, etc.",
            "parameters": {
                "type": "object",
                "properties": {
                    "command": {
                        "type": "string",
                        "description": "The bash command to execute."
                    }
                },
                "required": ["command"]
            }
        }
    }
]

# 3. Load or Initialize Conversation History
history_file = "/tmp/history.json"
# Fallback to local directory if not in E2B
if not os.path.exists("/tmp"):
    history_file = "history.json"

if os.path.exists(history_file):
    with open(history_file, "r") as f:
        messages = json.load(f)
else:
    messages = [
        {"role": "system", "content": "You are a highly capable CLI AI assistant. You have access to a tool to run bash commands."}
    ]

# 4. Interactive CLI Loop
print("="*50)
print("🤖 DAYTONA CLI AGENT STARTED (Like Claude)")
print("Type 'exit' or 'quit' to end the session.")
print("="*50)

while True:
    try:
        user_input = input("\nYou: ")
        if user_input.strip().lower() in ['exit', 'quit']:
            print("Goodbye!")
            break
            
        if not user_input.strip():
            continue
            
        messages.append({"role": "user", "content": user_input})
        
        # Ask the LLM
        response = client.chat.completions.create(
            model=MODEL_ID,
            messages=messages,
            tools=tools,
            tool_choice="auto",
        )
        
        response_message = response.choices[0].message
        
        # Did the LLM decide to call a tool?
        if response_message.tool_calls:
            messages.append(response_message.model_dump())
            
            for tool_call in response_message.tool_calls:
                function_name = tool_call.function.name
                function_args = json.loads(tool_call.function.arguments)
                
                if function_name == "execute_bash_command":
                    command_to_run = function_args.get("command")
                    print(f"\n[⚡ Executing command]: {command_to_run}")
                    
                    # Run the command locally inside Daytona!
                    command_output = execute_bash_command(command_to_run)
                    print(f"[📝 Output]:\n{command_output.strip()}")
                    
                    messages.append({
                        "tool_call_id": tool_call.id,
                        "role": "tool",
                        "name": function_name,
                        "content": command_output,
                    })
            
            # Get the final answer after tool execution
            second_response = client.chat.completions.create(
                model=MODEL_ID,
                messages=messages,
            )
            
            final_answer = second_response.choices[0].message.content
            print(f"\nAgent: {final_answer}")
            messages.append({"role": "assistant", "content": final_answer})

        else:
            final_answer = response_message.content
            print(f"\nAgent: {final_answer}")
            messages.append({"role": "assistant", "content": final_answer})

        # Save history after each turn
        with open(history_file, "w") as f:
            json.dump(messages, f)

    except KeyboardInterrupt:
        print("\nGoodbye!")
        break
    except Exception as e:
        print(f"\n❌ Error: {e}")
