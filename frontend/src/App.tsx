import { BrowserRouter, Routes, Route, Navigate } from 'react-router-dom';
import ImmersiveLayout from './components/ImmersiveLayout';
import SourcesView from './views/SourcesView';
import FeedView from './views/FeedView';
import { AppProvider } from './contexts/AppContext';

function App() {
  return (
    <AppProvider>
      <BrowserRouter>
        <Routes>
          <Route path="/" element={<ImmersiveLayout />}>
            <Route index element={<Navigate to="/feed" replace />} />
            <Route path="sources" element={<SourcesView />} />
            <Route path="feed" element={<FeedView />} />
          </Route>
        </Routes>
      </BrowserRouter>
    </AppProvider>
  );
}

export default App;
