import api from './api';

export interface Event {
  id: number;
  title: string;
  slug: string;
  description?: string;
  start_datetime: string;
  end_datetime?: string;
  location?: string;
  place_id?: number;
  created_at: string;
  updated_at: string;
}

export interface EventCreate {
  title: string;
  slug?: string;
  description?: string;
  start_datetime: string;
  end_datetime?: string;
  location?: string;
  place_id?: number;
}

export const getEvents = async (skip = 0, limit = 100) => {
  return api.get<Event[]>('/event', {
    params: { skip, limit }
  });
};

export const getEvent = async (eventSlug: string) => {
  return api.get<Event>(`/event/${eventSlug}`);
};

export const createEvent = async (data: EventCreate) => {
  return api.post<Event>('/event', data);
};

export const updateEvent = async (eventId: number, data: EventCreate) => {
  return api.put<Event>(`/event/${eventId}`, data);
};

export const deleteEvent = async (eventId: number) => {
  return api.delete(`/event/${eventId}`);
};

export const getEventNotes = async (eventId: number) => {
  return api.get(`/event/${eventId}/notes`);
};
