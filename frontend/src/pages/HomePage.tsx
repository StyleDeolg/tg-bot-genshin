import { useState, useEffect } from 'react';
import { useAuthStore } from '../store/authStore';
import { spinWheel } from '../api/wheel';
import { checkTasks } from '../api/tasks';
import Wheel from '../components/Wheel';
import TicketIcon from '../components/TicketIcon';
import ShardIcon from '../components/ShardIcon';
import ButtonGenshin from '../components/ButtonGenshin';
import GlassCard from '../components/GlassCard';

export default function HomePage() {
    const { user, updateProfile } = useAuthStore();
    const [isSpinning, setIsSpinning] = useState(false);
    const [result, setResult] = useState<any>(null);
    const [error, setError] = useState<string | null>(null);
    const [showResult, setShowResult] = useState(false);
    const [isClosing, setIsClosing] = useState(false); // 🔥 фаза "уход"

    const OFFSET = -2;

    // 🔥 Открытие модалки
    useEffect(() => {
        if (!showResult) return;

        // Через 2 секунды начинаем плавно скрывать
        const closeTimer = setTimeout(() => {
            setIsClosing(true);
        }, 2000);

        // Ещё через 400мс полностью убираем (когда анимация завершится)
        const removeTimer = setTimeout(() => {
            setShowResult(false);
            setIsClosing(false);
        }, 2400);

        return () => {
            clearTimeout(closeTimer);
            clearTimeout(removeTimer);
        };
    }, [showResult]);

    const handleSpin = async () => {
        if (!user || isSpinning) return;
        if (user.tickets < 1) {
            alert('Недостаточно билетиков!');
            return;
        }

        setIsSpinning(true);
        setResult(null);
        setError(null);
        setShowResult(false);
        setIsClosing(false);

        try {
            const data = await spinWheel(user.telegram_id);
            const visualIndex = (data.segment_index + OFFSET) % 8;

            setResult({
                ...data,
                visual_index: visualIndex,
            });

            try {
                await checkTasks(user.telegram_id);
            } catch (e) {
                console.log('checkTasks error:', e);
            }

            await updateProfile();

        } catch (err: any) {
            setError(err.response?.data?.detail || 'Ошибка при вращении');
            setIsSpinning(false);
        }
    };

    const handleSpinComplete = async () => {
        await updateProfile();
        setIsSpinning(false);
        setShowResult(true);
    };

    // 🔥 Возвращает: { emoji/icon, label, sublabel, isMoon }
    const getResultDisplay = () => {
        if (!result) return null;

        // 🌙 ЛУНА ИЗ 6 ОСКОЛКОВ — самый эпичный случай
        if (result.moon_completed) {
            return {
                emoji: '🌙',
                label: 'ЛУНА ТВОЯ!',
                sublabel: 'Ты собрал 6 осколков и получил ЛУНУ в Genshin Impact',
                isMoon: true,
            };
        }

        // 💨 ПУСТО
        if (result.prize_type?.startsWith('empty')) {
            return {
                emoji: '💨',
                label: 'ПУСТО',
                sublabel: 'Ничего не выпало. Попробуй ещё раз!',
                isMoon: false,
            };
        }

        // 🌙 ЛУНА НАПРЯМУЮ
        if (result.prize_type === 'moon' || result.prize_type === 'moon_from_shards') {
            return {
                emoji: '🌙',
                label: 'ЛУНА ТВОЯ!',
                sublabel: 'Ты выиграл ЛУНУ в Genshin Pool!',
                isMoon: true,
            };
        }

        // 🔮 ОСКОЛОК
        if (result.prize_type === 'shard') {
            return {
                icon: <ShardIcon size={56} />,
                label: 'ОСКОЛОК ЛУНЫ!',
                sublabel: `Собрано ${result.shards}/6. Ещё немного!`,
                isMoon: false,
            };
        }

        // 💎 КРИСТАЛЛЫ
        if (result.prize_type === 'crystals_60' || result.prize_type === 'crystals_330') {
            return {
                emoji: '💎',
                label: 'ПОЗДРАВЛЯЮ!',
                sublabel: `Ты выиграл ${result.prize_value} кристаллов!`,
                isMoon: false,
            };
        }

        // Fallback
        return {
            emoji: result.emoji || '🎁',
            label: 'ПОБЕДА!',
            sublabel: `Ты выиграл ${result.prize}!`,
            isMoon: false,
        };
    };

    const resultDisplay = getResultDisplay();

    return (
        <div className="page home-page">
            <div className="home-content">
                <div className="page-header">
                    <h1 className="page-title">Колесо Фортуны</h1>
                    <p className="page-subtitle">Крути и выигрывай призы</p>
                </div>

                <GlassCard>
                    <Wheel
                        isSpinning={isSpinning}
                        resultSegmentIndex={result?.visual_index ?? null}
                        onSpinComplete={handleSpinComplete}
                    />
                </GlassCard>

                <div className="d-flex justify-content-center w-100">
                    <ButtonGenshin
                        text={isSpinning ? 'Вращается...' : 'Вращать'}
                        onClick={handleSpin}
                        disabled={isSpinning || (user?.tickets ?? 0) < 1}
                        icon={!isSpinning ? <TicketIcon size={18} /> : undefined}
                    />
                </div>

                {/* 🔥 МОДАЛЬНОЕ ОКНО */}
                {showResult && resultDisplay && (
                    <div className={`spin-modal-overlay ${isClosing ? 'closing' : ''}`}>
                        <div className={`spin-modal ${resultDisplay.isMoon ? 'spin-modal-moon' : ''}`}>
                            <div className="spin-modal-content">
                                {resultDisplay.icon ? (
                                    <div className="spin-modal-emoji">{resultDisplay.icon}</div>
                                ) : (
                                    <div className="spin-modal-emoji">{resultDisplay.emoji}</div>
                                )}

                                {/* 🔥 Акцентная надпись */}
                                <h2 className="spin-modal-label">{resultDisplay.label}</h2>

                                {/* Подпись */}
                                <p className="spin-modal-sublabel">{resultDisplay.sublabel}</p>
                            </div>
                        </div>
                    </div>
                )}

                {error && (
                    <div className="spin-error">
                        <p>❌ {error}</p>
                    </div>
                )}
            </div>
        </div>
    );
}