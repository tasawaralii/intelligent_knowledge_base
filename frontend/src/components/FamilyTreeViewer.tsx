import { useState, useEffect } from 'react';
import { User, Heart, Users } from 'lucide-react';
import type { FamilyTree, FamilyMember, FamilyTreeNode } from '../api/persons';
import { Card, CardContent, CardHeader } from './ui/Card';

interface FamilyTreeViewerProps {
  familyTree: FamilyTree;
  onPersonClick?: (personId: number) => void;
}

const FamilyMemberCard = ({ 
  member, 
  onClick, 
  label 
}: { 
  member: FamilyMember; 
  onClick?: (id: number) => void;
  label?: string;
}) => {
  const getAge = (dob?: string) => {
    if (!dob) return null;
    const birthDate = new Date(dob);
    const today = new Date();
    let age = today.getFullYear() - birthDate.getFullYear();
    const monthDiff = today.getMonth() - birthDate.getMonth();
    if (monthDiff < 0 || (monthDiff === 0 && today.getDate() < birthDate.getDate())) {
      age--;
    }
    return age;
  };

  return (
    <div 
      className="bg-white border-2 border-gray-300 rounded-lg p-3 shadow-md cursor-pointer hover:shadow-lg transition-all min-w-[150px] max-w-[180px]"
      onClick={() => onClick?.(member.id)}
    >
      {label && (
        <div className="text-xs text-gray-500 font-semibold mb-1">{label}</div>
      )}
      <div className="flex flex-col items-center gap-2">
        {member.picture_url ? (
          <img 
            src={member.picture_url} 
            alt={member.first_name}
            className="w-16 h-16 rounded-full object-cover border-2 border-blue-400"
          />
        ) : (
          <div className="w-16 h-16 rounded-full bg-gradient-to-br from-blue-400 to-purple-500 flex items-center justify-center">
            <User className="w-8 h-8 text-white" />
          </div>
        )}
        <div className="text-center">
          <div className="font-semibold text-sm">
            {member.first_name} {member.last_name || ''}
          </div>
          {member.gender && (
            <div className="text-xs text-gray-500 capitalize">{member.gender}</div>
          )}
          {member.date_of_birth && (
            <div className="text-xs text-gray-500">
              Age {getAge(member.date_of_birth)}
            </div>
          )}
        </div>
      </div>
    </div>
  );
};

export const FamilyTreeViewer = ({ familyTree, onPersonClick }: FamilyTreeViewerProps) => {
  const [selectedNode, setSelectedNode] = useState<FamilyTreeNode | null>(null);

  useEffect(() => {
    // Set root person as initially selected
    const rootNode = familyTree.nodes.find(
      node => node.person.id === familyTree.root_person.id
    );
    if (rootNode) {
      setSelectedNode(rootNode);
    }
  }, [familyTree]);

  if (!selectedNode) return null;

  return (
    <div className="w-full space-y-6">
      <Card>
        <CardHeader>
          <h2 className="text-2xl font-bold text-gray-800">
            Family Tree - {familyTree.root_person.first_name} {familyTree.root_person.last_name || ''}
          </h2>
          <p className="text-sm text-gray-500">
            {familyTree.generations} generation(s) • {familyTree.nodes.length} family member(s)
          </p>
        </CardHeader>
        <CardContent>
          <div className="space-y-8">
            {/* Parents Section */}
            {(selectedNode.father || selectedNode.mother) && (
              <div className="border-b pb-6">
                <h3 className="text-lg font-semibold mb-4 flex items-center gap-2">
                  <Users className="w-5 h-5" />
                  Parents
                </h3>
                <div className="flex gap-6 justify-center flex-wrap">
                  {selectedNode.father && (
                    <FamilyMemberCard 
                      member={selectedNode.father} 
                      onClick={(id) => {
                        const node = familyTree.nodes.find(n => n.person.id === id);
                        if (node) setSelectedNode(node);
                        onPersonClick?.(id);
                      }}
                      label="Father"
                    />
                  )}
                  {selectedNode.mother && (
                    <FamilyMemberCard 
                      member={selectedNode.mother} 
                      onClick={(id) => {
                        const node = familyTree.nodes.find(n => n.person.id === id);
                        if (node) setSelectedNode(node);
                        onPersonClick?.(id);
                      }}
                      label="Mother"
                    />
                  )}
                </div>
              </div>
            )}

            {/* Current Person & Spouse */}
            <div className="border-b pb-6">
              <h3 className="text-lg font-semibold mb-4 flex items-center gap-2">
                <User className="w-5 h-5" />
                Current Person
              </h3>
              <div className="flex gap-6 justify-center items-center flex-wrap">
                <FamilyMemberCard 
                  member={selectedNode.person} 
                  onClick={(id) => onPersonClick?.(id)}
                />
                {selectedNode.spouse && (
                  <>
                    <Heart className="w-6 h-6 text-red-500" />
                    <FamilyMemberCard 
                      member={selectedNode.spouse} 
                      onClick={(id) => {
                        const node = familyTree.nodes.find(n => n.person.id === id);
                        if (node) setSelectedNode(node);
                        onPersonClick?.(id);
                      }}
                      label="Spouse"
                    />
                  </>
                )}
              </div>
            </div>

            {/* Siblings Section */}
            {selectedNode.siblings.length > 0 && (
              <div className="border-b pb-6">
                <h3 className="text-lg font-semibold mb-4 flex items-center gap-2">
                  <Users className="w-5 h-5" />
                  Siblings ({selectedNode.siblings.length})
                </h3>
                <div className="flex gap-4 justify-center flex-wrap">
                  {selectedNode.siblings.map(sibling => (
                    <FamilyMemberCard 
                      key={sibling.id}
                      member={sibling} 
                      onClick={(id) => {
                        const node = familyTree.nodes.find(n => n.person.id === id);
                        if (node) setSelectedNode(node);
                        onPersonClick?.(id);
                      }}
                    />
                  ))}
                </div>
              </div>
            )}

            {/* Children Section */}
            {selectedNode.children.length > 0 && (
              <div>
                <h3 className="text-lg font-semibold mb-4 flex items-center gap-2">
                  <Users className="w-5 h-5" />
                  Children ({selectedNode.children.length})
                </h3>
                <div className="flex gap-4 justify-center flex-wrap">
                  {selectedNode.children.map(child => (
                    <FamilyMemberCard 
                      key={child.id}
                      member={child} 
                      onClick={(id) => {
                        const node = familyTree.nodes.find(n => n.person.id === id);
                        if (node) setSelectedNode(node);
                        onPersonClick?.(id);
                      }}
                    />
                  ))}
                </div>
              </div>
            )}

            {/* All Family Members List */}
            <div className="mt-8 pt-6 border-t">
              <h3 className="text-lg font-semibold mb-4">All Family Members</h3>
              <div className="grid grid-cols-2 md:grid-cols-4 lg:grid-cols-6 gap-3">
                {familyTree.nodes.map(node => (
                  <button
                    key={node.person.id}
                    onClick={() => {
                      setSelectedNode(node);
                      onPersonClick?.(node.person.id);
                    }}
                    className={`p-2 rounded-lg text-left transition-all ${
                      selectedNode.person.id === node.person.id
                        ? 'bg-blue-100 border-2 border-blue-500'
                        : 'bg-gray-50 border border-gray-200 hover:bg-gray-100'
                    }`}
                  >
                    <div className="text-sm font-medium truncate">
                      {node.person.first_name} {node.person.last_name || ''}
                    </div>
                    {node.person.gender && (
                      <div className="text-xs text-gray-500 capitalize">
                        {node.person.gender}
                      </div>
                    )}
                  </button>
                ))}
              </div>
            </div>
          </div>
        </CardContent>
      </Card>
    </div>
  );
};
