import { BrowserRouter, Routes, Route, Navigate } from 'react-router-dom';
import Layout from './components/Layout';
import SourcesView from './views/SourcesView';
import FeedView from './views/FeedView';
import NotesView from './views/NotesView';
import { AppProvider } from './contexts/AppContext';

function App() {
  return (
    <AppProvider>
      <BrowserRouter>
        <Routes>
          <Route path="/" element={<Layout />}>
            <Route index element={<Navigate to="/feed" replace />} />
            <Route path="sources" element={<SourcesView />} />
            <Route path="feed" element={<FeedView />} />
            <Route path="notes" element={<NotesView />} />
          </Route>
        </Routes>
      </BrowserRouter>
    </AppProvider>
  );
}

export default App;
