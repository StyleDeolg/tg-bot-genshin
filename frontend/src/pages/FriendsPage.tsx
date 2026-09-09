import { useEffect, useState } from 'react';
import { useAuthStore } from '../store/authStore';
import { getReferral } from '../api/referral';
import TicketIcon from '../components/TicketIcon';
import PageOrnament from '../components/PageOrnament';

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

    if (loading) return <div className="loading-text">Загрузка...</div>;

    return (
        <div className="page friends-page">
            <PageOrnament />
            <h1 className="page-title">👥 Друзья</h1>
            <p className="page-subtitle">Приглашай друзей и получай бонусы!</p>

            <div className="invite-card">
                <div className="corner-decor tl"></div>
                <div className="corner-decor tr"></div>
                <div className="corner-decor bl"></div>
                <div className="corner-decor br"></div>
                <p style={{
                    fontFamily: "'Cormorant Garamond', serif",
                    color: 'rgba(232,224,212,0.5)',
                    fontSize: '13px',
                    marginBottom: '8px'
                }}>
                    Твоя реферальная ссылка:
                </p>
                <div className="invite-link-wrapper">
                    <span className="invite-link" onClick={() => handleCopy(data?.link || '')}>
                        {data?.link}
                    </span>
                    {copied && <span className="copy-tooltip">✅ Скопировано!</span>}
                </div>
            </div>

            <div className="referral-stats">
                <div className="stat-card">
                    <span className="stat-number">{data?.count || 0}</span>
                    <span className="stat-label">👥 Приглашено</span>
                </div>
            </div>

            <h3 className="list-title">🎁 Прогресс наград</h3>

            <div className="referral-progress-wrapper">
                {data?.rewards?.map((r: any, index: number) => {
                    const isCompleted = (data?.count || 0) >= r.level;
                    const isLast = index === data?.rewards?.length - 1;
                    const progress = Math.min((data?.count || 0) / r.level * 100, 100);

                    return (
                        <div key={r.level} className="referral-progress-item">
                            <div className={`referral-progress-dot ${isCompleted ? 'completed' : ''}`}>
                                <span className="referral-progress-level">{r.level}</span>
                            </div>
                            {!isLast && (
                                <div className="referral-progress-line">
                                    <div
                                        className="referral-progress-line-fill"
                                        style={{ width: `${isCompleted ? 100 : progress}%` }}
                                    />
                                </div>
                            )}
                            <div className="referral-progress-reward">
                                <TicketIcon size={14} /> {r.reward}
                            </div>
                        </div>
                    );
                })}
            </div>
        </div>
    );
}