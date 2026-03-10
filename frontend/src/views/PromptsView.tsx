import { useState, useEffect } from 'react';
import { Save, History, AlignLeft, Send, CheckSquare } from 'lucide-react';
import { api } from '../services/api';

const PromptsView = () => {
    const [activeTab, setActiveTab] = useState<'filter' | 'extract' | 'distribute'>('filter');
    const [promptText, setPromptText] = useState('');
    const [version, setVersion] = useState('default');
    const [isLoading, setIsLoading] = useState(false);

    useEffect(() => {
        const loadPrompt = async () => {
            setIsLoading(true);
            try {
                // Determine stage string mapping from tab
                const stages = { filter: 'filter', extract: 'extract', distribute: 'format' };
                const stage = stages[activeTab];

                try {
                    const data = await api.getPrompt(stage);
                    setPromptText(data.content || '');
                } catch (e) {
                    console.log("No prompt found or error", e);
                    setPromptText('');
                }
            } finally {
                setIsLoading(false);
            }
        };
        loadPrompt();
    }, [activeTab, version]);

    const handleSave = async () => {
        const stages = { filter: 'filter', extract: 'extract', distribute: 'format' };
        const stage = stages[activeTab];
        try {
            await api.updatePrompt(stage, promptText, version);
            alert('Saved successfully!');
        } catch (e) {
            console.error('Failed to save prompt', e);
        }
    };

    return (
        <div className="flex flex-col h-full bg-white/30 backdrop-blur-md">
            {/* Header Area */}
            <div className="px-8 py-6 border-b border-gray-200/50 bg-white/50">
                <div className="flex justify-between items-center mb-6">
                    <div>
                        <h1 className="text-2xl font-bold text-gray-900 mb-1">Prompt Engineering</h1>
                        <p className="text-gray-500 text-sm">Configure instructions for different pipeline stages</p>
                    </div>
                    <div className="flex items-center gap-3">
                        <select
                            value={version}
                            onChange={(e) => setVersion(e.target.value)}
                            className="px-4 py-2 border border-gray-200 rounded-xl bg-white text-sm font-medium focus:outline-none focus:border-primary focus:ring-1 focus:ring-primary flex items-center gap-2"
                        >
                            <option value="default">v1.0 (Default)</option>
                            <option value="v1.1">v1.1 (Experimental)</option>
                        </select>
                        <button
                            onClick={handleSave}
                            className="bg-primary hover:bg-orange-600 text-white px-5 py-2 rounded-xl flex items-center gap-2 font-medium transition-colors shadow-sm shadow-primary/20 min-touch-target"
                        >
                            <Save size={18} /> Save Changes
                        </button>
                    </div>
                </div>

                {/* Main Tabs */}
                <div className="flex gap-2">
                    <button
                        onClick={() => setActiveTab('filter')}
                        className={`flex items-center gap-2 px-5 py-2.5 rounded-xl font-medium text-sm transition-all ${activeTab === 'filter' ? 'bg-white shadow-sm text-primary' : 'text-gray-500 hover:bg-white/50 hover:text-gray-800'
                            }`}
                    >
                        <CheckSquare size={16} /> Filtering Standards
                    </button>
                    <button
                        onClick={() => setActiveTab('extract')}
                        className={`flex items-center gap-2 px-5 py-2.5 rounded-xl font-medium text-sm transition-all ${activeTab === 'extract' ? 'bg-white shadow-sm text-primary' : 'text-gray-500 hover:bg-white/50 hover:text-gray-800'
                            }`}
                    >
                        <AlignLeft size={16} /> Information Extraction
                    </button>
                    <button
                        onClick={() => setActiveTab('distribute')}
                        className={`flex items-center gap-2 px-5 py-2.5 rounded-xl font-medium text-sm transition-all ${activeTab === 'distribute' ? 'bg-white shadow-sm text-primary' : 'text-gray-500 hover:bg-white/50 hover:text-gray-800'
                            }`}
                    >
                        <Send size={16} /> Distribution Format
                    </button>
                </div>
            </div>

            {/* Sub-tabs for Distribute */}
            {activeTab === 'distribute' && (
                <div className="px-8 py-3 border-b border-gray-100 bg-gray-50/50 flex gap-4 text-sm">
                    <button className="text-primary font-medium px-3 py-1 bg-primary/10 rounded-lg">Bot / Feeds Messages</button>
                    <button className="text-gray-500 hover:text-gray-800 font-medium px-3 py-1 hover:bg-gray-200/50 rounded-lg transition-colors">Local Storage Format</button>
                </div>
            )}

            {/* Editor Area */}
            <div className="flex-1 p-8 overflow-hidden flex flex-col">
                {isLoading ? (
                    <div className="flex-1 flex items-center justify-center text-gray-400">Loading prompt...</div>
                ) : (
                    <div className="flex-1 bg-white rounded-2xl shadow-sm border border-gray-100 overflow-hidden flex flex-col">
                        <div className="bg-gray-50 border-b border-gray-100 px-4 py-2 flex items-center gap-4 text-sm text-gray-500 font-medium">
                            <span>Markdown Supported</span>
                            <div className="h-4 w-px bg-gray-300"></div>
                            <button className="flex items-center gap-1.5 hover:text-gray-800 transition-colors"><History size={14} /> View History</button>
                        </div>
                        <textarea
                            value={promptText}
                            onChange={(e) => setPromptText(e.target.value)}
                            placeholder="Enter the system instruction for the LLM here..."
                            className="flex-1 w-full p-6 resize-none focus:outline-none font-mono text-sm leading-relaxed text-gray-700 bg-transparent scrollbar-thin scrollbar-thumb-gray-200"
                        />
                    </div>
                )}
            </div>
        </div>
    );
};

export default PromptsView;
