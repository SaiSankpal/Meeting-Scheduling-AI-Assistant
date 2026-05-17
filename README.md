** Meeting Scheduling AI Agent **

Project Review:
* Project Name- ‘Meeting Scheduling AI Agent’

* Description- This is a Meeting Scheduling AI Agent; to schedule, cancel, and edit meetings using natural language prompts

Objectives:
* Why this project was built- Reduce the effort required in coordinating meetings, Eliminate repetitive manual scheduling tasks

* Problem it solves- Traditional meeting scheduling methods are inefficient and time-consuming. This project addresses challenges such as- Manual coordination between participants leading to delays, Lack of automation in existing basic scheduling workflows.

Key Features:  
* Automate meeting schedule, reschedule and cancel. 
* Offers reschedule and cancel options pre-confirmation and post-confirmation. 
* Multi-user support (4.) Exposes REST API endpoints for external integration.

Tech Stack:
* Language → Python= ">=3.10,<3.11"
* Framework → FastAPI= "^0.135.1"
* Orchestration → LangGraph= "^0.2.0"
* LLM → Groq (model_name="llama-3.1-8b-instant")
* Tools/APIs → Google Calendar

Architecture:
The user interacts with the system through a chat interface. Streamlit UI acts as the frontend interface. FastAPI Backend serves as the API layer between UI and AI logic. LangGraph engine is the core orchestration layer, it manages the flow of logic. Nodes are the modular steps in langgraph- Extract node: Extracts details from user input such as date, participants, time.
Confirm node: Confirms details with the user.
Schedule Node: Contributes to final steps- Calls Google Calendar API and Creates and updates events.
Google Calendar API handles external integration. It authenticates user (OAuth), create, update, delete calendar events and return event status. Layer communicate back-and-forth this allows real-time updates, error handling and interactive confirmations.

Workflow:
* User enters: “Schedule meeting tomorrow at 5 PM”
* Streamlit sends request → FastAPI
* FastAPI calls LangGraph
* LangGraph:
    Extracts details
    Confirms if needed
    Calls schedule node
* Schedule node → Google Calendar API
* Event is created
* Response flows back to UI:
    “Your meeting is scheduled successfully”

Explanation of some key nodes:
1.	Intent Extraction Node- This node is responsible for understanding what the user wants to do from natural language input.
Takes raw user input (say: schedule a meeting with xyz@gmail.com today at 10am)
Uses LLM to identify intent(schedule/reschedule/cancel) and extract entities(participants/date/time).
Output- 
Please confirm the following:
Action: schedule
With: ['xyz@gmail.com']
Date: today
Time: 10am
Here, the LLM is constrained to structure the output using schema, then convert it into json programmatically.
2.	Confirm Node- Ensures extracted data is correct, complete, and usable before scheduling.
* Date/Time Parsing:
Converts natural language → standard format
For eg: “tomorrow” → 2026-03-20, “5 pm” → 17:00
We have used python libraries (datetime, dateutil)
* Handles edge cases like: Past dates, Invalid time and missing fields.
* Validates the flow: If flow is valid- moves to scheduling, If flow is invalid- loops back to the user for correction.
3.	Schedule Node: This node performs the actual meeting creation using calendar integration. Connects with Google Calendar API. It authenticates user(OAuth), creates event and sends invite.

Setup Instructions:
* Install dependencies- 
pip install poetry (install poetry if not)
poetry install (install project dependencies)
poetry shell (Activate the virtual environment)
* Add API Keys- Create .env file and add groq_api_key
* Run FastAPI Server-
uvicorn backend.main: app –reload

API Documentation:
* Base URL: http://127.0.0.1:8000
* Method: POST /chat
* Request Body: 
{
  "user_id": "user_123",
  "user_input": "schedule a meeting with saisankpal16@gmail.com at 9pm"
}

* Response Body: 
{
  "response": "Please confirm the following:\n\nAction: schedule\n\nWith: ['saisankpal16@gmail.com']\n\nDate: tomorrow\n\nTime: 10am\n\nReply with **Confirm** to confirm and **Change** to change\n"
}
* cURL:
curl -X 'POST' \
  'http://127.0.0.1:8000/chat' \
  -H 'accept: application/json' \
  -H 'Content-Type: application/json' \
  -d '{
  "user_id": "user_123",
  "user_input": "schedule a meeting with saisankpal16@gmail.com at 9pm"
}'

* Interactive API Docs-
FastAPI provides built-in interactive documentation:
- Swagger UI: http://127.0.0.1:8000/docs
* Status Code-
200 – Successful Response
422 – Validation Error

Challenges and Solutions: 
* Handled Ambiguous User Inputs- 
Challenge- Users often provide vague and incomplete inputs. They lack key details such as time, participants, etc.
Solution- Designed an Intent Extraction Module using structured LLM output. Implemented follow-up prompts to clarify missing fields.
* Timezone Handling Issues-
Challenge- Different users may operate in different time zones, causing incorrect scheduling in calendars.
Solution- Standardized all extracted times into a consistent timezone format
* Structured Output from LLM-
Challenge- LLMs often return unstructured or inconsistent responses.
Solution- Used structured output parsing (MeetingIntent), Enforced schema using .model_dump() and .model_dump_json()


Future Improvements:
* Outlook Integration
* Microsoft teams integration- allowing scheduling directly from chat platforms
* Voice input Support
* Multilingual Support
* Conflict Detection
* Improved Natural language understanding.

Conclusion:
This project demonstrates the design and implementation of an AI-powered meeting scheduling assistant using FastAPI and LLM-based intent extraction.

Author:
Name- Sai Sankpal
Email- saisankpal16@gmail.com