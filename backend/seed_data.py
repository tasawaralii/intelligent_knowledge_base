"""
Seed Database with Pakistani Dummy Data
Run: cd backend && .\\venv\\Scripts\\python.exe seed_data.py
"""

from datetime import datetime, date
from database.core import engine, SessionLocal, Base
from database.models import (
    Users, Notes, Persons, PersonRelation, Places, Events,
    note_persons, note_places, note_events
)
from database.facts import Facts, NoteFact
import bcrypt

def hash_password(password: str) -> str:
    """Use same hashing as auth.py"""
    salt = bcrypt.gensalt(rounds=12)
    hashed = bcrypt.hashpw(password.encode("utf-8"), salt)
    return hashed.decode("utf-8")

def seed_database():
    """Seed all tables with Pakistani dummy data"""
    
    # Create tables if they don't exist
    Base.metadata.create_all(bind=engine)
    
    db = SessionLocal()
    
    try:
        # Check if data already exists
        existing_user = db.query(Users).filter(Users.username == "ahmed").first()
        if existing_user:
            print("Data already exists. Deleting old data...")
            # Delete in reverse order of dependencies
            db.execute(note_events.delete())
            db.execute(note_places.delete())
            db.execute(note_persons.delete())
            db.query(NoteFact).delete()
            db.query(Facts).delete()
            db.query(PersonRelation).delete()
            db.query(Events).delete()
            db.query(Places).delete()
            db.query(Persons).delete()
            db.query(Notes).delete()
            db.query(Users).filter(Users.username == "ahmed").delete()
            db.commit()
        
        print("Creating user...")
        # ==================== USER ====================
        user = Users(
            email="ahmed@example.com",
            username="ahmed",
            first_name="Ahmed",
            last_name="Khan",
            password_hashed=hash_password("password123")
        )
        db.add(user)
        db.commit()
        db.refresh(user)
        user_id = user.id
        print(f"Created user: {user.username} (ID: {user_id})")
        
        # ==================== PERSONS (Family Tree) ====================
        print("Creating persons...")
        persons_data = [
            # Generation 1 (Grandparents)
            {
                "first_name": "Muhammad", "last_name": "Aslam", "father_name": "Abdul Rehman",
                "slug": "muhammad-aslam", "gender": "male", "date_of_birth": date(1950, 3, 15),
                "city": "Lahore", "country": "Pakistan", "phone_number": "03001234567",
                "email": "aslam@email.com", "cnic": "3520112345671"
            },
            {
                "first_name": "Fatima", "last_name": "Begum", "father_name": "Ghulam Hussain",
                "slug": "fatima-begum", "gender": "female", "date_of_birth": date(1955, 7, 20),
                "city": "Lahore", "country": "Pakistan", "phone_number": "03001234568",
                "email": "fatima@email.com", "cnic": "3520112345672"
            },
            {
                "first_name": "Abdul", "last_name": "Malik", "father_name": "Haji Karim",
                "slug": "abdul-malik", "gender": "male", "date_of_birth": date(1952, 1, 10),
                "city": "Karachi", "country": "Pakistan", "phone_number": "03001234569",
                "email": "malik@email.com", "cnic": "3520112345673"
            },
            {
                "first_name": "Amina", "last_name": "Bibi", "father_name": "Muhammad Yusuf",
                "slug": "amina-bibi", "gender": "female", "date_of_birth": date(1958, 11, 5),
                "city": "Karachi", "country": "Pakistan", "phone_number": "03001234570",
                "email": "amina@email.com", "cnic": "3520112345674"
            },
            
            # Generation 2 (Parents)
            {
                "first_name": "Imran", "last_name": "Aslam", "father_name": "Muhammad Aslam",
                "slug": "imran-aslam", "gender": "male", "date_of_birth": date(1975, 5, 25),
                "city": "Lahore", "country": "Pakistan", "phone_number": "03211234567",
                "email": "imran@email.com", "cnic": "3520112345675",
                "address": "House 123, DHA Phase 5, Lahore"
            },
            {
                "first_name": "Sadia", "last_name": "Imran", "father_name": "Abdul Malik",
                "slug": "sadia-imran", "gender": "female", "date_of_birth": date(1980, 9, 12),
                "city": "Lahore", "country": "Pakistan", "phone_number": "03211234568",
                "email": "sadia@email.com", "cnic": "3520112345676",
                "address": "House 123, DHA Phase 5, Lahore"
            },
            {
                "first_name": "Kamran", "last_name": "Aslam", "father_name": "Muhammad Aslam",
                "slug": "kamran-aslam", "gender": "male", "date_of_birth": date(1978, 2, 18),
                "city": "Islamabad", "country": "Pakistan", "phone_number": "03331234567",
                "email": "kamran@email.com", "cnic": "3520112345677"
            },
            {
                "first_name": "Ayesha", "last_name": "Kamran", "father_name": "Tariq Mehmood",
                "slug": "ayesha-kamran", "gender": "female", "date_of_birth": date(1982, 4, 30),
                "city": "Islamabad", "country": "Pakistan", "phone_number": "03331234568",
                "email": "ayesha@email.com", "cnic": "3520112345678"
            },
            
            # Generation 3 (Children - Main characters)
            {
                "first_name": "Ali", "last_name": "Imran", "father_name": "Imran Aslam",
                "slug": "ali-imran", "gender": "male", "date_of_birth": date(2000, 8, 14),
                "city": "Lahore", "country": "Pakistan", "phone_number": "03451234567",
                "email": "ali@email.com", "cnic": "3520112345679",
                "address": "House 123, DHA Phase 5, Lahore"
            },
            {
                "first_name": "Zara", "last_name": "Imran", "father_name": "Imran Aslam",
                "slug": "zara-imran", "gender": "female", "date_of_birth": date(2003, 12, 25),
                "city": "Lahore", "country": "Pakistan", "phone_number": "03451234568",
                "email": "zara@email.com", "cnic": "3520112345680"
            },
            {
                "first_name": "Hassan", "last_name": "Kamran", "father_name": "Kamran Aslam",
                "slug": "hassan-kamran", "gender": "male", "date_of_birth": date(2005, 6, 1),
                "city": "Islamabad", "country": "Pakistan", "phone_number": "03451234569",
                "email": "hassan@email.com", "cnic": "3520112345681"
            },
            {
                "first_name": "Maryam", "last_name": "Kamran", "father_name": "Kamran Aslam",
                "slug": "maryam-kamran", "gender": "female", "date_of_birth": date(2008, 3, 8),
                "city": "Islamabad", "country": "Pakistan", "phone_number": "03451234570",
                "email": "maryam@email.com", "cnic": "3520112345682"
            },
            
            # Friends and Colleagues
            {
                "first_name": "Bilal", "last_name": "Ahmed", "father_name": "Ahmed Raza",
                "slug": "bilal-ahmed", "gender": "male", "date_of_birth": date(2000, 4, 15),
                "city": "Lahore", "country": "Pakistan", "phone_number": "03121234567",
                "email": "bilal@email.com", "cnic": "3520112345683"
            },
            {
                "first_name": "Sara", "last_name": "Malik", "father_name": "Malik Riaz",
                "slug": "sara-malik", "gender": "female", "date_of_birth": date(2001, 10, 20),
                "city": "Lahore", "country": "Pakistan", "phone_number": "03121234568",
                "email": "sara@email.com", "cnic": "3520112345684"
            },
            {
                "first_name": "Usman", "last_name": "Ghani", "father_name": "Ghani Butt",
                "slug": "usman-ghani", "gender": "male", "date_of_birth": date(1999, 7, 7),
                "city": "Faisalabad", "country": "Pakistan", "phone_number": "03121234569",
                "email": "usman@email.com", "cnic": "3520112345685"
            },
        ]
        
        persons = []
        for p_data in persons_data:
            person = Persons(user_id=user_id, **p_data)
            db.add(person)
            persons.append(person)
        
        db.commit()
        for p in persons:
            db.refresh(p)
        
        print(f"Created {len(persons)} persons")
        
        # Create person lookup by slug
        person_by_slug = {p.slug: p for p in persons}
        
        # ==================== PERSON RELATIONS ====================
        print("Creating family relations...")
        relations_data = [
            # Grandparents marriage
            ("muhammad-aslam", "fatima-begum", "spouse"),
            ("abdul-malik", "amina-bibi", "spouse"),
            
            # Parents of Generation 2
            ("imran-aslam", "muhammad-aslam", "father"),
            ("imran-aslam", "fatima-begum", "mother"),
            ("kamran-aslam", "muhammad-aslam", "father"),
            ("kamran-aslam", "fatima-begum", "mother"),
            ("sadia-imran", "abdul-malik", "father"),
            ("sadia-imran", "amina-bibi", "mother"),
            
            # Generation 2 marriages
            ("imran-aslam", "sadia-imran", "spouse"),
            ("kamran-aslam", "ayesha-kamran", "spouse"),
            
            # Siblings in Generation 2
            ("imran-aslam", "kamran-aslam", "sibling"),
            
            # Parents of Generation 3
            ("ali-imran", "imran-aslam", "father"),
            ("ali-imran", "sadia-imran", "mother"),
            ("zara-imran", "imran-aslam", "father"),
            ("zara-imran", "sadia-imran", "mother"),
            ("hassan-kamran", "kamran-aslam", "father"),
            ("hassan-kamran", "ayesha-kamran", "mother"),
            ("maryam-kamran", "kamran-aslam", "father"),
            ("maryam-kamran", "ayesha-kamran", "mother"),
            
            # Siblings in Generation 3
            ("ali-imran", "zara-imran", "sibling"),
            ("hassan-kamran", "maryam-kamran", "sibling"),
        ]
        
        # Add relations with inverse
        created_relations = set()
        for person_slug, related_slug, rel_type in relations_data:
            person = person_by_slug[person_slug]
            related = person_by_slug[related_slug]
            
            key = (person.id, related.id, rel_type)
            if key not in created_relations:
                relation = PersonRelation(
                    user_id=user_id,
                    person_id=person.id,
                    related_person_id=related.id,
                    relation_type=rel_type
                )
                db.add(relation)
                created_relations.add(key)
                
                # Create inverse relation
                if rel_type == "father":
                    inv_key = (related.id, person.id, "child")
                    if inv_key not in created_relations:
                        inv_relation = PersonRelation(
                            user_id=user_id,
                            person_id=related.id,
                            related_person_id=person.id,
                            relation_type="child"
                        )
                        db.add(inv_relation)
                        created_relations.add(inv_key)
                elif rel_type == "mother":
                    inv_key = (related.id, person.id, "child")
                    if inv_key not in created_relations:
                        inv_relation = PersonRelation(
                            user_id=user_id,
                            person_id=related.id,
                            related_person_id=person.id,
                            relation_type="child"
                        )
                        db.add(inv_relation)
                        created_relations.add(inv_key)
                elif rel_type == "spouse":
                    inv_key = (related.id, person.id, "spouse")
                    if inv_key not in created_relations:
                        inv_relation = PersonRelation(
                            user_id=user_id,
                            person_id=related.id,
                            related_person_id=person.id,
                            relation_type="spouse"
                        )
                        db.add(inv_relation)
                        created_relations.add(inv_key)
                elif rel_type == "sibling":
                    inv_key = (related.id, person.id, "sibling")
                    if inv_key not in created_relations:
                        inv_relation = PersonRelation(
                            user_id=user_id,
                            person_id=related.id,
                            related_person_id=person.id,
                            relation_type="sibling"
                        )
                        db.add(inv_relation)
                        created_relations.add(inv_key)
        
        db.commit()
        print(f"Created {len(created_relations)} relations")
        
        # ==================== PLACES ====================
        print("Creating places...")
        places_data = [
            {
                "name": "FAST-NUCES Lahore", "slug": "fast-lahore", "place_type": "university",
                "address": "Block B, Faisal Town", "city": "Lahore", "country": "Pakistan",
                "description": "National University of Computer and Emerging Sciences, Lahore Campus"
            },
            {
                "name": "LUMS", "slug": "lums", "place_type": "university",
                "address": "DHA, Lahore Cantt", "city": "Lahore", "country": "Pakistan",
                "description": "Lahore University of Management Sciences"
            },
            {
                "name": "Packages Mall", "slug": "packages-mall", "place_type": "mall",
                "address": "Walton Road", "city": "Lahore", "country": "Pakistan",
                "description": "Popular shopping mall in Lahore"
            },
            {
                "name": "Minar-e-Pakistan", "slug": "minar-e-pakistan", "place_type": "landmark",
                "address": "Greater Iqbal Park", "city": "Lahore", "country": "Pakistan",
                "description": "National monument commemorating Pakistan Resolution"
            },
            {
                "name": "Badshahi Masjid", "slug": "badshahi-masjid", "place_type": "mosque",
                "address": "Walled City", "city": "Lahore", "country": "Pakistan",
                "description": "Historic Mughal era mosque"
            },
            {
                "name": "Arfa Software Technology Park", "slug": "arfa-tower", "place_type": "office",
                "address": "Ferozepur Road", "city": "Lahore", "country": "Pakistan",
                "description": "IT hub and tech park in Lahore"
            },
            {
                "name": "Jinnah Hospital", "slug": "jinnah-hospital", "place_type": "hospital",
                "address": "Canal Road", "city": "Lahore", "country": "Pakistan",
                "description": "Major government hospital"
            },
            {
                "name": "Liberty Market", "slug": "liberty-market", "place_type": "market",
                "address": "Gulberg III", "city": "Lahore", "country": "Pakistan",
                "description": "Famous shopping area in Lahore"
            },
            {
                "name": "Fortress Stadium", "slug": "fortress-stadium", "place_type": "stadium",
                "address": "Lahore Cantt", "city": "Lahore", "country": "Pakistan",
                "description": "Multi-purpose stadium"
            },
            {
                "name": "Ali Home", "slug": "ali-home", "place_type": "home",
                "address": "House 123, DHA Phase 5", "city": "Lahore", "country": "Pakistan",
                "description": "Ali Imran's family residence"
            },
        ]
        
        places = []
        for pl_data in places_data:
            place = Places(user_id=user_id, **pl_data)
            db.add(place)
            places.append(place)
        
        db.commit()
        for pl in places:
            db.refresh(pl)
        
        print(f"Created {len(places)} places")
        place_by_slug = {pl.slug: pl for pl in places}
        
        # ==================== EVENTS ====================
        print("Creating events...")
        events_data = [
            {
                "title": "Semester Final Exams", "slug": "final-exams-2025",
                "event_type": "academic", "place_id": place_by_slug["fast-lahore"].id,
                "start_datetime": datetime(2025, 12, 15, 9, 0),
                "end_datetime": datetime(2025, 12, 25, 17, 0),
                "description": "Fall 2025 semester final examinations"
            },
            {
                "title": "DSA Project Presentation", "slug": "dsa-presentation",
                "event_type": "academic", "place_id": place_by_slug["fast-lahore"].id,
                "start_datetime": datetime(2026, 1, 7, 10, 0),
                "end_datetime": datetime(2026, 1, 7, 12, 0),
                "description": "Data Structures and Algorithms final project presentation"
            },
            {
                "title": "Family Eid Gathering", "slug": "eid-gathering-2025",
                "event_type": "family", "place_id": place_by_slug["ali-home"].id,
                "start_datetime": datetime(2025, 6, 17, 11, 0),
                "end_datetime": datetime(2025, 6, 17, 18, 0),
                "description": "Eid-ul-Adha family lunch at home"
            },
            {
                "title": "Zara's Birthday", "slug": "zara-birthday-2025",
                "event_type": "birthday", "place_id": place_by_slug["packages-mall"].id,
                "start_datetime": datetime(2025, 12, 25, 19, 0),
                "end_datetime": datetime(2025, 12, 25, 23, 0),
                "description": "Zara's birthday celebration at Packages Mall"
            },
            {
                "title": "Tech Conference 2025", "slug": "tech-conf-2025",
                "event_type": "conference", "place_id": place_by_slug["arfa-tower"].id,
                "start_datetime": datetime(2025, 10, 15, 9, 0),
                "end_datetime": datetime(2025, 10, 16, 17, 0),
                "description": "Annual technology conference at Arfa Tower"
            },
            {
                "title": "Cricket Match", "slug": "cricket-match-dec",
                "event_type": "sports", "place_id": place_by_slug["fortress-stadium"].id,
                "start_datetime": datetime(2025, 12, 20, 14, 0),
                "end_datetime": datetime(2025, 12, 20, 20, 0),
                "description": "PSL practice match"
            },
            {
                "title": "Grandparents Anniversary", "slug": "grandparents-anniversary",
                "event_type": "family", "place_id": place_by_slug["ali-home"].id,
                "start_datetime": datetime(2025, 8, 10, 13, 0),
                "end_datetime": datetime(2025, 8, 10, 18, 0),
                "description": "Muhammad Aslam and Fatima's 50th wedding anniversary"
            },
            {
                "title": "Study Group Session", "slug": "study-group",
                "event_type": "academic", "place_id": place_by_slug["lums"].id,
                "start_datetime": datetime(2025, 11, 5, 15, 0),
                "end_datetime": datetime(2025, 11, 5, 19, 0),
                "description": "Group study session for midterms with Bilal and Sara"
            },
        ]
        
        events = []
        for ev_data in events_data:
            event = Events(user_id=user_id, **ev_data)
            db.add(event)
            events.append(event)
        
        db.commit()
        for ev in events:
            db.refresh(ev)
        
        print(f"Created {len(events)} events")
        event_by_slug = {ev.slug: ev for ev in events}
        
        # ==================== NOTES ====================
        print("Creating notes...")
        notes_data = [
            {
                "title": "Family History",
                "content": """# Our Family History

My grandfather @p.muhammad-aslam was born in 1950 in Lahore. He married my grandmother @p.fatima-begum in 1972.

They had two sons:
- @p.imran-aslam (my father, born 1975)
- @p.kamran-aslam (my uncle, born 1978)

My father married @p.sadia-imran and they live at @pl.ali-home in DHA.

The whole family gathered for @e.grandparents-anniversary to celebrate 50 years of marriage!""",
                "is_pinned": True
            },
            {
                "title": "University Life",
                "content": """# My University Journey

I study Computer Science at @pl.fast-lahore. It's one of the best CS programs in Pakistan.

My close friends:
- @p.bilal-ahmed - we work on projects together
- @p.sara-malik - helps with assignments
- @p.usman-ghani - from Faisalabad, stays in hostel

We have our @e.final-exams-2025 coming up in December. Need to prepare well!

The @e.dsa-presentation is on January 7th - very important for our grades.""",
                "is_pinned": True
            },
            {
                "title": "Eid Planning",
                "content": """# Eid-ul-Adha 2025 Planning

The @e.eid-gathering-2025 will be at @pl.ali-home.

Guest list:
- @p.muhammad-aslam and @p.fatima-begum (grandparents)
- @p.kamran-aslam and @p.ayesha-kamran (uncle & aunt from Islamabad)
- @p.hassan-kamran and @p.maryam-kamran (cousins)

Menu to prepare:
- Biryani
- Seekh Kabab
- Kheer

@p.sadia-imran will handle the cooking with help from @p.zara-imran.""",
                "is_pinned": False
            },
            {
                "title": "Zara's Birthday Plan",
                "content": """# Birthday Surprise for Zara

@p.zara-imran turns 22 on December 25th!

Event: @e.zara-birthday-2025
Venue: @pl.packages-mall (food court area)

Invitees:
- Family: @p.imran-aslam, @p.sadia-imran, @p.muhammad-aslam, @p.fatima-begum
- Friends: @p.sara-malik and her friends

Gift ideas:
- New phone (contribution from @p.kamran-aslam)
- Jewelry from parents
- Books from me (@p.ali-imran)""",
                "is_pinned": False
            },
            {
                "title": "Tech Conference Notes",
                "content": """# Tech Conference 2025

Attended @e.tech-conf-2025 at @pl.arfa-tower with @p.bilal-ahmed.

Key Sessions:
1. AI in Pakistan's Tech Industry
2. Startup Ecosystem Growth
3. Cloud Computing Workshop

Met some interesting people. @p.usman-ghani was also there from his Faisalabad office.

Next year they might host it at @pl.lums campus.""",
                "is_pinned": False
            },
            {
                "title": "Study Notes - DSA",
                "content": """# DSA Important Topics

Preparing for @e.dsa-presentation at @pl.fast-lahore.

Topics covered:
1. **Trees** - Binary trees, BST, AVL
2. **Graphs** - DFS, BFS, Dijkstra
3. **Hash Tables** - Collision handling
4. **Tries** - Prefix matching

Study group at @e.study-group with @p.bilal-ahmed and @p.sara-malik.

Project partner: @p.bilal-ahmed
We're building a Family Tree Knowledge Base system!""",
                "is_pinned": True
            },
            {
                "title": "Lahore Trip Guide",
                "content": """# Lahore Tourist Spots

When cousins @p.hassan-kamran and @p.maryam-kamran visit from Islamabad:

Must visit places:
- @pl.badshahi-masjid - Historic mosque, beautiful architecture
- @pl.minar-e-pakistan - National monument
- @pl.liberty-market - Shopping for clothes and shoes
- @pl.packages-mall - Modern mall, good food court

Best restaurants nearby:
- Butt Karahi (near old city)
- Cafe Zouk (Gulberg)

@p.zara-imran knows all the best spots!""",
                "is_pinned": False
            },
            {
                "title": "Cricket Outing",
                "content": """# PSL Match Day

Going to @e.cricket-match-dec at @pl.fortress-stadium!

Who's coming:
- Me (@p.ali-imran)
- @p.bilal-ahmed
- @p.usman-ghani
- Maybe @p.hassan-kamran if he visits

Need to book tickets early. Will ask @p.imran-aslam for help getting good seats.""",
                "is_pinned": False
            },
        ]
        
        notes = []
        for n_data in notes_data:
            note = Notes(owner_id=user_id, **n_data)
            db.add(note)
            notes.append(note)
        
        db.commit()
        for n in notes:
            db.refresh(n)
        
        print(f"Created {len(notes)} notes")
        
        # ==================== NOTE-ENTITY LINKS ====================
        print("Creating note-entity links...")
        import re
        
        for note in notes:
            content = note.content
            
            # Find person mentions
            person_mentions = re.findall(r'@p\.([a-z0-9-]+)', content)
            for slug in set(person_mentions):
                if slug in person_by_slug:
                    db.execute(note_persons.insert().values(
                        note_id=note.id,
                        person_id=person_by_slug[slug].id,
                        mention_text=f"@p.{slug}"
                    ))
            
            # Find place mentions
            place_mentions = re.findall(r'@pl\.([a-z0-9-]+)', content)
            for slug in set(place_mentions):
                if slug in place_by_slug:
                    db.execute(note_places.insert().values(
                        note_id=note.id,
                        place_id=place_by_slug[slug].id,
                        mention_text=f"@pl.{slug}"
                    ))
            
            # Find event mentions
            event_mentions = re.findall(r'@e\.([a-z0-9-]+)', content)
            for slug in set(event_mentions):
                if slug in event_by_slug:
                    db.execute(note_events.insert().values(
                        note_id=note.id,
                        event_id=event_by_slug[slug].id,
                        mention_text=f"@e.{slug}"
                    ))
        
        db.commit()
        print("Created note-entity links")
        
        # ==================== FACTS ====================
        print("Creating facts...")
        facts_data = [
            # Person-Place facts
            {
                "source_type": "person", "source_id": person_by_slug["ali-imran"].id,
                "target_type": "place", "target_id": place_by_slug["fast-lahore"].id,
                "relation_type": "studies_at", "confidence_score": 5,
                "description": "Ali Imran studies at FAST-NUCES Lahore"
            },
            {
                "source_type": "person", "source_id": person_by_slug["bilal-ahmed"].id,
                "target_type": "place", "target_id": place_by_slug["fast-lahore"].id,
                "relation_type": "studies_at", "confidence_score": 3,
                "description": "Bilal Ahmed studies at FAST-NUCES Lahore"
            },
            {
                "source_type": "person", "source_id": person_by_slug["ali-imran"].id,
                "target_type": "place", "target_id": place_by_slug["ali-home"].id,
                "relation_type": "lives_at", "confidence_score": 5,
                "description": "Ali Imran lives at his family home in DHA"
            },
            {
                "source_type": "person", "source_id": person_by_slug["usman-ghani"].id,
                "target_type": "place", "target_id": place_by_slug["arfa-tower"].id,
                "relation_type": "works_at", "confidence_score": 2,
                "description": "Usman Ghani works at Arfa Tower"
            },
            
            # Person-Event facts
            {
                "source_type": "person", "source_id": person_by_slug["ali-imran"].id,
                "target_type": "event", "target_id": event_by_slug["dsa-presentation"].id,
                "relation_type": "participates", "confidence_score": 5,
                "description": "Ali Imran is presenting at DSA project presentation"
            },
            {
                "source_type": "person", "source_id": person_by_slug["bilal-ahmed"].id,
                "target_type": "event", "target_id": event_by_slug["tech-conf-2025"].id,
                "relation_type": "attends", "confidence_score": 3,
                "description": "Bilal Ahmed attended Tech Conference 2025"
            },
            {
                "source_type": "person", "source_id": person_by_slug["zara-imran"].id,
                "target_type": "event", "target_id": event_by_slug["zara-birthday-2025"].id,
                "relation_type": "hosts", "confidence_score": 5,
                "description": "Zara Imran is the host of her birthday celebration"
            },
            
            # Person-Person facts
            {
                "source_type": "person", "source_id": person_by_slug["ali-imran"].id,
                "target_type": "person", "target_id": person_by_slug["bilal-ahmed"].id,
                "relation_type": "friend_of", "confidence_score": 5,
                "description": "Ali Imran and Bilal Ahmed are close friends"
            },
            {
                "source_type": "person", "source_id": person_by_slug["ali-imran"].id,
                "target_type": "person", "target_id": person_by_slug["sara-malik"].id,
                "relation_type": "colleague_of", "confidence_score": 3,
                "description": "Ali and Sara are classmates at FAST"
            },
            {
                "source_type": "person", "source_id": person_by_slug["bilal-ahmed"].id,
                "target_type": "person", "target_id": person_by_slug["ali-imran"].id,
                "relation_type": "works_with", "confidence_score": 4,
                "description": "Bilal works on projects with Ali"
            },
        ]
        
        for fact_data in facts_data:
            fact = Facts(user_id=user_id, **fact_data)
            db.add(fact)
        
        db.commit()
        print(f"Created {len(facts_data)} facts")
        
        # ==================== SUMMARY ====================
        print("\n" + "="*50)
        print("SEED DATA COMPLETE!")
        print("="*50)
        print(f"""
Login Credentials:
  Username: ahmed
  Password: password123
  Email: ahmed@example.com

Data Created:
  - 1 User
  - {len(persons)} Persons (3-generation family + friends)
  - {len(created_relations)} Family Relations (bidirectional)
  - {len(places)} Places (universities, landmarks, homes)
  - {len(events)} Events (academic, family, sports)
  - {len(notes)} Notes (with @mentions)
  - {len(facts_data)} Facts (extracted relationships)

Family Tree Structure:
  Generation 1: Muhammad Aslam + Fatima Begum
                Abdul Malik + Amina Bibi
  
  Generation 2: Imran Aslam (married to Sadia)
                Kamran Aslam (married to Ayesha)
  
  Generation 3: Ali, Zara (children of Imran)
                Hassan, Maryam (children of Kamran)

Test the family tree with person IDs:
  - Ali Imran: {person_by_slug['ali-imran'].id}
  - Muhammad Aslam (grandpa): {person_by_slug['muhammad-aslam'].id}
""")
        
    except Exception as e:
        db.rollback()
        print(f"Error: {e}")
        raise
    finally:
        db.close()


if __name__ == "__main__":
    seed_database()
