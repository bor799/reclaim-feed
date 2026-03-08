import { useState, useMemo, useRef, useEffect } from 'react';
import { Share2, Bookmark, MoreHorizontal, ArrowRight, ExternalLink, Check, Filter, Calendar, Tag as TagIcon, ChevronLeft, ChevronRight } from 'lucide-react';
import { format, subDays, isSameDay, parseISO } from 'date-fns';
import { mockFeedItems } from '../data/mockData';
import type { FeedItem } from '../types';
import { useApp } from '../contexts/AppContext';
import TagsManager from '../components/TagsManager';

const FeedView = () => {
    const { addBookmark, removeBookmark, isBookmarked, tagCategories } = useApp();
    const [shareMessage, setShareMessage] = useState<string | null>(null);
    const [isTagsManagerOpen, setIsTagsManagerOpen] = useState(false);
    const [selectedIndex, setSelectedIndex] = useState<number>(-1);

    // refs for scrolling to selected item
    const itemRefs = useRef<(HTMLElement | null)[]>([]);

    // 日期筛选状态
    const [selectedDate, setSelectedDate] = useState<Date>(new Date());
    const timelineRef = useRef<HTMLDivElement>(null);

    // 筛选状态
    const [activeFilter, setActiveFilter] = useState<'all' | 'favorites' | 'uncategorized'>('all');
    const [selectedTag, setSelectedTag] = useState<string | null>(null);

    // 获取所有可用标签
    const allTags = useMemo(() => {
        const tags = new Set<string>();
        Object.values(tagCategories).forEach(catTags => {
            catTags.forEach(tag => tags.add(tag));
        });
        return Array.from(tags);
    }, [tagCategories]);

    // 生成过去 14 天的日期数组
    const timelineDates = useMemo(() => {
        return Array.from({ length: 14 }).map((_, i) => subDays(new Date(), i)).reverse();
    }, []);

    // 滚动时间轴
    const scrollTimeline = (direction: 'left' | 'right') => {
        if (timelineRef.current) {
            const scrollAmount = direction === 'left' ? -200 : 200;
            timelineRef.current.scrollBy({ left: scrollAmount, behavior: 'smooth' });
        }
    };

    // 筛选 Feed Items (考虑日期、Active Filters 和 Tags)
    // mock 数据默认都是今天的，如果是过去的日期假设会发 API 请求获取
    const filteredItems = useMemo(() => {
        let items = mockFeedItems;

        // Filter by selected date
        items = items.filter(item => isSameDay(parseISO(item.timestamp), selectedDate));

        if (activeFilter === 'favorites') {
            items = items.filter(item => isBookmarked(item.id));
        } else if (activeFilter === 'uncategorized') {
            items = items.filter(item => !item.tags || item.tags.length === 0);
        }

        if (selectedTag) {
            items = items.filter(item => item.tags?.includes(selectedTag));
        }

        return items;
    }, [activeFilter, selectedTag, isBookmarked, selectedDate]);

    // Keyboard Navigation (J/K to move, Enter to open)
    useEffect(() => {
        const handleKeyDown = (e: KeyboardEvent) => {
            // Ignore if in input/textarea
            if (['INPUT', 'TEXTAREA'].includes((e.target as HTMLElement).tagName)) return;

            if (e.key === 'j') {
                setSelectedIndex(prev => {
                    const next = Math.min(prev + 1, filteredItems.length - 1);
                    itemRefs.current[next]?.scrollIntoView({ behavior: 'smooth', block: 'center' });
                    return next;
                });
            } else if (e.key === 'k') {
                setSelectedIndex(prev => {
                    const next = Math.max(prev - 1, 0);
                    itemRefs.current[next]?.scrollIntoView({ behavior: 'smooth', block: 'center' });
                    return next;
                });
            } else if (e.key === 'Enter' && selectedIndex >= 0 && selectedIndex < filteredItems.length) {
                window.open(filteredItems[selectedIndex].url, '_blank');
            }
        };

        window.addEventListener('keydown', handleKeyDown);
        return () => window.removeEventListener('keydown', handleKeyDown);
    }, [filteredItems, selectedIndex]);

    // 处理收藏/取消收藏
    const handleBookmark = (item: FeedItem, e: React.MouseEvent) => {
        e.stopPropagation();
        if (isBookmarked(item.id)) {
            removeBookmark(item.id);
        } else {
            addBookmark(item);
        }
    };

    // 处理分享
    const handleShare = async (item: FeedItem, e: React.MouseEvent) => {
        e.stopPropagation();

        const shareData = {
            title: item.title,
            text: `${item.summary}\n\n来源: ${item.source}\n评分: ${item.score}`,
            url: window.location.href
        };

        try {
            if (navigator.share) {
                await navigator.share(shareData);
                showMessage('已分享');
            } else {
                // 降级：复制到剪贴板
                await navigator.clipboard.writeText(
                    `${item.title}\n\n${shareData.text}\n\n${window.location.href}`
                );
                showMessage('已复制到剪贴板');
            }
        } catch (error) {
            console.error('分享失败:', error);
        }
    };

    // 显示临时消息
    const showMessage = (msg: string) => {
        setShareMessage(msg);
        setTimeout(() => setShareMessage(null), 2000);
    };

    return (
        <div className="p-8 max-w-4xl mx-auto">
            {/* 分享成功提示 */}
            {shareMessage && (
                <div className="fixed top-4 right-4 bg-emerald-500 text-white px-4 py-2 rounded-lg shadow-lg flex items-center gap-2 z-50 animate-fade-in">
                    <Check size={18} />
                    {shareMessage}
                </div>
            )}

            <div className="mb-8 border-b border-gray-100 pb-6">
                {/* 页面头部及时间轴 */}
                <div className="mb-6 flex flex-col sm:flex-row justify-between items-start sm:items-center gap-4">
                    <div>
                        <h1 className="text-3xl font-bold text-text mb-2 animate-fade-in">Insights</h1>
                        <p className="text-gray-500 flex items-center gap-2">
                            <span>{format(selectedDate, 'MMM d, yyyy')}</span>
                            <span className="w-1 h-1 rounded-full bg-gray-300"></span>
                            <span>{filteredItems.length} items</span>
                        </p>
                    </div>

                    {/* Timeline Widget */}
                    <div className="flex items-center gap-1 bg-white border border-gray-100 p-1.5 rounded-2xl shadow-sm w-full sm:w-auto overflow-hidden animate-slide-up">
                        <button
                            onClick={() => scrollTimeline('left')}
                            className="p-1.5 text-gray-400 hover:text-primary hover:bg-gray-50 rounded-full transition-colors flex-shrink-0"
                        >
                            <ChevronLeft size={18} />
                        </button>

                        <div
                            ref={timelineRef}
                            className="flex gap-1 overflow-x-auto scrollbar-hide scroll-smooth flex-nowrap mask-edges"
                            style={{ maxWidth: '280px' }}
                        >
                            {timelineDates.map(date => {
                                const isSelected = isSameDay(date, selectedDate);
                                return (
                                    <button
                                        key={date.toISOString()}
                                        onClick={() => setSelectedDate(date)}
                                        className={`flex flex-col items-center min-w-[3.5rem] py-1.5 rounded-xl transition-all flex-shrink-0 ${isSelected
                                            ? 'bg-primary text-white shadow-md shadow-primary/20 scale-105 transform'
                                            : 'text-gray-500 hover:bg-gray-50 hover:text-gray-900'
                                            }`}
                                    >
                                        <span className={`text-[10px] uppercase font-semibold ${isSelected ? 'text-white/80' : 'text-gray-400'}`}>
                                            {format(date, 'EEE')}
                                        </span>
                                        <span className="text-sm font-bold mt-0.5">{format(date, 'd')}</span>
                                    </button>
                                );
                            })}
                        </div>

                        <button
                            onClick={() => scrollTimeline('right')}
                            className="p-1.5 text-gray-400 hover:text-primary hover:bg-gray-50 rounded-full transition-colors flex-shrink-0"
                        >
                            <ChevronRight size={18} />
                        </button>
                    </div>
                </div>

                <div className="flex justify-between items-center mb-4">
                    <h2 className="text-xl font-semibold text-gray-800 flex items-center gap-2">
                        <Calendar size={20} className="text-primary" />
                        Daily Digest
                    </h2>

                    <div className="flex gap-2">
                        <button
                            onClick={() => setIsTagsManagerOpen(true)}
                            className="flex items-center gap-2 px-3 py-1.5 bg-gray-50 hover:bg-gray-100 text-gray-700 rounded-lg transition-colors text-sm font-medium border border-gray-200"
                        >
                            <TagIcon size={16} />
                            Tags
                        </button>
                    </div>
                </div>

                {/* 快捷筛选器 & 标签筛选器 */}
                <div className="flex flex-col sm:flex-row gap-4 mt-6">
                    <div className="flex items-center gap-2 bg-gray-50 p-1 rounded-lg w-fit">
                        {(['all', 'favorites', 'uncategorized'] as const).map(filter => (
                            <button
                                key={filter}
                                onClick={() => setActiveFilter(filter)}
                                className={`px-4 py-1.5 rounded-md text-sm font-medium transition-all ${activeFilter === filter
                                    ? 'bg-white text-primary shadow-sm'
                                    : 'text-gray-500 hover:text-gray-900'
                                    }`}
                            >
                                {filter.charAt(0).toUpperCase() + filter.slice(1)}
                            </button>
                        ))}
                    </div>

                    <div className="flex-1 flex gap-2 overflow-x-auto pb-2 sm:pb-0 items-center scrollbar-hide">
                        <div className="h-6 w-px bg-gray-200 mx-2 hidden sm:block"></div>
                        <Filter size={16} className="text-gray-400 shrink-0" />
                        <button
                            onClick={() => setSelectedTag(null)}
                            className={`px-3 py-1 rounded-full text-sm whitespace-nowrap transition-colors ${selectedTag === null
                                ? 'bg-primary/10 text-primary font-medium border border-primary/20'
                                : 'bg-white text-gray-500 border border-gray-200 hover:border-primary/50'
                                }`}
                        >
                            Any Tag
                        </button>
                        {allTags.map(tag => (
                            <button
                                key={tag}
                                onClick={() => setSelectedTag(tag === selectedTag ? null : tag)}
                                className={`px-3 py-1 rounded-full text-sm whitespace-nowrap transition-colors ${selectedTag === tag
                                    ? 'bg-primary text-white font-medium border border-primary'
                                    : 'bg-white text-gray-600 border border-gray-200 hover:border-primary/50 hover:text-primary'
                                    }`}
                            >
                                #{tag}
                            </button>
                        ))}
                    </div>
                </div>
            </div>

            <div className="space-y-8">
                {filteredItems.map((item: FeedItem, index: number) => {
                    const bookmarked = isBookmarked(item.id);
                    const isSelected = index === selectedIndex;

                    return (
                        <article
                            key={item.id}
                            ref={el => itemRefs.current[index] = el}
                            className={`bg-white border rounded-2xl p-6 hover:shadow-md transition-all duration-300 ${isSelected ? 'border-primary ring-2 ring-primary/20 shadow-md' : 'border-gray-100'
                                }`}
                        >
                            <div className="flex justify-between items-start mb-4">
                                <div className="flex items-center gap-3">
                                    <span className="px-2.5 py-1 bg-primary/10 text-primary text-sm font-semibold rounded-md flex items-center gap-1">
                                        ⭐ {item.score}
                                    </span>
                                    <span className="text-sm font-medium text-gray-500 bg-gray-50 px-2.5 py-1 rounded-md">
                                        {item.source}
                                    </span>
                                    <span className="text-sm text-gray-400">{item.timestamp}</span>
                                </div>
                                <div className="flex items-center gap-2">
                                    {/* 收藏按钮 */}
                                    <button
                                        onClick={(e) => handleBookmark(item, e)}
                                        className={`p-2 rounded-full transition-all cursor-pointer ${bookmarked
                                            ? 'text-primary bg-primary/10 hover:bg-primary/20'
                                            : 'text-gray-400 hover:text-primary hover:bg-primary/5'
                                            }`}
                                        title={bookmarked ? '取消收藏' : '收藏'}
                                    >
                                        <Bookmark size={18} fill={bookmarked ? 'currentColor' : 'none'} />
                                    </button>

                                    {/* 分享按钮 */}
                                    <button
                                        onClick={(e) => handleShare(item, e)}
                                        className="p-2 text-gray-400 hover:text-gray-900 hover:bg-gray-50 rounded-full transition-colors cursor-pointer"
                                        title="分享"
                                    >
                                        <Share2 size={18} />
                                    </button>

                                    {/* 更多按钮 */}
                                    <button className="p-2 text-gray-400 hover:text-gray-900 hover:bg-gray-50 rounded-full transition-colors cursor-pointer">
                                        <MoreHorizontal size={18} />
                                    </button>
                                </div>
                            </div>

                            <h2 className="text-2xl font-bold text-gray-900 mb-3 leading-tight hover:text-primary transition-colors cursor-pointer">
                                {item.title}
                            </h2>

                            <p className="text-gray-600 mb-6 text-lg leading-relaxed">
                                {item.summary}
                            </p>

                            {/* Key Insights Section */}
                            <div className="bg-background/50 rounded-xl p-5 mb-6 border border-primary/10">
                                <h3 className="text-sm font-bold text-primary mb-3 uppercase tracking-wider flex items-center gap-2">
                                    <ArrowRight size={14} />
                                    Key Insights
                                </h3>
                                <ul className="space-y-2">
                                    {item.keyInsights.map((insight, idx) => (
                                        <li key={idx} className="flex items-start gap-2 text-gray-700">
                                            <span className="text-primary mt-1">•</span>
                                            <span className="leading-relaxed">{insight}</span>
                                        </li>
                                    ))}
                                </ul>
                            </div>

                            <div className="flex items-center justify-between pt-4 border-t border-gray-50">
                                <div className="flex items-center gap-2">
                                    {item.tags.map((tag) => (
                                        <span key={tag} className="text-xs font-medium text-gray-500 bg-gray-100 px-2.5 py-1 rounded-full cursor-pointer hover:bg-gray-200 transition-colors">
                                            #{tag}
                                        </span>
                                    ))}
                                </div>
                                <button className="flex items-center gap-1.5 text-sm font-medium text-primary hover:text-teal-700 transition-colors cursor-pointer">
                                    Read Original
                                    <ExternalLink size={14} />
                                </button>
                            </div>
                        </article>
                    );
                })}
                {filteredItems.length === 0 && (
                    <div className="text-center py-20 bg-gray-50 rounded-2xl border border-dashed border-gray-200">
                        <Filter className="mx-auto text-gray-300 mb-4" size={48} />
                        <h3 className="text-lg font-medium text-gray-900 mb-2">No items found</h3>
                        <p className="text-gray-500">Try adjusting your filters or selecting a different tag.</p>
                        <button
                            onClick={() => {
                                setActiveFilter('all');
                                setSelectedTag(null);
                            }}
                            className="mt-4 text-primary font-medium hover:underline"
                        >
                            Clear all filters
                        </button>
                    </div>
                )}
            </div>

            {isTagsManagerOpen && (
                <TagsManager onClose={() => setIsTagsManagerOpen(false)} />
            )}
        </div>
    );
};

export default FeedView;
