import { useState, useMemo, useEffect } from 'react';
import { Plus, Trash2, Edit2, Search, Filter, X, Save } from 'lucide-react';
import { Source, SourceStatus, SourceType } from '../types';
import { filterBySearchTerm } from '../utils';
import { api } from '../services/api';

const SourcesView = () => {
    const [searchTerm, setSearchTerm] = useState('');
    const [sources, setSources] = useState<Source[]>([]);
    const [isModalOpen, setIsModalOpen] = useState(false);
    const [editingIndex, setEditingIndex] = useState<number | null>(null);
    const [editForm, setEditForm] = useState<Partial<Source>>({
        name: '', type: SourceType.RSS, url: '', enabled: true, status: SourceStatus.Active, category: ''
    });

    useEffect(() => {
        loadSources();
    }, []);

    const loadSources = async () => {
        try {
            const data = await api.getSources();
            setSources(data);
        } catch (error) {
            console.error('Failed to load sources', error);
        }
    };

    // Filter sources based on search term
    const filteredSources = useMemo(() => {
        return filterBySearchTerm(sources, searchTerm);
    }, [searchTerm, sources]);

    const handleOpenModal = (index: number | null = null) => {
        if (index !== null) {
            setEditingIndex(index);
            setEditForm(sources[index]);
        } else {
            setEditingIndex(null);
            setEditForm({ name: '', type: SourceType.RSS, url: '', enabled: true, status: SourceStatus.Active, category: '' });
        }
        setIsModalOpen(true);
    };

    const handleSaveSource = async () => {
        try {
            if (editingIndex !== null) {
                await api.updateSource(editingIndex, editForm as Source);
            } else {
                await api.addSource(editForm as Omit<Source, 'id'>);
            }
            setIsModalOpen(false);
            loadSources();
        } catch (error) {
            console.error('Failed to save source', error);
        }
    };

    const handleDeleteSource = async (index: number) => {
        if (confirm('确定要删除这个信息源吗？')) {
            try {
                await api.deleteSource(index);
                loadSources();
            } catch (error) {
                console.error('Failed to delete source', error);
            }
        }
    };

    return (
        <div className="p-8 max-w-6xl mx-auto">
            <div className="flex justify-between items-center mb-8">
                <div>
                    <h1 className="text-3xl font-bold text-text mb-2 animate-fade-in">Sources</h1>
                    <p className="text-gray-500">Manage your high-quality information feeds.</p>
                </div>
                <button
                    onClick={() => handleOpenModal(null)}
                    className="bg-cta hover:bg-orange-600 text-white px-5 py-2.5 rounded-lg flex items-center gap-2 font-medium transition-colors shadow-sm shadow-cta/20"
                >
                    <Plus size={20} />
                    Add Source
                </button>
            </div>

            <div className="bg-white border border-gray-100 rounded-2xl overflow-hidden shadow-sm">
                {/* Toolbar */}
                <div className="p-4 border-b border-gray-100 flex gap-4">
                    <div className="relative flex-1 max-w-md">
                        <Search className="absolute left-3 top-1/2 -translate-y-1/2 text-gray-400" size={18} />
                        <input
                            type="text"
                            placeholder="Search sources..."
                            className="w-full pl-10 pr-4 py-2 border border-gray-200 rounded-lg focus:outline-none focus:border-primary focus:ring-1 focus:ring-primary transition-all"
                            value={searchTerm}
                            onChange={(e) => setSearchTerm(e.target.value)}
                        />
                    </div>
                    <button className="px-4 py-2 border border-gray-200 rounded-lg flex items-center gap-2 text-gray-600 hover:bg-gray-50 transition-colors">
                        <Filter size={18} />
                        Filter
                    </button>
                </div>

                {/* Table */}
                <div className="overflow-x-auto">
                    <table className="w-full text-left border-collapse">
                        <thead>
                            <tr className="bg-gray-50/50 border-b border-gray-100 text-sm text-gray-500">
                                <th className="py-4 px-6 font-medium text-gray-500">Name</th>
                                <th className="py-4 px-6 font-medium text-gray-500 w-24">Type</th>
                                <th className="py-4 px-6 font-medium text-gray-500">URL</th>
                                <th className="py-4 px-6 font-medium text-gray-500">Category</th>
                                <th className="py-4 px-6 font-medium text-gray-500 w-32">Status</th>
                                <th className="py-4 px-6 font-medium text-right">Actions</th>
                            </tr>
                        </thead>
                        <tbody>
                            {filteredSources.map((source: Source, index: number) => (
                                <tr key={index} className="border-b border-gray-50 hover:bg-gray-50/50 transition-colors group">
                                    <td className="py-4 px-6 font-medium text-gray-900">{source.name}</td>
                                    <td className="py-4 px-6">
                                        <span className="inline-block px-3 py-1 bg-gray-100 text-gray-600 text-sm rounded-full font-medium">
                                            {source.type}
                                        </span>
                                    </td>
                                    <td className="py-4 px-6 text-gray-500 text-sm truncate max-w-xs">{source.url}</td>
                                    <td className="py-4 px-6">
                                        <span className="inline-block px-3 py-1 bg-purple-50 text-purple-700 text-sm rounded-full font-medium">
                                            {source.category || 'Uncategorized'}
                                        </span>
                                    </td>
                                    <td className="py-4 px-6">
                                        <span className={`inline-flex items-center gap-1.5 px-3 py-1 rounded-full text-sm font-medium ${source.enabled
                                            ? 'bg-emerald-50 text-emerald-700'
                                            : 'bg-amber-50 text-amber-700'
                                            }`}>
                                            <span className={`w-1.5 h-1.5 rounded-full ${source.enabled ? 'bg-emerald-500' : 'bg-amber-500'}`}></span>
                                            {source.enabled ? SourceStatus.Active : SourceStatus.Paused}
                                        </span>
                                    </td>
                                    <td className="py-4 px-6 text-right">
                                        <div className="flex items-center justify-end gap-2 opacity-0 group-hover:opacity-100 transition-opacity">
                                            <button onClick={() => handleOpenModal(index)} className="p-2 text-gray-400 hover:text-primary transition-colors cursor-pointer rounded-lg hover:bg-primary/10">
                                                <Edit2 size={18} />
                                            </button>
                                            <button onClick={() => handleDeleteSource(index)} className="p-2 text-gray-400 hover:text-red-500 transition-colors cursor-pointer rounded-lg hover:bg-red-50">
                                                <Trash2 size={18} />
                                            </button>
                                        </div>
                                    </td>
                                </tr>
                            ))}
                        </tbody>
                    </table>
                </div>
            </div>

            {/* 编辑 Modal */}
            {isModalOpen && (
                <div className="fixed inset-0 bg-black/50 backdrop-blur-sm z-50 flex items-center justify-center p-4">
                    <div className="bg-white rounded-2xl shadow-xl w-full max-w-lg overflow-hidden animate-fade-in">
                        <div className="flex items-center justify-between p-6 border-b border-gray-100">
                            <h2 className="text-xl font-bold flex items-center gap-2 text-gray-900">
                                {editingIndex !== null ? 'Edit Source' : 'Add Source'}
                            </h2>
                            <button onClick={() => setIsModalOpen(false)} className="p-2 text-gray-400 hover:text-gray-900 transition-colors rounded-full hover:bg-gray-100">
                                <X size={20} />
                            </button>
                        </div>

                        <div className="p-6 space-y-4 bg-gray-50/50">
                            <div>
                                <label className="block text-sm font-medium text-gray-700 mb-1">Name</label>
                                <input
                                    type="text"
                                    value={editForm.name}
                                    onChange={e => setEditForm({ ...editForm, name: e.target.value })}
                                    className="w-full px-4 py-2 border border-gray-200 rounded-xl focus:outline-none focus:border-primary focus:ring-1 focus:ring-primary transition-all bg-white"
                                />
                            </div>
                            <div className="grid grid-cols-2 gap-4">
                                <div>
                                    <label className="block text-sm font-medium text-gray-700 mb-1">Type</label>
                                    <select
                                        value={editForm.type}
                                        onChange={e => setEditForm({ ...editForm, type: e.target.value as SourceType })}
                                        className="w-full px-4 py-2 border border-gray-200 rounded-xl focus:outline-none focus:border-primary focus:ring-1 focus:ring-primary transition-all bg-white"
                                    >
                                        <option value="RSS">RSS</option>
                                        <option value="Twitter">Twitter</option>
                                        <option value="YouTube">YouTube</option>
                                        <option value="WeChat">WeChat</option>
                                    </select>
                                </div>
                                <div>
                                    <label className="block text-sm font-medium text-gray-700 mb-1">Status</label>
                                    <select
                                        value={editForm.enabled ? SourceStatus.Active : SourceStatus.Paused}
                                        onChange={e => setEditForm({ ...editForm, enabled: e.target.value === SourceStatus.Active as string })}
                                        className="w-full px-4 py-2 border border-gray-200 rounded-xl focus:outline-none focus:border-primary focus:ring-1 focus:ring-primary transition-all bg-white"
                                    >
                                        <option value={SourceStatus.Active}>Active</option>
                                        <option value={SourceStatus.Paused}>Paused</option>
                                    </select>
                                </div>
                            </div>
                            <div>
                                <label className="block text-sm font-medium text-gray-700 mb-1">Category (Tag)</label>
                                <input
                                    type="text"
                                    value={editForm.category || ''}
                                    onChange={e => setEditForm({ ...editForm, category: e.target.value })}
                                    className="w-full px-4 py-2 border border-gray-200 rounded-xl focus:outline-none focus:border-primary focus:ring-1 focus:ring-primary transition-all bg-white"
                                    placeholder="Enter a category or tag..."
                                />
                            </div>
                            <div>
                                <label className="block text-sm font-medium text-gray-700 mb-1">URL (Optional)</label>
                                <input
                                    type="text"
                                    value={editForm.url || ''}
                                    onChange={e => setEditForm({ ...editForm, url: e.target.value })}
                                    className="w-full px-4 py-2 border border-gray-200 rounded-xl focus:outline-none focus:border-primary focus:ring-1 focus:ring-primary transition-all bg-white"
                                />
                            </div>
                        </div>

                        <div className="p-6 border-t border-gray-100 bg-white flex justify-end gap-3">
                            <button onClick={() => setIsModalOpen(false)} className="px-5 py-2.5 border border-gray-200 text-gray-600 rounded-xl hover:bg-gray-50 transition-colors font-medium">
                                Cancel
                            </button>
                            <button onClick={handleSaveSource} className="px-5 py-2.5 bg-cta text-white rounded-xl hover:bg-orange-600 transition-colors font-medium flex items-center gap-2 shadow-sm shadow-cta/20">
                                <Save size={18} /> Save Source
                            </button>
                        </div>
                    </div>
                </div>
            )}
        </div>
    );
};

export default SourcesView;
