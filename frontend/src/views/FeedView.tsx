import { useState, useMemo, useRef, useEffect } from 'react';
import { Bookmark, ArrowRight, ExternalLink, Calendar, X, Save, Edit3 } from 'lucide-react';
import { format, isSameDay, parseISO } from 'date-fns';
import { api } from '../services/api';
import { FeedItem } from '../types';
import { useApp } from '../contexts/AppContext';
import { useHotkeys } from 'react-hotkeys-hook';

const FeedView = () => {
    const { addBookmark, removeBookmark, isBookmarked } = useApp();

    // Nav State
    const [selectedIndex, setSelectedIndex] = useState(0);
    const [isExpanded, setIsExpanded] = useState(false);

    // Filters
    const [selectedDate] = useState<Date>(new Date());
    const [activeFilter, setActiveFilter] = useState<'all' | 'favorites' | 'uncategorized'>('all');
    const [selectedTag] = useState<string | null>(null);

    const containerRef = useRef<HTMLDivElement>(null);
    const itemRefs = useRef<(HTMLElement | null)[]>([]);

    const [fetchedItems, setFetchedItems] = useState<FeedItem[]>([]);

    useEffect(() => {
        const loadFeed = async () => {
            try {
                const data = await api.getFeedItems({ limit: 50 });
                setFetchedItems(data.items);
            } catch (err) {
                console.error("Failed to load feed", err);
            }
        };
        loadFeed();
    }, []);

    const filteredItems = useMemo(() => {
        let items = fetchedItems;
        items = items.filter(item => {
            const timeStr = item.published_at || item.created_at || (item as any).timestamp;
            if (!timeStr) return true;
            try {
                return isSameDay(parseISO(timeStr), selectedDate);
            } catch {
                return true;
            }
        });
        if (activeFilter === 'favorites') items = items.filter(item => isBookmarked(item.id));
        else if (activeFilter === 'uncategorized') items = items.filter(item => !item.tags || item.tags.length === 0);
        if (selectedTag) items = items.filter(item => item.tags?.includes(selectedTag));
        return items;
    }, [activeFilter, selectedTag, isBookmarked, selectedDate, fetchedItems]);

    // Handle Snap Scroll Syncing with selectedIndex
    const handleScroll = () => {
        if (!containerRef.current || isExpanded) return;
        const container = containerRef.current;
        const scrollPosition = container.scrollTop;
        const viewportHeight = container.clientHeight;
        const index = Math.round(scrollPosition / viewportHeight);
        if (index !== selectedIndex && index >= 0 && index < filteredItems.length) {
            setSelectedIndex(index);
        }
    };

    // Keyboard Navigation
    useHotkeys('j', () => {
        if (isExpanded) return;
        setSelectedIndex(prev => {
            const next = Math.min(prev + 1, filteredItems.length - 1);
            itemRefs.current[next]?.scrollIntoView({ behavior: 'smooth', block: 'start' });
            return next;
        });
    }, [filteredItems, isExpanded]);

    useHotkeys('k', () => {
        if (isExpanded) return;
        setSelectedIndex(prev => {
            const next = Math.max(prev - 1, 0);
            itemRefs.current[next]?.scrollIntoView({ behavior: 'smooth', block: 'start' });
            return next;
        });
    }, [filteredItems, isExpanded]);

    useHotkeys('enter', () => {
        if (!isExpanded && filteredItems[selectedIndex]) setIsExpanded(true);
    }, [isExpanded, selectedIndex, filteredItems]);

    useHotkeys('esc', () => {
        if (isExpanded) setIsExpanded(false);
    }, [isExpanded]);

    const activeItem = filteredItems[selectedIndex];

    const expandItem = (index: number) => {
        setSelectedIndex(index);
        itemRefs.current[index]?.scrollIntoView({ behavior: 'smooth', block: 'start' });
        setIsExpanded(true);
    };

    return (
        <div className="relative min-h-screen w-full bg-background text-text flex">
            {/* Mobile Filter Bar */}
            <div className={`sticky top-0 z-40 glass-strong border-b border-white/20 md:hidden transition-transform duration-300 ${isExpanded ? '-translate-y-full' : 'translate-y-0'}`}>
                <div className="flex items-center gap-3 px-4 py-3 overflow-x-auto scrollbar-hide">
                    <div className="flex items-center gap-1.5 text-sm font-medium text-gray-600 whitespace-nowrap">
                        <Calendar size={16} className="text-primary" />
                        <span>{format(selectedDate, 'MMM d')}</span>
                    </div>
                    <div className="w-px h-4 bg-gray-200"></div>
                    <div className="flex gap-1 bg-gray-100/50 rounded-full p-1">
                        <button onClick={() => setActiveFilter('all')} className={`px-3 py-1.5 rounded-full text-xs font-medium transition-all ${activeFilter === 'all' ? 'bg-white text-primary shadow-sm' : 'text-gray-500'}`}>All</button>
                        <button onClick={() => setActiveFilter('favorites')} className={`px-3 py-1.5 rounded-full text-xs font-medium transition-all ${activeFilter === 'favorites' ? 'bg-white text-primary shadow-sm' : 'text-gray-500'}`}>Favs</button>
                    </div>
                </div>
            </div>

            {/* Desktop Floating Filter Bar */}
            <div className={`hidden md:block absolute top-6 left-1/2 -translate-x-1/2 z-40 glass-strong px-5 py-2.5 rounded-full shadow-sm border border-white/20 items-center gap-6 transition-all duration-300 ${isExpanded ? 'opacity-0 pointer-events-none' : 'opacity-100'}`}>
                <div className="flex items-center gap-2 font-medium text-gray-700">
                    <Calendar size={18} className="text-primary" />
                    <span className="text-sm">{format(selectedDate, 'MMM d, yyyy')}</span>
                </div>
                <div className="w-px h-4 bg-gray-300"></div>
                <div className="flex gap-4 text-sm font-medium text-gray-500">
                    <button onClick={() => setActiveFilter('all')} className={activeFilter === 'all' ? 'text-primary' : 'hover:text-primary transition-colors'}>All</button>
                    <button onClick={() => setActiveFilter('favorites')} className={activeFilter === 'favorites' ? 'text-primary' : 'hover:text-primary transition-colors'}>Favorites</button>
                </div>
            </div>

            {/* Main Feed - Mobile: Scroll Cards, Desktop: Snap Scroll */}
            <div
                ref={containerRef}
                onScroll={handleScroll}
                className="w-full min-h-screen overflow-y-auto md:h-screen md:snap-y md:snap-mandatory scroll-smooth scrollbar-hide relative pb-safe md:pb-0"
            >
                {filteredItems.length === 0 ? (
                    <div className="min-h-screen md:h-screen flex items-center justify-center">
                        <div className="text-center text-gray-400">No items available.</div>
                    </div>
                ) : (
                    filteredItems.map((item, index) => (
                        <div
                            key={item.id}
                            ref={el => itemRefs.current[index] = el}
                            className="w-full md:h-screen md:snap-center flex items-start justify-center p-3 md:p-6 lg:p-8"
                        >
                            {/* Mobile Card - Compact */}
                            <div
                                onClick={() => expandItem(index)}
                                className="md:hidden w-full bg-white/90 backdrop-blur-xl border rounded-2xl p-4 cursor-pointer transition-all duration-200 active:scale-[0.98] touch-manipulation"
                            >
                                <div className="flex justify-between items-start mb-3">
                                    <div className="flex gap-2 items-center">
                                        <span className="px-2 py-1 bg-primary/10 text-primary font-bold rounded-lg text-xs">⭐ {item.score || item.quality_score || item.analysis_score || 0}</span>
                                        <span className="text-xs text-gray-500 font-medium">{item.source || (item as any).source_detail}</span>
                                    </div>
                                    <button
                                        onClick={(e) => { e.stopPropagation(); if (isBookmarked(item.id)) removeBookmark(item.id); else addBookmark(item); }}
                                        className="p-2 -mr-2 min-touch-target"
                                    >
                                        <Bookmark size={20} className={isBookmarked(item.id) ? 'fill-primary text-primary' : 'text-gray-400'} />
                                    </button>
                                </div>

                                <h2 className="text-base font-bold text-gray-900 mb-2 leading-snug">{item.title}</h2>
                                <p className="text-sm text-gray-600 mb-3 line-clamp-2 leading-relaxed">{item.summary || item.extraction?.summary || item.content?.substring(0, 200) || ""}</p>

                                <div className="bg-primary/5 rounded-xl p-3 border border-primary/10">
                                    <h3 className="text-xs font-bold text-primary mb-2 flex items-center gap-1"><ArrowRight size={14} /> Insights</h3>
                                    <ul className="space-y-1.5">
                                        {((item as any).keyInsights || item.key_insights || item.extraction?.key_insights || []).slice(0, 2).map((insight: string, idx: number) => (
                                            <li key={idx} className="flex gap-2 text-gray-800 text-sm"><span className="text-primary">•</span>{insight}</li>
                                        ))}
                                    </ul>
                                </div>
                            </div>

                            {/* Desktop Card - Full Screen */}
                            <div
                                onClick={() => expandItem(index)}
                                className={`hidden md:block w-full max-w-3xl bg-white/90 backdrop-blur-xl border rounded-[2rem] p-8 lg:p-10 cursor-pointer transition-all duration-300 ${selectedIndex === index ? 'scale-100 border-primary/40 shadow-2xl' : 'scale-95 border-gray-100 shadow-md opacity-60 hover:opacity-100 hover:scale-100'}`}
                            >
                                <div className="flex justify-between items-center mb-6">
                                    <div className="flex gap-3 items-center">
                                        <span className="px-3 py-1.5 bg-primary/10 text-primary font-bold rounded-lg text-sm">⭐ {item.score || item.quality_score || item.analysis_score || 0}</span>
                                        <span className="text-sm text-gray-500 font-medium">{item.source || (item as any).source_detail} • {(item as any).timestamp || item.published_at || item.created_at}</span>
                                    </div>
                                    <div className="flex items-center gap-3">
                                        <Bookmark size={22} className={isBookmarked(item.id) ? 'fill-primary text-primary' : 'text-gray-400'} onClick={(e) => { e.stopPropagation(); if (isBookmarked(item.id)) removeBookmark(item.id); else addBookmark(item); }} />
                                    </div>
                                </div>

                                <h2 className="text-2xl lg:text-3xl font-bold text-gray-900 mb-6 leading-tight">{item.title}</h2>
                                <p className="text-lg text-gray-600 mb-8 leading-relaxed line-clamp-3">{item.summary || item.extraction?.summary || item.content?.substring(0, 200) || ""}</p>

                                <div className="bg-primary/5 rounded-2xl p-6 border border-primary/10">
                                    <h3 className="text-sm font-bold text-primary mb-4 uppercase flex items-center gap-2"><ArrowRight size={16} /> Key Insights</h3>
                                    <ul className="space-y-3">
                                        {((item as any).keyInsights || item.key_insights || item.extraction?.key_insights || []).slice(0, 2).map((insight: string, idx: number) => (
                                            <li key={idx} className="flex gap-3 text-gray-800 font-medium"><span className="text-primary">•</span>{insight}</li>
                                        ))}
                                    </ul>
                                </div>
                                <div className="mt-8 flex items-center gap-2 text-primary font-semibold text-sm opacity-80">
                                    Press <kbd className="font-mono bg-primary/10 px-2 py-1 rounded text-xs mx-1">Enter</kbd> to expand details & notes
                                </div>
                            </div>
                        </div>
                    ))
                )}
            </div>

            {/* Slide-out Expanded Panel */}
            <div className={`fixed inset-y-0 right-0 w-full md:w-full max-w-5xl bg-white shadow-[-20px_0_40px_rgba(0,0,0,0.1)] transform transition-transform duration-500 ease-[cubic-bezier(0.19,1,0.22,1)] z-50 flex flex-col ${isExpanded ? 'translate-x-0' : 'translate-x-full'}`}>
                {activeItem && (
                    <div className="flex-1 flex flex-col md:flex-row overflow-hidden">
                        {/* Top: Original Extraction (Mobile) / Left Side (Desktop) */}
                        <div className="w-full md:w-1/2 p-4 md:p-8 lg:p-10 overflow-y-auto border-b md:border-b-0 md:border-r border-gray-100 bg-gray-50/50">
                            <button onClick={() => setIsExpanded(false)} className="mb-4 md:mb-8 p-2 bg-white rounded-full shadow-sm hover:bg-gray-50 text-gray-500 min-touch-target"><X size={20} /></button>
                            <h2 className="text-xl md:text-2xl font-bold mb-4">{activeItem.title}</h2>
                            <p className="text-base md:text-lg text-gray-600 mb-6 md:mb-8">{activeItem.summary || activeItem.extraction?.summary || activeItem.content?.substring(0, 500) || ""}</p>

                            <h3 className="text-xs md:text-sm font-bold text-primary uppercase mb-3 md:mb-4">Full Key Insights</h3>
                            <ul className="space-y-3 md:space-y-4 mb-6 md:mb-8">
                                {((activeItem as any).keyInsights || activeItem.key_insights || activeItem.extraction?.key_insights || []).map((insight: string, idx: number) => (
                                    <li key={idx} className="flex gap-2 text-gray-800 text-sm md:text-base"><span className="text-primary font-bold">•</span>{insight}</li>
                                ))}
                            </ul>

                            <a href={activeItem.url} target="_blank" rel="noreferrer" className="inline-flex items-center gap-2 text-primary hover:underline font-semibold bg-white px-4 py-2.5 rounded-xl border border-primary/20 shadow-sm">
                                View Original <ExternalLink size={16} />
                            </a>
                        </div>

                        {/* Bottom: Markdown Note Editor (Mobile) / Right Side (Desktop) */}
                        <div className="w-full md:w-1/2 p-4 md:p-8 lg:p-10 flex flex-col bg-white">
                            <div className="flex items-center justify-between mb-4 md:mb-6">
                                <h3 className="text-base md:text-lg font-bold text-gray-800 flex items-center gap-2"><Edit3 size={18} /> Notes</h3>
                                <button className="hidden md:flex items-center gap-2 text-sm text-primary font-medium hover:bg-primary/5 px-3 py-1.5 rounded-lg transition-colors"><Save size={16} /> Save (Cmd+S)</button>
                                <button className="md:hidden p-2 text-primary"><Save size={20} /></button>
                            </div>
                            <textarea
                                className="flex-1 w-full bg-transparent border-none focus:ring-0 resize-none font-mono text-gray-700 leading-relaxed text-sm outline-none min-h-[200px] md:min-h-0"
                                placeholder="Write your thoughts..."
                                defaultValue={`# ${activeItem.title}\n\n`}
                            />
                        </div>
                    </div>
                )}
            </div>

            {/* Backdrop for Slide-out */}
            {isExpanded && (
                <div
                    className="fixed inset-0 bg-text/5 backdrop-blur-sm z-40 transition-opacity"
                    onClick={() => setIsExpanded(false)}
                />
            )}
        </div>
    );
};

export default FeedView;
