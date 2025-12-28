import { useState, useEffect } from 'react';
import { X } from 'lucide-react';

interface InputFieldProps {
  label: string;
  placeholder?: string;
  value: string;
  onChange: (value: string) => void;
  type?: 'text' | 'email' | 'tel' | 'date' | 'url';
  required?: boolean;
  error?: string;
}

export const InputField = ({
  label,
  placeholder,
  value,
  onChange,
  type = 'text',
  required = false,
  error
}: InputFieldProps) => {
  return (
    <div className="space-y-1">
      <label className="block text-xs font-500 text-gray-700">
        {label}
        {required && <span className="text-red-500 ml-0.5">*</span>}
      </label>
      <input
        type={type}
        value={value}
        onChange={(e) => onChange(e.target.value)}
        placeholder={placeholder}
        className={`w-full px-3 py-1.5 text-sm border rounded-md focus:outline-none focus:ring-2 focus:ring-blue-500 focus:border-transparent transition-colors ${
          error ? 'border-red-500' : 'border-gray-300'
        }`}
      />
      {error && <p className="text-xs text-red-500">{error}</p>}
    </div>
  );
};

interface TextAreaProps {
  label: string;
  placeholder?: string;
  value: string;
  onChange: (value: string) => void;
  required?: boolean;
  error?: string;
  rows?: number;
}

export const TextArea = ({
  label,
  placeholder,
  value,
  onChange,
  required = false,
  error,
  rows = 4
}: TextAreaProps) => {
  return (
    <div className="space-y-1">
      <label className="block text-xs font-500 text-gray-700">
        {label}
        {required && <span className="text-red-500 ml-0.5">*</span>}
      </label>
      <textarea
        value={value}
        onChange={(e) => onChange(e.target.value)}
        placeholder={placeholder}
        rows={rows}
        className={`w-full px-3 py-1.5 text-sm border rounded-md focus:outline-none focus:ring-2 focus:ring-blue-500 focus:border-transparent transition-colors resize-none ${
          error ? 'border-red-500' : 'border-gray-300'
        }`}
      />
      {error && <p className="text-xs text-red-500">{error}</p>}
    </div>
  );
};

interface SelectFieldProps {
  label: string;
  placeholder?: string;
  value: string;
  onChange: (value: string) => void;
  options: { value: string; label: string }[];
  required?: boolean;
  error?: string;
}

export const SelectField = ({
  label,
  placeholder,
  value,
  onChange,
  options,
  required = false,
  error
}: SelectFieldProps) => {
  return (
    <div className="space-y-1">
      <label className="block text-xs font-500 text-gray-700">
        {label}
        {required && <span className="text-red-500 ml-0.5">*</span>}
      </label>
      <select
        value={value}
        onChange={(e) => onChange(e.target.value)}
        className={`w-full px-3 py-1.5 text-sm border rounded-md focus:outline-none focus:ring-2 focus:ring-blue-500 focus:border-transparent transition-colors ${
          error ? 'border-red-500' : 'border-gray-300'
        }`}
      >
        {placeholder && <option value="">{placeholder}</option>}
        {options.map((option) => (
          <option key={option.value} value={option.value}>
            {option.label}
          </option>
        ))}
      </select>
      {error && <p className="text-xs text-red-500">{error}</p>}
    </div>
  );
};

interface TagInputProps {
  label: string;
  placeholder?: string;
  tags: string[];
  onTagsChange: (tags: string[]) => void;
  error?: string;
}

export const TagInput = ({
  label,
  placeholder,
  tags,
  onTagsChange,
  error
}: TagInputProps) => {
  const [inputValue, setInputValue] = useState('');

  const handleAddTag = () => {
    if (inputValue.trim() && !tags.includes(inputValue.trim())) {
      onTagsChange([...tags, inputValue.trim()]);
      setInputValue('');
    }
  };

  const handleRemoveTag = (tagToRemove: string) => {
    onTagsChange(tags.filter((tag) => tag !== tagToRemove));
  };

  const handleKeyPress = (e: React.KeyboardEvent<HTMLInputElement>) => {
    if (e.key === 'Enter') {
      e.preventDefault();
      handleAddTag();
    }
  };

  return (
    <div className="space-y-2">
      <label className="block text-sm font-medium text-gray-700">{label}</label>
      <div className="space-y-2">
        <div className="flex gap-2">
          <input
            type="text"
            value={inputValue}
            onChange={(e) => setInputValue(e.target.value)}
            onKeyPress={handleKeyPress}
            placeholder={placeholder}
            className={`flex-1 px-4 py-2 border rounded-lg focus:outline-none focus:ring-2 focus:ring-blue-500 focus:border-transparent transition-colors ${
              error ? 'border-red-500' : 'border-gray-300'
            }`}
          />
          <button
            type="button"
            onClick={handleAddTag}
            className="px-4 py-2 bg-blue-500 text-white rounded-lg hover:bg-blue-600 transition-colors"
          >
            Add
          </button>
        </div>
        {tags.length > 0 && (
          <div className="flex flex-wrap gap-2">
            {tags.map((tag) => (
              <span
                key={tag}
                className="inline-flex items-center gap-1 px-3 py-1 bg-blue-100 text-blue-700 rounded-full text-sm"
              >
                {tag}
                <button
                  type="button"
                  onClick={() => handleRemoveTag(tag)}
                  className="hover:text-blue-900"
                >
                  <X className="w-3 h-3" />
                </button>
              </span>
            ))}
          </div>
        )}
      </div>
      {error && <p className="text-sm text-red-500">{error}</p>}
    </div>
  );
};
