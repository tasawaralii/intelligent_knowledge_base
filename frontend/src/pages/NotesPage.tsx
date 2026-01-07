import { useState, useEffect } from 'react';
import { Plus, Search, Grid, List } from 'lucide-react';
import { useNavigate } from 'react-router-dom';
import { NoteCard } from '../components/NoteCard';
import { Button } from '../components/ui/Button';
import { getNotes, updateNote, deleteNote, type Note } from '../api/notes';
import { getPersons } from '../api/persons';
import { getPlaces } from '../api/places';
import { getEvents } from '../api/events';

type ViewMode = 'grid' | 'list';

export const NotesPage = () => {
  const navigate = useNavigate();
  const [notes, setNotes] = useState<Note[]>([]);
  const [filteredNotes, setFilteredNotes] = useState<Note[]>([]);
  const [loading, setLoading] = useState(true);
  const [viewMode, setViewMode] = useState<ViewMode>('grid');
  const [searchQuery, setSearchQuery] = useState('');
  const [filterTag, setFilterTag] = useState('');

  // Fetch all data
  useEffect(() => {
    const fetchData = async () => {
      try {
        setLoading(true);
        const [notesRes] = await Promise.all([
          getNotes(0, 100),
        ]);

        setNotes(notesRes.data);
      } catch (error) {
        console.error('Failed to fetch data:', error);
      } finally {
        setLoading(false);
      }
    };

    fetchData();
  }, []);

  // Filter notes based on search and tag
  useEffect(() => {
    let filtered = notes;

    if (searchQuery) {
      const query = searchQuery.toLowerCase();
      filtered = filtered.filter(note =>
        (note.title?.toLowerCase().includes(query) || '') ||
        (note.content?.toLowerCase().includes(query) || '')
      );
    }

    if (filterTag) {
      filtered = filtered.filter(note => {
        const mentions = note.mentions;
        return (
          mentions.persons?.some(p => p.slug === filterTag) ||
          mentions.places?.some(p => p.slug === filterTag) ||
          mentions.events?.some(e => e.slug === filterTag)
        );
      });
    }

    // Sort: pinned first, then by most recent
    filtered.sort((a, b) => {
      if (a.is_pinned !== b.is_pinned) {
        return a.is_pinned ? -1 : 1;
      }
      return new Date(b.updated_at).getTime() - new Date(a.updated_at).getTime();
    });

    setFilteredNotes(filtered);
  }, [notes, searchQuery, filterTag]);

  const handleDeleteNote = async (noteId: number) => {
    if (confirm('Are you sure you want to delete this note?')) {
      try {
        await deleteNote(noteId);
        setNotes(notes.filter(n => n.id !== noteId));
      } catch (error) {
        console.error('Failed to delete note:', error);
      }
    }
  };

  const handlePinNote = async (noteId: number, isPinned: boolean) => {
    try {
      const note = notes.find(n => n.id === noteId);
      if (note) {
        const updated = await updateNote(noteId, {
          title: note.title,
          content: note.content,
          is_pinned: isPinned
        });
        setNotes(notes.map(n => n.id === noteId ? updated.data : n));
      }
    } catch (error) {
      console.error('Failed to pin note:', error);
    }
  };

  const handleEditNote = (note: Note) => {
    navigate(`/notes/${note.id}`);
  };

  if (loading) {
    return (
      <div className="flex items-center justify-center h-screen">
        <div className="text-center">
          <div className="w-12 h-12 border-4 border-blue-500 border-t-transparent rounded-full animate-spin mx-auto mb-4" />
          <p className="text-gray-600">Loading your notes...</p>
        </div>
      </div>
    );
  }

  return (
    <div className="min-h-screen bg-gray-50">
      {/* Header */}
      <div className="bg-white border-b border-gray-200 sticky top-0 z-40">
        <div className="max-w-7xl mx-auto px-4 sm:px-6 lg:px-8 py-3">
          <div className="flex items-center justify-between mb-4">
            <h1 className="text-2xl font-600 text-gray-900">Notes</h1>
            <Button onClick={() => navigate('/notes/new')} size="sm">
              <Plus className="w-4 h-4" />
              New Note
            </Button>
          </div>

          {/* Search and Controls */}
          <div className="space-y-3">
            <div className="flex gap-3 items-center flex-wrap">
              <div className="flex-1 min-w-48 relative">
                <Search className="absolute left-3 top-1/2 -translate-y-1/2 w-4 h-4 text-gray-400" />
                <input
                  type="text"
                  placeholder="Search notes..."
                  value={searchQuery}
                  onChange={(e) => setSearchQuery(e.target.value)}
                  className="w-full pl-9 pr-3 py-1.5 text-sm border border-gray-300 rounded-md focus:outline-none focus:ring-2 focus:ring-blue-500"
                />
              </div>

              {/* View Toggle */}
              <div className="flex border border-gray-300 rounded-md">
                <button
                  onClick={() => setViewMode('grid')}
                  className={`p-1.5 ${viewMode === 'grid' ? 'bg-blue-600 text-white' : 'bg-white text-gray-600'}`}
                  title="Grid view"
                >
                  <Grid className="w-4 h-4" />
                </button>
                <button
                  onClick={() => setViewMode('list')}
                  className={`p-1.5 ${viewMode === 'list' ? 'bg-blue-600 text-white' : 'bg-white text-gray-600'}`}
                  title="List view"
                >
                  <List className="w-4 h-4" />
                </button>
              </div>
            </div>

            {/* Stats */}
            <div className="text-xs text-gray-500">
              {filteredNotes.length} of {notes.length} notes
            </div>
          </div>
        </div>
      </div>

      {/* Content */}
      <div className="max-w-7xl mx-auto px-4 sm:px-6 lg:px-8 py-6">
        {filteredNotes.length === 0 ? (
          <div className="text-center py-12">
            <p className="text-sm text-gray-500 mb-3">No notes yet. Start creating!</p>
            <Button onClick={() => navigate('/notes/new')}>
              <Plus className="w-4 h-4" />
              Create Your First Note
            </Button>
          </div>
        ) : (
          <div
            className={viewMode === 'grid'
              ? 'grid grid-cols-1 md:grid-cols-2 lg:grid-cols-3 gap-3'
              : 'space-y-2'
            }
          >
            {filteredNotes.map(note => (
              <NoteCard
                key={note.id}
                note={note}
                onEdit={handleEditNote}
                onDelete={handleDeleteNote}
                onPin={handlePinNote}
              />
            ))}
          </div>
        )}
      </div>
    </div>
  );
};

export default NotesPage;
