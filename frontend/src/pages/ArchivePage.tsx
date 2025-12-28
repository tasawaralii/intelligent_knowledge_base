import { useState, useEffect } from 'react';
import { Archive, Trash2 } from 'lucide-react';
import { Card, CardContent, CardHeader } from '../components/ui/Card';
import { Button } from '../components/ui/Button';

export const ArchivePage = () => {
  const [archived, setArchived] = useState<any[]>([]);
  const [loading, setLoading] = useState(true);

  useEffect(() => {
    // TODO: Fetch archived items from backend
    setLoading(false);
  }, []);

  return (
    <div className="min-h-screen bg-gray-50">
      {/* Header */}
      <div className="bg-white border-b border-gray-200 sticky top-0 z-40">
        <div className="max-w-7xl mx-auto px-4 sm:px-6 lg:px-8 py-3">
          <h1 className="text-2xl font-600 text-gray-900 flex items-center gap-2">
            <Archive className="w-5 h-5" />
            Archive
          </h1>
          <p className="text-xs text-gray-500 mt-1">View your archived notes and items</p>
        </div>
      </div>

      {/* Content */}
      <div className="max-w-7xl mx-auto px-4 sm:px-6 lg:px-8 py-6">
        {loading ? (
          <div className="flex items-center justify-center h-96">
            <div className="text-center">
              <div className="w-10 h-10 border-4 border-blue-500 border-t-transparent rounded-full animate-spin mx-auto mb-3" />
              <p className="text-xs text-gray-600">Loading archived items...</p>
            </div>
          </div>
        ) : archived.length === 0 ? (
          <div className="text-center py-12">
            <Archive className="w-12 h-12 text-gray-300 mx-auto mb-3" />
            <p className="text-sm text-gray-500">No archived items</p>
          </div>
        ) : (
          <div className="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-3 gap-3">
            {archived.map(item => (
              <Card key={item.id}>
                <CardHeader>
                  <h3 className="text-sm font-600 text-gray-900">{item.title}</h3>
                </CardHeader>
                <CardContent>
                  <p className="text-xs text-gray-600">{item.content}</p>
                </CardContent>
              </Card>
            ))}
          </div>
        )}
      </div>
    </div>
  );
};

export default ArchivePage;
