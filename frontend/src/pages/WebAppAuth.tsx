import { useEffect, useState } from 'react';
import { useAuthStore } from '../store/authStore';
import { getTelegramUser, initTelegramWebApp } from '../utils/telegram';
import apiClient from '../api/client';
import LoadingScreen from './LoadingScreen';

export default function WebAppAuth({ children }: { children: React.ReactNode }) {
    const { setUser, loadUserData } = useAuthStore();
    const [authChecked, setAuthChecked] = useState(false);
    const [error, setError] = useState<string | null>(null);
    const [showLoading, setShowLoading] = useState(true);

    useEffect(() => {
        const authenticate = async () => {
            try {
                // Минимальное время показа загрузки — 6 секунд
                const minLoadingTime = new Promise(resolve => setTimeout(resolve, 6000));

                initTelegramWebApp();
                const user = getTelegramUser();

                let userData;
                if (user) {
                    userData = {
                        telegram_id: String(user.id),
                        username: user.username || null,
                        first_name: user.first_name || null,
                        last_name: user.last_name || null,
                    };
                } else {
                    userData = {
                        telegram_id: '123456789',
                        username: 'testuser',
                        first_name: 'Тестовый',
                        last_name: 'Пользователь',
                    };
                }

                const response = await apiClient.post('/api/auth/login', userData);
                setUser(response.data);
                await loadUserData(userData.telegram_id);

                // Ждём окончания минимального времени загрузки
                await minLoadingTime;
                setAuthChecked(true);
            } catch (err: any) {
                console.error('❌ Ошибка:', err);
                setError(err.message || 'Ошибка подключения к серверу');
                setAuthChecked(true);
            }
        };

        authenticate();
    }, []);

    useEffect(() => {
        if (!authChecked) return;
        // После проверки авторизации даём ещё 0.5 секунды на анимацию
        setTimeout(() => {
            setShowLoading(false);
        }, 500);
    }, [authChecked]);

    if (showLoading || !authChecked) {
        return <LoadingScreen onLoadingComplete={() => setShowLoading(false)} />;
    }

    if (error) {
        return (
            <div style={{
                display: 'flex',
                justifyContent: 'center',
                alignItems: 'center',
                height: '100vh',
                background: '#0d0b1a',
                color: '#e74c3c',
                flexDirection: 'column',
                gap: '16px',
                padding: '20px',
                textAlign: 'center'
            }}>
                <p style={{ fontSize: 20 }}>❌ {error}</p>
                <button
                    onClick={() => window.location.reload()}
                    style={{
                        padding: '12px 24px',
                        background: '#d4af37',
                        border: 'none',
                        borderRadius: 8,
                        color: '#0d0b1a',
                        fontSize: 16,
                        cursor: 'pointer',
                        fontWeight: 600,
                    }}
                >
                    🔄 Перезагрузить
                </button>
            </div>
        );
    }

    return children;
}