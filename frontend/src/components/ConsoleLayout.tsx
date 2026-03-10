import { Outlet, NavLink, useNavigate } from 'react-router-dom';
import { AlignLeft, Settings, Database, ArrowLeft } from 'lucide-react';

const ConsoleLayout = () => {
    const navigate = useNavigate();

    return (
        <div className="flex h-screen w-full bg-background text-text overflow-hidden">
            {/* Sidebar */}
            <aside className="w-64 bg-white/50 backdrop-blur-3xl border-r border-white/20 flex flex-col pt-8 pb-4">
                <div className="px-6 mb-8 flex items-center gap-3">
                    <button
                        onClick={() => navigate('/feed')}
                        className="p-2 -ml-2 text-gray-400 hover:text-gray-900 transition-colors rounded-full hover:bg-gray-200 min-touch-target"
                        title="Back to Feed"
                    >
                        <ArrowLeft size={20} />
                    </button>
                    <h1 className="text-xl font-bold bg-clip-text text-transparent bg-gradient-to-r from-primary to-orange-400">Console</h1>
                </div>

                <nav className="flex-1 px-4 space-y-2">
                    <NavLink
                        to="/console/prompts"
                        className={({ isActive }) => `flex items-center gap-3 px-4 py-3 rounded-2xl font-medium transition-all ${isActive ? 'bg-white shadow-sm text-primary' : 'text-gray-500 hover:bg-white/40 hover:text-gray-800'}`}
                    >
                        <AlignLeft size={18} /> Prompts
                    </NavLink>
                    <NavLink
                        to="/console/sources"
                        className={({ isActive }) => `flex items-center gap-3 px-4 py-3 rounded-2xl font-medium transition-all ${isActive ? 'bg-white shadow-sm text-primary' : 'text-gray-500 hover:bg-white/40 hover:text-gray-800'}`}
                    >
                        <Database size={18} /> Sources
                    </NavLink>
                    <NavLink
                        to="/console/settings"
                        className={({ isActive }) => `flex items-center gap-3 px-4 py-3 rounded-2xl font-medium transition-all ${isActive ? 'bg-white shadow-sm text-primary' : 'text-gray-500 hover:bg-white/40 hover:text-gray-800'}`}
                    >
                        <Settings size={18} /> Settings
                    </NavLink>
                </nav>
            </aside>

            {/* Main Content Pane */}
            <main className="flex-1 h-full overflow-y-auto relative bg-gray-50/30">
                <div className="absolute inset-0 transition-opacity duration-300">
                    <Outlet />
                </div>
            </main>
        </div>
    );
};

export default ConsoleLayout;
