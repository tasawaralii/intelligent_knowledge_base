import { useState, useEffect, useMemo } from 'react';
import { useNavigate, useParams } from 'react-router-dom';
import { ArrowLeft, Trash2, Save, Pin, PinOff, User, MapPin, Calendar, Plus } from 'lucide-react';
import { Button } from '../components/ui/Button';
import { Card } from '../components/ui/Card';
import { InputField } from '../components/FormFields';
import { SmartNoteEditor } from '../components/SmartNoteEditor';
import { getNotes, createNote, updateNote, deleteNote, type Note } from '../api/notes';
import { getPersons } from '../api/persons';
import { getPlaces } from '../api/places';
import { getEvents } from '../api/events';
import { useAlert } from '../context/alertContext';

export const NotePage = () => {
    const { note_id } = useParams();
    const navigate = useNavigate();
    const { addAlert } = useAlert();

    const [note, setNote] = useState<Note | null>(null);
    const [title, setTitle] = useState('');
    const [content, setContent] = useState('');
    const [isPinned, setIsPinned] = useState(false);
    const [loading, setLoading] = useState(true);
    const [saving, setSaving] = useState(false);
    const [suggestions, setSuggestions] = useState<SuggestionItem[]>([]);
    const [mentionedPersons, setMentionedPersons] = useState<MentionWithMeta[]>([]);
    const [mentionedPlaces, setMentionedPlaces] = useState<MentionWithMeta[]>([]);
    const [mentionedEvents, setMentionedEvents] = useState<MentionWithMeta[]>([]);

    // Parse mentions from content  
    type SuggestionItem = {
        id: string | number;
        name: string;
        type: 'person' | 'place' | 'event';
        slug: string;
        description?: string;
    };

    type Mention = {
        slug: string;
        type: 'person' | 'place' | 'event';
        isNew: boolean;
    };

    type MentionWithMeta = Mention & {
        name: string;
        id?: string | number;
    };

    const parseMentions = (text: string) => {
        const regex = /@(?:(n)\.)?(p|pl|e)\.([a-z0-9-]+)/g;

        const persons: Mention[] = [];
        const places: Mention[] = [];
        const events: Mention[] = [];

        let match;
        while ((match = regex.exec(text)) !== null) {
            const isNew = Boolean(match[1]);
            const entityType = match[2];
            const slug = match[3];

            const mention: Mention = {
                slug,
                isNew,
                type:
                    entityType === 'p'
                        ? 'person'
                        : entityType === 'pl'
                            ? 'place'
                            : 'event',
            };

            if (mention.type === 'person') persons.push(mention);
            if (mention.type === 'place') places.push(mention);
            if (mention.type === 'event') events.push(mention);
        }

        return { persons, places, events };
    };

    const buildLookup = (items: SuggestionItem[]) => {
        const map = new Map<string, SuggestionItem>();
        items.forEach((item) => {
            if (item.slug) {
                map.set(`${item.type}:${item.slug}`, item);
            }
        });
        return map;
    };

    const suggestionsMap = useMemo(() => buildLookup(suggestions), [suggestions]);

    const withMetadata = (mentions: Mention[], lookup: Map<string, SuggestionItem>): MentionWithMeta[] => {
        const seen = new Set<string>();
        return mentions
            .filter((mention) => {
                const key = `${mention.type}:${mention.slug}`;
                if (seen.has(key)) return false;
                seen.add(key);
                return true;
            })
            .map((mention) => {
                const key = `${mention.type}:${mention.slug}`;
                const match = lookup.get(key);
                return {
                    ...mention,
                    id: match?.id,
                    name: match?.name || mention.slug
                };
            });
    };


    // Fetch initial data and load note if editing
    useEffect(() => {
        const fetchData = async () => {
            try {
                setLoading(true);
                const [personsRes, placesRes, eventsRes, notesRes] = await Promise.all([
                    getPersons(0, 100),
                    getPlaces(0, 100),
                    getEvents(0, 100),
                    getNotes(0, 100)
                ]);

                // Build suggestions for autocomplete
                const allSuggestions: SuggestionItem[] = [
                    ...personsRes.data.map((p: any) => ({
                        id: `p-${p.id}`,
                        name: `${p.first_name} ${p.last_name || ''}`.trim(),
                        type: 'person' as const,
                        slug: p.slug,
                        description: p.email || p.phone_number
                    })),
                    ...placesRes.data.map((p: any) => ({
                        id: `pl-${p.id}`,
                        name: p.name,
                        type: 'place' as const,
                        slug: p.slug,
                        description: p.address || p.city
                    })),
                    ...eventsRes.data.map((e: any) => ({
                        id: `e-${e.id}`,
                        name: e.title,
                        type: 'event' as const,
                        slug: e.slug,
                        description: new Date(e.start_datetime).toLocaleDateString()
                    }))
                ];
                setSuggestions(allSuggestions);
                const suggestionLookup = buildLookup(allSuggestions);

                // If editing, find and load the note from the list
                if (note_id && note_id !== 'new') {
                    const foundNote = notesRes.data.find((n: Note) => n.id === parseInt(note_id, 10));
                    if (foundNote) {
                        setNote(foundNote);
                        setTitle(foundNote.title || '');
                        setContent(foundNote.content || '');
                        setIsPinned(foundNote.is_pinned || false);

                        const { persons, places, events } = parseMentions(foundNote.content || '');
                        setMentionedPersons(withMetadata(persons, suggestionLookup));
                        setMentionedPlaces(withMetadata(places, suggestionLookup));
                        setMentionedEvents(withMetadata(events, suggestionLookup));
                    }
                }
            } catch (error: any) {
                addAlert(error?.response?.data?.detail || 'Failed to load data', 'error', 3000);
            } finally {
                setLoading(false);
            }
        };

        fetchData();
    }, [note_id, addAlert]);

    // Update mentions when content changes
    useEffect(() => {
        const { persons, places, events } = parseMentions(content);
        setMentionedPersons(withMetadata(persons, suggestionsMap));
        setMentionedPlaces(withMetadata(places, suggestionsMap));
        setMentionedEvents(withMetadata(events, suggestionsMap));
    }, [content, suggestionsMap]);

    const handleSave = async () => {
        if (!content.trim()) {
            addAlert('Note content cannot be empty', 'error', 3000);
            return;
        }

        setSaving(true);
        try {
            const noteData = {
                title: title || undefined,
                content: content,
                is_pinned: isPinned
            };

            if (note && note_id !== 'new') {
                // Update existing note
                const res = await updateNote(note.id, noteData);
                setNote(res.data);
                addAlert('Note updated successfully', 'success', 2000);
            } else {
                // Create new note
                const res = await createNote(noteData);
                setNote(res.data);
                navigate(`/notes/${res.data.id}`);
                addAlert('Note created successfully', 'success', 2000);
            }
        } catch (error: any) {
            addAlert(error?.response?.data?.detail || 'Failed to save note', 'error', 3000);
        } finally {
            setSaving(false);
        }
    };

    const handleDelete = async () => {
        if (!note) return;
        if (!window.confirm('Are you sure you want to delete this note?')) return;

        try {
            await deleteNote(note.id);
            addAlert('Note deleted successfully', 'success', 2000);
            navigate('/notes');
        } catch (error: any) {
            addAlert(error?.response?.data?.detail || 'Failed to delete note', 'error', 3000);
        }
    };

    const handleTogglePin = async () => {
        if (!note) return;

        setSaving(true);
        try {
            const res = await updateNote(note.id, {
                title: note.title || undefined,
                content: note.content,
                is_pinned: !isPinned
            });
            setNote(res.data);
            setIsPinned(!isPinned);
            addAlert(isPinned ? 'Note unpinned' : 'Note pinned', 'success', 2000);
        } catch (error: any) {
            addAlert(error?.response?.data?.detail || 'Failed to update note', 'error', 3000);
        } finally {
            setSaving(false);
        }
    };

    if (loading) {
        return (
            <div className="flex items-center justify-center min-h-screen bg-gray-50">
                <div className="text-center">
                    <div className="w-12 h-12 border-4 border-blue-500 border-t-transparent rounded-full animate-spin mx-auto mb-4" />
                    <p className="text-gray-600">Loading note...</p>
                </div>
            </div>
        );
    }

    const hasMentions = mentionedPersons.length > 0 || mentionedPlaces.length > 0 || mentionedEvents.length > 0;

    return (
        <div className="min-h-screen bg-gray-50 flex">
            {/* Main Content */}
            <div className="flex-1 p-6">
                <div className="max-w-3xl mx-auto space-y-6">
                    {/* Header */}
                    <div className="flex items-center justify-between">
                        <div className="flex items-center gap-3">
                            <Button variant="secondary" onClick={() => navigate('/notes')}>
                                <ArrowLeft className="w-4 h-4" />
                                Back
                            </Button>
                            <h1 className="text-3xl font-bold text-gray-900">
                                {note_id ? 'Edit Note' : 'New Note'}
                            </h1>
                        </div>
                        <div className="flex gap-2">
                            {note_id && (
                                <Button
                                    variant="secondary"
                                    onClick={() => setIsPinned(!isPinned)}
                                    title={isPinned ? 'Unpin' : 'Pin'}
                                >
                                    {isPinned ? <PinOff className="w-4 h-4" /> : <Pin className="w-4 h-4" />}
                                </Button>
                            )}
                            <Button onClick={handleSave} isLoading={saving}>
                                <Save className="w-4 h-4" />
                                Save
                            </Button>
                            {note_id && (
                                <Button variant="danger" onClick={handleDelete}>
                                    <Trash2 className="w-4 h-4" />
                                    Delete
                                </Button>
                            )}
                        </div>
                    </div>

                    {/* Note Card */}
                    <Card>
                        <div className="space-y-4 pt-6 px-6 pb-6">
                            {/* Title */}
                            <InputField
                                label="Title"
                                placeholder="Note title..."
                                value={title}
                                onChange={setTitle}
                            />

                            {/* Content Editor */}
                            <div>
                                <label className="block text-sm font-medium text-gray-700 mb-2">
                                    Content
                                </label>
                                <SmartNoteEditor
                                    value={content}
                                    onChange={setContent}
                                    suggestions={suggestions}
                                    placeholder="Write your note here... Use @p for persons, @pl for places, @e for events"
                                />
                                <p className="text-xs text-gray-500 mt-2">
                                    💡 Tip: Type @p followed by a space to mention a person, @pl for places, @e for events
                                </p>
                            </div>

                            {/* Meta Info */}
                            <div className="pt-4 border-t border-gray-200 text-xs text-gray-500">
                                {note && (
                                    <>
                                        <div>Created: {new Date(note.created_at).toLocaleString()}</div>
                                        <div>Modified: {new Date(note.updated_at).toLocaleString()}</div>
                                    </>
                                )}
                            </div>
                        </div>
                    </Card>
                </div>
            </div>

            {/* Sidebar - Mentioned Entities */}
            {hasMentions && (
                <div className="w-80 border-l border-gray-200 bg-white p-6 overflow-y-auto">
                    <div className="space-y-6">
                        <h3 className="text-lg font-semibold text-gray-900 mb-4">Mentioned Entities</h3>

                        {/* Persons */}
                        {mentionedPersons.length > 0 && (
                            <div>
                                <h4 className="text-sm font-semibold text-blue-600 mb-3 flex items-center gap-2">
                                    <User className="w-4 h-4" />
                                    Persons ({mentionedPersons.length})
                                </h4>
                                <div className="space-y-2">
                                    {mentionedPersons.map(person => {
                                        const exists = person.id !== undefined;
                                        return exists ? (
                                            <button
                                                key={person.slug}
                                                onClick={() => navigate(`/persons/${person.slug}`)}
                                                className="w-full text-left p-3 rounded-lg bg-blue-50 hover:bg-blue-100 transition border border-blue-200"
                                            >
                                                <div className="font-medium text-sm text-blue-900">
                                                    {person.name || person.slug}
                                                </div>
                                                <div className="text-xs text-blue-700 mt-1">View person →</div>
                                            </button>
                                        ) : (
                                            <div
                                                key={person.slug}
                                                className="w-full text-left p-3 rounded-lg bg-blue-50 border border-blue-200 opacity-60"
                                            >
                                                <div className="font-medium text-sm text-blue-900">
                                                    {person.name || person.slug}
                                                </div>
                                                <div className="text-xs text-blue-500 mt-1">New (not saved yet)</div>
                                            </div>
                                        );
                                    })}
                                </div>
                            </div>
                        )}

                        {/* Places */}
                        {mentionedPlaces.length > 0 && (
                            <div>
                                <h4 className="text-sm font-semibold text-green-600 mb-3 flex items-center gap-2">
                                    <MapPin className="w-4 h-4" />
                                    Places ({mentionedPlaces.length})
                                </h4>
                                <div className="space-y-2">
                                    {mentionedPlaces.map(place => {
                                        const exists = place.id !== undefined;
                                        return exists ? (
                                            <button
                                                key={place.slug}
                                                onClick={() => navigate(`/places/${place.slug}`)}
                                                className="w-full text-left p-3 rounded-lg bg-green-50 hover:bg-green-100 transition border border-green-200"
                                            >
                                                <div className="font-medium text-sm text-green-900">
                                                    {place.name || place.slug}
                                                </div>
                                                <div className="text-xs text-green-700 mt-1">View place →</div>
                                            </button>
                                        ) : (
                                            <div
                                                key={place.slug}
                                                className="w-full text-left p-3 rounded-lg bg-green-50 border border-green-200 opacity-60"
                                            >
                                                <div className="font-medium text-sm text-green-900">
                                                    {place.name || place.slug}
                                                </div>
                                                <div className="text-xs text-green-500 mt-1">New (not saved yet)</div>
                                            </div>
                                        );
                                    })}
                                </div>
                            </div>
                        )}

                        {/* Events */}
                        {mentionedEvents.length > 0 && (
                            <div>
                                <h4 className="text-sm font-semibold text-purple-600 mb-3 flex items-center gap-2">
                                    <Calendar className="w-4 h-4" />
                                    Events ({mentionedEvents.length})
                                </h4>
                                <div className="space-y-2">
                                    {mentionedEvents.map(event => {
                                        const exists = event.id !== undefined;
                                        return exists ? (
                                            <button
                                                key={event.slug}
                                                onClick={() => navigate(`/events/${event.slug}`)}
                                                className="w-full text-left p-3 rounded-lg bg-purple-50 hover:bg-purple-100 transition border border-purple-200"
                                            >
                                                <div className="font-medium text-sm text-purple-900">
                                                    {event.name || event.slug}
                                                </div>
                                                <div className="text-xs text-purple-700 mt-1">View event →</div>
                                            </button>
                                        ) : (
                                            <div
                                                key={event.slug}
                                                className="w-full text-left p-3 rounded-lg bg-purple-50 border border-purple-200 opacity-60"
                                            >
                                                <div className="font-medium text-sm text-purple-900">
                                                    {event.name || event.slug}
                                                </div>
                                                <div className="text-xs text-purple-500 mt-1">New (not saved yet)</div>
                                            </div>
                                        );
                                    })}
                                </div>
                            </div>
                        )}
                    </div>
                </div>
            )}

            {/* Empty Sidebar State */}
            {!hasMentions && (
                <div className="w-80 border-l border-gray-200 bg-gradient-to-b from-gray-50 to-gray-100 p-6 flex flex-col items-center justify-center text-center">
                    <div className="text-gray-400 mb-3">
                        <Plus className="w-12 h-12 mx-auto" />
                    </div>
                    <h4 className="font-semibold text-gray-700 mb-2">No Mentions Yet</h4>
                    <p className="text-sm text-gray-500">
                        Mention persons, places, or events in your note to see them here
                    </p>
                </div>
            )}
        </div>
    );
};

export default NotePage;
