import { useState, useEffect } from 'react';
import { Lightbulb, Plus, Trash2, ArrowRight, User, MapPin, Calendar } from 'lucide-react';
import { Card, CardContent } from '../components/ui/Card';
import { Button } from '../components/ui/Button';
import { Dialog } from '../components/ui/Dialog';
import { SelectField } from '../components/FormFields';
import api from '../api/api';
import { useAlert } from '../context/alertContext';

// Types
interface Fact {
  id: number;
  source_type: string;
  source_id: number;
  target_type: string;
  target_id: number;
  relation_type: string;
  confidence_score: number;
  description?: string;
  created_at: string;
  updated_at: string;
}

interface Entity {
  id: number;
  name: string;
  slug: string;
}

interface Person extends Entity {
  first_name: string;
  last_name?: string;
}

interface Place extends Entity {
  place_type?: string;
}

interface Event extends Entity {
  title: string;
  event_type?: string;
}

// Relation types available
const RELATION_TYPES = [
  { value: 'studies_at', label: 'Studies At' },
  { value: 'works_at', label: 'Works At' },
  { value: 'lives_at', label: 'Lives At' },
  { value: 'visits', label: 'Visits' },
  { value: 'owns', label: 'Owns' },
  { value: 'manages', label: 'Manages' },
  { value: 'attends', label: 'Attends' },
  { value: 'organizes', label: 'Organizes' },
  { value: 'participates', label: 'Participates' },
  { value: 'hosts', label: 'Hosts' },
  { value: 'knows', label: 'Knows' },
  { value: 'works_with', label: 'Works With' },
  { value: 'related_to', label: 'Related To' },
  { value: 'friend_of', label: 'Friend Of' },
  { value: 'colleague_of', label: 'Colleague Of' },
  { value: 'supervisor_of', label: 'Supervisor Of' },
  { value: 'subordinate_of', label: 'Subordinate Of' },
  { value: 'located_at', label: 'Located At' },
  { value: 'hosted_at', label: 'Hosted At' },
  { value: 'related', label: 'Related' },
];

const ENTITY_TYPES = [
  { value: 'person', label: 'Person', icon: User },
  { value: 'place', label: 'Place', icon: MapPin },
  { value: 'event', label: 'Event', icon: Calendar },
];

const getEntityIcon = (type: string) => {
  switch (type) {
    case 'person': return <User className="w-4 h-4" />;
    case 'place': return <MapPin className="w-4 h-4" />;
    case 'event': return <Calendar className="w-4 h-4" />;
    default: return null;
  }
};

const getEntityColor = (type: string) => {
  switch (type) {
    case 'person': return 'bg-blue-100 text-blue-700 border-blue-200';
    case 'place': return 'bg-green-100 text-green-700 border-green-200';
    case 'event': return 'bg-purple-100 text-purple-700 border-purple-200';
    default: return 'bg-gray-100 text-gray-700 border-gray-200';
  }
};

export const FactsPage = () => {
  const { addAlert } = useAlert();
  
  // Data states
  const [facts, setFacts] = useState<Fact[]>([]);
  const [persons, setPersons] = useState<Person[]>([]);
  const [places, setPlaces] = useState<Place[]>([]);
  const [events, setEvents] = useState<Event[]>([]);
  
  // Entity name lookup maps
  const [entityNames, setEntityNames] = useState<Record<string, string>>({});
  
  // UI states
  const [loading, setLoading] = useState(true);
  const [showDialog, setShowDialog] = useState(false);
  const [isSubmitting, setIsSubmitting] = useState(false);
  
  // Form states
  const [sourceType, setSourceType] = useState('person');
  const [sourceId, setSourceId] = useState('');
  const [relationType, setRelationType] = useState('knows');
  const [targetType, setTargetType] = useState('person');
  const [targetId, setTargetId] = useState('');
  const [description, setDescription] = useState('');

  // Load all data
  useEffect(() => {
    const fetchData = async () => {
      try {
        setLoading(true);
        
        // Fetch all entities and facts in parallel
        const [factsRes, personsRes, placesRes, eventsRes] = await Promise.all([
          api.get('/api/relations/facts'),
          api.get('/person/'),
          api.get('/place/'),
          api.get('/event/'),
        ]);
        
        setFacts(factsRes.data.facts || []);
        setPersons(personsRes.data || []);
        setPlaces(placesRes.data || []);
        setEvents(eventsRes.data || []);
        
        // Build entity name lookup
        const names: Record<string, string> = {};
        (personsRes.data || []).forEach((p: Person) => {
          names[`person:${p.id}`] = `${p.first_name} ${p.last_name || ''}`.trim();
        });
        (placesRes.data || []).forEach((p: Place) => {
          names[`place:${p.id}`] = p.name;
        });
        (eventsRes.data || []).forEach((e: Event) => {
          names[`event:${e.id}`] = e.title;
        });
        setEntityNames(names);
        
      } catch (error: any) {
        console.error('Failed to fetch data:', error);
        addAlert('Failed to load facts', 'error', 3000);
      } finally {
        setLoading(false);
      }
    };

    fetchData();
  }, []);

  // Get entity name from lookup
  const getEntityName = (type: string, id: number): string => {
    return entityNames[`${type}:${id}`] || `Unknown ${type}`;
  };

  // Get entities list based on type
  const getEntitiesForType = (type: string) => {
    switch (type) {
      case 'person':
        return persons.map(p => ({
          value: p.id.toString(),
          label: `${p.first_name} ${p.last_name || ''}`.trim()
        }));
      case 'place':
        return places.map(p => ({
          value: p.id.toString(),
          label: p.name
        }));
      case 'event':
        return events.map(e => ({
          value: e.id.toString(),
          label: e.title
        }));
      default:
        return [];
    }
  };

  // Reset form
  const resetForm = () => {
    setSourceType('person');
    setSourceId('');
    setRelationType('knows');
    setTargetType('person');
    setTargetId('');
    setDescription('');
  };

  // Create fact
  const handleCreateFact = async () => {
    if (!sourceId || !targetId) {
      addAlert('Please select both source and target entities', 'error', 3000);
      return;
    }

    try {
      setIsSubmitting(true);
      
      const factData = {
        source_type: sourceType,
        source_id: parseInt(sourceId),
        target_type: targetType,
        target_id: parseInt(targetId),
        relation_type: relationType,
        confidence_score: 5,
        description: description || `${getEntityName(sourceType, parseInt(sourceId))} ${relationType.replace('_', ' ')} ${getEntityName(targetType, parseInt(targetId))}`
      };
      
      const res = await api.post('/api/relations/facts', factData);
      
      setFacts([res.data, ...facts]);
      setShowDialog(false);
      resetForm();
      addAlert('Fact created successfully', 'success', 2000);
      
    } catch (error: any) {
      console.error('Failed to create fact:', error);
      addAlert(error?.response?.data?.detail || 'Failed to create fact', 'error', 3000);
    } finally {
      setIsSubmitting(false);
    }
  };

  // Delete fact
  const handleDeleteFact = async (factId: number) => {
    if (!confirm('Are you sure you want to delete this fact?')) return;
    
    try {
      await api.delete(`/api/relations/facts/${factId}`);
      setFacts(facts.filter(f => f.id !== factId));
      addAlert('Fact deleted', 'success', 2000);
    } catch (error: any) {
      console.error('Failed to delete fact:', error);
      addAlert(error?.response?.data?.detail || 'Failed to delete fact', 'error', 3000);
    }
  };

  // Format relation type for display
  const formatRelationType = (type: string) => {
    return type.split('_').map(word => 
      word.charAt(0).toUpperCase() + word.slice(1)
    ).join(' ');
  };

  return (
    <div className="min-h-screen bg-gray-50">
      {/* Header */}
      <div className="bg-white border-b border-gray-200 sticky top-0 z-40">
        <div className="max-w-7xl mx-auto px-4 sm:px-6 lg:px-8 py-3">
          <div className="flex items-center justify-between">
            <div>
              <h1 className="text-2xl font-600 text-gray-900 flex items-center gap-2">
                <Lightbulb className="w-5 h-5" />
                Facts
              </h1>
              <p className="text-xs text-gray-500 mt-1">
                {facts.length} fact{facts.length !== 1 ? 's' : ''} • Relationships between entities
              </p>
            </div>
            <Button onClick={() => setShowDialog(true)} size="sm">
              <Plus className="w-4 h-4" />
              Add Fact
            </Button>
          </div>
        </div>
      </div>

      {/* Content */}
      <div className="max-w-4xl mx-auto px-4 sm:px-6 lg:px-8 py-6">
        {loading ? (
          <div className="flex items-center justify-center h-96">
            <div className="text-center">
              <div className="w-10 h-10 border-4 border-blue-500 border-t-transparent rounded-full animate-spin mx-auto mb-3" />
              <p className="text-xs text-gray-600">Loading facts...</p>
            </div>
          </div>
        ) : facts.length === 0 ? (
          <div className="text-center py-12">
            <Lightbulb className="w-12 h-12 text-gray-300 mx-auto mb-3" />
            <p className="text-sm text-gray-500 mb-3">No facts yet</p>
            <p className="text-xs text-gray-400 mb-4">
              Facts represent relationships between persons, places, and events
            </p>
            <Button onClick={() => setShowDialog(true)}>
              <Plus className="w-4 h-4" />
              Create Your First Fact
            </Button>
          </div>
        ) : (
          <div className="space-y-3">
            {facts.map(fact => (
              <Card key={fact.id} className="hover:shadow-md transition-shadow">
                <CardContent className="py-4">
                  <div className="flex items-center justify-between">
                    {/* Fact visualization */}
                    <div className="flex items-center gap-3 flex-wrap">
                      {/* Source Entity */}
                      <div className={`flex items-center gap-2 px-3 py-2 rounded-lg border ${getEntityColor(fact.source_type)}`}>
                        {getEntityIcon(fact.source_type)}
                        <span className="font-medium text-sm">
                          {getEntityName(fact.source_type, fact.source_id)}
                        </span>
                      </div>
                      
                      {/* Relation */}
                      <div className="flex items-center gap-1 text-gray-500">
                        <ArrowRight className="w-4 h-4" />
                        <span className="text-xs font-medium bg-gray-100 px-2 py-1 rounded">
                          {formatRelationType(fact.relation_type)}
                        </span>
                        <ArrowRight className="w-4 h-4" />
                      </div>
                      
                      {/* Target Entity */}
                      <div className={`flex items-center gap-2 px-3 py-2 rounded-lg border ${getEntityColor(fact.target_type)}`}>
                        {getEntityIcon(fact.target_type)}
                        <span className="font-medium text-sm">
                          {getEntityName(fact.target_type, fact.target_id)}
                        </span>
                      </div>
                    </div>
                    
                    {/* Actions */}
                    <div className="flex items-center gap-2">
                      <span className="text-xs text-gray-400">
                        Confidence: {fact.confidence_score}
                      </span>
                      <Button
                        size="xs"
                        variant="danger"
                        onClick={() => handleDeleteFact(fact.id)}
                      >
                        <Trash2 className="w-3 h-3" />
                      </Button>
                    </div>
                  </div>
                  
                  {/* Description */}
                  {fact.description && (
                    <p className="text-xs text-gray-500 mt-2 pl-1">
                      {fact.description}
                    </p>
                  )}
                </CardContent>
              </Card>
            ))}
          </div>
        )}
      </div>

      {/* Add Fact Dialog */}
      <Dialog
        isOpen={showDialog}
        onClose={() => {
          setShowDialog(false);
          resetForm();
        }}
        title="Add New Fact"
        size="lg"
      >
        <div className="space-y-4">
          <p className="text-xs text-gray-500 mb-4">
            Create a relationship fact: Entity → Relation → Entity
          </p>
          
          {/* Source Entity */}
          <div className="p-4 bg-blue-50 rounded-lg space-y-3">
            <h4 className="text-sm font-medium text-blue-900">Source Entity</h4>
            <div className="grid grid-cols-2 gap-3">
              <SelectField
                label="Entity Type"
                value={sourceType}
                onChange={(value) => {
                  setSourceType(value);
                  setSourceId('');
                }}
                options={ENTITY_TYPES.map(t => ({ value: t.value, label: t.label }))}
              />
              <SelectField
                label="Select Entity"
                value={sourceId}
                onChange={(value) => setSourceId(value)}
                placeholder="-- Select --"
                options={getEntitiesForType(sourceType)}
              />
            </div>
          </div>
          
          {/* Relation Type */}
          <div className="p-4 bg-gray-50 rounded-lg">
            <SelectField
              label="Relation Type"
              value={relationType}
              onChange={(value) => setRelationType(value)}
              options={RELATION_TYPES}
            />
          </div>
          
          {/* Target Entity */}
          <div className="p-4 bg-green-50 rounded-lg space-y-3">
            <h4 className="text-sm font-medium text-green-900">Target Entity</h4>
            <div className="grid grid-cols-2 gap-3">
              <SelectField
                label="Entity Type"
                value={targetType}
                onChange={(value) => {
                  setTargetType(value);
                  setTargetId('');
                }}
                options={ENTITY_TYPES.map(t => ({ value: t.value, label: t.label }))}
              />
              <SelectField
                label="Select Entity"
                value={targetId}
                onChange={(value) => setTargetId(value)}
                placeholder="-- Select --"
                options={getEntitiesForType(targetType)}
              />
            </div>
          </div>
          
          {/* Description (optional) */}
          <div>
            <label className="block text-xs font-medium text-gray-700 mb-1">
              Description (optional)
            </label>
            <textarea
              value={description}
              onChange={(e) => setDescription(e.target.value)}
              placeholder="Add additional context..."
              rows={2}
              className="w-full px-3 py-2 text-sm border border-gray-300 rounded-md focus:outline-none focus:ring-2 focus:ring-blue-500 resize-none"
            />
          </div>
          
          {/* Preview */}
          {sourceId && targetId && (
            <div className="p-3 bg-yellow-50 rounded-lg border border-yellow-200">
              <p className="text-xs text-yellow-800 font-medium mb-1">Preview:</p>
              <p className="text-sm text-yellow-900">
                <strong>{getEntityName(sourceType, parseInt(sourceId))}</strong>
                {' '}{formatRelationType(relationType).toLowerCase()}{' '}
                <strong>{getEntityName(targetType, parseInt(targetId))}</strong>
              </p>
            </div>
          )}

          {/* Actions */}
          <div className="flex gap-2 justify-end pt-2 border-t border-gray-200">
            <Button
              variant="secondary"
              size="sm"
              onClick={() => {
                setShowDialog(false);
                resetForm();
              }}
            >
              Cancel
            </Button>
            <Button
              size="sm"
              onClick={handleCreateFact}
              isLoading={isSubmitting}
              disabled={!sourceId || !targetId}
            >
              Create Fact
            </Button>
          </div>
        </div>
      </Dialog>
    </div>
  );
};

export default FactsPage;
