import { useEffect, useState } from 'react';
import { useAuthStore } from '../store/authStore';
import { getReferral } from '../api/referral';
import TicketIcon from '../components/TicketIcon';

export default function FriendsPage() {
    const { user } = useAuthStore();
    const [data, setData] = useState<any>(null);
    const [loading, setLoading] = useState(true);
    const [copied, setCopied] = useState(false);

    const loadReferral = async () => {
        if (!user) return;
        try {
            const referralData = await getReferral(user.telegram_id);
            setData(referralData);
        } catch (error) {
            console.error('Ошибка загрузки рефералов:', error);
        } finally {
            setLoading(false);
        }
    };

    useEffect(() => {
        loadReferral();
    }, [user]);

    const handleCopy = async (text: string) => {
        try {
            await navigator.clipboard.writeText(text);
            setCopied(true);
            setTimeout(() => setCopied(false), 2000);
        } catch (err) {
            console.error('Ошибка копирования:', err);
        }
    };

    if (loading) return <div className="loading-text text-center py-5" style={{ color: 'rgba(232,224,212,0.15)' }}>Загрузка...</div>;

    return (
        <div className="page friends-page">
            <div className="friends-content">
                <div className="page-header">
                    <h1 className="page-title">Друзья</h1>
                    <p className="page-subtitle">Приглашай и получай бонусы</p>
                </div>

                <div className="glass-card">
                    <p style={{ color: 'rgba(232,224,212,0.35)', fontSize: '13px', marginBottom: '8px' }}>
                        Твоя реферальная ссылка:
                    </p>
                    <div className="invite-link-wrapper">
                        <span className="invite-link" onClick={() => handleCopy(data?.link || '')}>
                            {data?.link}
                        </span>
                        {copied && <span className="copy-tooltip">Скопировано!</span>}
                    </div>
                </div>

                <div className="referral-stats">
                    <div className="stat-card">
                        <span className="stat-number">{data?.count || 0}</span>
                        <span className="stat-label" style={{ color: 'rgba(232,224,212,0.25)' }}>Приглашено</span>
                    </div>
                </div>

                <div className="w-100 text-center mt-3">
                    <span className="list-title">🎁 Прогресс наград</span>
                </div>

                {/* 🔥 НОВЫЙ ДИЗАЙН — ПЛАШКИ С ЗЕЛЁНОЙ ПОДСВЕТКОЙ */}
                <div className="referral-rewards-grid">
                    {data?.rewards?.map((r: any) => {
                        const isCompleted = (data?.count || 0) >= r.level;
                        return (
                            <div
                                key={r.level}
                                className={`referral-reward-card ${isCompleted ? 'completed' : ''}`}
                            >
                                <div className="referral-reward-level">{r.level}</div>
                                <div className="referral-reward-icon">
                                    <TicketIcon size={20} />
                                </div>
                                <div className="referral-reward-amount">+{r.reward}</div>
                                <div className="referral-reward-check">
                                    {isCompleted && <span>✅</span>}
                                </div>
                            </div>
                        );
                    })}
                </div>
            </div>
        </div>
    );
}