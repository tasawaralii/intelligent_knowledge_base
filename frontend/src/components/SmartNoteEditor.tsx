import { useState, useRef, useEffect } from 'react';
import { X } from 'lucide-react';

interface AutocompleteOption {
  id: string;
  name: string;
  type: 'person' | 'place' | 'event';
  description?: string;
}

interface SmartNoteEditorProps {
  value: string;
  onChange: (value: string) => void;
  onMentionDetected?: (mentions: any) => void;
  suggestions?: AutocompleteOption[];
  isLoading?: boolean;
  placeholder?: string;
}

export const SmartNoteEditor = ({
  value,
  onChange,
  onMentionDetected,
  suggestions = [],
  isLoading = false,
  placeholder = "Start typing... Use @p for persons, @pl for places, @e for events"
}: SmartNoteEditorProps) => {
  const [showSuggestions, setShowSuggestions] = useState(false);
  const [filteredSuggestions, setFilteredSuggestions] = useState<AutocompleteOption[]>([]);
  const [cursorPosition, setCursorPosition] = useState(0);
  const [currentMentionType, setCurrentMentionType] = useState<string | null>(null);
  const [searchTerm, setSearchTerm] = useState('');
  const [suggestionIndex, setSuggestionIndex] = useState(0);
  const textareaRef = useRef<HTMLTextAreaElement>(null);
  const suggestionBoxRef = useRef<HTMLDivElement>(null);

  useEffect(() => {
    // Detect mention trigger
    const text = value.substring(0, cursorPosition);
    const lastAtIndex = text.lastIndexOf('@');
    
    if (lastAtIndex !== -1) {
      const afterAt = text.substring(lastAtIndex + 1);
      
      // Check for mention types: @p (person), @pl (place), @e (event)
      if (afterAt.startsWith('p.') || afterAt.startsWith('p ')) {
        setCurrentMentionType('person');
        setSearchTerm(afterAt.substring(2).trim());
        const filtered = suggestions.filter(s => 
          s.type === 'person' && s.name.toLowerCase().includes(searchTerm.toLowerCase())
        );
        setFilteredSuggestions(filtered);
        setShowSuggestions(filtered.length > 0);
      } else if (afterAt.startsWith('pl.') || afterAt.startsWith('pl ')) {
        setCurrentMentionType('place');
        setSearchTerm(afterAt.substring(3).trim());
        const filtered = suggestions.filter(s => 
          s.type === 'place' && s.name.toLowerCase().includes(searchTerm.toLowerCase())
        );
        setFilteredSuggestions(filtered);
        setShowSuggestions(filtered.length > 0);
      } else if (afterAt.startsWith('e.') || afterAt.startsWith('e ')) {
        setCurrentMentionType('event');
        setSearchTerm(afterAt.substring(2).trim());
        const filtered = suggestions.filter(s => 
          s.type === 'event' && s.name.toLowerCase().includes(searchTerm.toLowerCase())
        );
        setFilteredSuggestions(filtered);
        setShowSuggestions(filtered.length > 0);
      } else if (afterAt === '' || afterAt.match(/^[a-z]*/i)) {
        setCurrentMentionType(null);
        setShowSuggestions(false);
      }
      setSuggestionIndex(0);
    } else {
      setShowSuggestions(false);
      setCurrentMentionType(null);
    }
  }, [cursorPosition, value, suggestions, searchTerm]);

  const handleSelectSuggestion = (option: AutocompleteOption) => {
    const text = value.substring(0, cursorPosition);
    const lastAtIndex = text.lastIndexOf('@');
    
    if (lastAtIndex !== -1) {
      const before = value.substring(0, lastAtIndex);
      const after = value.substring(cursorPosition);
      
      const mentionPrefix = currentMentionType === 'person' ? '@p.' : 
                           currentMentionType === 'place' ? '@pl.' : '@e.';
      const newValue = `${before}${mentionPrefix}${option.name}${after}`;
      
      onChange(newValue);
      setShowSuggestions(false);
      
      // Call the callback with detected mentions
      if (onMentionDetected) {
        const allMentions = extractMentions(newValue);
        onMentionDetected(allMentions);
      }
    }
  };

  const handleKeyDown = (e: React.KeyboardEvent<HTMLTextAreaElement>) => {
    if (!showSuggestions) return;

    switch (e.key) {
      case 'ArrowDown':
        e.preventDefault();
        setSuggestionIndex(prev => 
          (prev + 1) % filteredSuggestions.length
        );
        break;
      case 'ArrowUp':
        e.preventDefault();
        setSuggestionIndex(prev => 
          prev === 0 ? filteredSuggestions.length - 1 : prev - 1
        );
        break;
      case 'Enter':
        e.preventDefault();
        if (filteredSuggestions[suggestionIndex]) {
          handleSelectSuggestion(filteredSuggestions[suggestionIndex]);
        }
        break;
      case 'Escape':
        e.preventDefault();
        setShowSuggestions(false);
        break;
      default:
        break;
    }
  };

  const handleChange = (e: React.ChangeEvent<HTMLTextAreaElement>) => {
    onChange(e.target.value);
    setCursorPosition(e.target.selectionStart);
  };

  const handleClick = (e: React.MouseEvent<HTMLTextAreaElement>) => {
    setCursorPosition(e.currentTarget.selectionStart);
  };

  return (
    <div className="relative w-full">
      <textarea
        ref={textareaRef}
        value={value}
        onChange={handleChange}
        onClick={handleClick}
        onKeyDown={handleKeyDown}
        onKeyUp={() => setCursorPosition(textareaRef.current?.selectionStart || 0)}
        placeholder={placeholder}
        className="w-full h-40 p-4 border border-gray-300 rounded-lg focus:outline-none focus:ring-2 focus:ring-blue-500 focus:border-transparent resize-none font-sm text-gray-800"
      />

      {showSuggestions && filteredSuggestions.length > 0 && (
        <div
          ref={suggestionBoxRef}
          className="absolute top-full left-4 right-4 mt-2 bg-white border border-gray-200 rounded-lg shadow-lg z-10 max-h-48 overflow-y-auto"
        >
          {isLoading ? (
            <div className="p-3 text-gray-500 text-sm">Loading suggestions...</div>
          ) : (
            filteredSuggestions.map((option, index) => (
              <div
                key={option.id}
                onClick={() => handleSelectSuggestion(option)}
                className={`px-4 py-2.5 cursor-pointer border-b last:border-b-0 ${
                  index === suggestionIndex
                    ? 'bg-blue-100 text-blue-900'
                    : 'hover:bg-gray-100 text-gray-900'
                }`}
              >
                <div className="flex items-center gap-2">
                  <span className="text-xs px-2 py-1 rounded-full bg-gray-200 text-gray-700">
                    {option.type}
                  </span>
                  <span className="font-medium">{option.name}</span>
                </div>
                {option.description && (
                  <p className="text-xs text-gray-500 mt-1">{option.description}</p>
                )}
              </div>
            ))
          )}
        </div>
      )}

      {currentMentionType && !showSuggestions && filteredSuggestions.length === 0 && (
        <div className="absolute top-full left-4 right-4 mt-2 bg-white border border-gray-200 rounded-lg shadow-lg z-10 p-3">
          <p className="text-xs text-gray-500">
            No {currentMentionType}s found. Type to create a new one.
          </p>
        </div>
      )}
    </div>
  );
};

function extractMentions(content: string) {
  const mentions = {
    persons: [] as { slug: string; type: string; new: boolean }[],
    places: [] as { slug: string; type: string; new: boolean }[],
    events: [] as { slug: string; type: string; new: boolean }[]
  };

  const personMatches = content.matchAll(/@p\.(\w+)/g);
  const placeMatches = content.matchAll(/@pl\.(\w+)/g);
  const eventMatches = content.matchAll(/@e\.(\w+)/g);

  for (const match of personMatches) {
    mentions.persons.push({ slug: match[1], type: 'person', new: false });
  }
  for (const match of placeMatches) {
    mentions.places.push({ slug: match[1], type: 'place', new: false });
  }
  for (const match of eventMatches) {
    mentions.events.push({ slug: match[1], type: 'event', new: false });
  }

  return mentions;
}
