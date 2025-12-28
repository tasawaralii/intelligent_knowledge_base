import { useState, useEffect } from 'react';
import { Lightbulb, Plus, Trash2, Edit } from 'lucide-react';
import { Card, CardContent, CardHeader } from '../components/ui/Card';
import { Button } from '../components/ui/Button';
import { Dialog } from '../components/ui/Dialog';
import { InputField } from '../components/FormFields';
import api from '../api/api';

interface Fact {
  id: number;
  content: string;
  entities: string[];
  created_at: string;
  updated_at: string;
}

export const FactsPage = () => {
  const [facts, setFacts] = useState<Fact[]>([]);
  const [loading, setLoading] = useState(true);
  const [showDialog, setShowDialog] = useState(false);
  const [editingFact, setEditingFact] = useState<Fact | null>(null);
  const [factContent, setFactContent] = useState('');
  const [isSubmitting, setIsSubmitting] = useState(false);

  useEffect(() => {
    const fetchFacts = async () => {
      try {
        setLoading(true);
        // TODO: Implement facts API endpoint
        // const res = await api.get('/api/facts');
        // setFacts(res.data);
        setFacts([]);
      } catch (error) {
        console.error('Failed to fetch facts:', error);
      } finally {
        setLoading(false);
      }
    };

    fetchFacts();
  }, []);

  const handleCreateFact = async () => {
    if (!factContent.trim()) return;

    try {
      setIsSubmitting(true);
      // TODO: Implement create fact API
      // const res = await api.post('/api/facts', { content: factContent });
      // setFacts([res.data, ...facts]);
      setShowDialog(false);
      setFactContent('');
    } catch (error) {
      console.error('Failed to create fact:', error);
    } finally {
      setIsSubmitting(false);
    }
  };

  const handleDeleteFact = async (factId: number) => {
    if (confirm('Are you sure?')) {
      try {
        // TODO: Implement delete fact API
        // await api.delete(`/api/facts/${factId}`);
        setFacts(facts.filter(f => f.id !== factId));
      } catch (error) {
        console.error('Failed to delete fact:', error);
      }
    }
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
              <p className="text-xs text-gray-500 mt-1">Extracted facts from your notes</p>
            </div>
            <Button onClick={() => {
              setEditingFact(null);
              setFactContent('');
              setShowDialog(true);
            }} size="sm">
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
            <Button onClick={() => setShowDialog(true)}>
              <Plus className="w-4 h-4" />
              Create Fact
            </Button>
          </div>
        ) : (
          <div className="space-y-3">
            {facts.map(fact => (
              <Card key={fact.id}>
                <CardHeader>
                  <p className="text-sm text-gray-900">{fact.content}</p>
                </CardHeader>
                <CardContent className="space-y-3">
                  {fact.entities.length > 0 && (
                    <div className="flex flex-wrap gap-1">
                      {fact.entities.map((entity, idx) => (
                        <span
                          key={idx}
                          className="text-xs px-2 py-1 bg-blue-100 text-blue-700 rounded"
                        >
                          {entity}
                        </span>
                      ))}
                    </div>
                  )}
                  <div className="flex gap-2 pt-2">
                    <Button
                      size="xs"
                      variant="ghost"
                      onClick={() => {
                        setEditingFact(fact);
                        setFactContent(fact.content);
                        setShowDialog(true);
                      }}
                      className="flex-1"
                    >
                      <Edit className="w-3 h-3" />
                      Edit
                    </Button>
                    <Button
                      size="xs"
                      variant="danger"
                      onClick={() => handleDeleteFact(fact.id)}
                      className="flex-1"
                    >
                      <Trash2 className="w-3 h-3" />
                      Delete
                    </Button>
                  </div>
                </CardContent>
              </Card>
            ))}
          </div>
        )}
      </div>

      {/* Dialog */}
      <Dialog
        isOpen={showDialog}
        onClose={() => {
          setShowDialog(false);
          setEditingFact(null);
        }}
        title={editingFact ? 'Edit Fact' : 'Add New Fact'}
        size="md"
      >
        <div className="space-y-3">
          <div>
            <label className="block text-xs font-medium text-gray-700 mb-1">
              Fact Content
            </label>
            <textarea
              value={factContent}
              onChange={(e) => setFactContent(e.target.value)}
              placeholder="Enter a fact..."
              rows={4}
              className="w-full px-3 py-2 text-sm border border-gray-300 rounded-md focus:outline-none focus:ring-2 focus:ring-blue-500 resize-none"
            />
          </div>

          <div className="flex gap-2 justify-end pt-2 border-t border-gray-200">
            <Button
              variant="secondary"
              size="sm"
              onClick={() => {
                setShowDialog(false);
                setEditingFact(null);
              }}
            >
              Cancel
            </Button>
            <Button
              size="sm"
              onClick={handleCreateFact}
              isLoading={isSubmitting}
            >
              {editingFact ? 'Update' : 'Add Fact'}
            </Button>
          </div>
        </div>
      </Dialog>
    </div>
  );
};

export default FactsPage;
