import { useState, useMemo, useRef } from 'react';
import { Bookmark, ArrowRight, ExternalLink, Calendar, X, Save, Edit3 } from 'lucide-react';
import { format, isSameDay, parseISO } from 'date-fns';
import { mockFeedItems } from '../data/mockData';
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

    const filteredItems = useMemo(() => {
        let items = mockFeedItems;
        items = items.filter(item => isSameDay(parseISO(item.timestamp), selectedDate));
        if (activeFilter === 'favorites') items = items.filter(item => isBookmarked(item.id));
        else if (activeFilter === 'uncategorized') items = items.filter(item => !item.tags || item.tags.length === 0);
        if (selectedTag) items = items.filter(item => item.tags?.includes(selectedTag));
        return items;
    }, [activeFilter, selectedTag, isBookmarked, selectedDate]);

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
        <div className="relative h-screen w-full bg-background overflow-hidden text-text flex">
            {/* Top Bar Floating (Filters & Info) */}
            <div className={`absolute top-4 left-1/2 -translate-x-1/2 z-40 bg-white/70 backdrop-blur-md px-6 py-3 rounded-full shadow-sm border border-white/20 flex items-center gap-6 transition-transform duration-500 delay-100 ${isExpanded ? '-translate-y-24' : 'translate-y-0'}`}>
                <div className="flex items-center gap-2 font-semibold">
                    <Calendar size={18} className="text-primary" />
                    <span>{format(selectedDate, 'MMM d, yyyy')}</span>
                </div>
                <div className="w-px h-4 bg-gray-300"></div>
                <div className="flex gap-4 text-sm font-medium text-gray-500">
                    <button onClick={() => setActiveFilter('all')} className={activeFilter === 'all' ? 'text-primary' : 'hover:text-primary'}>All</button>
                    <button onClick={() => setActiveFilter('favorites')} className={activeFilter === 'favorites' ? 'text-primary' : 'hover:text-primary'}>Favs</button>
                </div>
            </div>

            {/* Main Immersive Feed List */}
            <div
                ref={containerRef}
                onScroll={handleScroll}
                className="w-full h-full overflow-y-auto snap-y snap-mandatory scroll-smooth scrollbar-hide relative"
            >
                {filteredItems.length === 0 ? (
                    <div className="h-screen flex items-center justify-center">
                        <div className="text-center text-gray-400">No items available.</div>
                    </div>
                ) : (
                    filteredItems.map((item, index) => (
                        <div
                            key={item.id}
                            ref={el => itemRefs.current[index] = el}
                            className="w-full h-screen snap-center flex items-center justify-center p-8"
                        >
                            {/* Feed Card */}
                            <div
                                onClick={() => expandItem(index)}
                                className={`w-full max-w-3xl bg-white/80 backdrop-blur-xl border rounded-[2rem] p-10 cursor-pointer transition-all duration-300 transform ${selectedIndex === index ? 'scale-100 border-primary/40 shadow-2xl' : 'scale-95 border-gray-100 shadow-md opacity-60 hover:opacity-100 hover:scale-100'}`}
                            >
                                <div className="flex justify-between items-center mb-6">
                                    <div className="flex gap-3 items-center">
                                        <span className="px-3 py-1.5 bg-primary/10 text-primary font-bold rounded-lg text-sm">⭐ {item.score}</span>
                                        <span className="text-sm text-gray-500 font-medium">{item.source} • {item.timestamp}</span>
                                    </div>
                                    <div className="flex items-center gap-3">
                                        <Bookmark size={22} className={isBookmarked(item.id) ? 'fill-primary text-primary' : 'text-gray-400'} onClick={(e) => { e.stopPropagation(); if (isBookmarked(item.id)) removeBookmark(item.id); else addBookmark(item); }} />
                                    </div>
                                </div>

                                <h2 className="text-3xl font-extrabold text-gray-900 mb-6 leading-tight">{item.title}</h2>
                                <p className="text-xl text-gray-600 mb-8 leading-relaxed line-clamp-3">{item.summary}</p>

                                <div className="bg-primary/5 rounded-2xl p-6 border border-primary/10">
                                    <h3 className="text-sm font-bold text-primary mb-4 uppercase flex items-center gap-2"><ArrowRight size={16} /> Key Insights</h3>
                                    <ul className="space-y-3">
                                        {item.keyInsights.slice(0, 2).map((insight, idx) => (
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

            {/* Slide-out Expanded Panel (Notes and Details Split) */}
            <div className={`fixed inset-y-0 right-0 w-full max-w-5xl bg-white shadow-[-20px_0_40px_rgba(0,0,0,0.1)] transform transition-transform duration-500 ease-[cubic-bezier(0.19,1,0.22,1)] z-50 flex flex-col ${isExpanded ? 'translate-x-0' : 'translate-x-full'}`}>
                {activeItem && (
                    <div className="flex-1 flex overflow-hidden">
                        {/* Left Side: Original Extraction */}
                        <div className="w-1/2 p-10 overflow-y-auto border-r border-gray-100 bg-gray-50/50">
                            <button onClick={() => setIsExpanded(false)} className="mb-8 p-2 bg-white rounded-full shadow-sm hover:bg-gray-50 text-gray-500"><X size={20} /></button>
                            <h2 className="text-2xl font-bold mb-4">{activeItem.title}</h2>
                            <p className="text-lg text-gray-600 mb-8">{activeItem.summary}</p>

                            <h3 className="text-sm font-bold text-primary uppercase mb-4">Full Key Insights</h3>
                            <ul className="space-y-4 mb-8">
                                {activeItem.keyInsights.map((insight, idx) => (
                                    <li key={idx} className="flex gap-2 text-gray-800"><span className="text-primary font-bold">•</span>{insight}</li>
                                ))}
                            </ul>

                            <a href={activeItem.url} target="_blank" rel="noreferrer" className="inline-flex items-center gap-2 text-primary hover:underline font-semibold bg-white px-4 py-2 rounded-xl border border-primary/20 shadow-sm">
                                View Original Source <ExternalLink size={16} />
                            </a>
                        </div>

                        {/* Right Side: Markdown Note Editor */}
                        <div className="w-1/2 p-10 flex flex-col bg-white">
                            <div className="flex items-center justify-between mb-6">
                                <h3 className="text-lg font-bold text-gray-800 flex items-center gap-2"><Edit3 size={18} /> Scratchpad</h3>
                                <button className="flex items-center gap-2 text-sm text-primary font-medium hover:bg-primary/5 px-3 py-1.5 rounded-lg transition-colors"><Save size={16} /> Save Note (Cmd+S)</button>
                            </div>
                            <textarea
                                className="flex-1 w-full bg-transparent border-none focus:ring-0 resize-none font-mono text-gray-700 leading-relaxed text-sm outline-none"
                                placeholder="Write down your thoughts, takeaways, or tasks derived from this..."
                                defaultValue={`# Note for: ${activeItem.title}\n\n`}
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
