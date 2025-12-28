import { useState, useEffect } from 'react';
import { Plus, Search, Trash2, Edit, Mail, Phone, MapPin, User } from 'lucide-react';
import { Dialog } from '../components/ui/Dialog';
import { Button } from '../components/ui/Button';
import { Card, CardContent, CardHeader } from '../components/ui/Card';
import { InputField, SelectField } from '../components/FormFields';
import { getPersons, createPerson, updatePerson, deletePerson, type Person, type PersonCreate } from '../api/persons';

export const PersonsPage = () => {
  const [persons, setPersons] = useState<Person[]>([]);
  const [filteredPersons, setFilteredPersons] = useState<Person[]>([]);
  const [loading, setLoading] = useState(true);
  const [searchQuery, setSearchQuery] = useState('');
  const [showDialog, setShowDialog] = useState(false);
  const [editingPerson, setEditingPerson] = useState<Person | null>(null);
  const [isSubmitting, setIsSubmitting] = useState(false);

  const [formData, setFormData] = useState<PersonCreate>({
    first_name: '',
    last_name: '',
    father_name: '',
    email: '',
    phone_number: '',
    address: '',
    city: '',
    country: '',
    date_of_birth: '',
    gender: '',
    cnic: ''
  });

  const [errors, setErrors] = useState<Record<string, string>>({});

  // Fetch persons
  useEffect(() => {
    const fetchPersons = async () => {
      try {
        setLoading(true);
        const res = await getPersons();
        setPersons(res.data);
      } catch (error) {
        console.error('Failed to fetch persons:', error);
      } finally {
        setLoading(false);
      }
    };

    fetchPersons();
  }, []);

  // Filter persons
  useEffect(() => {
    const query = searchQuery.toLowerCase();
    const filtered = persons.filter(p =>
      `${p.first_name} ${p.last_name || ''}`.toLowerCase().includes(query) ||
      (p.email?.toLowerCase().includes(query)) ||
      (p.phone_number?.includes(query))
    );
    setFilteredPersons(filtered);
  }, [persons, searchQuery]);

  const validateForm = () => {
    const newErrors: Record<string, string> = {};
    if (!formData.first_name.trim()) {
      newErrors.first_name = 'First name is required';
    }
    setErrors(newErrors);
    return Object.keys(newErrors).length === 0;
  };

  const handleSubmit = async () => {
    if (!validateForm()) return;

    try {
      setIsSubmitting(true);
      if (editingPerson) {
        const res = await updatePerson(editingPerson.id, formData);
        setPersons(persons.map(p => p.id === editingPerson.id ? res.data : p));
      } else {
        const res = await createPerson(formData);
        setPersons([res.data, ...persons]);
      }
      setShowDialog(false);
      resetForm();
    } catch (error) {
      console.error('Failed to save person:', error);
    } finally {
      setIsSubmitting(false);
    }
  };

  const handleDelete = async (personId: number) => {
    if (confirm('Are you sure you want to delete this person?')) {
      try {
        await deletePerson(personId);
        setPersons(persons.filter(p => p.id !== personId));
      } catch (error) {
        console.error('Failed to delete person:', error);
      }
    }
  };

  const handleEdit = (person: Person) => {
    setEditingPerson(person);
    setFormData({
      first_name: person.first_name,
      last_name: person.last_name || '',
      father_name: person.father_name || '',
      email: person.email || '',
      phone_number: person.phone_number || '',
      address: person.address || '',
      city: person.city || '',
      country: person.country || '',
      date_of_birth: person.date_of_birth || '',
      gender: person.gender || '',
      cnic: person.cnic || ''
    });
    setShowDialog(true);
  };

  const handleOpenCreate = () => {
    setEditingPerson(null);
    resetForm();
    setShowDialog(true);
  };

  const resetForm = () => {
    setFormData({
      first_name: '',
      last_name: '',
      father_name: '',
      email: '',
      phone_number: '',
      address: '',
      city: '',
      country: '',
      date_of_birth: '',
      gender: '',
      cnic: ''
    });
    setErrors({});
  };

  if (loading) {
    return (
      <div className="flex items-center justify-center h-screen">
        <div className="text-center">
          <div className="w-12 h-12 border-4 border-blue-500 border-t-transparent rounded-full animate-spin mx-auto mb-4" />
          <p className="text-gray-600">Loading persons...</p>
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
            <h1 className="text-3xl font-bold text-gray-900">Persons</h1>
            <Button onClick={handleOpenCreate} size="lg">
              <Plus className="w-5 h-5" />
              Add Person
            </Button>
          </div>

          {/* Search */}
          <div className="relative">
            <Search className="absolute left-3 top-1/2 -translate-y-1/2 w-5 h-5 text-gray-400" />
            <input
              type="text"
              placeholder="Search by name, email, or phone..."
              value={searchQuery}
              onChange={(e) => setSearchQuery(e.target.value)}
              className="w-full pl-10 pr-4 py-2 border border-gray-300 rounded-lg focus:outline-none focus:ring-2 focus:ring-blue-500"
            />
          </div>

          <div className="text-sm text-gray-600 mt-3">
            Showing {filteredPersons.length} of {persons.length} persons
          </div>
        </div>
      </div>

      {/* Content */}
      <div className="max-w-7xl mx-auto px-4 sm:px-6 lg:px-8 py-8">
        {filteredPersons.length === 0 ? (
          <div className="text-center py-12">
            <User className="w-16 h-16 text-gray-300 mx-auto mb-4" />
            <p className="text-gray-500 mb-4">No persons added yet</p>
            <Button onClick={handleOpenCreate}>
              <Plus className="w-5 h-5" />
              Add Your First Person
            </Button>
          </div>
        ) : (
          <div className="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-3 gap-6">
            {filteredPersons.map(person => (
              <Card key={person.id} className="hover:shadow-lg transition-shadow">
                <CardHeader>
                  <div className="flex items-start justify-between">
                    <div>
                      <h3 className="text-lg font-semibold text-gray-900">
                        {person.first_name} {person.last_name || ''}
                      </h3>
                      {person.father_name && (
                        <p className="text-sm text-gray-500">s/o {person.father_name}</p>
                      )}
                    </div>
                    <div className="w-12 h-12 bg-blue-100 rounded-full flex items-center justify-center">
                      <User className="w-6 h-6 text-blue-600" />
                    </div>
                  </div>
                </CardHeader>

                <CardContent className="space-y-3">
                  {person.email && (
                    <div className="flex items-center gap-2 text-gray-700">
                      <Mail className="w-4 h-4 text-gray-400" />
                      <span className="text-sm">{person.email}</span>
                    </div>
                  )}

                  {person.phone_number && (
                    <div className="flex items-center gap-2 text-gray-700">
                      <Phone className="w-4 h-4 text-gray-400" />
                      <span className="text-sm">{person.phone_number}</span>
                    </div>
                  )}

                  {(person.city || person.address) && (
                    <div className="flex items-start gap-2 text-gray-700">
                      <MapPin className="w-4 h-4 text-gray-400 mt-0.5" />
                      <div className="text-sm">
                        {person.address && <div>{person.address}</div>}
                        {person.city && <div>{person.city}, {person.country}</div>}
                      </div>
                    </div>
                  )}

                  {person.date_of_birth && (
                    <div className="text-sm text-gray-600">
                      DOB: {new Date(person.date_of_birth).toLocaleDateString()}
                    </div>
                  )}

                  {person.cnic && (
                    <div className="text-sm text-gray-600">
                      CNIC: {person.cnic}
                    </div>
                  )}

                  {person.gender && (
                    <div className="text-sm text-gray-600 capitalize">
                      Gender: {person.gender}
                    </div>
                  )}
                </CardContent>

                <div className="px-6 py-4 border-t border-gray-200 flex gap-2">
                  <Button
                    variant="secondary"
                    size="sm"
                    onClick={() => handleEdit(person)}
                    className="flex-1"
                  >
                    <Edit className="w-4 h-4" />
                    Edit
                  </Button>
                  <Button
                    variant="danger"
                    size="sm"
                    onClick={() => handleDelete(person.id)}
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
        title={editingPerson ? 'Edit Person' : 'Add New Person'}
        description={editingPerson ? 'Update person details' : 'Add a new person to your contacts'}
        size="lg"
      >
        <div className="space-y-4 max-h-96 overflow-y-auto">
          <InputField
            label="First Name"
            placeholder="John"
            value={formData.first_name}
            onChange={(val) => setFormData({ ...formData, first_name: val })}
            required
            error={errors.first_name}
          />

          <div className="grid grid-cols-2 gap-4">
            <InputField
              label="Last Name"
              placeholder="Doe"
              value={formData.last_name || ''}
              onChange={(val) => setFormData({ ...formData, last_name: val })}
            />
            <InputField
              label="Father Name"
              placeholder="James"
              value={formData.father_name || ''}
              onChange={(val) => setFormData({ ...formData, father_name: val })}
            />
          </div>

          <div className="grid grid-cols-2 gap-4">
            <InputField
              label="Email"
              type="email"
              placeholder="john@example.com"
              value={formData.email || ''}
              onChange={(val) => setFormData({ ...formData, email: val })}
            />
            <InputField
              label="Phone"
              type="tel"
              placeholder="+1234567890"
              value={formData.phone_number || ''}
              onChange={(val) => setFormData({ ...formData, phone_number: val })}
            />
          </div>

          <div className="grid grid-cols-2 gap-4">
            <InputField
              label="Date of Birth"
              type="date"
              value={formData.date_of_birth || ''}
              onChange={(val) => setFormData({ ...formData, date_of_birth: val })}
            />
            <SelectField
              label="Gender"
              value={formData.gender || ''}
              onChange={(val) => setFormData({ ...formData, gender: val })}
              options={[
                { value: 'male', label: 'Male' },
                { value: 'female', label: 'Female' },
                { value: 'other', label: 'Other' }
              ]}
            />
          </div>

          <InputField
            label="CNIC"
            placeholder="12345-1234567-1"
            value={formData.cnic || ''}
            onChange={(val) => setFormData({ ...formData, cnic: val })}
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
              {editingPerson ? 'Update Person' : 'Add Person'}
            </Button>
          </div>
        </div>
      </Dialog>
    </div>
  );
};

export default PersonsPage;
