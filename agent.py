import os
from dotenv import load_dotenv
from typing import Dict, Any, cast
import getpass


from langchain_groq import ChatGroq
from langchain_core.messages import SystemMessage, HumanMessage, AIMessage
from langchain_core.runnables import RunnableSequence, RunnableLambda
from langchain_core.tools import BaseTool

from tools import schedule_meeting, edit_meeting, cancel_meeting

#load env
load_dotenv()

#Tools(typed, explicit)
TOOLS: list[BaseTool] = [  
    schedule_meeting,
    edit_meeting, 
    cancel_meeting
]


 
groq_api_key = os.getenv("GROQ_API_KEY")
 
if groq_api_key is None:
    print("Error: GROQ_API_KEY not found in environment variables or .env file.")
else:
    print("API key loaded successfully.")
# Check if the key exists, otherwise prompt for it
if "GROQ_API_KEY" not in os.environ:
    os.environ["GROQ_API_KEY"] = getpass.getpass("Enter your Groq API key: ")

 
# pyright: reportAbstractUsage=false
llm = ChatGroq(
    model="llama-3.1-8b-instant",
    temperature=0.2,
    stop_sequences=None,
)
 
def call_llm(state: Dict[str, Any]) -> AIMessage:
    messages = [
        SystemMessage(content=
        "You are Meeting Scheduling AI Assitant. \n"
        "You can schedule, edit or cancel meting \n"
        "Do not ask users for Internal IDs \n"
        "Use tools when required."
        ),
        HumanMessage(content=state["input"]),
    ]
    # `ChatGroq.invoke()` returns a BaseMessage; our chain expects an AIMessage.
    return cast(AIMessage, llm.invoke(messages))

def run_tools(llm_output):
    if not llm_output.tool_calls:
        return {"agent_output": llm_output.content}

    tool_call = llm_output.tool_calls[0]
    tool_map={
        "schedule_meeting": schedule_meeting,
        "edit_meeting": edit_meeting,
        "cancel_meeting": cancel_meeting,
    }

    tool_fn = tool_map[tool_call["name"]]
    result = tool_fn.invoke(tool_call["args"])

    return {"agent_output": result}

agent_chain = RunnableSequence[Any, Any](
    RunnableLambda[Dict[str, Any], AIMessage](call_llm),
    RunnableLambda[Any, dict[str, Any]](run_tools),
)
