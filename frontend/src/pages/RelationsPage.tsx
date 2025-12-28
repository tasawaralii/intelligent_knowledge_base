import { useState, useEffect } from 'react';
import { Search, Link2, TrendingUp } from 'lucide-react';
import { Card, CardContent, CardHeader } from '../components/ui/Card';
import api from '../api/api';

interface PathHop {
  from_entity: string;
  to_entity: string;
  relation_type: string;
  confidence: number;
}

interface RelationPath {
  start_entity_name: string;
  end_entity_name: string;
  path_length: number;
  hops: PathHop[];
}

interface RelationshipAnalysis {
  entities: Array<{ type: string; id: number; name: string }>;
  are_directly_connected: boolean;
  shortest_path?: RelationPath;
  relation_summary: string;
  confidence_level: 'high' | 'medium' | 'low' | 'none';
  connection_strength: number;
}

export const RelationsPage = () => {
  const [loading, setLoading] = useState(false);
  const [entity1, setEntity1] = useState<string>('');
  const [entity2, setEntity2] = useState<string>('');
  const [results, setResults] = useState<RelationshipAnalysis | null>(null);
  const [entities, setEntities] = useState<any[]>([]);

  useEffect(() => {
    const fetchEntities = async () => {
      try {
        const [persons, places, events] = await Promise.all([
          api.get('/person'),
          api.get('/place'),
          api.get('/event')
        ]);

        const allEntities = [
          ...persons.data.map(p => ({
            id: p.id,
            name: `${p.first_name} ${p.last_name || ''}`.trim(),
            type: 'person'
          })),
          ...places.data.map(p => ({
            id: p.id,
            name: p.name,
            type: 'place'
          })),
          ...events.data.map(e => ({
            id: e.id,
            name: e.title,
            type: 'event'
          }))
        ];
        setEntities(allEntities);
      } catch (error) {
        console.error('Failed to fetch entities:', error);
      }
    };

    fetchEntities();
  }, []);

  const handleFindRelation = async () => {
    if (!entity1 || !entity2) return;

    try {
      setLoading(true);
      const ent1 = entities.find(e => `${e.name}(${e.type})` === entity1);
      const ent2 = entities.find(e => `${e.name}(${e.type})` === entity2);

      if (!ent1 || !ent2) return;

      const response = await api.get(
        `/api/relations/find-relation/${ent1.type}/${ent1.id}/${ent2.type}/${ent2.id}`
      );

      setResults(response.data);
    } catch (error) {
      console.error('Failed to find relation:', error);
    } finally {
      setLoading(false);
    }
  };

  const getConfidenceColor = (level: string) => {
    switch (level) {
      case 'high':
        return 'bg-green-100 text-green-700';
      case 'medium':
        return 'bg-yellow-100 text-yellow-700';
      case 'low':
        return 'bg-orange-100 text-orange-700';
      default:
        return 'bg-gray-100 text-gray-700';
    }
  };

  return (
    <div className="min-h-screen bg-gray-50">
      {/* Header */}
      <div className="bg-white border-b border-gray-200 sticky top-0 z-40">
        <div className="max-w-7xl mx-auto px-4 sm:px-6 lg:px-8 py-3">
          <h1 className="text-2xl font-600 text-gray-900 flex items-center gap-2">
            <Link2 className="w-5 h-5" />
            Relations
          </h1>
          <p className="text-xs text-gray-500 mt-1">Discover connections between your entities</p>
        </div>
      </div>

      {/* Content */}
      <div className="max-w-4xl mx-auto px-4 sm:px-6 lg:px-8 py-6">
        {/* Search Card */}
        <Card className="mb-6">
          <CardHeader>
            <h2 className="text-sm font-600 text-gray-900">Find Relations</h2>
          </CardHeader>
          <CardContent className="space-y-3">
            <div className="grid grid-cols-1 md:grid-cols-2 gap-3">
              <div>
                <label className="block text-xs font-medium text-gray-700 mb-1">
                  From Entity
                </label>
                <select
                  value={entity1}
                  onChange={(e) => setEntity1(e.target.value)}
                  className="w-full px-3 py-1.5 text-sm border border-gray-300 rounded-md focus:outline-none focus:ring-2 focus:ring-blue-500"
                >
                  <option value="">Select entity...</option>
                  {entities.map(e => (
                    <option key={`${e.type}-${e.id}`} value={`${e.name}(${e.type})`}>
                      {e.name} ({e.type})
                    </option>
                  ))}
                </select>
              </div>

              <div>
                <label className="block text-xs font-medium text-gray-700 mb-1">
                  To Entity
                </label>
                <select
                  value={entity2}
                  onChange={(e) => setEntity2(e.target.value)}
                  className="w-full px-3 py-1.5 text-sm border border-gray-300 rounded-md focus:outline-none focus:ring-2 focus:ring-blue-500"
                >
                  <option value="">Select entity...</option>
                  {entities.map(e => (
                    <option key={`${e.type}-${e.id}`} value={`${e.name}(${e.type})`}>
                      {e.name} ({e.type})
                    </option>
                  ))}
                </select>
              </div>
            </div>

            <button
              onClick={handleFindRelation}
              disabled={!entity1 || !entity2 || loading}
              className="w-full px-4 py-1.5 text-sm bg-blue-600 text-white rounded-md hover:bg-blue-700 disabled:opacity-50 transition-colors"
            >
              {loading ? 'Finding...' : 'Find Relation'}
            </button>
          </CardContent>
        </Card>

        {/* Results */}
        {results && (
          <div className="space-y-4">
            {/* Summary Card */}
            <Card>
              <CardHeader>
                <div className="flex items-start justify-between">
                  <div>
                    <h2 className="text-sm font-600 text-gray-900">Connection Found</h2>
                    <p className="text-xs text-gray-500 mt-1">{results.relation_summary}</p>
                  </div>
                  <span className={`text-xs px-2 py-1 rounded-full font-medium ${getConfidenceColor(results.confidence_level)}`}>
                    {results.confidence_level}
                  </span>
                </div>
              </CardHeader>
              <CardContent className="space-y-3">
                {/* Confidence Strength */}
                <div>
                  <div className="flex items-center justify-between text-xs mb-1">
                    <span className="font-medium text-gray-700">Connection Strength</span>
                    <span className="text-gray-600">{Math.round(results.connection_strength)}%</span>
                  </div>
                  <div className="w-full bg-gray-200 rounded-full h-2">
                    <div
                      className="bg-blue-600 h-2 rounded-full"
                      style={{ width: `${results.connection_strength}%` }}
                    />
                  </div>
                </div>

                {/* Direct Connection */}
                {results.are_directly_connected && (
                  <div className="p-2 bg-green-50 border border-green-200 rounded text-xs text-green-700">
                    ✓ Directly connected
                  </div>
                )}

                {/* Path */}
                {results.shortest_path && (
                  <div>
                    <p className="text-xs font-medium text-gray-700 mb-2">Path ({results.shortest_path.path_length} hops):</p>
                    <div className="space-y-1">
                      {results.shortest_path.hops.map((hop, idx) => (
                        <div key={idx} className="text-xs text-gray-600">
                          <span className="font-medium">{hop.from_entity}</span>
                          <span className="mx-1">→ ({hop.relation_type}) →</span>
                          <span className="font-medium">{hop.to_entity}</span>
                        </div>
                      ))}
                    </div>
                  </div>
                )}
              </CardContent>
            </Card>
          </div>
        )}

        {!results && !loading && (
          <div className="text-center py-12">
            <TrendingUp className="w-12 h-12 text-gray-300 mx-auto mb-3" />
            <p className="text-sm text-gray-500">Select two entities to discover their connections</p>
          </div>
        )}
      </div>
    </div>
  );
};

export default RelationsPage;
