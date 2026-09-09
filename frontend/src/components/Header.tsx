import { useEffect, useState } from 'react';
import { useAuthStore } from '../store/authStore';
import { getAvatar } from '../api/auth';
import TicketIcon from './TicketIcon';
import ShardIcon from './ShardIcon';

export default function Header() {
    const { user } = useAuthStore();
    const [avatarUrl, setAvatarUrl] = useState<string | null>(null);

    useEffect(() => {
        if (user?.telegram_id) {
            getAvatar(user.telegram_id).then(setAvatarUrl);
        }
    }, [user?.telegram_id]);

    const name = user?.first_name || 'Путник';

    return (
        <header className="header">
            <div className="header-left">
                <div className="avatar">
                    {avatarUrl ? (
                        <img src={avatarUrl} alt={name} className="avatar-image" onError={() => setAvatarUrl(null)} />
                    ) : (
                        <span className="avatar-fallback">{name[0]}</span>
                    )}
                </div>
                <div>
                    <div className="user-name">{name}</div>
                    <div className="user-username">@{user?.username || 'путь'}</div>
                </div>
            </div>
            <div className="header-right">
                <div className="header-stats">
                    <span className="stat-item">
                        <TicketIcon size={20} />
                        <span className="stat-value">{user?.tickets ?? 0}</span>
                    </span>
                    <span className="stat-item">
                        <ShardIcon size={18} />
                        <span className="stat-value">{user?.moon_shards ?? 0}/6</span>
                    </span>
                </div>
            </div>
        </header>
    );
}