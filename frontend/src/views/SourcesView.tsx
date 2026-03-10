import { useState, useMemo, useEffect } from 'react';
import { Plus, Trash2, Edit2, Search, X, Save, MoreVertical } from 'lucide-react';
import { Source, SourceStatus, SourceType } from '../types';
import { filterBySearchTerm } from '../utils';
import { api } from '../services/api';

const SourcesView = () => {
    const [searchTerm, setSearchTerm] = useState('');
    const [sources, setSources] = useState<Source[]>([]);
    const [isModalOpen, setIsModalOpen] = useState(false);
    const [editingIndex, setEditingIndex] = useState<number | null>(null);
    const [activeMenuId, setActiveMenuId] = useState<number | null>(null);
    const [isScrolled, setIsScrolled] = useState(false);
    const [editForm, setEditForm] = useState<Partial<Source & { cron?: string }>>({
        name: '', type: SourceType.RSS, url: '', enabled: true, status: SourceStatus.Active, category: '', cron: '0 */8 * * *'
    });


    useEffect(() => {
        loadSources();
    }, []);

    useEffect(() => {
        const handleClickOutside = () => setActiveMenuId(null);
        document.addEventListener('click', handleClickOutside);
        return () => document.removeEventListener('click', handleClickOutside);
    }, []);

    const loadSources = async () => {
        try {
            const data = await api.getSources();
            setSources(data);
        } catch (error) {
            console.error('Failed to load sources', error);
        }
    };

    const filteredSources = useMemo(() => {
        return filterBySearchTerm(sources, searchTerm);
    }, [searchTerm, sources]);

    const handleOpenModal = (index: number | null = null) => {
        if (index !== null) {
            setEditingIndex(index);
            setEditForm(sources[index]);
        } else {
            setEditingIndex(null);
            setEditForm({ name: '', type: SourceType.RSS, url: '', enabled: true, status: SourceStatus.Active, category: '', cron: '0 */8 * * *' });
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

    const getSourceTypeColor = (type: string) => {
        const colors = {
            'RSS': 'bg-blue-50 text-blue-700',
            'Twitter': 'bg-sky-50 text-sky-700',
            'YouTube': 'bg-red-50 text-red-700',
            'WeChat': 'bg-green-50 text-green-700',
        };
        return colors[type as keyof typeof colors] || 'bg-gray-100 text-gray-600';
    };

    return (
        <div
            className="flex flex-col h-full bg-transparent overflow-hidden"
        >
            {/* Sticky Header Area */}
            <div className={`px-4 md:px-8 transition-all duration-300 z-30 ${isScrolled ? 'bg-white/80 backdrop-blur-xl border-b border-gray-200/50 py-3 shadow-sm' : 'bg-transparent py-6'}`}>
                {/* Title and Top Row */}
                <div className={`flex flex-col sm:flex-row justify-between items-start sm:items-center gap-4 transition-all duration-300 ${isScrolled ? 'mb-3' : 'mb-6'}`}>
                    <div>
                        <h1 className={`font-bold text-text transition-all ${isScrolled ? 'text-xl md:text-2xl' : 'text-2xl md:text-3xl'} mb-1`}>Sources</h1>
                        <p className={`text-gray-500 transition-all ${isScrolled ? 'text-xs md:text-sm' : 'text-sm md:text-base'}`}>Manage your information feeds</p>
                    </div>
                    <button
                        onClick={() => handleOpenModal(null)}
                        className="w-full sm:w-auto bg-cta hover:bg-orange-600 text-white px-5 py-2.5 rounded-xl flex items-center justify-center gap-2 font-medium transition-colors shadow-sm shadow-cta/20 min-touch-target"
                    >
                        <Plus size={20} />
                        Add Source
                    </button>
                </div>

                {/* Search Bar */}
                <div className="relative">
                    <Search className="absolute left-4 top-1/2 -translate-y-1/2 text-gray-400" size={18} />
                    <input
                        type="text"
                        placeholder="Search sources..."
                        className={`w-full pl-11 pr-4 transition-all bg-white/60 backdrop-blur-xl border border-white/40 rounded-2xl focus:outline-none focus:border-primary focus:ring-1 focus:ring-primary text-base ${isScrolled ? 'py-2' : 'py-3'}`}
                        value={searchTerm}
                        onChange={(e) => setSearchTerm(e.target.value)}
                    />
                </div>
            </div>

            {/* Scrollable Content */}
            <div
                className="flex-1 overflow-y-auto px-4 md:px-8 pb-24 pt-4 md:pb-8"
                onScroll={(e) => setIsScrolled(e.currentTarget.scrollTop > 20)}
            >

                {/* Mobile Card Grid */}
                <div className="grid grid-cols-1 sm:grid-cols-2 lg:grid-cols-3 gap-4 md:hidden">
                    {filteredSources.map((source: Source, index: number) => (
                        <div key={index} className="bg-white/70 backdrop-blur-xl border border-white/40 rounded-2xl p-4 shadow-sm">
                            <div className="flex items-start justify-between mb-3">
                                <div className="flex-1 min-w-0">
                                    <h3 className="font-semibold text-gray-900 truncate">{source.name}</h3>
                                    <p className="text-xs text-gray-500 mt-0.5 truncate">{source.url}</p>
                                </div>
                                <div className="relative">
                                    <button
                                        onClick={(e) => { e.stopPropagation(); setActiveMenuId(activeMenuId === index ? null : index); }}
                                        className="p-2 text-gray-400 hover:text-gray-600 hover:bg-gray-100 rounded-lg transition-colors min-touch-target"
                                    >
                                        <MoreVertical size={18} />
                                    </button>
                                    {activeMenuId === index && (
                                        <div className="absolute right-0 top-full mt-1 bg-white rounded-xl shadow-lg border border-gray-100 py-1 z-10 min-w-[120px]">
                                            <button onClick={() => { setActiveMenuId(null); handleOpenModal(index); }} className="w-full px-4 py-2 text-left text-sm hover:bg-gray-50 flex items-center gap-2">
                                                <Edit2 size={14} /> Edit
                                            </button>
                                            <button onClick={() => { setActiveMenuId(null); handleDeleteSource(index); }} className="w-full px-4 py-2 text-left text-sm text-red-600 hover:bg-red-50 flex items-center gap-2">
                                                <Trash2 size={14} /> Delete
                                            </button>
                                        </div>
                                    )}
                                </div>
                            </div>

                            <div className="flex items-center gap-2 mb-3">
                                <span className={`px-2.5 py-1 text-xs font-medium rounded-full ${getSourceTypeColor(source.type)}`}>
                                    {source.type}
                                </span>
                                <span className={`inline-flex items-center gap-1.5 px-2.5 py-1 rounded-full text-xs font-medium ${source.enabled
                                    ? 'bg-emerald-50 text-emerald-700'
                                    : 'bg-amber-50 text-amber-700'
                                    }`}>
                                    <span className={`w-1.5 h-1.5 rounded-full ${source.enabled ? 'bg-emerald-500' : 'bg-amber-500'}`}></span>
                                    {source.enabled ? 'Active' : 'Paused'}
                                </span>
                            </div>

                            {source.category && (
                                <span className="inline-block px-2.5 py-1 bg-blue-50 text-blue-700 text-xs rounded-full font-medium">
                                    {source.category}
                                </span>
                            )}

                            {source.cron && (
                                <div className="mt-3 text-xs text-primary font-mono bg-primary/5 px-2 py-1 rounded-lg">
                                    {source.cron}
                                </div>
                            )}
                        </div>
                    ))}
                </div>

                {/* Desktop Table */}
                <div className="hidden md:block bg-white/60 backdrop-blur-xl border border-white/40 rounded-3xl overflow-hidden shadow-sm">
                    <table className="w-full text-left border-collapse">
                        <thead>
                            <tr className="bg-white/40 border-b border-gray-100 text-sm text-gray-500">
                                <th className="py-4 px-6 font-medium">Name</th>
                                <th className="py-4 px-6 font-medium w-24">Type</th>
                                <th className="py-4 px-6 font-medium">URL & Cron</th>
                                <th className="py-4 px-6 font-medium">Category</th>
                                <th className="py-4 px-6 font-medium w-32">Status</th>
                                <th className="py-4 px-6 font-medium text-right">Actions</th>
                            </tr>
                        </thead>
                        <tbody>
                            {filteredSources.map((source: Source, index: number) => (
                                <tr key={index} className="border-b border-gray-50 hover:bg-white/60 transition-colors group">
                                    <td className="py-4 px-6 font-medium text-gray-900">{source.name}</td>
                                    <td className="py-4 px-6">
                                        <span className={`inline-block px-3 py-1 text-sm rounded-full font-medium ${getSourceTypeColor(source.type)}`}>
                                            {source.type}
                                        </span>
                                    </td>
                                    <td className="py-4 px-6 text-gray-500 text-sm">
                                        <div className="truncate max-w-xs">{source.url}</div>
                                        <div className="text-xs text-primary mt-1 font-mono">{source.cron || '0 */8 * * *'}</div>
                                    </td>
                                    <td className="py-4 px-6">
                                        <span className="inline-block px-3 py-1 bg-blue-50 text-blue-700 text-sm rounded-full font-medium">
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

                {/* Add/Edit Modal - Full screen on mobile */}
                {isModalOpen && (
                    <div className="fixed inset-0 bg-text/20 backdrop-blur-sm z-50 flex items-end sm:items-center justify-center p-0 sm:p-4">
                        <div className="bg-white w-full sm:max-w-lg rounded-t-3xl sm:rounded-3xl shadow-2xl overflow-hidden max-h-[90vh] sm:max-h-none overflow-y-auto animate-slide-up">
                            <div className="sticky top-0 bg-white flex items-center justify-between p-4 sm:p-6 border-b border-gray-100">
                                <h2 className="text-lg sm:text-xl font-bold text-gray-900">
                                    {editingIndex !== null ? 'Edit Source' : 'Add Source'}
                                </h2>
                                <button onClick={() => setIsModalOpen(false)} className="p-2 text-gray-400 hover:text-gray-900 transition-colors rounded-full hover:bg-gray-100 min-touch-target">
                                    <X size={20} />
                                </button>
                            </div>

                            <div className="p-4 sm:p-6 space-y-4">
                                <div>
                                    <label className="block text-sm font-medium text-gray-700 mb-1.5">Name</label>
                                    <input
                                        type="text"
                                        value={editForm.name}
                                        onChange={e => setEditForm({ ...editForm, name: e.target.value })}
                                        className="w-full px-4 py-3 border border-gray-200 rounded-xl focus:outline-none focus:border-primary focus:ring-1 focus:ring-primary transition-all bg-white/50"
                                        placeholder="Source name..."
                                    />
                                </div>

                                <div className="grid grid-cols-2 gap-4">
                                    <div>
                                        <label className="block text-sm font-medium text-gray-700 mb-1.5">Type</label>
                                        <select
                                            value={editForm.type}
                                            onChange={e => setEditForm({ ...editForm, type: e.target.value as SourceType })}
                                            className="w-full px-4 py-3 border border-gray-200 rounded-xl focus:outline-none focus:border-primary focus:ring-1 focus:ring-primary transition-all bg-white/50"
                                        >
                                            <option value="RSS">RSS</option>
                                            <option value="Twitter">Twitter</option>
                                            <option value="YouTube">YouTube</option>
                                            <option value="WeChat">WeChat</option>
                                        </select>
                                    </div>
                                    <div>
                                        <label className="block text-sm font-medium text-gray-700 mb-1.5">Status</label>
                                        <select
                                            value={editForm.enabled ? SourceStatus.Active : SourceStatus.Paused}
                                            onChange={e => setEditForm({ ...editForm, enabled: e.target.value === SourceStatus.Active })}
                                            className="w-full px-4 py-3 border border-gray-200 rounded-xl focus:outline-none focus:border-primary focus:ring-1 focus:ring-primary transition-all bg-white/50"
                                        >
                                            <option value={SourceStatus.Active}>Active</option>
                                            <option value={SourceStatus.Paused}>Paused</option>
                                        </select>
                                    </div>
                                </div>

                                <div>
                                    <label className="block text-sm font-medium text-gray-700 mb-1.5">Category</label>
                                    <input
                                        type="text"
                                        value={editForm.category || ''}
                                        onChange={e => setEditForm({ ...editForm, category: e.target.value })}
                                        className="w-full px-4 py-3 border border-gray-200 rounded-xl focus:outline-none focus:border-primary focus:ring-1 focus:ring-primary transition-all bg-white/50"
                                        placeholder="e.g. Tech, Design..."
                                    />
                                </div>

                                <div>
                                    <label className="block text-sm font-medium text-gray-700 mb-1.5">URL</label>
                                    <input
                                        type="text"
                                        value={editForm.url || ''}
                                        onChange={e => setEditForm({ ...editForm, url: e.target.value })}
                                        className="w-full px-4 py-3 border border-gray-200 rounded-xl focus:outline-none focus:border-primary focus:ring-1 focus:ring-primary transition-all bg-white/50"
                                        placeholder="https://..."
                                    />
                                </div>

                                <div>
                                    <label className="block text-sm font-medium text-gray-700 mb-1.5">Cron Schedule</label>
                                    <input
                                        type="text"
                                        value={editForm.cron || ''}
                                        onChange={e => setEditForm({ ...editForm, cron: e.target.value })}
                                        className="w-full px-4 py-3 border border-gray-200 rounded-xl focus:outline-none focus:border-primary focus:ring-1 focus:ring-primary transition-all bg-white/50 font-mono text-sm"
                                        placeholder="0 */8 * * *"
                                    />
                                </div>
                            </div>

                            <div className="sticky bottom-0 bg-white border-t border-gray-100 p-4 sm:p-6 flex justify-end gap-3">
                                <button onClick={() => setIsModalOpen(false)} className="px-5 py-2.5 border border-gray-200 text-gray-600 rounded-xl hover:bg-gray-50 transition-colors font-medium">
                                    Cancel
                                </button>
                                <button onClick={handleSaveSource} className="px-5 py-2.5 bg-cta text-white rounded-xl hover:bg-orange-600 transition-colors font-medium flex items-center gap-2 shadow-sm shadow-cta/20">
                                    <Save size={18} /> Save
                                </button>
                            </div>
                        </div>
                    </div>
                )}
            </div>
        </div>
    );
};

export default SourcesView;
