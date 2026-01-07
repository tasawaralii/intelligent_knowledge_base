#!/usr/bin/env python3
"""
Interactive system verification script
Shows all the test data and verifies the system is working
"""

import requests
import json

BASE_URL = "http://localhost:8000"

# Test credentials
TEST_USER = {
    "username": "testuser1767727651",
    "password": "Test@123456"
}

print("\n" + "="*70)
print("SYSTEM VERIFICATION - INTERACTIVE TEST")
print("="*70 + "\n")

# Step 1: Authenticate
print("Step 1: Authenticating user...")
signin_data = {
    "username": TEST_USER['username'],
    "password": TEST_USER['password']
}

response = requests.post(
    f"{BASE_URL}/auth/signin",
    data=signin_data,
    headers={"Content-Type": "application/x-www-form-urlencoded"}
)

if response.status_code != 200:
    print(f"❌ Authentication failed: {response.text}")
    exit(1)

token = response.json().get("access_token")
print(f"✅ Authentication successful\n")

AUTH_HEADERS = {"Authorization": f"Bearer {token}"}

# Step 2: Fetch all data
print("Step 2: Fetching all test data...\n")

# Get persons
response = requests.get(f"{BASE_URL}/person", headers=AUTH_HEADERS)
persons = response.json() if response.status_code == 200 else []
print(f"✅ Retrieved {len(persons)} Persons")

# Get places
response = requests.get(f"{BASE_URL}/place", headers=AUTH_HEADERS)
places = response.json() if response.status_code == 200 else []
print(f"✅ Retrieved {len(places)} Places")

# Get events
response = requests.get(f"{BASE_URL}/event", headers=AUTH_HEADERS)
events = response.json() if response.status_code == 200 else []
print(f"✅ Retrieved {len(events)} Events")

# Get notes
response = requests.get(f"{BASE_URL}/note", headers=AUTH_HEADERS)
notes = response.json() if response.status_code == 200 else []
print(f"✅ Retrieved {len(notes)} Notes\n")

# Step 3: Display data in tables
print("="*70)
print("PERSONS DATA")
print("="*70)
if persons:
    for p in persons[-4:]:  # Last 4
        print(f"  ID: {p.get('id')}, Name: {p.get('first_name', '')} {p.get('last_name', '')}, Email: {p.get('email', 'N/A')}, Phone: {p.get('phone_number', 'N/A')[:15]}")
else:
    print("No persons found")
print()

print("="*70)
print("PLACES DATA")
print("="*70)
if places:
    for p in places[-3:]:  # Last 3
        print(f"  ID: {p.get('id')}, Name: {p.get('name', '')}, City: {p.get('city', '')}, Country: {p.get('country', '')}")
else:
    print("No places found")
print()

print("="*70)
print("EVENTS DATA")
print("="*70)
if events:
    for e in events[-3:]:  # Last 3
        print(f"  ID: {e.get('id')}, Title: {e.get('title', '')}, Date: {e.get('start_datetime', '')[:10]}, Desc: {e.get('description', '')[:30]}")
else:
    print("No events found")
print()

print("="*70)
print("NOTES DATA WITH MENTIONS")
print("="*70)
if notes:
    for idx, note in enumerate(notes[-3:], 1):  # Last 3
        print(f"\nNote {idx}: {note.get('title', 'Untitled')}")
        print(f"ID: {note.get('id')}")
        print(f"Content:")
        content = note.get('content', '')[:100]
        print(f"  {content}...")
        print(f"Created: {note.get('created_at', '')[:10]}")
        
        # Check for mentions
        if '@p[' in note.get('content', ''):
            print(f"  ✅ Contains Person mentions")
        if '@pl[' in note.get('content', ''):
            print(f"  ✅ Contains Place mentions")
        if '@e[' in note.get('content', ''):
            print(f"  ✅ Contains Event mentions")
else:
    print("No notes found")
print()

# Step 4: Test navigation and consistency
print("="*70)
print("DATA CONSISTENCY CHECKS")
print("="*70 + "\n")

checks_passed = 0
total_checks = 0

# Check 1: All persons have IDs
total_checks += 1
if all('id' in p for p in persons):
    print("✅ All persons have valid IDs")
    checks_passed += 1
else:
    print("❌ Some persons missing IDs")

# Check 2: All places have IDs
total_checks += 1
if all('id' in p for p in places):
    print("✅ All places have valid IDs")
    checks_passed += 1
else:
    print("❌ Some places missing IDs")

# Check 3: All notes have mentions
total_checks += 1
notes_with_mentions = sum(1 for n in notes if '@p[' in n.get('content', '') or '@pl[' in n.get('content', '') or '@e[' in n.get('content', ''))
if notes_with_mentions == len(notes):
    print(f"✅ All {len(notes)} notes have proper mention formatting")
    checks_passed += 1
else:
    print(f"⚠️  {notes_with_mentions}/{len(notes)} notes have mentions (expected all to have)")

# Check 4: Data count consistency with dashboard
total_checks += 1
expected_counts = {
    'persons': 4,
    'places': 3,
    'events': 3,
    'notes': 3
}
actual_counts = {
    'persons': len(persons),
    'places': len(places),
    'events': len(events),
    'notes': len(notes)
}

counts_match = (
    actual_counts['persons'] >= expected_counts['persons'] and
    actual_counts['places'] >= expected_counts['places'] and
    actual_counts['events'] >= expected_counts['events'] and
    actual_counts['notes'] >= expected_counts['notes']
)

if counts_match:
    print(f"✅ All expected test data present")
    print(f"   Persons: {actual_counts['persons']} (expected {expected_counts['persons']})")
    print(f"   Places: {actual_counts['places']} (expected {expected_counts['places']})")
    print(f"   Events: {actual_counts['events']} (expected {expected_counts['events']})")
    print(f"   Notes: {actual_counts['notes']} (expected {expected_counts['notes']})")
    checks_passed += 1
else:
    print(f"❌ Data count mismatch")

# Check 5: Can fetch person details
total_checks += 1
if persons:
    try:
        person_id = persons[0]['id']
        response = requests.get(f"{BASE_URL}/person/{person_id}", headers=AUTH_HEADERS)
        if response.status_code == 200:
            print(f"✅ Can fetch individual person details")
            checks_passed += 1
        else:
            print(f"❌ Failed to fetch person details")
    except:
        print(f"❌ Error fetching person details")
else:
    print(f"⚠️  No persons to test (skipped)")

# Check 6: Notes contain proper mention format
total_checks += 1
mention_format_valid = True
for note in notes:
    content = note.get('content', '')
    # Check if mentions are properly formatted with ID
    if '@p[' in content or '@pl[' in content or '@e[' in content:
        # Should have format like @p[Name](id)
        if not '](' in content:
            mention_format_valid = False
            break

if mention_format_valid:
    print(f"✅ All note mentions properly formatted with IDs")
    checks_passed += 1
else:
    print(f"❌ Some note mentions have incorrect format")

print(f"\n{'='*70}")
print(f"VERIFICATION SUMMARY: {checks_passed}/{total_checks} checks passed")
print(f"{'='*70}\n")

if checks_passed == total_checks:
    print("🎉 ALL SYSTEM CHECKS PASSED!")
    print("\nYour application is working correctly. You can now:")
    print("1. Login to http://localhost:5173 with the test credentials")
    print("2. View all entities on their respective pages")
    print("3. Click on notes to see the mention sidebar in action")
    print("4. Navigate between related entities seamlessly")
else:
    print(f"⚠️  Some checks failed. Please review the issues above.")

print("\n" + "="*70)
print("Frontend Verification Checklist:")
print("="*70)
print("""
□ HomePage shows recent items from all categories
□ Dashboard shows accurate statistics
□ PersonsPage displays all 4 test persons
□ PlacesPage displays all 3 test places  
□ EventsPage displays all 3 test events
□ NotesPage displays all 3 test notes
□ Click on a note opens the dedicated NotePage
□ NotePage sidebar shows mentioned entities correctly
□ Click sidebar entities navigates to their detail pages
□ No console errors in browser DevTools
□ No 404 errors when navigating

""")
