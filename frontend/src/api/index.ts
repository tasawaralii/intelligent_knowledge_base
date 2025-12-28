import api from './api';

// Export all API functions for easy importing
export * from './persons';
export * from './places';
export * from './events';
export * from './notes';

// Relations API
export const getRelationship = async (entity1Type: string, entity1Id: number, entity2Type: string, entity2Id: number, maxDepth?: number) => {
  const params = maxDepth ? { max_depth: maxDepth } : {};
  return api.get(
    `/api/relations/find-relation/${entity1Type}/${entity1Id}/${entity2Type}/${entity2Id}`,
    { params }
  );
};

export const getEntityNeighbors = async (entityType: string, entityId: number) => {
  return api.get(`/api/relations/neighbors/${entityType}/${entityId}`);
};

// Facts API (placeholders - implement when backend ready)
export const getFacts = async () => {
  // return api.get('/api/facts');
  return Promise.resolve({ data: [] });
};

export const createFact = async (content: string) => {
  // return api.post('/api/facts', { content });
  return Promise.resolve({ data: { id: 1, content, entities: [] } });
};

export const updateFact = async (factId: number, content: string) => {
  // return api.put(`/api/facts/${factId}`, { content });
  return Promise.resolve({ data: { id: factId, content, entities: [] } });
};

export const deleteFact = async (factId: number) => {
  // return api.delete(`/api/facts/${factId}`);
  return Promise.resolve({});
};

// Archive API (placeholders)
export const getArchived = async () => {
  // return api.get('/note/archive');
  return Promise.resolve({ data: [] });
};

export const archiveNote = async (noteId: number) => {
  // return api.post(`/note/${noteId}/archive`);
  return Promise.resolve({});
};

export const unarchiveNote = async (noteId: number) => {
  // return api.post(`/note/${noteId}/unarchive`);
  return Promise.resolve({});
};

// Bin API (placeholders)
export const getDeleted = async () => {
  // return api.get('/note/deleted');
  return Promise.resolve({ data: [] });
};

export const permanentlyDeleteNote = async (noteId: number) => {
  // return api.delete(`/note/${noteId}/permanent`);
  return Promise.resolve({});
};

export const restoreNote = async (noteId: number) => {
  // return api.post(`/note/${noteId}/restore`);
  return Promise.resolve({});
};
