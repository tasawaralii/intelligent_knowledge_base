import { Card, CardContent, CardFooter, CardHeader } from './ui/Card';
import { formatDistanceToNow } from 'date-fns';
import { Pin, PinOff, Trash2, Edit } from 'lucide-react';

interface Note {
  id: number;
  title?: string;
  content?: string;
  mentions: {
    persons: any[];
    places: any[];
    events: any[];
  };
  is_pinned: boolean;
  created_at: string;
  updated_at: string;
}

interface NoteCardProps {
  note: Note;
  onEdit?: (note: Note) => void;
  onDelete?: (noteId: number) => void;
  onPin?: (noteId: number, isPinned: boolean) => void;
}

export const NoteCard = ({
  note,
  onEdit,
  onDelete,
  onPin
}: NoteCardProps) => {
  const mentionCount = (note.mentions?.persons?.length || 0) +
                      (note.mentions?.places?.length || 0) +
                      (note.mentions?.events?.length || 0);

  const truncateContent = (content: string, maxLength: number = 150) => {
    return content.length > maxLength ? content.substring(0, maxLength) + '...' : content;
  };

  return (
    <Card className={`hover:shadow-lg transition-shadow ${note.is_pinned ? 'border-yellow-300' : ''}`}>
      <CardHeader className="pb-3">
        <div className="flex items-start justify-between gap-2">
          <div className="flex-1">
            {note.title && (
              <h3 className="font-semibold text-gray-900 line-clamp-2">{note.title}</h3>
            )}
            <p className="text-xs text-gray-500 mt-1">
              {formatDistanceToNow(new Date(note.updated_at), { addSuffix: true })}
            </p>
          </div>
          {note.is_pinned && (
            <Pin className="w-4 h-4 text-yellow-500 flex-shrink-0" />
          )}
        </div>
      </CardHeader>

      {note.content && (
        <CardContent>
          <p className="text-sm text-gray-700 line-clamp-3">
            {truncateContent(note.content)}
          </p>
        </CardContent>
      )}

      {mentionCount > 0 && (
        <CardContent className="pt-2">
          <div className="flex flex-wrap gap-1">
            {note.mentions?.persons?.slice(0, 3).map((person, idx) => (
              <span
                key={`p-${idx}`}
                className="inline-block bg-blue-100 text-blue-700 text-xs px-2 py-1 rounded"
              >
                @p.{person.slug}
              </span>
            ))}
            {note.mentions?.places?.slice(0, 3).map((place, idx) => (
              <span
                key={`pl-${idx}`}
                className="inline-block bg-green-100 text-green-700 text-xs px-2 py-1 rounded"
              >
                @pl.{place.slug}
              </span>
            ))}
            {note.mentions?.events?.slice(0, 3).map((event, idx) => (
              <span
                key={`e-${idx}`}
                className="inline-block bg-purple-100 text-purple-700 text-xs px-2 py-1 rounded"
              >
                @e.{event.slug}
              </span>
            ))}
            {mentionCount > 3 && (
              <span className="text-xs text-gray-500">
                +{mentionCount - 3} more
              </span>
            )}
          </div>
        </CardContent>
      )}

      <CardFooter className="pt-3">
        <div className="flex gap-2 ml-auto">
          {onPin && (
            <button
              onClick={() => onPin(note.id, !note.is_pinned)}
              className="p-1.5 hover:bg-gray-100 rounded transition-colors"
              title={note.is_pinned ? 'Unpin note' : 'Pin note'}
            >
              {note.is_pinned ? (
                <PinOff className="w-4 h-4 text-gray-600" />
              ) : (
                <Pin className="w-4 h-4 text-gray-400" />
              )}
            </button>
          )}
          {onEdit && (
            <button
              onClick={() => onEdit(note)}
              className="p-1.5 hover:bg-gray-100 rounded transition-colors"
              title="Edit note"
            >
              <Edit className="w-4 h-4 text-gray-600" />
            </button>
          )}
          {onDelete && (
            <button
              onClick={() => onDelete(note.id)}
              className="p-1.5 hover:bg-red-50 rounded transition-colors"
              title="Delete note"
            >
              <Trash2 className="w-4 h-4 text-red-600" />
            </button>
          )}
        </div>
      </CardFooter>
    </Card>
  );
};
