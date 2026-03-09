import { Outlet, useNavigate } from 'react-router-dom';
import { Menu, Settings, Search } from 'lucide-react';
import { CommandPalette } from './CommandPalette';
import { useState } from 'react';
import SettingsModal from './SettingsModal';

const ImmersiveLayout = () => {
    const navigate = useNavigate();
    const [isSettingsOpen, setIsSettingsOpen] = useState(false);

    return (
        <div className="relative h-screen w-full bg-background overflow-hidden text-text">
            {/* Top Left Floating Area */}
            <div className="absolute top-4 left-4 z-50 flex items-center gap-3">
                <button
                    onClick={() => navigate('/sources')}
                    className="p-3 bg-white/60 backdrop-blur-md rounded-2xl shadow-sm border border-white/20 hover:bg-white/80 transition-all group cursor-pointer"
                    title="Menu & Sources"
                >
                    <Menu className="w-5 h-5 text-text/70 group-hover:text-primary transition-colors" />
                </button>
                <div className="flex items-center gap-2 px-4 py-2 bg-white/60 backdrop-blur-md rounded-full shadow-sm border border-white/20 cursor-text">
                    <Search className="w-4 h-4 text-text/50" />
                    <span className="text-sm font-medium text-text/60">Search or extract URL (Cmd+K)</span>
                </div>
            </div>

            {/* Main Content Area */}
            <main className="w-full h-full">
                <Outlet />
            </main>

            {/* Bottom Right Floating Area */}
            <div className="absolute bottom-6 right-6 z-50">
                <button
                    onClick={() => setIsSettingsOpen(true)}
                    className="p-4 bg-white/60 backdrop-blur-md rounded-full shadow-sm border border-white/20 hover:bg-white/80 transition-all group cursor-pointer"
                    title="Settings"
                >
                    <Settings className="w-5 h-5 text-text/70 group-hover:text-primary transition-colors" />
                </button>
            </div>

            <CommandPalette />
            {isSettingsOpen && <SettingsModal onClose={() => setIsSettingsOpen(false)} />}
        </div>
    );
};

export default ImmersiveLayout;
