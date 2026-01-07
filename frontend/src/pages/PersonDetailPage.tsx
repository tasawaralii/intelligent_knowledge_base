import { useEffect, useState } from 'react';
import { useNavigate, useParams } from 'react-router-dom';
import { ArrowLeft, Edit, Trash2, Mail, Phone, MapPin, User, GitBranch, Plus, X } from 'lucide-react';
import { Card, CardContent, CardHeader } from '../components/ui/Card';
import { Button } from '../components/ui/Button';
import { InputField, SelectField } from '../components/FormFields';
import { deletePerson, getPerson, getPersons, updatePerson, getPersonRelations, createPersonRelation, deletePersonRelation, type Person, type PersonCreate, type PersonRelation } from '../api/persons';
import { useAlert } from '../context/alertContext';

const emptyForm: PersonCreate = {
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
    cnic: '',
};

const formatDate = (value?: string) => {
    if (!value) return 'N/A';
    const date = new Date(value);
    return isNaN(date.getTime()) ? value : date.toLocaleDateString();
};

const RELATION_TYPES = [
    'father',
    'mother',
    'child',
    'spouse',
    'sibling',
];

export const PersonDetailPage = () => {
    const { person_slug } = useParams();
    const navigate = useNavigate();
    const { addAlert } = useAlert();

    const [person, setPerson] = useState<Person | null>(null);
    const [person_id, setPersonId] = useState<number | null>(null)
    const [allPersons, setAllPersons] = useState<Person[]>([]);
    const [relations, setRelations] = useState<PersonRelation[]>([]);
    const [formData, setFormData] = useState<PersonCreate>(emptyForm);
    const [loading, setLoading] = useState(true);
    const [saving, setSaving] = useState(false);
    const [isEditing, setIsEditing] = useState(false);

    // For adding new relations
    const [showAddRelation, setShowAddRelation] = useState(false);
    const [newRelation, setNewRelation] = useState({ related_person_id: '', relation_type: 'father' });

    const loadData = async () => {
        if (!person_slug) return;
        try {
            setLoading(true);
            const [personRes, personsRes] = await Promise.all([
                getPerson(person_slug),
                getPersons(),
            ]);

            setPersonId(personRes.data.id)
            const relationsRes = await getPersonRelations(personRes.data.id)

            setPerson(personRes.data);
            setAllPersons(personsRes.data);
            setRelations(relationsRes.data);
            setFormData({
                first_name: personRes.data.first_name,
                last_name: personRes.data.last_name || '',
                father_name: personRes.data.father_name || '',
                email: personRes.data.email || '',
                phone_number: personRes.data.phone_number || '',
                address: personRes.data.address || '',
                city: personRes.data.city || '',
                country: personRes.data.country || '',
                date_of_birth: personRes.data.date_of_birth || '',
                gender: personRes.data.gender || '',
                cnic: personRes.data.cnic || '',
            });
        } catch (error: any) {
            addAlert(error?.response?.data?.detail || 'Failed to load person', 'error', 3000);
        } finally {
            setLoading(false);
        }
    };

    useEffect(() => {
        loadData();
    }, [person_slug]);

    const handleSave = async () => {
        if (!person?.id) return;
        const id = person.id
        try {
            setSaving(true);
            // Convert empty strings to null for optional fields
            const dataToSend = {
                ...formData,
                last_name: formData.last_name || null,
                father_name: formData.father_name || null,
                email: formData.email || null,
                phone_number: formData.phone_number || null,
                address: formData.address || null,
                city: formData.city || null,
                country: formData.country || null,
                date_of_birth: formData.date_of_birth || null,
                gender: formData.gender || null,
                cnic: formData.cnic || null,
            };
            const res = await updatePerson(id, dataToSend as PersonCreate);
            setPerson(res.data);
            setIsEditing(false);
            addAlert('Person updated', 'success', 2000);
        } catch (error: any) {
            addAlert(error?.response?.data?.detail || 'Update failed', 'error', 3000);
        } finally {
            setSaving(false);
        }
    };

    const handleAddRelation = async () => {
        if (!person_id || !newRelation.related_person_id) return;
        const id = person_id
        try {
            const relationRes = await createPersonRelation(id, {
                person_id: id,
                related_person_id: parseInt(newRelation.related_person_id),
                relation_type: newRelation.relation_type
            });
            setRelations([...relations, relationRes.data]);
            setNewRelation({ related_person_id: '', relation_type: 'father' });
            setShowAddRelation(false);
            addAlert('Relation added', 'success', 2000);
        } catch (error: any) {
            addAlert(error?.response?.data?.detail || 'Failed to add relation', 'error', 3000);
        }
    };

    const handleDeleteRelation = async (relationId: number) => {
        if (!person_id) return;
        const id = person_id
        if (!confirm('Delete this relation?')) return;
        try {
            await deletePersonRelation(id, relationId);
            setRelations(relations.filter(r => r.id !== relationId));
            addAlert('Relation deleted', 'success', 2000);
        } catch (error: any) {
            addAlert(error?.response?.data?.detail || 'Failed to delete relation', 'error', 3000);
        }
    };

    const handleDelete = async () => {
        if (!person_id) return;
        const id = person_id
        if (!confirm('Delete this person?')) return;
        try {
            await deletePerson(id);
            addAlert('Person deleted', 'success', 2000);
            navigate('/persons');
        } catch (error: any) {
            addAlert(error?.response?.data?.detail || 'Delete failed', 'error', 3000);
        }
    };

    if (loading) {
        return (
            <div className="flex items-center justify-center min-h-screen bg-gray-50">
                <div className="text-center">
                    <div className="w-12 h-12 border-4 border-blue-500 border-t-transparent rounded-full animate-spin mx-auto mb-4" />
                    <p className="text-gray-600">Loading person...</p>
                </div>
            </div>
        );
    }

    if (!person) {
        return (
            <div className="flex flex-col items-center justify-center min-h-screen bg-gray-50 p-6">
                <p className="text-gray-700 mb-4">Person not found.</p>
                <Button onClick={() => navigate('/persons')}>Back to Persons</Button>
            </div>
        );
    }

    const relationOptions = (filter?: (p: Person) => boolean) => [
        { value: '', label: 'None' },
        ...allPersons
            .filter(p => (!filter || filter(p)) && p.id !== person.id)
            .map(p => ({ value: p.id.toString(), label: `${p.first_name} ${p.last_name || ''}` }))
    ];

    return (
        <div className="min-h-screen bg-gray-50 p-6">
            <div className="max-w-5xl mx-auto space-y-6">
                <div className="flex items-center gap-3">
                    <Button variant="secondary" onClick={() => navigate(-1)}>
                        <ArrowLeft className="w-4 h-4" />
                        Back
                    </Button>
                    <h1 className="text-3xl font-bold text-gray-900">Person Details</h1>
                </div>

                <Card>
                    <CardHeader>
                        <div className="flex items-start justify-between">
                            <div>
                                <div className="flex items-center gap-3">
                                    <div className="w-14 h-14 bg-blue-100 rounded-full flex items-center justify-center">
                                        <User className="w-7 h-7 text-blue-600" />
                                    </div>
                                    <div>
                                        <h2 className="text-2xl font-semibold text-gray-900">
                                            {person.first_name} {person.last_name || ''}
                                        </h2>
                                        {person.father_name && (
                                            <p className="text-sm text-gray-500">s/o {person.father_name}</p>
                                        )}
                                    </div>
                                </div>
                            </div>
                            <div className="flex gap-2">
                                <Button variant="secondary" onClick={() => navigate(`/family-tree/${person.id}`)}>
                                    <GitBranch className="w-4 h-4" />
                                    Family Tree
                                </Button>
                                <Button variant="secondary" onClick={() => setIsEditing(!isEditing)}>
                                    <Edit className="w-4 h-4" />
                                    {isEditing ? 'Cancel' : 'Edit'}
                                </Button>
                                <Button variant="danger" onClick={handleDelete}>
                                    <Trash2 className="w-4 h-4" />
                                    Delete
                                </Button>
                            </div>
                        </div>
                    </CardHeader>

                    <CardContent className="space-y-6">
                        {!isEditing && (
                            <div className="grid grid-cols-1 md:grid-cols-2 gap-4">
                                <div className="space-y-3">
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
                                                {person.city && <div>{person.city}{person.country ? `, ${person.country}` : ''}</div>}
                                            </div>
                                        </div>
                                    )}
                                </div>
                                <div className="space-y-2 text-sm text-gray-700">
                                    <div><span className="text-gray-500">DOB:</span> {formatDate(person.date_of_birth)}</div>
                                    <div><span className="text-gray-500">Gender:</span> {person.gender || 'N/A'}</div>
                                    <div><span className="text-gray-500">CNIC:</span> {person.cnic || 'N/A'}</div>
                                    <div><span className="text-gray-500">Slug:</span> {person.slug}</div>
                                </div>

                                {relations.length > 0 && (
                                    <div className="pt-4 border-t">
                                        <h3 className="text-sm font-semibold text-gray-900 mb-3">Family Relations</h3>
                                        <div className="space-y-2">
                                            {relations.map(rel => {
                                                const relatedPerson = allPersons.find(p => p.id === rel.related_person_id);
                                                return (
                                                    <div key={rel.id} className="flex items-center justify-between bg-gray-50 p-2 rounded">
                                                        <div>
                                                            <div className="text-sm font-medium text-gray-900">
                                                                {relatedPerson?.first_name} {relatedPerson?.last_name || ''}
                                                            </div>
                                                            <div className="text-xs text-gray-500 capitalize">{rel.relation_type}</div>
                                                        </div>
                                                        <button
                                                            onClick={() => handleDeleteRelation(rel.id)}
                                                            className="text-red-500 hover:text-red-700 transition"
                                                        >
                                                            <X className="w-4 h-4" />
                                                        </button>
                                                    </div>
                                                );
                                            })}
                                        </div>
                                    </div>
                                )}
                            </div>
                        )}

                        {isEditing && (
                            <div className="space-y-4">
                                <InputField
                                    label="First Name"
                                    placeholder="John"
                                    value={formData.first_name}
                                    onChange={(val) => setFormData({ ...formData, first_name: val })}
                                    required
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
                                            { value: '', label: '--Select--' },
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

                                <div className="pt-4 border-t border-gray-200">
                                    <div className="flex items-center justify-between mb-3">
                                        <h3 className="text-md font-semibold text-gray-900">Family Relations</h3>
                                        {!showAddRelation && (
                                            <Button size="sm" onClick={() => setShowAddRelation(true)}>
                                                <Plus className="w-4 h-4" />
                                                Add Relation
                                            </Button>
                                        )}
                                    </div>

                                    {showAddRelation && (
                                        <div className="bg-blue-50 p-4 rounded-lg space-y-3 mb-4">
                                            <SelectField
                                                label="Related Person"
                                                value={newRelation.related_person_id}
                                                onChange={(val) => setNewRelation({ ...newRelation, related_person_id: val })}
                                                options={[
                                                    { value: '', label: 'Select person...' },
                                                    ...allPersons
                                                        .filter(p => p.id !== person.id)
                                                        .map(p => ({ value: p.id.toString(), label: `${p.first_name} ${p.last_name || ''}` }))
                                                ]}
                                            />
                                            <SelectField
                                                label="Relation Type"
                                                value={newRelation.relation_type}
                                                onChange={(val) => setNewRelation({ ...newRelation, relation_type: val })}
                                                options={RELATION_TYPES.map(t => ({ value: t, label: t.charAt(0).toUpperCase() + t.slice(1) }))}
                                            />
                                            <div className="flex gap-2">
                                                <Button size="sm" onClick={handleAddRelation}>Add</Button>
                                                <Button size="sm" variant="secondary" onClick={() => setShowAddRelation(false)}>Cancel</Button>
                                            </div>
                                        </div>
                                    )}

                                    {relations.length > 0 && (
                                        <div className="space-y-2">
                                            {relations.map(rel => {
                                                const relatedPerson = allPersons.find(p => p.id === rel.related_person_id);
                                                return (
                                                    <div key={rel.id} className="flex items-center justify-between bg-gray-50 p-2 rounded">
                                                        <div>
                                                            <div className="text-sm font-medium text-gray-900">
                                                                {relatedPerson?.first_name} {relatedPerson?.last_name || ''}
                                                            </div>
                                                            <div className="text-xs text-gray-500 capitalize">{rel.relation_type}</div>
                                                        </div>
                                                        <button
                                                            onClick={() => handleDeleteRelation(rel.id)}
                                                            className="text-red-500 hover:text-red-700 transition"
                                                        >
                                                            <X className="w-4 h-4" />
                                                        </button>
                                                    </div>
                                                );
                                            })}
                                        </div>
                                    )}
                                </div>

                                <div className="flex gap-3 justify-end">
                                    <Button variant="secondary" onClick={() => setIsEditing(false)}>
                                        Cancel
                                    </Button>
                                    <Button onClick={handleSave} isLoading={saving}>
                                        Save Changes
                                    </Button>
                                </div>
                            </div>
                        )}
                    </CardContent>
                </Card>
            </div>
        </div>
    );
};

export default PersonDetailPage;
