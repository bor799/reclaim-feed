import React, { useState } from 'react';
import { TagCategory } from '../types';
import { useApp } from '../contexts/AppContext';
import { Plus, X, List, Save, Edit2, Check } from 'lucide-react';

interface TagsManagerProps {
    onClose: () => void;
}

const TagsManager: React.FC<TagsManagerProps> = ({ onClose }) => {
    const { tagCategories, saveTagCategories } = useApp();
    const [localCategories, setLocalCategories] = useState<TagCategory>(tagCategories);
    const [newCategoryName, setNewCategoryName] = useState('');
    const [newTagNames, setNewTagNames] = useState<Record<string, string>>({});
    const [editingCategory, setEditingCategory] = useState<string | null>(null);
    const [editingCategoryName, setEditingCategoryName] = useState('');

    const handleAddCategory = () => {
        if (newCategoryName.trim() && !localCategories[newCategoryName]) {
            setLocalCategories({
                ...localCategories,
                [newCategoryName.trim()]: [],
            });
            setNewCategoryName('');
        }
    };

    const handleDeleteCategory = (cat: string) => {
        const updated = { ...localCategories };
        delete updated[cat];
        setLocalCategories(updated);
    };

    const handleEditCategoryStart = (cat: string) => {
        setEditingCategory(cat);
        setEditingCategoryName(cat);
    };

    const handleEditCategorySave = (oldCat: string) => {
        if (editingCategoryName.trim() && editingCategoryName !== oldCat) {
            const updated = { ...localCategories };
            updated[editingCategoryName.trim()] = updated[oldCat];
            delete updated[oldCat];
            setLocalCategories(updated);
        }
        setEditingCategory(null);
    };

    const handleAddTag = (cat: string) => {
        const tag = newTagNames[cat]?.trim();
        if (tag && !localCategories[cat].includes(tag)) {
            setLocalCategories({
                ...localCategories,
                [cat]: [...localCategories[cat], tag],
            });
            setNewTagNames({ ...newTagNames, [cat]: '' });
        }
    };

    const handleDeleteTag = (cat: string, tag: string) => {
        setLocalCategories({
            ...localCategories,
            [cat]: localCategories[cat].filter((t) => t !== tag),
        });
    };

    const handleSaveAll = async () => {
        await saveTagCategories(localCategories);
        onClose();
    };

    return (
        <div className="fixed inset-0 bg-black/50 backdrop-blur-sm z-50 flex items-center justify-center p-4">
            <div className="bg-white rounded-2xl shadow-xl w-full max-w-3xl max-h-[80vh] flex flex-col overflow-hidden animate-fade-in">
                <div className="flex items-center justify-between p-6 border-b border-gray-100">
                    <h2 className="text-2xl font-bold flex items-center gap-2 text-gray-900">
                        <List className="text-primary" />
                        Manage Tags & Categories
                    </h2>
                    <button onClick={onClose} className="p-2 text-gray-400 hover:text-gray-900 transition-colors rounded-full hover:bg-gray-100">
                        <X size={20} />
                    </button>
                </div>

                <div className="p-6 overflow-y-auto flex-1 bg-gray-50/50">
                    <div className="space-y-6">
                        {Object.entries(localCategories).map(([cat, tags]) => (
                            <div key={cat} className="bg-white border border-gray-100 rounded-xl p-5 shadow-sm">
                                <div className="flex items-center justify-between mb-4 pb-2 border-b border-gray-50">
                                    {editingCategory === cat ? (
                                        <div className="flex items-center gap-2 w-1/2">
                                            <input
                                                className="flex-1 px-3 py-1 border border-primary rounded-lg focus:outline-none"
                                                value={editingCategoryName}
                                                onChange={(e) => setEditingCategoryName(e.target.value)}
                                                autoFocus
                                            />
                                            <button onClick={() => handleEditCategorySave(cat)} className="text-emerald-500 hover:bg-emerald-50 p-1.5 rounded-lg">
                                                <Check size={16} />
                                            </button>
                                        </div>
                                    ) : (
                                        <div className="flex items-center gap-2 group">
                                            <h3 className="font-semibold text-lg text-gray-800">{cat}</h3>
                                            <button onClick={() => handleEditCategoryStart(cat)} className="text-gray-400 opacity-0 group-hover:opacity-100 hover:text-primary p-1 rounded transition-all">
                                                <Edit2 size={14} />
                                            </button>
                                        </div>
                                    )}
                                    <button onClick={() => handleDeleteCategory(cat)} className="text-red-400 hover:text-red-600 hover:bg-red-50 p-1.5 rounded-lg transition-colors text-sm">
                                        Delete Category
                                    </button>
                                </div>

                                <div className="flex flex-wrap gap-2 mb-4">
                                    {tags.map((tag) => (
                                        <span key={tag} className="inline-flex items-center gap-1.5 bg-primary/10 text-primary px-3 py-1 rounded-full text-sm font-medium">
                                            #{tag}
                                            <button onClick={() => handleDeleteTag(cat, tag)} className="hover:text-red-500 transition-colors bg-primary/10 rounded-full p-0.5">
                                                <X size={12} />
                                            </button>
                                        </span>
                                    ))}
                                    {tags.length === 0 && <span className="text-sm text-gray-400 italic">No tags in this category</span>}
                                </div>

                                <div className="flex items-center gap-2 w-full max-w-sm">
                                    <input
                                        type="text"
                                        placeholder="New tag..."
                                        className="flex-1 px-3 py-1.5 bg-gray-50 border border-gray-200 rounded-lg text-sm focus:outline-none focus:border-primary focus:ring-1 focus:ring-primary transition-all"
                                        value={newTagNames[cat] || ''}
                                        onChange={(e) => setNewTagNames({ ...newTagNames, [cat]: e.target.value })}
                                        onKeyDown={(e) => e.key === 'Enter' && handleAddTag(cat)}
                                    />
                                    <button onClick={() => handleAddTag(cat)} className="bg-gray-100 hover:bg-gray-200 text-gray-700 px-3 py-1.5 rounded-lg text-sm font-medium transition-colors flex items-center gap-1">
                                        <Plus size={16} /> Add
                                    </button>
                                </div>
                            </div>
                        ))}
                    </div>

                    <div className="mt-8 flex items-center gap-3">
                        <input
                            type="text"
                            placeholder="New Category Name..."
                            className="flex-1 max-w-xs px-4 py-2 border border-gray-200 rounded-xl focus:outline-none focus:border-primary focus:ring-1 focus:ring-primary transition-all"
                            value={newCategoryName}
                            onChange={(e) => setNewCategoryName(e.target.value)}
                            onKeyDown={(e) => e.key === 'Enter' && handleAddCategory()}
                        />
                        <button onClick={handleAddCategory} className="bg-primary hover:bg-teal-700 text-white px-5 py-2 rounded-xl font-medium transition-colors flex items-center gap-2">
                            <Plus size={18} /> Add Category
                        </button>
                    </div>
                </div>

                <div className="p-6 border-t border-gray-100 bg-white flex justify-end gap-3">
                    <button onClick={onClose} className="px-5 py-2.5 border border-gray-200 text-gray-600 rounded-xl hover:bg-gray-50 transition-colors font-medium">
                        Cancel
                    </button>
                    <button onClick={handleSaveAll} className="px-5 py-2.5 bg-primary text-white rounded-xl hover:bg-teal-700 transition-colors font-medium flex items-center gap-2 shadow-sm shadow-primary/20">
                        <Save size={18} /> Save Changes
                    </button>
                </div>
            </div>
        </div>
    );
};

export default TagsManager;
