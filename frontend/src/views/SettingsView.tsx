import { useState, useEffect } from 'react';
import { Cpu, Globe, Key, Link as LinkIcon, RefreshCw, Bot, CheckCircle, AlertCircle } from 'lucide-react';
import { api } from '../services/api';

const SettingsView = () => {
    const [provider, setProvider] = useState('zhipu');
    const [apiKey, setApiKey] = useState('');
    const [baseUrl, setBaseUrl] = useState('');
    const [proxyUrl, setProxyUrl] = useState('');
    const [isTesting, setIsTesting] = useState(false);
    const [testResult, setTestResult] = useState<'success' | 'error' | null>(null);

    // Bot settings
    const [tgToken, setTgToken] = useState('');
    const [tgProxy, setTgProxy] = useState('');
    const [feishuWebhook, setFeishuWebhook] = useState('');

    useEffect(() => {
        const loadSettings = async () => {
            try {
                const providersInfo = await api.getProviderSettings();
                if (providersInfo && providersInfo.active_provider) {
                    setProvider(providersInfo.active_provider);
                    const activeConf = providersInfo.providers[providersInfo.active_provider];
                    if (activeConf) {
                        setApiKey(activeConf.api_key || '');
                        setBaseUrl(activeConf.base_url || '');
                    }
                }
                const envInfo = await api.getEnvironmentSettings();
                if (envInfo) {
                    setProxyUrl(envInfo.proxy_url || '');
                }
                const botsInfo = await api.getBots().catch(() => null);
                if (botsInfo) {
                    setTgToken(botsInfo.telegram_bot_token || '');
                    setTgProxy(botsInfo.telegram_proxy_url || '');
                    setFeishuWebhook(botsInfo.feishu_webhook_url || '');
                }
            } catch (error) {
                console.error("Failed to load settings", error);
            }
        };
        loadSettings();
    }, []);

    const handleSaveProviders = async () => {
        try {
            await api.updateProviderSettings({
                active_provider: provider,
                providers: {
                    [provider]: { api_key: apiKey, base_url: baseUrl }
                }
            });
            alert('Settings saved!');
        } catch (error) {
            console.error("Failed to save providers", error);
        }
    };

    const handleSaveEnv = async () => {
        try {
            await api.updateEnvironmentSettings({ proxy_url: proxyUrl });
            alert('Network settings saved!');
        } catch (error) {
            console.error("Failed to save environment", error);
        }
    };

    const handleSaveBots = async () => {
        try {
            await api.updateBots({
                telegram_bot_token: tgToken,
                telegram_proxy_url: tgProxy,
                feishu_webhook_url: feishuWebhook
            });
            alert('Bot settings saved!');
        } catch (error) {
            console.error("Failed to save bots", error);
        }
    };

    const handleTestConnection = async () => {
        setIsTesting(true);
        setTestResult(null);
        try {
            const result = await api.client.post('/api/v1/system/test-connection');
            if (result.status === 200) {
                setTestResult('success');
            } else {
                setTestResult('error');
            }
        } catch (error) {
            setTestResult('error');
        }
        setIsTesting(false);
    };

    return (
        <div className="p-8 md:p-12 lg:p-16 max-w-5xl mx-auto space-y-12 animate-fade-in pb-24">
            <div>
                <h1 className="text-3xl font-bold text-gray-900 mb-2">Settings</h1>
                <p className="text-gray-500">Manage your AI engines, network configurations, and dispatch bots.</p>
            </div>

            <div className="grid grid-cols-1 lg:grid-cols-2 gap-12">

                {/* AI Providers Section */}
                <section className="bg-white/70 backdrop-blur-xl border border-white/40 rounded-[2rem] p-8 shadow-sm">
                    <div className="flex justify-between items-center mb-6">
                        <h3 className="text-xl font-bold text-gray-900 flex items-center gap-2"><Cpu size={22} className="text-primary" /> Model Provider</h3>
                        <button onClick={handleSaveProviders} className="text-sm font-medium text-primary hover:bg-primary/5 px-4 py-2 rounded-xl transition-colors">Save</button>
                    </div>

                    <div className="space-y-5">
                        <div>
                            <label className="block text-sm font-medium text-gray-700 mb-2">Active Engine</label>
                            <select value={provider} onChange={(e) => setProvider(e.target.value)} className="w-full px-4 py-3 border border-gray-100 rounded-xl focus:outline-none focus:border-primary focus:ring-1 focus:ring-primary transition-all bg-white/50 text-gray-700">
                                <option value="zhipu">Zhipu AI (GLM-4)</option>
                                <option value="anthropic">Anthropic Claude</option>
                                <option value="openai">OpenAI</option>
                                <option value="ollama">Ollama (Local)</option>
                                <option value="deepseek">DeepSeek</option>
                            </select>
                        </div>
                        <div>
                            <label className="block text-sm font-medium text-gray-700 mb-2">API Key</label>
                            <div className="relative">
                                <Key className="absolute left-4 top-1/2 -translate-y-1/2 text-gray-400" size={16} />
                                <input type="password" value={apiKey} onChange={e => setApiKey(e.target.value)} placeholder="sk-..." className="w-full pl-11 pr-4 py-3 border border-gray-100 rounded-xl focus:outline-none focus:border-primary focus:ring-1 focus:ring-primary transition-all bg-white/50" />
                            </div>
                        </div>
                        <div>
                            <label className="block text-sm font-medium text-gray-700 mb-2">Base URL (Optional)</label>
                            <input type="text" value={baseUrl} onChange={e => setBaseUrl(e.target.value)} placeholder="https://api..." className="w-full px-4 py-3 border border-gray-100 rounded-xl focus:outline-none focus:border-primary focus:ring-1 focus:ring-primary transition-all bg-white/50 font-mono text-sm" />
                        </div>
                    </div>
                </section>

                {/* Network & Preferences */}
                <section className="space-y-8">
                    <div className="bg-white/70 backdrop-blur-xl border border-white/40 rounded-[2rem] p-8 shadow-sm">
                        <div className="flex justify-between items-center mb-6">
                            <h3 className="text-xl font-bold text-gray-900 flex items-center gap-2"><Globe size={22} className="text-primary" /> Network & Proxy</h3>
                            <button onClick={handleSaveEnv} className="text-sm font-medium text-primary hover:bg-primary/5 px-4 py-2 rounded-xl transition-colors">Save</button>
                        </div>

                        <div className="space-y-5">
                            <div>
                                <label className="block text-sm font-medium text-gray-700 mb-2">Proxy URL</label>
                                <div className="relative">
                                    <LinkIcon className="absolute left-4 top-1/2 -translate-y-1/2 text-gray-400" size={16} />
                                    <input type="text" value={proxyUrl} onChange={e => setProxyUrl(e.target.value)} placeholder="http://127.0.0.1:7890" className="w-full pl-11 pr-4 py-3 border border-gray-100 rounded-xl focus:outline-none focus:border-primary focus:ring-1 focus:ring-primary transition-all bg-white/50 font-mono text-sm" />
                                </div>
                                <p className="text-xs text-gray-500 mt-2">Required for accessing global APIs like Anthropic/OpenAI in restricted regions.</p>
                            </div>

                            <button
                                onClick={handleTestConnection}
                                disabled={isTesting}
                                className={`w-full flex items-center justify-center gap-2 py-3 rounded-xl font-medium transition-all border ${isTesting ? 'bg-gray-50 text-gray-400 border-gray-100' : 'bg-white hover:bg-gray-50 text-gray-700 border-gray-200'
                                    }`}
                            >
                                <RefreshCw size={16} className={isTesting ? 'animate-spin' : ''} />
                                {isTesting ? 'Testing Connection...' : 'Test Main Provider Connection'}
                            </button>

                            {testResult === 'success' && (
                                <div className="flex items-center gap-2 text-sm text-emerald-600 bg-emerald-50 px-4 py-3 rounded-xl">
                                    <CheckCircle size={16} /> Connection successful! API is reachable.
                                </div>
                            )}
                            {testResult === 'error' && (
                                <div className="flex items-center gap-2 text-sm text-red-600 bg-red-50 px-4 py-3 rounded-xl">
                                    <AlertCircle size={16} /> Connection failed. Check your API Key or Network/Proxy.
                                </div>
                            )}
                        </div>
                    </div>

                    <div className="bg-white/70 backdrop-blur-xl border border-white/40 rounded-[2rem] p-8 shadow-sm">
                        <div className="flex justify-between items-center mb-6">
                            <h3 className="text-xl font-bold text-gray-900 flex items-center gap-2"><Bot size={22} className="text-primary" /> Dispatch Bots</h3>
                            <button onClick={handleSaveBots} className="text-sm font-medium text-primary hover:bg-primary/5 px-4 py-2 rounded-xl transition-colors">Save</button>
                        </div>

                        <div className="space-y-5">
                            <div>
                                <label className="block text-sm font-medium text-gray-700 mb-2">Telegram Bot Token</label>
                                <input type="password" value={tgToken} onChange={e => setTgToken(e.target.value)} placeholder="000000000:AAAAA..." className="w-full px-4 py-3 border border-gray-100 rounded-xl focus:outline-none focus:border-primary focus:ring-1 focus:ring-primary transition-all bg-white/50 font-mono text-sm" />
                            </div>
                            <div>
                                <label className="block text-sm font-medium text-gray-700 mb-2">Telegram Proxy URL (Optional)</label>
                                <div className="relative">
                                    <LinkIcon className="absolute left-4 top-1/2 -translate-y-1/2 text-gray-400" size={16} />
                                    <input type="text" value={tgProxy} onChange={e => setTgProxy(e.target.value)} placeholder="http://127.0.0.1:7890" className="w-full pl-11 pr-4 py-3 border border-gray-100 rounded-xl focus:outline-none focus:border-primary focus:ring-1 focus:ring-primary transition-all bg-white/50 font-mono text-sm" />
                                </div>
                            </div>
                            <div>
                                <label className="block text-sm font-medium text-gray-700 mb-2">Feishu Webhook URL</label>
                                <input type="text" value={feishuWebhook} onChange={e => setFeishuWebhook(e.target.value)} placeholder="https://open.feishu.cn/open-apis/bot/v2/hook/..." className="w-full px-4 py-3 border border-gray-100 rounded-xl focus:outline-none focus:border-primary focus:ring-1 focus:ring-primary transition-all bg-white/50 font-mono text-sm" />
                            </div>
                        </div>
                    </div>
                </section>
            </div>
        </div>
    );
};

export default SettingsView;
