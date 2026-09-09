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

    if (loading) return <div className="loading-text">Загрузка...</div>;

    return (
        <div className="page friends-page">
            <div className="friends-content">
                <div className="page-header">
                    <span className="page-title-chinese">四海之内皆兄弟</span>
                    <h1 className="page-title">Друзья</h1>
                    <p className="page-subtitle">Приглашай и получай бонусы</p>
                </div>

                <div className="liyue-card">
                    <p style={{
                        fontFamily: "'Inter', sans-serif",
                        color: 'rgba(61, 53, 46, 0.3)',
                        fontSize: '13px',
                        marginBottom: '8px'
                    }}>
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
                        <span className="stat-label">Приглашено</span>
                    </div>
                </div>

                <span className="list-title">Прогресс наград</span>

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
        </div>
    );
}