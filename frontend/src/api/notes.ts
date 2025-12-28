import api from './api';

export interface Mention {
  slug: string;
  type: string;
  new: boolean;
}

export interface AllMentions {
  persons: Mention[];
  places: Mention[];
  events: Mention[];
}

export interface Note {
  id: number;
  title?: string;
  content?: string;
  mentions: AllMentions;
  is_pinned: boolean;
  created_at: string;
  updated_at: string;
}

export interface NoteCreate {
  title?: string;
  content?: string;
  is_pinned?: boolean;
}

export const getNotes = async (skip = 0, limit = 100) => {
  return api.get<Note[]>('/note', {
    params: { skip, limit }
  });
};

export const getNote = async (noteId: number) => {
  return api.get<Note>(`/note/${noteId}`);
};

export const createNote = async (data: NoteCreate) => {
  return api.post<Note>('/note', data);
};

export const updateNote = async (noteId: number, data: NoteCreate) => {
  return api.put<Note>(`/note/${noteId}`, data);
};

export const deleteNote = async (noteId: number) => {
  return api.delete(`/note/${noteId}`);
};
