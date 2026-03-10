import { NavLink, useLocation } from 'react-router-dom';
import { Home, Database, FileText, Settings, Command } from 'lucide-react';
import { cn } from '../utils';

interface BottomNavProps {
    onSearchTrigger?: () => void;
}

const navItems = [
    { path: '/feed', icon: Home, label: 'Feed' },
    { path: '/sources', icon: Database, label: 'Sources' },
    { path: '/notes', icon: FileText, label: 'Notes' },
    { path: '/settings', icon: Settings, label: 'Settings' },
] as const;

const BottomNav = ({ onSearchTrigger }: BottomNavProps) => {
    const location = useLocation();

    const getNavClasses = (isActive: boolean) => cn(
        'flex flex-col items-center justify-center gap-1 min-w-[64px] min-h-[56px] min-touch-target rounded-2xl transition-all duration-200',
        isActive
            ? 'text-primary bg-primary/10'
            : 'text-gray-400 hover:text-gray-600 hover:bg-gray-100/50'
    );

    return (
        <nav className="bottom-nav fixed bottom-0 left-0 right-0 z-50 glass border-t border-white/20 md:hidden">
            {/* Quick Action Bar (Command Palette Trigger) */}
            {onSearchTrigger && (
                <div className="flex items-center justify-between px-4 pb-2">
                    <button
                        onClick={onSearchTrigger}
                        className="flex-1 flex items-center gap-2 px-3 py-2 bg-gray-100/50 rounded-full cursor-text"
                    >
                        <Command size={16} className="text-gray-400" />
                        <span className="text-sm text-gray-500">Search</span>
                    </button>
                </div>
            )}

            {/* Main Navigation */}
            <div className="flex items-center justify-around px-2">
                {navItems.map((item) => {
                    const Icon = item.icon;
                    const isActive = location.pathname === item.path;

                    return (
                        <NavLink
                            key={item.path}
                            to={item.path}
                            className={getNavClasses(isActive)}
                            end
                        >
                            <Icon size={22} className={isActive ? 'stroke-[2.5px]' : 'stroke-[2px]'} />
                            <span className="text-[11px] font-medium leading-tight">{item.label}</span>
                        </NavLink>
                    );
                })}
            </div>
        </nav>
    );
};

export default BottomNav;
