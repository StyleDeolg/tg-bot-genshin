import { useEffect, useState } from 'react';
import { useAuthStore } from '../store/authStore';
import { getProfile } from '../api/profile';
import { getAvatar } from '../api/auth';
import TicketIcon from '../components/TicketIcon';
import ShardIcon from '../components/ShardIcon';
import PageOrnament from '../components/PageOrnament';

export default function ProfilePage() {
    const { user } = useAuthStore();
    const [profile, setProfile] = useState<any>(null);
    const [avatarUrl, setAvatarUrl] = useState<string | null>(null);
    const [loading, setLoading] = useState(true);

    useEffect(() => {
        if (user?.telegram_id) {
            getProfile(user.telegram_id).then(data => {
                setProfile(data);
                setLoading(false);
            });
            getAvatar(user.telegram_id).then(url => {
                setAvatarUrl(url);
            });
        }
    }, [user]);

    useEffect(() => {
        const header = document.querySelector('.header') as HTMLElement;
        if (!header) return;
        header.classList.remove('header-hidden');
        const timer = setTimeout(() => {
            header.classList.add('header-hidden');
        }, 500);
        return () => {
            clearTimeout(timer);
            header.classList.remove('header-hidden');
        };
    }, []);

    if (loading) {
        return <div className="loading-text">Загрузка профиля...</div>;
    }

    return (
        <div className="page profile-page">
            <div className="profile-header">
                <PageOrnament />
                <div className="profile-avatar">
                    {avatarUrl ? (
                        <img src={avatarUrl} alt={profile?.first_name || 'User'} className="profile-avatar-image" onError={() => setAvatarUrl(null)} />
                    ) : (
                        <span className="profile-avatar-fallback">{profile?.first_name?.[0] || '⚜'}</span>
                    )}
                </div>
                <h2>{profile?.first_name} {profile?.last_name}</h2>
                <p>@{profile?.username || 'Искатель приключений'}</p>
            </div>

            <div className="profile-card">
                <div className="corner-decor tl"></div>
                <div className="corner-decor tr"></div>
                <div className="corner-decor bl"></div>
                <div className="corner-decor br"></div>

                <div className="info-row">
                    <span className="info-label"><TicketIcon size={16} style={{ marginRight: 6 }} /> Билетики</span>
                    <span className="info-value">{profile?.tickets ?? 0}</span>
                </div>
                <hr />
                <div className="info-row">
                    <span className="info-label"><ShardIcon size={16} style={{ marginRight: 6 }} /> Осколки луны</span>
                    <span className="info-value">{profile?.moon_shards ?? 0}/6</span>
                </div>
                <hr />
                <div className="info-row">
                    <span className="info-label">👥 Рефералы</span>
                    <span className="info-value">{profile?.referrals_count ?? 0}</span>
                </div>
                <hr />
                <div className="info-row">
                    <span className="info-label">📋 Заданий выполнено</span>
                    <span className="info-value">{profile?.tasks_completed ?? 0}</span>
                </div>
                <hr />
                <div className="info-row">
                    <span className="info-label">🎮 Genshin UID</span>
                    <span className="info-value uid-inactive">{profile?.genshin_uid || 'Не привязан'}</span>
                </div>
            </div>
        </div>
    );
}