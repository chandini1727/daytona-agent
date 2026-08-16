import streamlit as st
import os
import subprocess
import json
from openai import OpenAI

# Configure Streamlit page
st.set_page_config(page_title="OpenRouter AI Agent", page_icon="🚀", layout="wide")
st.title("🚀 Custom AI Agent powered by OpenRouter")
st.markdown("A powerful custom chat agent that can execute Bash commands inside its container!")

# Setup OpenRouter client with the API key provided by the user
API_KEY = os.environ.get("OPENROUTER_API_KEY")
if not API_KEY:
    st.error("OpenRouter API Key is missing! Please set OPENROUTER_API_KEY.")
    st.stop()

client = OpenAI(
    base_url="https://openrouter.ai/api/v1",
    api_key=API_KEY,
)

# Define the Tool (Bash Execution)
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

# Define the JSON schema for the tool
tools = [
    {
        "type": "function",
        "function": {
            "name": "execute_bash_command",
            "description": "Execute a bash command in the agent's Linux container environment and return the output. Use this to read files, run scripts, list directories, etc.",
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

# Sidebar for Model Selection
with st.sidebar:
    st.header("⚙️ Agent Settings")
    st.markdown("Select your preferred AI model:")
    
    # List of some popular models on OpenRouter that support tool calling
    model_choices = {
        "Meta: Llama 3.3 70B Instruct": "meta-llama/llama-3.3-70b-instruct",
        "Anthropic: Claude 3.5 Sonnet": "anthropic/claude-3.5-sonnet",
        "Google: Gemini 2.5 Flash": "google/gemini-2.5-flash",
        "OpenAI: GPT-4o Mini": "openai/gpt-4o-mini"
    }
    
    selected_model_name = st.selectbox("Model", options=list(model_choices.keys()))
    model_id = model_choices[selected_model_name]
    
    st.markdown(f"**Current Model ID:**\n`{model_id}`")
    
    if st.button("Clear Chat History"):
        st.session_state.messages = []
        st.rerun()

# Initialize chat history
if "messages" not in st.session_state:
    st.session_state.messages = [
        {"role": "system", "content": "You are a highly capable AI assistant operating inside a Linux container. You have access to a tool to run bash commands. When a user asks you to do something that requires checking the system, reading a file, or running a command, use the tool. Provide precise and helpful answers."}
    ]

# Display chat messages (excluding the system message)
for message in st.session_state.messages:
    if message["role"] != "system":
        if message["role"] == "tool":
            with st.chat_message("tool", avatar="⚙️"):
                st.markdown(f"**Command Output:**\n```\n{message['content']}\n```")
        elif message.get("tool_calls"):
            with st.chat_message("assistant"):
                for tool_call in message["tool_calls"]:
                    args = json.loads(tool_call["function"]["arguments"])
                    st.markdown(f"**Executed Command:** `{args['command']}`")
        elif message["content"]:
            with st.chat_message(message["role"]):
                st.markdown(message["content"])

# Handle user input
if prompt := st.chat_input("Ask your custom agent to execute a command..."):
    # Add user message to chat history
    st.session_state.messages.append({"role": "user", "content": prompt})
    
    # Display user message in chat message container
    with st.chat_message("user"):
        st.markdown(prompt)

    # Display assistant response in chat message container
    with st.spinner("Agent is thinking..."):
        try:
            # We turn off streaming here to make tool calling flow significantly simpler and robust
            response = client.chat.completions.create(
                model=model_id,
                messages=st.session_state.messages,
                tools=tools,
                tool_choice="auto",
            )
            
            response_message = response.choices[0].message
            
            # Case 1: The model decided to use a tool!
            if response_message.tool_calls:
                # Add the assistant's tool call request to the history
                st.session_state.messages.append(response_message.model_dump())
                
                for tool_call in response_message.tool_calls:
                    function_name = tool_call.function.name
                    function_args = json.loads(tool_call.function.arguments)
                    
                    if function_name == "execute_bash_command":
                        command_to_run = function_args.get("command")
                        
                        with st.chat_message("assistant"):
                            st.markdown(f"**Executed Command:** `{command_to_run}`")
                        
                        # Execute the tool
                        command_output = execute_bash_command(command_to_run)
                        
                        # Display the tool result
                        with st.chat_message("tool", avatar="⚙️"):
                            st.markdown(f"**Command Output:**\n```\n{command_output}\n```")
                        
                        # Add the tool result to the history
                        st.session_state.messages.append({
                            "tool_call_id": tool_call.id,
                            "role": "tool",
                            "name": function_name,
                            "content": command_output,
                        })
                
                # Now we must call the API a second time with the tool result so the agent can form a final answer
                second_response = client.chat.completions.create(
                    model=model_id,
                    messages=st.session_state.messages,
                )
                
                final_answer = second_response.choices[0].message.content
                with st.chat_message("assistant"):
                    st.markdown(final_answer)
                st.session_state.messages.append({"role": "assistant", "content": final_answer})

            # Case 2: The model just answered with text normally
            else:
                final_answer = response_message.content
                with st.chat_message("assistant"):
                    st.markdown(final_answer)
                st.session_state.messages.append({"role": "assistant", "content": final_answer})
                
        except Exception as e:
            st.error(f"Error communicating with OpenRouter: {e}")
