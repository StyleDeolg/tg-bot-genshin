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

    const OFFSET = -2;

    // 🔥 Автоскрытие модалки через 2 секунды
    useEffect(() => {
        if (!showResult) return;
        const timer = setTimeout(() => {
            setShowResult(false);
        }, 2000);
        return () => clearTimeout(timer);
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

    const getResultDisplay = () => {
        if (!result) return null;

        if (result.moon_completed) {
            return {
                emoji: '🌙',
                text: 'Ты собрал 6 осколков и получил ЛУНУ!'
            };
        }
        if (result.prize_type?.startsWith('empty')) {
            return { emoji: '💨', text: 'Тебе ничего не выпало... Попробуй ещё раз!' };
        }
        if (result.prize_type === 'moon' || result.prize_type === 'moon_from_shards') {
            return { emoji: '🌙', text: 'Ты выиграл ЛУНУ! 🎉' };
        }
        if (result.prize_type === 'shard') {
            return {
                icon: <ShardIcon size={56} />,
                text: `Ты выиграл осколок! (${result.shards}/6)`
            };
        }
        if (result.prize_type === 'crystals_60' || result.prize_type === 'crystals_330') {
            return {
                emoji: '💎',
                text: `Ты выиграл ${result.prize_value} кристаллов!`
            };
        }
        return {
            emoji: result.emoji || '🎁',
            text: `Ты выиграл ${result.prize}!`
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

                {/* 🔥 МОДАЛЬНОЕ ОКНО ПОВЕРХ ЭКРАНА */}
                {showResult && resultDisplay && (
                    <div className="spin-modal-overlay">
                        <div className={`spin-modal ${result?.moon_completed ? 'spin-modal-moon' : ''}`}>
                            <div className="spin-modal-content">
                                {resultDisplay.icon ? (
                                    <div className="spin-modal-emoji">{resultDisplay.icon}</div>
                                ) : (
                                    <div className="spin-modal-emoji">{resultDisplay.emoji}</div>
                                )}
                                <p className="spin-modal-text">{resultDisplay.text}</p>
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