import { useState, useEffect } from 'react';
import { Trash2, RotateCcw } from 'lucide-react';
import { Card, CardContent, CardHeader } from '../components/ui/Card';
import { Button } from '../components/ui/Button';

export const BinPage = () => {
  const [deleted, setDeleted] = useState<any[]>([]);
  const [loading, setLoading] = useState(true);

  useEffect(() => {
    // TODO: Fetch deleted items from backend
    setLoading(false);
  }, []);

  const handleRestore = async (id: number) => {
    // TODO: Implement restore functionality
    console.log('Restore item', id);
  };

  const handlePermanentlyDelete = async (id: number) => {
    if (confirm('Are you sure? This cannot be undone.')) {
      // TODO: Implement permanent delete
      setDeleted(deleted.filter(d => d.id !== id));
    }
  };

  return (
    <div className="min-h-screen bg-gray-50">
      {/* Header */}
      <div className="bg-white border-b border-gray-200 sticky top-0 z-40">
        <div className="max-w-7xl mx-auto px-4 sm:px-6 lg:px-8 py-3">
          <h1 className="text-2xl font-600 text-gray-900 flex items-center gap-2">
            <Trash2 className="w-5 h-5" />
            Bin
          </h1>
          <p className="text-xs text-gray-500 mt-1">Permanently deleted items (30-day retention)</p>
        </div>
      </div>

      {/* Content */}
      <div className="max-w-7xl mx-auto px-4 sm:px-6 lg:px-8 py-6">
        {loading ? (
          <div className="flex items-center justify-center h-96">
            <div className="text-center">
              <div className="w-10 h-10 border-4 border-blue-500 border-t-transparent rounded-full animate-spin mx-auto mb-3" />
              <p className="text-xs text-gray-600">Loading deleted items...</p>
            </div>
          </div>
        ) : deleted.length === 0 ? (
          <div className="text-center py-12">
            <Trash2 className="w-12 h-12 text-gray-300 mx-auto mb-3" />
            <p className="text-sm text-gray-500">Bin is empty</p>
          </div>
        ) : (
          <div className="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-3 gap-3">
            {deleted.map(item => (
              <Card key={item.id}>
                <CardHeader>
                  <h3 className="text-sm font-600 text-gray-900">{item.title}</h3>
                  <p className="text-xs text-gray-500 mt-1">Deleted {new Date(item.deleted_at).toLocaleDateString()}</p>
                </CardHeader>
                <CardContent>
                  <p className="text-xs text-gray-600 line-clamp-2 mb-3">{item.content}</p>
                  <div className="flex gap-2">
                    <Button
                      size="xs"
                      variant="secondary"
                      onClick={() => handleRestore(item.id)}
                      className="flex-1"
                    >
                      <RotateCcw className="w-3 h-3" />
                      Restore
                    </Button>
                    <Button
                      size="xs"
                      variant="danger"
                      onClick={() => handlePermanentlyDelete(item.id)}
                      className="flex-1"
                    >
                      Delete
                    </Button>
                  </div>
                </CardContent>
              </Card>
            ))}
          </div>
        )}
      </div>
    </div>
  );
};

export default BinPage;
