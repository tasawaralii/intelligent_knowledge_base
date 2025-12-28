import { useState, useEffect } from 'react';
import { Plus, Search, Trash2, Edit, MapPin } from 'lucide-react';
import { Dialog } from '../components/ui/Dialog';
import { Button } from '../components/ui/Button';
import { Card, CardContent, CardHeader } from '../components/ui/Card';
import { InputField } from '../components/FormFields';
import { getPlaces, createPlace, updatePlace, deletePlace,type Place, type PlaceCreate } from '../api/places';

export const PlacesPage = () => {
  const [places, setPlaces] = useState<Place[]>([]);
  const [filteredPlaces, setFilteredPlaces] = useState<Place[]>([]);
  const [loading, setLoading] = useState(true);
  const [searchQuery, setSearchQuery] = useState('');
  const [showDialog, setShowDialog] = useState(false);
  const [editingPlace, setEditingPlace] = useState<Place | null>(null);
  const [isSubmitting, setIsSubmitting] = useState(false);

  const [formData, setFormData] = useState<PlaceCreate>({
    name: '',
    slug: '',
    place_type: '',
    address: '',
    city: '',
    country: '',
    description: ''
  });

  const [errors, setErrors] = useState<Record<string, string>>({});

  // Fetch places
  useEffect(() => {
    const fetchPlaces = async () => {
      try {
        setLoading(true);
        const res = await getPlaces();
        setPlaces(res.data);
      } catch (error) {
        console.error('Failed to fetch places:', error);
      } finally {
        setLoading(false);
      }
    };

    fetchPlaces();
  }, []);

  // Filter places
  useEffect(() => {
    const query = searchQuery.toLowerCase();
    const filtered = places.filter(p =>
      p.name.toLowerCase().includes(query) ||
      (p.address?.toLowerCase().includes(query)) ||
      (p.city?.toLowerCase().includes(query))
    );
    setFilteredPlaces(filtered);
  }, [places, searchQuery]);

  const validateForm = () => {
    const newErrors: Record<string, string> = {};
    if (!formData.name.trim()) {
      newErrors.name = 'Place name is required';
    }
    setErrors(newErrors);
    return Object.keys(newErrors).length === 0;
  };

  const handleSubmit = async () => {
    if (!validateForm()) return;

    try {
      setIsSubmitting(true);
      if (editingPlace) {
        const res = await updatePlace(editingPlace.id, formData);
        setPlaces(places.map(p => p.id === editingPlace.id ? res.data : p));
      } else {
        const res = await createPlace(formData);
        setPlaces([res.data, ...places]);
      }
      setShowDialog(false);
      resetForm();
    } catch (error) {
      console.error('Failed to save place:', error);
    } finally {
      setIsSubmitting(false);
    }
  };

  const handleDelete = async (placeId: number) => {
    if (confirm('Are you sure you want to delete this place?')) {
      try {
        await deletePlace(placeId);
        setPlaces(places.filter(p => p.id !== placeId));
      } catch (error) {
        console.error('Failed to delete place:', error);
      }
    }
  };

  const handleEdit = (place: Place) => {
    setEditingPlace(place);
    setFormData({
      name: place.name,
      slug: place.slug || '',
      place_type: place.place_type || '',
      address: place.address || '',
      city: place.city || '',
      country: place.country || '',
      description: place.description || ''
    });
    setShowDialog(true);
  };

  const handleOpenCreate = () => {
    setEditingPlace(null);
    resetForm();
    setShowDialog(true);
  };

  const resetForm = () => {
    setFormData({
      name: '',
      slug: '',
      place_type: '',
      address: '',
      city: '',
      country: '',
      description: ''
    });
    setErrors({});
  };

  if (loading) {
    return (
      <div className="flex items-center justify-center h-screen">
        <div className="text-center">
          <div className="w-12 h-12 border-4 border-blue-500 border-t-transparent rounded-full animate-spin mx-auto mb-4" />
          <p className="text-gray-600">Loading places...</p>
        </div>
      </div>
    );
  }

  return (
    <div className="min-h-screen bg-gray-50">
      {/* Header */}
      <div className="bg-white border-b border-gray-200 sticky top-0 z-40">
        <div className="max-w-7xl mx-auto px-4 sm:px-6 lg:px-8 py-4">
          <div className="flex items-center justify-between mb-6">
            <h1 className="text-3xl font-bold text-gray-900">Places</h1>
            <Button onClick={handleOpenCreate} size="lg">
              <Plus className="w-5 h-5" />
              Add Place
            </Button>
          </div>

          {/* Search */}
          <div className="relative">
            <Search className="absolute left-3 top-1/2 -translate-y-1/2 w-5 h-5 text-gray-400" />
            <input
              type="text"
              placeholder="Search by name, address, or city..."
              value={searchQuery}
              onChange={(e) => setSearchQuery(e.target.value)}
              className="w-full pl-10 pr-4 py-2 border border-gray-300 rounded-lg focus:outline-none focus:ring-2 focus:ring-blue-500"
            />
          </div>

          <div className="text-sm text-gray-600 mt-3">
            Showing {filteredPlaces.length} of {places.length} places
          </div>
        </div>
      </div>

      {/* Content */}
      <div className="max-w-7xl mx-auto px-4 sm:px-6 lg:px-8 py-8">
        {filteredPlaces.length === 0 ? (
          <div className="text-center py-12">
            <MapPin className="w-16 h-16 text-gray-300 mx-auto mb-4" />
            <p className="text-gray-500 mb-4">No places added yet</p>
            <Button onClick={handleOpenCreate}>
              <Plus className="w-5 h-5" />
              Add Your First Place
            </Button>
          </div>
        ) : (
          <div className="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-3 gap-6">
            {filteredPlaces.map(place => (
              <Card key={place.id} className="hover:shadow-lg transition-shadow">
                <CardHeader>
                  <div className="flex items-start justify-between">
                    <div>
                      <h3 className="text-lg font-semibold text-gray-900">{place.name}</h3>
                      {place.place_type && (
                        <p className="text-sm text-gray-500 capitalize">{place.place_type}</p>
                      )}
                    </div>
                    <div className="w-12 h-12 bg-green-100 rounded-full flex items-center justify-center">
                      <MapPin className="w-6 h-6 text-green-600" />
                    </div>
                  </div>
                </CardHeader>

                <CardContent className="space-y-3">
                  {place.address && (
                    <div className="text-sm text-gray-700">
                      <p className="font-medium">Address:</p>
                      <p className="text-gray-600">{place.address}</p>
                    </div>
                  )}

                  {(place.city || place.country) && (
                    <div className="text-sm text-gray-700">
                      <p className="font-medium">Location:</p>
                      <p className="text-gray-600">
                        {place.city}{place.country ? `, ${place.country}` : ''}
                      </p>
                    </div>
                  )}

                  {place.description && (
                    <div className="text-sm text-gray-700">
                      <p className="font-medium">Description:</p>
                      <p className="text-gray-600 line-clamp-3">{place.description}</p>
                    </div>
                  )}

                  {place.slug && (
                    <div className="text-xs text-gray-500">
                      ID: {place.slug}
                    </div>
                  )}
                </CardContent>

                <div className="px-6 py-4 border-t border-gray-200 flex gap-2">
                  <Button
                    variant="secondary"
                    size="sm"
                    onClick={() => handleEdit(place)}
                    className="flex-1"
                  >
                    <Edit className="w-4 h-4" />
                    Edit
                  </Button>
                  <Button
                    variant="danger"
                    size="sm"
                    onClick={() => handleDelete(place.id)}
                    className="flex-1"
                  >
                    <Trash2 className="w-4 h-4" />
                    Delete
                  </Button>
                </div>
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
          resetForm();
        }}
        title={editingPlace ? 'Edit Place' : 'Add New Place'}
        description={editingPlace ? 'Update place details' : 'Add a new place'}
        size="lg"
      >
        <div className="space-y-4 max-h-96 overflow-y-auto">
          <InputField
            label="Place Name"
            placeholder="e.g., Central Park, Coffee Shop, Home"
            value={formData.name}
            onChange={(val) => setFormData({ ...formData, name: val })}
            required
            error={errors.name}
          />

          <InputField
            label="Type"
            placeholder="e.g., Park, Restaurant, Office"
            value={formData.place_type || ''}
            onChange={(val) => setFormData({ ...formData, place_type: val })}
          />

          <InputField
            label="Address"
            placeholder="123 Main Street"
            value={formData.address || ''}
            onChange={(val) => setFormData({ ...formData, address: val })}
          />

          <div className="grid grid-cols-2 gap-4">
            <InputField
              label="City"
              placeholder="New York"
              value={formData.city || ''}
              onChange={(val) => setFormData({ ...formData, city: val })}
            />
            <InputField
              label="Country"
              placeholder="USA"
              value={formData.country || ''}
              onChange={(val) => setFormData({ ...formData, country: val })}
            />
          </div>

          <InputField
            label="Slug"
            placeholder="central-park (for mentions)"
            value={formData.slug || ''}
            onChange={(val) => setFormData({ ...formData, slug: val })}
          />

          <div>
            <label className="block text-sm font-medium text-gray-700 mb-2">
              Description
            </label>
            <textarea
              value={formData.description || ''}
              onChange={(val) => setFormData({ ...formData, description: val })}
              placeholder="Add a description about this place..."
              rows={4}
              className="w-full px-4 py-2 border border-gray-300 rounded-lg focus:outline-none focus:ring-2 focus:ring-blue-500 focus:border-transparent resize-none"
            />
          </div>

          <div className="flex gap-3 justify-end pt-4 border-t border-gray-200">
            <Button
              variant="secondary"
              onClick={() => {
                setShowDialog(false);
                resetForm();
              }}
            >
              Cancel
            </Button>
            <Button
              onClick={handleSubmit}
              isLoading={isSubmitting}
            >
              {editingPlace ? 'Update Place' : 'Add Place'}
            </Button>
          </div>
        </div>
      </Dialog>
    </div>
  );
};

export default PlacesPage;
