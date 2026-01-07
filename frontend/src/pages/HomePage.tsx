import { useState, useEffect } from 'react';
import { useNavigate } from 'react-router-dom';
import { Plus, Users, Calendar, MapPin } from 'lucide-react';
import { Button } from '../components/ui/Button';
import { getNotes } from '../api/notes';
import { getPersons } from '../api/persons';
import { getPlaces } from '../api/places';
import { getEvents } from '../api/events';

const HomePage = () => {
  const navigate = useNavigate();
  const [recentNotes, setRecentNotes] = useState<any[]>([]);
  const [recentPersons, setRecentPersons] = useState<any[]>([]);
  const [recentEvents, setRecentEvents] = useState<any[]>([]);
  const [recentPlaces, setRecentPlaces] = useState<any[]>([]);
  const [loading, setLoading] = useState(true);

  useEffect(() => {
    const fetchData = async () => {
      try {
        setLoading(true);
        const [notesRes, personsRes, eventsRes, placesRes] = await Promise.all([
          getNotes(0, 5),
          getPersons(0, 5),
          getEvents(0, 5),
          getPlaces(0, 5),
        ]);

        setRecentNotes(notesRes.data.slice(0, 3));
        setRecentPersons(personsRes.data.slice(0, 3));
        setRecentEvents(eventsRes.data.slice(0, 3));
        setRecentPlaces(placesRes.data.slice(0, 3));
      } catch (error) {
        console.error('Failed to fetch data:', error);
      } finally {
        setLoading(false);
      }
    };

    fetchData();
  }, []);

  return (
    <div className="space-y-6">
      {/* Welcome Header */}
      <div className="rounded-lg border border-blue-200 bg-gradient-to-r from-blue-50 to-indigo-50 p-8">
        <h1 className="text-4xl font-bold text-gray-900">Welcome to Your Archive</h1>
        <p className="mt-2 text-lg text-gray-600">
          Organize, document, and explore your memories, people, and places all in one place.
        </p>
        <div className="mt-6 flex flex-wrap gap-3">
          <Button onClick={() => navigate('/notes/new')}>
            <Plus className="w-4 h-4" />
            New Note
          </Button>
          <Button variant="secondary" onClick={() => navigate('/persons')}>
            <Users className="w-4 h-4" />
            Add Person
          </Button>
          <Button variant="secondary" onClick={() => navigate('/events')}>
            <Calendar className="w-4 h-4" />
            New Event
          </Button>
        </div>
      </div>

      {/* Recent Items Grid */}
      {!loading && (
        <div className="grid gap-6 lg:grid-cols-2">
          {/* Recent Notes */}
          <div className="rounded-lg border border-gray-200 bg-white p-6 shadow-sm">
            <div className="flex items-center justify-between mb-4">
              <h2 className="text-lg font-semibold text-gray-900">Recent Notes</h2>
              <Button variant="secondary" size="sm" onClick={() => navigate('/notes')}>
                View All
              </Button>
            </div>
            {recentNotes.length > 0 ? (
              <div className="space-y-3">
                {recentNotes.map(note => (
                  <div
                    key={note.id}
                    onClick={() => navigate(`/notes/${note.id}`)}
                    className="p-3 rounded-lg bg-gray-50 hover:bg-blue-50 cursor-pointer transition border border-transparent hover:border-blue-200"
                  >
                    <p className="font-medium text-sm text-gray-900">{note.title || 'Untitled Note'}</p>
                    <p className="text-xs text-gray-500 mt-1 line-clamp-1">{note.content}</p>
                    <p className="text-xs text-gray-400 mt-1">
                      {new Date(note.updated_at).toLocaleDateString()}
                    </p>
                  </div>
                ))}
              </div>
            ) : (
              <p className="text-sm text-gray-500">No notes yet. Create your first note!</p>
            )}
          </div>

          {/* Recent Persons */}
          <div className="rounded-lg border border-gray-200 bg-white p-6 shadow-sm">
            <div className="flex items-center justify-between mb-4">
              <h2 className="text-lg font-semibold text-gray-900">Recent Persons</h2>
              <Button variant="secondary" size="sm" onClick={() => navigate('/persons')}>
                View All
              </Button>
            </div>
            {recentPersons.length > 0 ? (
              <div className="space-y-3">
                {recentPersons.map(person => (
                  <div
                    key={person.id}
                    onClick={() => navigate(`/persons/${person.id}`)}
                    className="p-3 rounded-lg bg-gray-50 hover:bg-blue-50 cursor-pointer transition border border-transparent hover:border-blue-200"
                  >
                    <p className="font-medium text-sm text-gray-900">{person.first_name} {person.last_name || ''}</p>
                    {person.email && <p className="text-xs text-gray-500 mt-1">{person.email}</p>}
                    {person.phone_number && <p className="text-xs text-gray-500">{person.phone_number}</p>}
                  </div>
                ))}
              </div>
            ) : (
              <p className="text-sm text-gray-500">No persons yet. Add your first person!</p>
            )}
          </div>

          {/* Recent Events */}
          <div className="rounded-lg border border-gray-200 bg-white p-6 shadow-sm">
            <div className="flex items-center justify-between mb-4">
              <h2 className="text-lg font-semibold text-gray-900">Upcoming Events</h2>
              <Button variant="secondary" size="sm" onClick={() => navigate('/events')}>
                View All
              </Button>
            </div>
            {recentEvents.length > 0 ? (
              <div className="space-y-3">
                {recentEvents.map(event => (
                  <div
                    key={event.id}
                    onClick={() => navigate(`/events/${event.id}`)}
                    className="p-3 rounded-lg bg-gray-50 hover:bg-blue-50 cursor-pointer transition border border-transparent hover:border-blue-200"
                  >
                    <p className="font-medium text-sm text-gray-900">{event.title}</p>
                    <p className="text-xs text-gray-500 mt-1">
                      {new Date(event.start_datetime).toLocaleDateString()}
                    </p>
                  </div>
                ))}
              </div>
            ) : (
              <p className="text-sm text-gray-500">No events yet. Create your first event!</p>
            )}
          </div>

          {/* Recent Places */}
          <div className="rounded-lg border border-gray-200 bg-white p-6 shadow-sm">
            <div className="flex items-center justify-between mb-4">
              <h2 className="text-lg font-semibold text-gray-900">Recent Places</h2>
              <Button variant="secondary" size="sm" onClick={() => navigate('/places')}>
                View All
              </Button>
            </div>
            {recentPlaces.length > 0 ? (
              <div className="space-y-3">
                {recentPlaces.map(place => (
                  <div
                    key={place.id}
                    onClick={() => navigate(`/places/${place.id}`)}
                    className="p-3 rounded-lg bg-gray-50 hover:bg-blue-50 cursor-pointer transition border border-transparent hover:border-blue-200"
                  >
                    <p className="font-medium text-sm text-gray-900">{place.name}</p>
                    {place.city && <p className="text-xs text-gray-500 mt-1">{place.city}</p>}
                  </div>
                ))}
              </div>
            ) : (
              <p className="text-sm text-gray-500">No places yet. Add your first place!</p>
            )}
          </div>
        </div>
      )}
    </div>
  )
}

export default HomePage