import os
from datetime import datetime
from google.adk.agents import Agent
from google.adk.models.lite_llm import LiteLlm


# ---------------------------------------------------------------------------
# Sample book library data
# ---------------------------------------------------------------------------

BOOK_LIBRARY = [
    {
        'id': 1,
        'title': 'The Silicon Gold',
        'author': 'Pritesh Mistry',
        'genre': 'Tech Thriller',
        'available': True,
        'total_copies': 3,
        'available_copies': 2,
    },
    {
        'id': 2,
        'title': 'Whispers of the Quantum Mind',
        'author': 'Arjun Verlekar',
        'genre': 'Science Fiction',
        'available': True,
        'total_copies': 5,
        'available_copies': 3,
    },
    {
        'id': 3,
        'title': 'Echoes in the Dark Valley',
        'author': 'Sophia Marlowe',
        'genre': 'Mystery',
        'available': False,
        'total_copies': 2,
        'available_copies': 0,
    },
    {
        'id': 4,
        'title': 'The Last Algorithm',
        'author': 'Rivan Desai',
        'genre': 'Tech Thriller',
        'available': True,
        'total_copies': 4,
        'available_copies': 1,
    },
    {
        'id': 5,
        'title': 'Beneath the Neon Sky',
        'author': 'Luna Harcastle',
        'genre': 'Cyberpunk',
        'available': True,
        'total_copies': 6,
        'available_copies': 4,
    },
    {
        'id': 6,
        'title': 'Flames of the Forgotten Empire',
        'author': 'Marcus Albright',
        'genre': 'Fantasy',
        'available': False,
        'total_copies': 3,
        'available_copies': 0,
    },
    {
        'id': 7,
        'title': 'The Infinite Corridor',
        'author': 'Neha Singhania',
        'genre': 'Psychological Thriller',
        'available': True,
        'total_copies': 2,
        'available_copies': 1,
    },
    {
        'id': 8,
        'title': 'Stars Beyond the Veil',
        'author': 'Eliot Crane',
        'genre': 'Space Opera',
        'available': True,
        'total_copies': 7,
        'available_copies': 5,
    },
]


# ---------------------------------------------------------------------------
# Tool: Search books
# ---------------------------------------------------------------------------

def search_books(query: dict) -> dict:
    """Search for books in the library by title, author, or genre and check availability.

    Args:
        query: A dictionary with optional keys:
               - 'title'   : partial or full book title to search
               - 'author'  : partial or full author name to search
               - 'genre'   : genre to filter by
               - 'available_only': if True, return only available books (default: False)

    Returns:
        A dictionary with matched books and their availability status.
    """
    title_query  = query.get('title', '').lower()
    author_query = query.get('author', '').lower()
    genre_query  = query.get('genre', '').lower()
    available_only = query.get('available_only', False)

    results = []

    for book in BOOK_LIBRARY:
        # Apply filters
        if title_query and title_query not in book['title'].lower():
            continue
        if author_query and author_query not in book['author'].lower():
            continue
        if genre_query and genre_query not in book['genre'].lower():
            continue
        if available_only and not book['available']:
            continue

        results.append({
            'id'               : book['id'],
            'title'            : book['title'],
            'author'           : book['author'],
            'genre'            : book['genre'],
            'availability'     : 'Available' if book['available'] else 'Not Available',
            'available_copies' : book['available_copies'],
            'total_copies'     : book['total_copies'],
        })

    if not results:
        return {
            'status'  : 'not_found',
            'message' : 'No books found matching your search criteria.',
            'books'   : [],
        }

    return {
        'status'       : 'success',
        'total_results': len(results),
        'books'        : results,
    }


# ---------------------------------------------------------------------------
# Tool: Create calendar event
# ---------------------------------------------------------------------------

def create_calendar_event(event_details: dict) -> dict:
    """Create a calendar event with the provided details.

    Args:
        event_details: A dictionary containing event information such as
                       title, date, time, and attendees.

    Returns:
        A dictionary with status and confirmation message.
    """
    title     = event_details.get('title', 'Untitled Event')
    date      = event_details.get('date', datetime.now().strftime('%B %d, %Y'))
    time      = event_details.get('time', '12:00 PM')
    attendees = event_details.get('attendees', 'Not specified')

    return {
        'status': 'success',
        'message': (
            f"Event '{title}' scheduled on {date} at {time} "
            f"for {attendees} has been created successfully."
        ),
        'event': {
            'title'    : title,
            'date'     : date,
            'time'     : time,
            'attendees': attendees,
        }
    }


# ---------------------------------------------------------------------------
# Agent
# ---------------------------------------------------------------------------

LITELLM_MODEL = os.getenv('LITELLM_MODEL', 'gemini/gemini-2.5-flash-lite')

root_agent = Agent(
    name='calendar_agent',
    model=LiteLlm(model=LITELLM_MODEL),
    description=(
        "A smart assistant that helps users manage their calendar events and explore the book library. "
        "It can schedule appointments, create reminders, search for books by title, author, or genre, "
        "and check real-time book availability. The agent understands natural language date/time "
        "expressions and provides friendly, accurate responses for both calendar and library queries."
    ),
    instruction=(
        f"You are a smart and helpful assistant with two core capabilities: "
        f"calendar management and library book search.\n\n"
        f"Today's date and time is: {datetime.now().strftime('%A, %B %d, %Y %I:%M %p')}. "
        "Always use this as your reference for relative terms like 'today', 'tomorrow', 'this evening', etc. "
        "Never ask the user to clarify the date or year if they use relative expressions.\n\n"

        "--- CALENDAR MANAGEMENT ---\n"
        "1. **Scheduling Events**: Extract title, date, time, and attendees from the user's message "
        "and call `create_calendar_event`.\n"
        "2. **Defaults**: If details are missing, use sensible defaults — never ask unless absolutely critical.\n"
        "   - title     → 'Untitled Event'\n"
        "   - date      → today's date\n"
        "   - time      → 12:00 PM\n"
        "   - attendees → 'Not specified'\n"
        "3. **Confirmation**: After creating an event, summarize the event name, date, and time back to the user.\n\n"

        "--- LIBRARY BOOK SEARCH ---\n"
        "4. **Search Books**: When the user asks about books, authors, genres, or availability, "
        "call `search_books` with the appropriate query dictionary.\n"
        "5. **Availability**: Clearly tell the user how many copies are available. "
        "If a book is not available, let the user know politely.\n"
        "6. **Filters**: Support search by title, author, genre, or available-only books.\n"
        "   Examples:\n"
        "   - 'Do you have The Silicon Gold?' → search by title\n"
        "   - 'Books by Pritesh Mistry'       → search by author\n"
        "   - 'Any sci-fi books available?'   → search by genre + available_only: True\n\n"

        "Always respond in a friendly, concise, and professional manner.\n"
    ),
    tools=[create_calendar_event, search_books],
)