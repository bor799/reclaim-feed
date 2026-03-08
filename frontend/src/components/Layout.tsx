import { Outlet, NavLink, useNavigate } from 'react-router-dom';
import { Rss, Newspaper, NotebookPen, Command } from 'lucide-react';
import { cn } from '../utils';
import { useEffect, useState } from 'react';

// Desktop NavLink styles
const getDesktopNavClasses = ({ isActive }: { isActive: boolean }) => {
    return cn(
        'flex items-center gap-3 px-4 py-3 rounded-xl transition-all duration-200',
        isActive
            ? 'bg-primary/10 text-primary font-medium'
            : 'text-gray-600 hover:bg-gray-50 hover:text-gray-900'
    );
};

// Mobile Bottom NavLink styles
const getMobileNavClasses = ({ isActive }: { isActive: boolean }) => {
    return cn(
        'flex flex-col items-center justify-center flex-1 h-full space-y-1 transition-colors',
        isActive ? 'text-primary' : 'text-gray-400 hover:text-gray-600'
    );
};

const Layout = () => {
    const navigate = useNavigate();
    const [showCmdK, setShowCmdK] = useState(false);

    // Global Keyboard Shortcuts (Mac Optimization)
    useEffect(() => {
        const handleKeyDown = (e: KeyboardEvent) => {
            // Cmd+K (Mac) or Ctrl+K (Windows) to Quick Navigate / Search
            if ((e.metaKey || e.ctrlKey) && e.key === 'k') {
                e.preventDefault();
                setShowCmdK(true);
                setTimeout(() => setShowCmdK(false), 2000); // Highlight animation
                navigate('/notes'); // For now, route to Notes where search lives
            }
        };

        window.addEventListener('keydown', handleKeyDown);
        return () => window.removeEventListener('keydown', handleKeyDown);
    }, [navigate]);

    return (
        <div className="flex h-screen bg-background overscroll-none">
            {/* Desktop Sidebar (Hidden on Mobile) */}
            <aside className="hidden md:flex w-64 bg-white border-r border-gray-100 flex-col pt-safe pb-safe z-10 shrink-0">
                <div className="p-6 pb-2">
                    <h2 className="text-xl font-bold text-primary flex items-center justify-between gap-2">
                        <span className="flex items-center gap-2"><span className="text-2xl">🔮</span> 炼器房</span>
                        {/* Cmd+K Hint */}
                        <div className={`hidden lg:flex items-center gap-1 text-[10px] font-medium px-2 py-1 rounded bg-gray-50 border border-gray-100 text-gray-400 transition-all ${showCmdK ? 'ring-2 ring-primary/20 text-primary border-primary/20' : ''}`}>
                            <Command size={12} /> K
                        </div>
                    </h2>
                </div>

                <nav className="flex-1 px-4 space-y-2 mt-4">
                    <NavLink to="/sources" className={getDesktopNavClasses}>
                        <Rss size={20} />
                        Sources
                    </NavLink>

                    <NavLink to="/feed" className={getDesktopNavClasses}>
                        <Newspaper size={20} />
                        Feed
                    </NavLink>

                    <NavLink to="/notes" className={getDesktopNavClasses}>
                        <NotebookPen size={20} />
                        Notes
                    </NavLink>
                </nav>
            </aside>

            {/* Main Content Area */}
            {/* Added pt-safe for top notch, pb-24 padding to avoid mobile bottom nav overlap */}
            <main className="flex-1 overflow-y-auto w-full pt-safe pb-20 md:pb-safe hide-scrollbar bg-background">
                <Outlet />
            </main>

            {/* Mobile Bottom Navigation (Hidden on Desktop) */}
            <nav className="md:hidden fixed bottom-0 left-0 right-0 bg-white border-t border-gray-100 pb-safe z-50 shadow-[0_-4px_24px_rgba(0,0,0,0.04)] h-16 flex items-center justify-between px-2">
                <NavLink to="/sources" className={getMobileNavClasses}>
                    <Rss size={22} className="stroke-2" />
                    <span className="text-[10px] font-medium font-sans">Sources</span>
                </NavLink>
                <NavLink to="/feed" className={getMobileNavClasses}>
                    <Newspaper size={22} className="stroke-2" />
                    <span className="text-[10px] font-medium font-sans">Feed</span>
                </NavLink>
                <NavLink to="/notes" className={getMobileNavClasses}>
                    <NotebookPen size={22} className="stroke-2" />
                    <span className="text-[10px] font-medium font-sans">Notes</span>
                </NavLink>
            </nav>
        </div>
    );
};

export default Layout;
