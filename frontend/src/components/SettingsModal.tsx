import { X, Cpu, Globe, Key } from 'lucide-react';
import { useState } from 'react';

const SettingsModal = ({ onClose }: { onClose: () => void }) => {
    const [provider, setProvider] = useState('anthropic');
    const [lang, setLang] = useState('en');

    return (
        <div className="fixed inset-0 bg-text/20 backdrop-blur-sm z-[200] flex items-center justify-center p-4">
            <div className="bg-white/80 backdrop-blur-2xl border border-white/50 rounded-[2rem] shadow-2xl w-full max-w-2xl overflow-hidden animate-fade-in relative flex max-h-[90vh]">

                {/* Modal Sidebar */}
                <div className="w-64 bg-gray-50/50 border-r border-white/20 p-6 hidden md:block">
                    <h2 className="text-2xl font-bold mb-8 text-gray-900">Settings</h2>

                    <nav className="space-y-2 text-sm font-medium">
                        <button className="flex justify-start w-full items-center gap-3 px-4 py-3 bg-white rounded-2xl shadow-sm text-primary transition-all">
                            <Cpu size={18} /> AI Providers
                        </button>
                        <button className="flex w-full items-center justify-start gap-3 px-4 py-3 hover:bg-white/40 rounded-2xl text-gray-600 transition-all">
                            <Globe size={18} /> Preferences
                        </button>
                    </nav>
                </div>

                {/* Content */}
                <div className="flex-1 p-8 overflow-y-auto">
                    <button onClick={onClose} className="absolute top-6 right-6 p-2 text-gray-400 hover:text-gray-900 transition-colors cursor-pointer rounded-full hover:bg-gray-100">
                        <X size={20} />
                    </button>

                    <div className="space-y-10 mt-4 md:mt-0">
                        <section>
                            <h3 className="text-xl font-bold text-gray-900 mb-6 flex items-center gap-2"><Cpu size={22} className="text-primary" /> Model Provider</h3>
                            <div className="space-y-5">
                                <div>
                                    <label className="block text-sm font-medium text-gray-700 mb-2">Active Engine</label>
                                    <select value={provider} onChange={(e) => setProvider(e.target.value)} className="w-full px-4 py-2.5 border border-black/5 rounded-xl focus:outline-none focus:border-primary focus:ring-2 focus:ring-primary/20 transition-all bg-white/50 backdrop-blur shadow-sm cursor-pointer text-gray-700">
                                        <option value="anthropic">Anthropic Claude</option>
                                        <option value="openai">OpenAI</option>
                                        <option value="ollama">Ollama (Local)</option>
                                        <option value="deepseek">DeepSeek</option>
                                    </select>
                                </div>
                                <div>
                                    <label className="block text-sm font-medium text-gray-700 mb-2">API Key</label>
                                    <div className="relative">
                                        <Key className="absolute left-3 top-1/2 -translate-y-1/2 text-gray-400" size={16} />
                                        <input type="password" placeholder="sk-..." className="w-full pl-10 pr-4 py-2.5 border border-black/5 rounded-xl focus:outline-none focus:border-primary focus:ring-2 focus:ring-primary/20 transition-all bg-white/50 backdrop-blur shadow-sm" />
                                    </div>
                                </div>
                                <div>
                                    <label className="block text-sm font-medium text-gray-700 mb-2">Base URL (Optional)</label>
                                    <input type="text" placeholder="https://api.anthropic.com" className="w-full px-4 py-2.5 border border-black/5 rounded-xl focus:outline-none focus:border-primary focus:ring-2 focus:ring-primary/20 transition-all bg-white/50 backdrop-blur font-mono text-sm shadow-sm" />
                                </div>
                            </div>
                        </section>

                        <hr className="border-white/20" />

                        <section>
                            <h3 className="text-xl font-bold text-gray-900 mb-6 flex items-center gap-2"><Globe size={22} className="text-primary" /> General</h3>
                            <div className="space-y-5">
                                <div>
                                    <label className="block text-sm font-medium text-gray-700 mb-2">Interface Language</label>
                                    <select value={lang} onChange={(e) => setLang(e.target.value)} className="w-full px-4 py-2.5 border border-black/5 rounded-xl focus:outline-none focus:border-primary focus:ring-2 focus:ring-primary/20 transition-all bg-white/50 backdrop-blur shadow-sm cursor-pointer text-gray-700">
                                        <option value="en">English</option>
                                        <option value="zh">简体中文</option>
                                    </select>
                                </div>
                            </div>
                        </section>
                    </div>
                </div>
            </div>
        </div>
    );
};

export default SettingsModal;
