import { Outlet, useNavigate } from 'react-router-dom';
import { Search, Command, Link as LinkIcon, ArrowRight, Loader2, CheckCircle, AlertCircle } from 'lucide-react';
import { useState } from 'react';
import { api } from '../services/api';
import { CommandPaletteWithTrigger } from './CommandPaletteWithTrigger';
import BottomNav from './BottomNav';

const ImmersiveLayout = () => {
    const navigate = useNavigate();
    const [extractUrl, setExtractUrl] = useState('');
    const [isExtracting, setIsExtracting] = useState(false);
    const [extractStatus, setExtractStatus] = useState<'idle' | 'success' | 'error'>('idle');

    const handleExtract = async (e: React.FormEvent) => {
        e.preventDefault();
        if (!extractUrl.trim() || isExtracting) return;

        setIsExtracting(true);
        setExtractStatus('idle');
        try {
            await api.quickExtract([extractUrl]);
            setExtractStatus('success');
            setExtractUrl('');
            setTimeout(() => setExtractStatus('idle'), 3000);
        } catch (error) {
            console.error("Extraction failed", error);
            setExtractStatus('error');
            setTimeout(() => setExtractStatus('idle'), 4000);
        } finally {
            setIsExtracting(false);
        }
    };

    return (
        <div className="relative min-h-screen w-full bg-background text-text pb-safe md:pb-0">
            {/* Mobile Header */}
            <header className="sticky top-0 z-40 glass-strong border-b border-white/20 md:hidden flex flex-col">
                <div className="flex items-center gap-3 px-4 py-3">
                    <CommandPaletteWithTrigger>
                        {(trigger) => (
                            <button onClick={trigger} className="p-2.5 bg-gray-100/70 rounded-full text-gray-500 hover:bg-gray-200 transition-colors">
                                <Search size={18} />
                            </button>
                        )}
                    </CommandPaletteWithTrigger>

                    <form onSubmit={handleExtract} className="flex-1 flex items-center gap-2 px-3 py-2 bg-gray-100/50 rounded-full focus-within:bg-white focus-within:ring-1 focus-within:ring-primary shadow-inner transition-all">
                        <LinkIcon size={16} className={extractStatus === 'error' ? 'text-red-400' : extractStatus === 'success' ? 'text-green-500' : 'text-gray-400'} />
                        <input
                            type="url"
                            required
                            value={extractUrl}
                            onChange={(e) => setExtractUrl(e.target.value)}
                            placeholder="Paste URL to extract..."
                            className="bg-transparent border-none focus:outline-none text-sm w-full text-gray-700 placeholder-gray-400"
                        />
                        <button type="submit" disabled={isExtracting || !extractUrl.trim()} className={`p-1 rounded-full ${extractUrl.trim() ? 'bg-primary text-white' : 'bg-gray-200 text-gray-400'} transition-colors`}>
                            {isExtracting ? <Loader2 size={14} className="animate-spin" /> : <ArrowRight size={14} />}
                        </button>
                    </form>
                </div>
            </header>

            {/* Desktop Floating Header */}
            <div className="hidden md:block absolute top-6 left-6 z-50">
                <div className="flex items-center gap-3">
                    <CommandPaletteWithTrigger>
                        {(trigger) => (
                            <div className="flex items-center gap-2 px-4 py-2 bg-white/70 backdrop-blur-md rounded-full shadow-sm border border-white/20 cursor-text hover:bg-white/85 transition-colors h-11" onClick={trigger}>
                                <Command size={16} className="text-gray-400" />
                                <span className="text-sm font-medium text-gray-500 pr-2">Search (Cmd+K)</span>
                            </div>
                        )}
                    </CommandPaletteWithTrigger>

                    <form onSubmit={handleExtract} className="flex items-center gap-2 pl-4 pr-1.5 py-1.5 bg-white/70 backdrop-blur-md rounded-full shadow-sm border border-white/20 transition-all focus-within:bg-white/95 focus-within:border-primary/40 focus-within:ring-2 focus-within:ring-primary/20 h-11">
                        {extractStatus === 'success' ? (
                            <CheckCircle size={16} className="text-green-500" />
                        ) : extractStatus === 'error' ? (
                            <AlertCircle size={16} className="text-red-500" />
                        ) : (
                            <LinkIcon size={16} className="text-gray-400" />
                        )}

                        <input
                            type="url"
                            required
                            value={extractUrl}
                            onChange={(e) => setExtractUrl(e.target.value)}
                            placeholder="Paste URL to extract securely..."
                            className="bg-transparent border-none focus:outline-none text-sm w-64 text-gray-700 placeholder-gray-400"
                        />
                        <button
                            type="submit"
                            disabled={isExtracting || !extractUrl.trim()}
                            className={`p-2 rounded-full flex items-center justify-center transition-all ${extractUrl.trim() ? 'bg-primary text-white shadow-md shadow-primary/20 hover:bg-primary/90' : 'bg-gray-100 text-gray-400'}`}
                        >
                            {isExtracting ? <Loader2 size={16} className="animate-spin" /> : <ArrowRight size={16} />}
                        </button>
                    </form>
                </div>
            </div>

            {/* Desktop Settings & Console Button */}
            <div className="hidden md:block absolute bottom-6 right-6 z-50">
                <button
                    onClick={() => navigate('/console')}
                    className="p-4 bg-white/70 backdrop-blur-md rounded-full shadow-sm border border-white/20 hover:bg-white/90 transition-all cursor-pointer group flex items-center gap-3"
                    title="Console & Settings"
                >
                    <span className="text-sm font-bold text-gray-600 hidden group-hover:block transition-all mr-1">Console</span>
                    <svg className="w-5 h-5 text-gray-600" fill="none" stroke="currentColor" viewBox="0 0 24 24">
                        <circle cx="12" cy="12" r="3" strokeWidth="2" />
                        <path d="M12 1v6m0 6v6M4.22 4.22l4.24 4.24m8.48 8.48l4.24 4.24M1 12h6m6 0h6M4.22 19.78l4.24-4.24m8.48-8.48l4.24-4.24" strokeWidth="2" strokeLinecap="round" />
                    </svg>
                </button>
            </div>

            {/* Main Content Area */}
            <main className="w-full min-h-screen">
                <Outlet />
            </main>

            {/* Bottom Navigation (Mobile Only) */}
            <CommandPaletteWithTrigger>
                {(trigger) => <BottomNav onSearchTrigger={trigger} />}
            </CommandPaletteWithTrigger>
        </div>
    );
};

export default ImmersiveLayout;
