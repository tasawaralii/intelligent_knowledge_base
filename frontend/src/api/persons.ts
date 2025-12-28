import api from './api';

export interface Person {
  id: number;
  first_name: string;
  last_name?: string;
  father_name?: string;
  slug?: string;
  cnic?: string;
  phone_number?: string;
  email?: string;
  address?: string;
  city?: string;
  country?: string;
  date_of_birth?: string;
  gender?: string;
  picture_url?: string;
  created_at: string;
  updated_at: string;
}

export interface PersonCreate {
  first_name: string;
  last_name?: string;
  father_name?: string;
  slug?: string;
  cnic?: string;
  phone_number?: string;
  email?: string;
  address?: string;
  city?: string;
  country?: string;
  date_of_birth?: string;
  gender?: string;
  picture_url?: string;
}

export const getPersons = async (skip = 0, limit = 100) => {
  return api.get<Person[]>('/person', {
    params: { skip, limit }
  });
};

export const getPerson = async (personId: number) => {
  return api.get<Person>(`/person/${personId}`);
};

export const createPerson = async (data: PersonCreate) => {
  return api.post<Person>('/person', data);
};

export const updatePerson = async (personId: number, data: PersonCreate) => {
  return api.put<Person>(`/person/${personId}`, data);
};

export const deletePerson = async (personId: number) => {
  return api.delete(`/person/${personId}`);
};

export const getPersonNotes = async (personId: number) => {
  return api.get(`/person/${personId}/notes`);
};
