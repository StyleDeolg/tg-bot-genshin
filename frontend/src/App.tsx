import { useEffect, useState } from 'react';
import { BrowserRouter, Routes, Route } from 'react-router-dom';
import WebAppAuth from './pages/WebAppAuth';
import Layout from './components/Layout';
import HomePage from './pages/HomePage';
import ProfilePage from './pages/ProfilePage';
import TasksPage from './pages/TasksPage';
import FriendsPage from './pages/FriendsPage';
import SubscriptionGate from './components/SubscriptionGate';
import { useAuthStore } from './store/authStore';
import { checkAccess, type AccessStatus } from './api/sponsors';

function App() {
  const { user } = useAuthStore();
  const [access, setAccess] = useState<AccessStatus | null>(null);
  const [checking, setChecking] = useState(false);

  const loadAccess = async () => {
    if (!user?.telegram_id) return;
    setChecking(true);
    try {
      const data = await checkAccess(user.telegram_id);
      setAccess(data);
    } catch (e) {
      console.error('Ошибка проверки доступа:', e);
    } finally {
      setChecking(false);
    }
  };

  useEffect(() => {
    if (user?.telegram_id) {
      loadAccess();
    }
  }, [user?.telegram_id]);

  // Пока грузится — ничего не показываем (WebAppAuth уже отрисует лоадер)
  if (!user) {
    return (
      <BrowserRouter>
        <WebAppAuth>
          <Layout>
            <Routes>
              <Route path="/" element={<HomePage />} />
            </Routes>
          </Layout>
        </WebAppAuth>
      </BrowserRouter>
    );
  }

  // Ещё не проверили доступ — показываем лоадер
  if (!access) {
    return (
      <div style={{
        display: 'flex',
        alignItems: 'center',
        justifyContent: 'center',
        height: '100vh',
        color: 'rgba(232,224,212,0.3)',
        fontSize: '14px',
      }}>
        Проверяем доступ...
      </div>
    );
  }

  // Нет доступа — гейт
  if (!access.has_access) {
    return (
      <SubscriptionGate
        missing={access.missing}
        botUsername="GenshinPoolBot"
        onRetry={loadAccess}
        checking={checking}
      />
    );
  }

  // Доступ есть — обычный интерфейс
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