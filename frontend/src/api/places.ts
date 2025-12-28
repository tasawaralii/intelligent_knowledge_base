import api from './api';

export interface Place {
  id: number;
  name: string;
  slug?: string;
  place_type?: string;
  address?: string;
  city?: string;
  country?: string;
  description?: string;
  created_at: string;
  updated_at: string;
}

export interface PlaceCreate {
  name: string;
  slug?: string;
  place_type?: string;
  address?: string;
  city?: string;
  country?: string;
  description?: string;
}

export const getPlaces = async (skip = 0, limit = 100) => {
  return api.get<Place[]>('/place', {
    params: { skip, limit }
  });
};

export const getPlace = async (placeId: number) => {
  return api.get<Place>(`/place/${placeId}`);
};

export const createPlace = async (data: PlaceCreate) => {
  return api.post<Place>('/place', data);
};

export const updatePlace = async (placeId: number, data: PlaceCreate) => {
  return api.put<Place>(`/place/${placeId}`, data);
};

export const deletePlace = async (placeId: number) => {
  return api.delete(`/place/${placeId}`);
};

export const getPlaceNotes = async (placeId: number) => {
  return api.get(`/place/${placeId}/notes`);
};
