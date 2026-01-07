import { useState, useEffect } from 'react';
import { useNavigate } from 'react-router-dom';
import { Calendar, Users, BrainIcon, MapPin, Plus, TrendingUp } from 'lucide-react';
import { Button } from '../components/ui/Button';
import { getNotes } from '../api/notes';
import { getPersons } from '../api/persons';
import { getPlaces } from '../api/places';
import { getEvents } from '../api/events';

const DashboardPage = () => {
  const navigate = useNavigate();
  const [stats, setStats] = useState({ notes: 0, persons: 0, events: 0, places: 0 });
  const [recentItems, setRecentItems] = useState<any[]>([]);
  const [loading, setLoading] = useState(true);

  useEffect(() => {
    const fetchData = async () => {
      try {
        setLoading(true);
        const [notesRes, personsRes, eventsRes, placesRes] = await Promise.all([
          getNotes(0, 100),
          getPersons(0, 100),
          getEvents(0, 100),
          getPlaces(0, 100),
        ]);

        setStats({
          notes: notesRes.data.length,
          persons: personsRes.data.length,
          events: eventsRes.data.length,
          places: placesRes.data.length,
        });

        // Combine and sort recent items by updated_at
        const allItems = [
          ...notesRes.data.slice(0, 3).map(n => ({ ...n, type: 'note' })),
          ...personsRes.data.slice(0, 3).map(p => ({ ...p, type: 'person' })),
          ...eventsRes.data.slice(0, 3).map(e => ({ ...e, type: 'event' })),
          ...placesRes.data.slice(0, 3).map(p => ({ ...p, type: 'place' })),
        ].sort((a, b) => new Date(b.updated_at || b.created_at).getTime() - new Date(a.updated_at || a.created_at).getTime())
          .slice(0, 5);

        setRecentItems(allItems);
      } catch (error) {
        console.error('Failed to fetch data:', error);
      } finally {
        setLoading(false);
      }
    };

    fetchData();
  }, []);

  const statCards = [
    {
      title: 'Total Notes',
      value: stats.notes,
      description: 'Knowledge Base',
      icon: BrainIcon,
      color: 'bg-green-500',
      action: () => navigate('/notes'),
    },
    {
      title: 'Total People',
      value: stats.persons,
      description: 'Person Records',
      icon: Users,
      color: 'bg-blue-500',
      action: () => navigate('/persons'),
    },
    {
      title: 'Total Events',
      value: stats.events,
      description: 'Event Timeline',
      icon: Calendar,
      color: 'bg-purple-500',
      action: () => navigate('/events'),
    },
    {
      title: 'Total Places',
      value: stats.places,
      description: 'Locations',
      icon: MapPin,
      color: 'bg-orange-500',
      action: () => navigate('/places'),
    },
  ];

  return (
    <div className="space-y-6">
      {/* Page Header */}
      <div>
        <h1 className="text-3xl font-bold text-gray-900">Dashboard</h1>
        <p className="mt-1 text-sm text-gray-500">
          Overview of your archive. Click on any stat to view details.
        </p>
      </div>

      {/* Stats Grid */}
      {!loading && (
        <>
          <div className="grid gap-6 md:grid-cols-2 lg:grid-cols-4">
            {statCards.map((stat, index) => {
              const Icon = stat.icon;
              return (
                <button
                  key={index}
                  onClick={stat.action}
                  className="rounded-lg border border-gray-200 bg-white p-6 shadow-sm transition hover:shadow-md hover:border-gray-300 text-left"
                >
                  <div className="flex items-center justify-between">
                    <div>
                      <p className="text-sm font-medium text-gray-600">{stat.title}</p>
                      <p className="mt-2 text-3xl font-bold text-gray-900">{stat.value}</p>
                      <p className="mt-2 text-sm text-gray-500">{stat.description}</p>
                    </div>
                    <div className={`rounded-full ${stat.color} p-3`}>
                      <Icon className="h-6 w-6 text-white" />
                    </div>
                  </div>
                </button>
              );
            })}
          </div>

          {/* Content Sections */}
          <div className="grid gap-6 lg:grid-cols-2">
            {/* Recent Activity */}
            <div className="rounded-lg border border-gray-200 bg-white p-6 shadow-sm">
              <h2 className="text-lg font-semibold text-gray-900 mb-4">Recent Activity</h2>
              {recentItems.length > 0 ? (
                <div className="space-y-3">
                  {recentItems.map((item, idx) => {
                    const typeColors: Record<string, string> = {
                      note: 'bg-green-100 text-green-700',
                      person: 'bg-blue-100 text-blue-700',
                      event: 'bg-purple-100 text-purple-700',
                      place: 'bg-orange-100 text-orange-700',
                    };

                    const getItemName = (item: any) => {
                      if (item.type === 'note') return item.title || 'Untitled Note';
                      if (item.type === 'person') return `${item.first_name} ${item.last_name || ''}`;
                      if (item.type === 'event') return item.title;
                      if (item.type === 'place') return item.name;
                      return 'Unknown';
                    };

                    const getItemLink = (item: any) => {
                      if (item.type === 'note') return `/notes/${item.id}`;
                      if (item.type === 'person') return `/persons/${item.id}`;
                      if (item.type === 'event') return `/events/${item.id}`;
                      if (item.type === 'place') return `/places/${item.id}`;
                      return '/';
                    };

                    return (
                      <div
                        key={idx}
                        onClick={() => navigate(getItemLink(item))}
                        className="flex items-center gap-3 p-3 rounded-lg bg-gray-50 hover:bg-blue-50 cursor-pointer transition"
                      >
                        <div className={`px-2.5 py-1 rounded text-xs font-semibold capitalize ${typeColors[item.type]}`}>
                          {item.type}
                        </div>
                        <div className="flex-1 min-w-0">
                          <p className="text-sm font-medium text-gray-900 truncate">{getItemName(item)}</p>
                          <p className="text-xs text-gray-500">
                            {new Date(item.updated_at || item.created_at).toLocaleDateString()}
                          </p>
                        </div>
                      </div>
                    );
                  })}
                </div>
              ) : (
                <p className="text-sm text-gray-500">No recent activity. Start adding items!</p>
              )}
            </div>

            {/* Quick Actions */}
            <div className="rounded-lg border border-gray-200 bg-white p-6 shadow-sm">
              <h2 className="text-lg font-semibold text-gray-900 mb-4">Quick Actions</h2>
              <div className="grid grid-cols-2 gap-3">
                <Button
                  onClick={() => navigate('/notes/new')}
                  variant="secondary"
                  className="w-full"
                >
                  <Plus className="w-4 h-4" />
                  New Note
                </Button>
                <Button
                  onClick={() => navigate('/persons')}
                  variant="secondary"
                  className="w-full"
                >
                  <Users className="w-4 h-4" />
                  Add Person
                </Button>
                <Button
                  onClick={() => navigate('/events')}
                  variant="secondary"
                  className="w-full"
                >
                  <Calendar className="w-4 h-4" />
                  New Event
                </Button>
                <Button
                  onClick={() => navigate('/places')}
                  variant="secondary"
                  className="w-full"
                >
                  <MapPin className="w-4 h-4" />
                  Add Place
                </Button>
              </div>
            </div>
          </div>

          {/* Stats Summary */}
          <div className="rounded-lg border border-blue-200 bg-gradient-to-r from-blue-50 to-indigo-50 p-6">
            <div className="flex items-center gap-3 mb-2">
              <TrendingUp className="w-5 h-5 text-blue-600" />
              <h2 className="text-lg font-semibold text-gray-900">Summary</h2>
            </div>
            <p className="text-gray-600">
              You have <strong>{stats.notes}</strong> notes documenting <strong>{stats.persons}</strong> people, 
              <strong> {stats.events}</strong> events, and <strong>{stats.places}</strong> places. 
              Keep adding to build your complete archive!
            </p>
          </div>
        </>
      )}
    </div>
  );
};

export default DashboardPage;
