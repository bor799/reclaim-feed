/**
 * SourcesView - 使用真实 API 的示例
 *
 * 将此文件内容复制到 frontend/src/views/SourcesView.tsx
 * 修改点：
 * 1. 导入 api 客户端
 * 2. 使用 useEffect 加载数据
 * 3. 替换 mockSources 为真实数据
 */

import { useState, useEffect, useMemo } from 'react';
import { Plus, Trash2, Edit2, Search, Filter, Refresh } from 'lucide-react';
import { api, Source } from '../services/api'; // ← 新增
// import { mockSources } from '../data/mockData'; // ← 移除
import { SourceStatus } from '../types';
import { filterBySearchTerm } from '../utils';

const SourcesView = () => {
  const [searchTerm, setSearchTerm] = useState('');
  const [sources, setSources] = useState<Source[]>([]); // ← 新增
  const [loading, setLoading] = useState(true); // ← 新增

  // ← 新增: 加载真实数据
  useEffect(() => {
    const fetchSources = async () => {
      try {
        setLoading(true);
        const data = await api.getSources();
        setSources(data);
      } catch (error) {
        console.error('Failed to fetch sources:', error);
      } finally {
        setLoading(false);
      }
    };

    fetchSources();
  }, []);

  // Filter sources based on search term
  const filteredSources = useMemo(() => {
    return filterBySearchTerm(sources, searchTerm); // ← 使用真实数据
  }, [sources, searchTerm]);

  return (
    <div className="p-8 max-w-6xl mx-auto">
      <div className="flex justify-between items-center mb-8">
        <div>
          <h1 className="text-3xl font-bold text-text mb-2">Sources</h1>
          <p className="text-gray-500">Manage your high-quality information feeds.</p>
        </div>
        <div className="flex gap-3">
          {/* ← 新增: 刷新按钮 */}
          <button
            onClick={() => window.location.reload()}
            className="px-4 py-2.5 border border-gray-200 rounded-lg flex items-center gap-2 text-gray-600 hover:bg-gray-50 transition-colors"
          >
            <Refresh size={18} />
          </button>
          <button className="bg-cta hover:bg-orange-600 text-white px-5 py-2.5 rounded-lg flex items-center gap-2 font-medium transition-colors">
            <Plus size={20} />
            Add Source
          </button>
        </div>
      </div>

      {/* ← 新增: 加载状态 */}
      {loading ? (
        <div className="text-center py-12 text-gray-500">
          <Refresh className="animate-spin mx-auto mb-3" size={32} />
          <p>Loading sources...</p>
        </div>
      ) : (
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
                onChange={(e) => setSearchTerm(e.targetvalue)}
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
                  <th className="py-4 px-6 font-medium">Name</th>
                  <th className="py-4 px-6 font-medium">Type</th>
                  <th className="py-4 px-6 font-medium">URL/Identifier</th>
                  <th className="py-4 px-6 font-medium">Category</th>
                  <th className="py-4 px-6 font-medium">Status</th>
                  <th className="py-4 px-6 font-medium text-right">Actions</th>
                </tr>
              </thead>
              <tbody>
                {filteredSources.map((source: Source) => (
                  <tr key={source.id} className="border-b border-gray-50 hover:bg-gray-50/50 transition-colors group">
                    <td className="py-4 px-6 font-medium text-gray-900">{source.name}</td>
                    <td className="py-4 px-6">
                      <span className="inline-block px-3 py-1 bg-gray-100 text-gray-600 text-sm rounded-full font-medium">
                        {source.type}
                      </span>
                    </td>
                    <td className="py-4 px-6 text-gray-500 text-sm truncate max-w-xs">{source.url}</td>
                    <td className="py-4 px-6 text-gray-500 text-sm">{source.category || '-'}</td>
                    <td className="py-4 px-6">
                      <span className={`inline-flex items-center gap-1.5 px-3 py-1 rounded-full text-sm font-medium ${
                        source.enabled
                          ? 'bg-emerald-50 text-emerald-700'
                          : 'bg-amber-50 text-amber-700'
                      }`}>
                        <span className={`w-1.5 h-1.5 rounded-full ${source.enabled ? 'bg-emerald-500' : 'bg-amber-500'}`}></span>
                        {source.enabled ? 'Active' : 'Paused'}
                      </span>
                    </td>
                    <td className="py-4 px-6 text-right">
                      <div className="flex items-center justify-end gap-2 opacity-0 group-hover:opacity-100 transition-opacity">
                        <button className="p-2 text-gray-400 hover:text-primary transition-colors cursor-pointer rounded-lg hover:bg-primary/10">
                          <Edit2 size={18} />
                        </button>
                        <button className="p-2 text-gray-400 hover:text-red-500 transition-colors cursor-pointer rounded-lg hover:bg-red-50">
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
      )}
    </div>
  );
};

export default SourcesView;
