import { useState, useEffect } from 'react';
import { Plus, Search, Trash2, Edit, Calendar } from 'lucide-react';
import { Dialog } from '../components/ui/Dialog';
import { Button } from '../components/ui/Button';
import { Card, CardContent, CardHeader } from '../components/ui/Card';
import { InputField } from '../components/FormFields';
import { getEvents, createEvent, updateEvent, deleteEvent,type Event,type EventCreate } from '../api/events';
import { formatDistanceToNow } from 'date-fns';

export const EventsPage = () => {
  const [events, setEvents] = useState<Event[]>([]);
  const [filteredEvents, setFilteredEvents] = useState<Event[]>([]);
  const [loading, setLoading] = useState(true);
  const [searchQuery, setSearchQuery] = useState('');
  const [showDialog, setShowDialog] = useState(false);
  const [editingEvent, setEditingEvent] = useState<Event | null>(null);
  const [isSubmitting, setIsSubmitting] = useState(false);

  const [formData, setFormData] = useState<EventCreate>({
    title: '',
    description: '',
    start_datetime: '',
    end_datetime: '',
    location: ''
  });

  const [errors, setErrors] = useState<Record<string, string>>({});

  // Fetch events
  useEffect(() => {
    const fetchEvents = async () => {
      try {
        setLoading(true);
        const res = await getEvents();
        setEvents(res.data);
      } catch (error) {
        console.error('Failed to fetch events:', error);
      } finally {
        setLoading(false);
      }
    };

    fetchEvents();
  }, []);

  // Filter events
  useEffect(() => {
    const query = searchQuery.toLowerCase();
    const filtered = events.filter(e =>
      e.title.toLowerCase().includes(query) ||
      (e.description?.toLowerCase().includes(query)) ||
      (e.location?.toLowerCase().includes(query))
    );

    // Sort by start time
    filtered.sort((a, b) =>
      new Date(b.start_datetime).getTime() - new Date(a.start_datetime).getTime()
    );

    setFilteredEvents(filtered);
  }, [events, searchQuery]);

  const validateForm = () => {
    const newErrors: Record<string, string> = {};
    if (!formData.title.trim()) {
      newErrors.title = 'Event title is required';
    }
    if (!formData.start_datetime) {
      newErrors.start_datetime = 'Start date and time is required';
    }
    setErrors(newErrors);
    return Object.keys(newErrors).length === 0;
  };

  const handleSubmit = async () => {
    if (!validateForm()) return;

    try {
      setIsSubmitting(true);
      if (editingEvent) {
        const res = await updateEvent(editingEvent.id, formData);
        setEvents(events.map(e => e.id === editingEvent.id ? res.data : e));
      } else {
        const res = await createEvent(formData);
        setEvents([res.data, ...events]);
      }
      setShowDialog(false);
      resetForm();
    } catch (error) {
      console.error('Failed to save event:', error);
    } finally {
      setIsSubmitting(false);
    }
  };

  const handleDelete = async (eventId: number) => {
    if (confirm('Are you sure you want to delete this event?')) {
      try {
        await deleteEvent(eventId);
        setEvents(events.filter(e => e.id !== eventId));
      } catch (error) {
        console.error('Failed to delete event:', error);
      }
    }
  };

  const handleEdit = (event: Event) => {
    setEditingEvent(event);
    setFormData({
      title: event.title,
      description: event.description || '',
      start_datetime: event.start_datetime,
      end_datetime: event.end_datetime || '',
      location: event.location || ''
    });
    setShowDialog(true);
  };

  const handleOpenCreate = () => {
    setEditingEvent(null);
    resetForm();
    setShowDialog(true);
  };

  const resetForm = () => {
    setFormData({
      title: '',
      description: '',
      start_datetime: '',
      end_datetime: '',
      location: ''
    });
    setErrors({});
  };

  const getEventStatus = (event: Event) => {
    const now = new Date();
    const start = new Date(event.start_datetime);
    const end = event.end_datetime ? new Date(event.end_datetime) : null;

    if (end && now > end) return 'past';
    if (now > start) return 'ongoing';
    return 'upcoming';
  };

  if (loading) {
    return (
      <div className="flex items-center justify-center h-screen">
        <div className="text-center">
          <div className="w-12 h-12 border-4 border-blue-500 border-t-transparent rounded-full animate-spin mx-auto mb-4" />
          <p className="text-gray-600">Loading events...</p>
        </div>
      </div>
    );
  }

  return (
    <div className="min-h-screen bg-gray-50">
      {/* Header */}
      <div className="bg-white border-b border-gray-200 sticky top-0 z-40">
        <div className="max-w-7xl mx-auto px-4 sm:px-6 lg:px-8 py-4">
          <div className="flex items-center justify-between mb-6">
            <h1 className="text-3xl font-bold text-gray-900">Events</h1>
            <Button onClick={handleOpenCreate} size="lg">
              <Plus className="w-5 h-5" />
              Add Event
            </Button>
          </div>

          {/* Search */}
          <div className="relative">
            <Search className="absolute left-3 top-1/2 -translate-y-1/2 w-5 h-5 text-gray-400" />
            <input
              type="text"
              placeholder="Search by title, description, or location..."
              value={searchQuery}
              onChange={(e) => setSearchQuery(e.target.value)}
              className="w-full pl-10 pr-4 py-2 border border-gray-300 rounded-lg focus:outline-none focus:ring-2 focus:ring-blue-500"
            />
          </div>

          <div className="text-sm text-gray-600 mt-3">
            Showing {filteredEvents.length} of {events.length} events
          </div>
        </div>
      </div>

      {/* Content */}
      <div className="max-w-7xl mx-auto px-4 sm:px-6 lg:px-8 py-8">
        {filteredEvents.length === 0 ? (
          <div className="text-center py-12">
            <Calendar className="w-16 h-16 text-gray-300 mx-auto mb-4" />
            <p className="text-gray-500 mb-4">No events added yet</p>
            <Button onClick={handleOpenCreate}>
              <Plus className="w-5 h-5" />
              Add Your First Event
            </Button>
          </div>
        ) : (
          <div className="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-3 gap-6">
            {filteredEvents.map(event => {
              const status = getEventStatus(event);
              const statusColor = {
                upcoming: 'bg-blue-100 text-blue-700',
                ongoing: 'bg-green-100 text-green-700',
                past: 'bg-gray-100 text-gray-700'
              }[status];

              return (
                <Card key={event.id} className="hover:shadow-lg transition-shadow">
                  <CardHeader>
                    <div className="flex items-start justify-between gap-2">
                      <div>
                        <h3 className="text-lg font-semibold text-gray-900">{event.title}</h3>
                        <p className="text-xs text-gray-500 mt-1">
                          {formatDistanceToNow(new Date(event.start_datetime), { addSuffix: true })}
                        </p>
                      </div>
                      <div className="w-12 h-12 bg-purple-100 rounded-full flex items-center justify-center">
                        <Calendar className="w-6 h-6 text-purple-600" />
                      </div>
                    </div>
                  </CardHeader>

                  <CardContent className="space-y-3">
                    {/* Status Badge */}
                    <div className="flex gap-2">
                      <span className={`text-xs px-3 py-1 rounded-full font-medium capitalize ${statusColor}`}>
                        {status}
                      </span>
                    </div>

                    {/* Start DateTime */}
                    <div className="text-sm">
                      <p className="font-medium text-gray-700">Start:</p>
                      <p className="text-gray-600">
                        {new Date(event.start_datetime).toLocaleString()}
                      </p>
                    </div>

                    {/* End DateTime */}
                    {event.end_datetime && (
                      <div className="text-sm">
                        <p className="font-medium text-gray-700">End:</p>
                        <p className="text-gray-600">
                          {new Date(event.end_datetime).toLocaleString()}
                        </p>
                      </div>
                    )}

                    {/* Location */}
                    {event.location && (
                      <div className="text-sm">
                        <p className="font-medium text-gray-700">Location:</p>
                        <p className="text-gray-600">{event.location}</p>
                      </div>
                    )}

                    {/* Description */}
                    {event.description && (
                      <div className="text-sm">
                        <p className="font-medium text-gray-700">Description:</p>
                        <p className="text-gray-600 line-clamp-3">{event.description}</p>
                      </div>
                    )}
                  </CardContent>

                  <div className="px-6 py-4 border-t border-gray-200 flex gap-2">
                    <Button
                      variant="secondary"
                      size="sm"
                      onClick={() => handleEdit(event)}
                      className="flex-1"
                    >
                      <Edit className="w-4 h-4" />
                      Edit
                    </Button>
                    <Button
                      variant="danger"
                      size="sm"
                      onClick={() => handleDelete(event.id)}
                      className="flex-1"
                    >
                      <Trash2 className="w-4 h-4" />
                      Delete
                    </Button>
                  </div>
                </Card>
              );
            })}
          </div>
        )}
      </div>

      {/* Dialog */}
      <Dialog
        isOpen={showDialog}
        onClose={() => {
          setShowDialog(false);
          resetForm();
        }}
        title={editingEvent ? 'Edit Event' : 'Add New Event'}
        description={editingEvent ? 'Update event details' : 'Create a new event'}
        size="lg"
      >
        <div className="space-y-4 max-h-96 overflow-y-auto">
          <InputField
            label="Event Title"
            placeholder="e.g., Meeting, Conference, Birthday"
            value={formData.title}
            onChange={(val) => setFormData({ ...formData, title: val })}
            required
            error={errors.title}
          />

          <InputField
            label="Location"
            placeholder="e.g., Conference Room A, Zoom Link"
            value={formData.location || ''}
            onChange={(val) => setFormData({ ...formData, location: val })}
          />

          <div className="grid grid-cols-2 gap-4">
            <InputField
              label="Start Date & Time"
              type="datetime-local"
              value={formData.start_datetime}
              onChange={(val) => setFormData({ ...formData, start_datetime: val })}
              required
              error={errors.start_datetime}
            />
            <InputField
              label="End Date & Time"
              type="datetime-local"
              value={formData.end_datetime || ''}
              onChange={(val) => setFormData({ ...formData, end_datetime: val })}
            />
          </div>

          <div>
            <label className="block text-sm font-medium text-gray-700 mb-2">
              Description
            </label>
            <textarea
              value={formData.description || ''}
              onChange={(val) => setFormData({ ...formData, description: val })}
              placeholder="Add event details, agenda, or notes..."
              rows={4}
              className="w-full px-4 py-2 border border-gray-300 rounded-lg focus:outline-none focus:ring-2 focus:ring-blue-500 focus:border-transparent resize-none"
            />
          </div>

          <div className="flex gap-3 justify-end pt-4 border-t border-gray-200">
            <Button
              variant="secondary"
              onClick={() => {
                setShowDialog(false);
                resetForm();
              }}
            >
              Cancel
            </Button>
            <Button
              onClick={handleSubmit}
              isLoading={isSubmitting}
            >
              {editingEvent ? 'Update Event' : 'Add Event'}
            </Button>
          </div>
        </div>
      </Dialog>
    </div>
  );
};

export default EventsPage;
