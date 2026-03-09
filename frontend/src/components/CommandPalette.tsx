import { useState, useRef, useEffect } from 'react';
import { useHotkeys } from 'react-hotkeys-hook';
import { Search, Loader2 } from 'lucide-react';

export const CommandPalette = () => {
    const [isOpen, setIsOpen] = useState(false);
    const [query, setQuery] = useState('');
    const [isExtracting, setIsExtracting] = useState(false);
    const inputRef = useRef<HTMLInputElement>(null);

    // Toggle menu with Cmd+K
    useHotkeys('meta+k, ctrl+k', (e) => {
        e.preventDefault();
        setIsOpen((prev) => !prev);
    }, { enableOnFormTags: true });

    // Close on Escape
    useHotkeys('esc', () => setIsOpen(false), { enableOnFormTags: true });

    useEffect(() => {
        if (isOpen && inputRef.current) {
            inputRef.current.focus();
        }
    }, [isOpen]);

    const handleAction = async (e: React.FormEvent) => {
        e.preventDefault();
        if (!query.trim()) return;

        // Simulate API call for URL extraction
        if (query.startsWith('http')) {
            setIsExtracting(true);
            try {
                await new Promise((r) => setTimeout(r, 1000));
                // call POST /api/v1/extract/quick
            } finally {
                setIsExtracting(false);
                setIsOpen(false);
                setQuery('');
            }
        }
    };

    if (!isOpen) return null;

    return (
        <div className="fixed inset-0 z-[100] flex items-start justify-center pt-32 bg-text/20 backdrop-blur-sm">
            <div
                className="w-full max-w-xl bg-white rounded-2xl shadow-2xl border border-gray-100 overflow-hidden transform transition-all"
                onClick={(e) => e.stopPropagation()}
            >
                <form onSubmit={handleAction} className="flex items-center px-4 py-4 border-b border-gray-100">
                    <Search className="w-5 h-5 text-gray-400 mr-3" />
                    <input
                        ref={inputRef}
                        type="text"
                        className="flex-1 bg-transparent text-lg text-text focus:outline-none placeholder-gray-400"
                        placeholder="Paste URL to extract or search notes..."
                        value={query}
                        onChange={(e) => setQuery(e.target.value)}
                    />
                    {isExtracting && <Loader2 className="w-5 h-5 text-primary animate-spin" />}
                </form>

                <div className="p-2">
                    <div className="px-3 py-2 text-xs font-semibold text-gray-400 uppercase tracking-wider">
                        Quick Actions
                    </div>
                    {/* Add action menu items later if needed */}
                    <div className="px-3 py-3 rounded-lg hover:bg-gray-50 flex items-center justify-between cursor-pointer group text-text/80 hover:text-primary">
                        <span className="text-sm font-medium">Extract URL</span>
                        <div className="flex gap-1">
                            <kbd className="px-2 py-1 text-xs bg-gray-100 rounded border border-gray-200">Enter</kbd>
                        </div>
                    </div>
                </div>
            </div>

            {/* Click outside to close (handled by an overlay click if we want, but doing it simply here) */}
            <div className="fixed inset-0 -z-10" onClick={() => setIsOpen(false)} />
        </div>
    );
};
