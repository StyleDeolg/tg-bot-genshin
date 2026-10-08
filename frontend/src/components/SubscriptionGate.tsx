import { useEffect } from 'react';

interface SponsorLink {
    id: string;
    name: string;
    link: string;
}

interface SubscriptionGateProps {
    missing: SponsorLink[];
    botUsername: string;
    onRetry: () => void;
    checking?: boolean;
}

export default function SubscriptionGate({
    missing,
    botUsername,
    onRetry,
    checking = false,
}: SubscriptionGateProps) {
    // При загрузке — раскрываем Mini App на весь экран
    useEffect(() => {
        if (window.Telegram?.WebApp) {
            window.Telegram.WebApp.expand();
            window.Telegram.WebApp.disableVerticalSwipes?.();
        }
    }, []);

    const handleOpenBot = () => {
        // В Telegram Mini App — закрываем приложение
        if (window.Telegram?.WebApp) {
            window.Telegram.WebApp.close();
            return;
        }

        // Fallback: если открыто в обычном браузере — открываем бота
        if (botUsername) {
            window.open(`https://t.me/${botUsername}`, '_blank');
        }
    };

    return (
        <div className="subscription-gate">
            <div className="subscription-gate-bg" />
            <div className="subscription-gate-content">
                <div className="subscription-gate-icon">🔒</div>

                <h1 className="subscription-gate-title">ДОСТУП ЗАКРЫТ</h1>

                <p className="subscription-gate-subtitle">
                    Чтобы пользоваться приложением,<br />
                    подпишись на всех спонсоров
                </p>

                <div className="subscription-gate-count">
                    Осталось подписаться: <span>{missing.length}</span>
                </div>

                <button
                    className="subscription-gate-button"
                    onClick={handleOpenBot}
                >
                    📢 ПОДПИСАТЬСЯ В БОТЕ
                </button>

                <button
                    className="subscription-gate-retry"
                    onClick={onRetry}
                    disabled={checking}
                >
                    {checking ? '⏳ Проверяю...' : '🔄 Я подписался, проверить'}
                </button>

                <p className="subscription-gate-hint">
                    После подписки вернись в приложение
                </p>
            </div>
        </div>
    );
}