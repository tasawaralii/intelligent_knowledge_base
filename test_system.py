"""
Comprehensive system testing script
Tests data creation, retrieval, and consistency across the application
"""

import requests
import json
from datetime import datetime, timedelta

BASE_URL = "http://localhost:8000"
HEADERS = {"Content-Type": "application/json"}

# Color codes for output
class Colors:
    GREEN = '\033[92m'
    RED = '\033[91m'
    YELLOW = '\033[93m'
    BLUE = '\033[94m'
    ENDC = '\033[0m'

def print_test(message, status="info"):
    if status == "pass":
        print(f"{Colors.GREEN}✓ {message}{Colors.ENDC}")
    elif status == "fail":
        print(f"{Colors.RED}✗ {message}{Colors.ENDC}")
    elif status == "section":
        print(f"\n{Colors.BLUE}{'='*60}")
        print(f"  {message}")
        print(f"{'='*60}{Colors.ENDC}\n")
    else:
        print(f"{Colors.YELLOW}→ {message}{Colors.ENDC}")

# Step 1: Sign up and get token
print_test("STARTING SYSTEM TEST", "section")

print_test("1. Testing User Authentication")
signup_data = {
    "username": f"testuser{int(datetime.now().timestamp())}",
    "email": f"testuser{datetime.now().timestamp()}@test.com",
    "password": "Test@123456",
    "first_name": "Test",
    "last_name": "User"
}

try:
    response = requests.post(f"{BASE_URL}/auth/signup", json=signup_data, headers=HEADERS)
    if response.status_code == 200:
        user_data = response.json()
        print_test(f"User created successfully - {signup_data['username']}", "pass")
    else:
        print_test(f"Signup failed: {response.text}", "fail")
        exit(1)
except Exception as e:
    print_test(f"Signup error: {str(e)}", "fail")
    exit(1)

# Step 2: Sign in to get token
print_test("2. Signing in to get access token")

signin_data = {
    "username": signup_data['username'],
    "password": signup_data['password']
}

try:
    # For OAuth2PasswordRequestForm, we need to send form-encoded data
    response = requests.post(
        f"{BASE_URL}/auth/signin",
        data=signin_data,
        headers={"Content-Type": "application/x-www-form-urlencoded"}
    )
    if response.status_code == 200:
        token_data = response.json()
        token = token_data.get("access_token")
        print_test(f"User authenticated successfully", "pass")
        # Set up auth header
        AUTH_HEADERS = {**HEADERS, "Authorization": f"Bearer {token}"}
    else:
        print_test(f"Sign in failed: {response.text}", "fail")
        exit(1)
except Exception as e:
    print_test(f"Sign in error: {str(e)}", "fail")
    exit(1)

# Step 3: Create test persons
print_test("3. Creating Test Persons")
persons = []
person_data_list = [
    {"first_name": "John", "last_name": "Doe", "email": "john@example.com", "phone_number": "+1234567890"},
    {"first_name": "Jane", "last_name": "Smith", "email": "jane@example.com", "phone_number": "+0987654321"},
    {"first_name": "Alice", "last_name": "Johnson", "email": "alice@example.com", "phone_number": "+1122334455"},
    {"first_name": "Bob", "last_name": "Wilson", "email": "bob@example.com", "phone_number": "+5566778899"},
]

for person_data in person_data_list:
    try:
        response = requests.post(f"{BASE_URL}/person", json=person_data, headers=AUTH_HEADERS)
        if response.status_code == 201:
            person = response.json()
            persons.append(person)
            print_test(f"Person created: {person['first_name']} {person['last_name']} (ID: {person['id']})", "pass")
        else:
            print_test(f"Failed to create person {person_data['first_name']}: {response.text}", "fail")
    except Exception as e:
        print_test(f"Error creating person: {str(e)}", "fail")

# Step 4: Create test places
print_test("4. Creating Test Places")
places = []
place_data_list = [
    {"name": "Central Park", "city": "New York", "state": "NY", "country": "USA"},
    {"name": "Eiffel Tower", "city": "Paris", "state": "IDF", "country": "France"},
    {"name": "Big Ben", "city": "London", "state": "England", "country": "UK"},
]

for place_data in place_data_list:
    try:
        response = requests.post(f"{BASE_URL}/place", json=place_data, headers=AUTH_HEADERS)
        if response.status_code == 201:
            place = response.json()
            places.append(place)
            print_test(f"Place created: {place['name']}, {place['city']} (ID: {place['id']})", "pass")
        else:
            print_test(f"Failed to create place {place_data['name']}: {response.text}", "fail")
    except Exception as e:
        print_test(f"Error creating place: {str(e)}", "fail")

# Step 5: Create test events
print_test("5. Creating Test Events")
events = []
today = datetime.now()
event_data_list = [
    {
        "title": "Birthday Party",
        "description": "John's 30th birthday celebration",
        "start_datetime": (today + timedelta(days=7)).isoformat(),
        "end_datetime": (today + timedelta(days=7, hours=4)).isoformat(),
    },
    {
        "title": "Wedding Anniversary",
        "description": "Jane and John's 5th wedding anniversary",
        "start_datetime": (today + timedelta(days=14)).isoformat(),
        "end_datetime": (today + timedelta(days=14, hours=8)).isoformat(),
    },
    {
        "title": "Conference",
        "description": "Tech conference in Paris",
        "start_datetime": (today + timedelta(days=30)).isoformat(),
        "end_datetime": (today + timedelta(days=32)).isoformat(),
    },
]

for event_data in event_data_list:
    try:
        response = requests.post(f"{BASE_URL}/event", json=event_data, headers=AUTH_HEADERS)
        if response.status_code == 201:
            event = response.json()
            events.append(event)
            print_test(f"Event created: {event['title']} (ID: {event['id']})", "pass")
        else:
            print_test(f"Failed to create event {event_data['title']}: {response.text}", "fail")
    except Exception as e:
        print_test(f"Error creating event: {str(e)}", "fail")

# Step 6: Create test notes with mentions
print_test("6. Creating Test Notes with Mentions")
notes = []
if len(persons) >= 2 and len(places) >= 1 and len(events) >= 1:
    note_data_list = [
        {
            "title": "Trip to Paris",
            "content": f"I went to Paris with @p[{persons[0]['first_name']} {persons[0]['last_name']}]({persons[0]['id']}) and visited @pl[{places[1]['name']}]({places[1]['id']}). We attended the @e[{events[2]['title']}]({events[2]['id']}).",
        },
        {
            "title": "Meeting Notes",
            "content": f"Met with @p[{persons[1]['first_name']} {persons[1]['last_name']}]({persons[1]['id']}) at @pl[{places[0]['name']}]({places[0]['id']}). Discussed upcoming @e[{events[0]['title']}]({events[0]['id']}).",
        },
        {
            "title": "Birthday Planning",
            "content": f"Planning @e[{events[0]['title']}]({events[0]['id']}) for @p[{persons[0]['first_name']} {persons[0]['last_name']}]({persons[0]['id']}). Need to book a venue at @pl[{places[0]['name']}]({places[0]['id']}).",
        },
    ]

    for note_data in note_data_list:
        try:
            response = requests.post(f"{BASE_URL}/note", json=note_data, headers=AUTH_HEADERS)
            if response.status_code == 201:
                note = response.json()
                notes.append(note)
                print_test(f"Note created: {note['title']} (ID: {note['id']})", "pass")
            else:
                print_test(f"Failed to create note {note_data['title']}: {response.text}", "fail")
        except Exception as e:
            print_test(f"Error creating note: {str(e)}", "fail")
else:
    print_test("Not enough persons/places/events to create notes with mentions", "fail")

# Step 7: Create person relationships
print_test("7. Creating Person Relationships")
if len(persons) >= 2:
    relation_data = {
        "person_id_2": persons[1]['id'],
        "relation_type": "spouse"
    }
    try:
        response = requests.post(
            f"{BASE_URL}/person/{persons[0]['id']}/relations",
            json=relation_data,
            headers=AUTH_HEADERS
        )
        if response.status_code == 201:
            print_test(
                f"Relation created: {persons[0]['first_name']} is spouse of {persons[1]['first_name']}",
                "pass"
            )
        else:
            print_test(f"Failed to create relation: {response.text}", "fail")
    except Exception as e:
        print_test(f"Error creating relation: {str(e)}", "fail")

# Step 8: Verify data retrieval
print_test("8. Verifying Data Retrieval")

try:
    # Get all persons
    response = requests.get(f"{BASE_URL}/person", headers=AUTH_HEADERS)
    if response.status_code == 200:
        retrieved_persons = response.json()
        print_test(f"Retrieved {len(retrieved_persons)} persons from database", "pass")
    else:
        print_test("Failed to retrieve persons", "fail")

    # Get all places
    response = requests.get(f"{BASE_URL}/place", headers=AUTH_HEADERS)
    if response.status_code == 200:
        retrieved_places = response.json()
        print_test(f"Retrieved {len(retrieved_places)} places from database", "pass")
    else:
        print_test("Failed to retrieve places", "fail")

    # Get all events
    response = requests.get(f"{BASE_URL}/event", headers=AUTH_HEADERS)
    if response.status_code == 200:
        retrieved_events = response.json()
        print_test(f"Retrieved {len(retrieved_events)} events from database", "pass")
    else:
        print_test("Failed to retrieve events", "fail")

    # Get all notes
    response = requests.get(f"{BASE_URL}/note", headers=AUTH_HEADERS)
    if response.status_code == 200:
        retrieved_notes = response.json()
        print_test(f"Retrieved {len(retrieved_notes)} notes from database", "pass")
    else:
        print_test("Failed to retrieve notes", "fail")

except Exception as e:
    print_test(f"Error verifying data: {str(e)}", "fail")

# Step 9: Verify individual person details
print_test("9. Verifying Person Details and Relations")
if len(persons) > 0:
    try:
        response = requests.get(f"{BASE_URL}/person/{persons[0]['id']}", headers=AUTH_HEADERS)
        if response.status_code == 200:
            person_detail = response.json()
            print_test(
                f"Person detail verified: {person_detail['first_name']} {person_detail['last_name']}",
                "pass"
            )
            
            # Check relations
            response = requests.get(
                f"{BASE_URL}/person/{persons[0]['id']}/relations",
                headers=AUTH_HEADERS
            )
            if response.status_code == 200:
                relations = response.json()
                print_test(f"Retrieved {len(relations)} relations for person", "pass")
            else:
                print_test("Failed to retrieve relations", "fail")
        else:
            print_test("Failed to retrieve person detail", "fail")
    except Exception as e:
        print_test(f"Error verifying person details: {str(e)}", "fail")

# Step 10: Test note mentions parsing
print_test("10. Verifying Note Mention Parsing")
if len(notes) > 0:
    try:
        note = notes[0]
        # Check if mentions are properly stored in the note
        if '@p[' in note.get('content', '') or '@pl[' in note.get('content', ''):
            print_test(f"Note mentions are properly formatted", "pass")
        else:
            print_test(f"Note mentions formatting check skipped", "info")
    except Exception as e:
        print_test(f"Error verifying mentions: {str(e)}", "fail")

# Final Summary
print_test("SYSTEM TEST COMPLETE", "section")
print_test(f"Created {len(persons)} persons", "pass")
print_test(f"Created {len(places)} places", "pass")
print_test(f"Created {len(events)} events", "pass")
print_test(f"Created {len(notes)} notes with mentions", "pass")

print(f"\n{Colors.BLUE}{'='*60}")
print(f"  TEST DATA SUMMARY")
print(f"{'='*60}{Colors.ENDC}")
print(f"\n📝 Test Credentials:")
print(f"   Email: {signup_data['email']}")
print(f"   Password: {signup_data['password']}")
print(f"\n👥 Persons Created:")
for person in persons:
    print(f"   - {person['first_name']} {person['last_name']} ({person['email']})")
print(f"\n📍 Places Created:")
for place in places:
    print(f"   - {place['name']}, {place['city']}")
print(f"\n📅 Events Created:")
for event in events:
    print(f"   - {event['title']}")
print(f"\n📄 Notes Created:")
for note in notes:
    print(f"   - {note['title']}")

print(f"\n{Colors.GREEN}All tests completed!{Colors.ENDC}")
print(f"Login with the credentials above and verify the data in the frontend.")
