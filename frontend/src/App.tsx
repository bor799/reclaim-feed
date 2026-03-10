import { BrowserRouter, Routes, Route, Navigate } from 'react-router-dom';
import ImmersiveLayout from './components/ImmersiveLayout';
import ConsoleLayout from './components/ConsoleLayout';
import SourcesView from './views/SourcesView';
import FeedView from './views/FeedView';
import PromptsView from './views/PromptsView';
import SettingsView from './views/SettingsView';
import { AppProvider } from './contexts/AppContext';

// Placeholder NotesView component
const NotesView = () => (
  <div className="p-4 md:p-8 pb-24 md:pb-8 min-h-screen">
    <h1 className="text-2xl md:text-3xl font-bold mb-4">Notes</h1>
    <p className="text-gray-500">Your saved notes will appear here.</p>
  </div>
);

function App() {
  return (
    <AppProvider>
      <BrowserRouter>
        <Routes>
          {/* Main Reading/Consuming Flow */}
          <Route path="/" element={<ImmersiveLayout />}>
            <Route index element={<Navigate to="/feed" replace />} />
            <Route path="feed" element={<FeedView />} />
            <Route path="notes" element={<NotesView />} />
          </Route>

          {/* Management Console Flow */}
          <Route path="/console" element={<ConsoleLayout />}>
            <Route index element={<Navigate to="/console/prompts" replace />} />
            <Route path="prompts" element={<PromptsView />} />
            <Route path="sources" element={<SourcesView />} />
            <Route path="settings" element={<SettingsView />} />
          </Route>
        </Routes>
      </BrowserRouter>
    </AppProvider>
  );
}

export default App;
