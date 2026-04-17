import os
from datetime import datetime
from google.adk.agents import Agent
from google.adk.models.lite_llm import LiteLlm


def create_calendar_event(event_details: dict) -> dict:
    """Create a calendar event with the provided details.
    
    Args:
        event_details: A dictionary containing event information such as
                       title, date, time, and attendees.
    
    Returns:
        A dictionary with status and confirmation message.
    """
    title = event_details.get('title', 'Untitled Event')
    date = event_details.get('date', datetime.now().strftime('%B %d, %Y'))
    time = event_details.get('time', '12:00 PM')
    attendees = event_details.get('attendees', 'Not specified')

    return {
        'status': 'success',
        'message': (
            f"Event '{title}' scheduled on {date} at {time} "
            f"for {attendees} has been created successfully."
        ),
        'event': {
            'title': title,
            'date': date,
            'time': time,
            'attendees': attendees,
        }
    }


LITELLM_MODEL = os.getenv('LITELLM_MODEL', 'gemini/gemini-2.5-flash-lite')

root_agent = Agent(
    name='calendar_agent',
    model=LiteLlm(model=LITELLM_MODEL),
    description=(
        "A smart calendar management agent that helps users create, schedule, and organize "
        "their calendar events. It can handle appointment bookings, meeting scheduling, reminders, "
        "and any time-based event management. The agent understands natural language date and time "
        "expressions like 'today', 'tomorrow', 'next Monday', or 'at 7 PM' and converts them into "
        "structured calendar events."
    ),
    instruction=(
        f"You are a smart and helpful calendar management assistant. "
        f"Today's date and time is: {datetime.now().strftime('%A, %B %d, %Y %I:%M %p')}. "
        "Always use this as your reference for relative terms like 'today', 'tomorrow', 'this evening', etc. "
        "Never ask the user to clarify the date or year if they use relative expressions. "
        "\n\n"
        "Your responsibilities include:\n"
        "1. **Scheduling Events**: When a user asks to schedule a meeting, appointment, or any event, "
        "extract the title, date, time, and any other relevant details from their message.\n"
        "2. **Handling Ambiguity**: If critical details like the title or time are missing, use sensible "
        "defaults instead of asking the user. Never ask for details the user has already provided.\n"
        "3. **Confirmation**: After creating an event, always confirm back to the user with a clear summary "
        "including the event name, date, and time.\n"
        "4. **Natural Language Understanding**: Understand expressions like 'doctor's appointment', "
        "'team standup', 'lunch with client', and map them to proper event titles.\n"
        "5. **Politeness**: Always respond in a friendly, concise, and professional manner.\n"
        "\n"
        "When calling `create_calendar_event`, pass a dictionary with:\n"
        "  - 'title'    : event name (default: 'Untitled Event' if not mentioned)\n"
        "  - 'date'     : full date  (default: today's date if not mentioned)\n"
        "  - 'time'     : event time (default: '12:00 PM' if not mentioned)\n"
        "  - 'attendees': user name  (default: 'Not specified' if not mentioned)\n"
        "Only ask the user for missing info if it is absolutely critical.\n"
    ),
    tools=[create_calendar_event],
)
