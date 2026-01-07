import { useState, useRef, useEffect, useMemo } from 'react';
import { SuggestionIndex } from '../utils/suggestionSearch';

interface AutocompleteOption {
  id: string;
  name: string;
  type: 'person' | 'place' | 'event';
  slug: string;
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
  const [isNewMention, setIsNewMention] = useState(false);
  const [highlightIndex, setHighlightIndex] = useState(0);
  const textareaRef = useRef<HTMLTextAreaElement>(null);
  const suggestionBoxRef = useRef<HTMLDivElement>(null);

  const trie = useMemo(() => new SuggestionIndex(suggestions), [suggestions]);
  useEffect(() => {
    const textBeforeCursor = value.slice(0, cursorPosition);
    const lastAtIndex = textBeforeCursor.lastIndexOf('@');

    if (lastAtIndex === -1) {
      setShowSuggestions(false);
      setCurrentMentionType(null);
      return;
    }

    const afterAt = textBeforeCursor.slice(lastAtIndex + 1);

    const match = afterAt.match(/^(n\.)?(p|pl|e)\.([a-z0-9-]*)$/i);

    if (!match) {
      setShowSuggestions(false);
      setCurrentMentionType(null);
      setIsNewMention(false);
      return;
    }

    setIsNewMention(Boolean(match[1]));
    
    const entityCode = match[2];
    const search = match[3].toLowerCase();

    const type =
      entityCode === 'p'
        ? 'person'
        : entityCode === 'pl'
          ? 'place'
          : 'event';

    setCurrentMentionType(type);

    const filtered = trie.searchPrefix(search, type as 'person' | 'place' | 'event');

    setFilteredSuggestions(filtered);
    setShowSuggestions(filtered.length > 0);
    setHighlightIndex(0);
  }, [value, cursorPosition, trie]);  

  const handleSelectSuggestion = (option: AutocompleteOption) => {
    const textBeforeCursor = value.slice(0, cursorPosition);
    const lastAtIndex = textBeforeCursor.lastIndexOf('@');

    if (lastAtIndex === -1) return;

    const before = value.slice(0, lastAtIndex);
    const after = value.slice(cursorPosition);

    const prefix =
      `${isNewMention ? '@n.' : '@'}` +
      (currentMentionType === 'person'
        ? 'p.'
        : currentMentionType === 'place'
          ? 'pl.'
          : 'e.');

    const mentionText = `${prefix}${option.slug}`;
    const newValue = `${before}${mentionText}${after}`;

    onChange(newValue);
    setShowSuggestions(false);

    requestAnimationFrame(() => {
      textareaRef.current?.setSelectionRange(
        before.length + mentionText.length,
        before.length + mentionText.length
      );
    });

    onMentionDetected?.(extractMentions(newValue));
  };
  

  const handleKeyDown = (e: React.KeyboardEvent<HTMLTextAreaElement>) => {
    if (!showSuggestions) return;

    switch (e.key) {
      case 'ArrowDown':
        e.preventDefault();
        setHighlightIndex(prev => 
          (prev + 1) % filteredSuggestions.length
        );
        break;
      case 'ArrowUp':
        e.preventDefault();
        setHighlightIndex(prev => 
          prev === 0 ? filteredSuggestions.length - 1 : prev - 1
        );
        break;
      case 'Enter':
        e.preventDefault();
        if (filteredSuggestions[highlightIndex]) {
          handleSelectSuggestion(filteredSuggestions[highlightIndex]);
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
                  index === highlightIndex
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

  const regex = /@(?:(n)\.)?(p|pl|e)\.([a-z0-9-]+)/gi;

  for (const match of content.matchAll(regex)) {
    const isNew = Boolean(match[1]);
    const code = match[2];
    const slug = match[3];

    const entry = { slug, type: '', new: isNew };

    if (code === 'p') {
      entry.type = 'person';
      mentions.persons.push(entry);
    } else if (code === 'pl') {
      entry.type = 'place';
      mentions.places.push(entry);
    } else {
      entry.type = 'event';
      mentions.events.push(entry);
    }
  }

  return mentions;
} 