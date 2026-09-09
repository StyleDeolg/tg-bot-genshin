import { BrowserRouter, Routes, Route } from 'react-router-dom';
import WebAppAuth from './pages/WebAppAuth';
import Layout from './components/Layout';
import HomePage from './pages/HomePage';
import ProfilePage from './pages/ProfilePage';
import TasksPage from './pages/TasksPage';
import FriendsPage from './pages/FriendsPage';

function App() {
  return (
    <BrowserRouter>
      <WebAppAuth>
        <Layout>
          <Routes>
            <Route path="/" element={<HomePage />} />
            <Route path="/profile" element={<ProfilePage />} />
            <Route path="/tasks" element={<TasksPage />} />
            <Route path="/friends" element={<FriendsPage />} />
          </Routes>
        </Layout>
      </WebAppAuth>
    </BrowserRouter>
  );
}

export default App;