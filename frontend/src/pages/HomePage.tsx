import { useState } from 'react';
import { useAuthStore } from '../store/authStore';
import { spinWheel } from '../api/wheel';
import { checkTasks } from '../api/tasks';
import Wheel from '../components/Wheel';
import LiyueButton from '../components/LiyueButton';
import LiyueCard from '../components/LiyueCard';
import TicketIcon from '../components/TicketIcon';
import ShardIcon from '../components/ShardIcon';
import PageOrnament from '../components/PageOrnament';

export default function HomePage() {
    const { user, updateProfile } = useAuthStore();
    const [isSpinning, setIsSpinning] = useState(false);
    const [result, setResult] = useState<any>(null);
    const [error, setError] = useState<string | null>(null);
    const [showResult, setShowResult] = useState(false);
    const [debugInfo, setDebugInfo] = useState<string>('');

    const OFFSET = -2;

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
        setDebugInfo('⏳ Отправка запроса...');

        try {
            const data = await spinWheel(user.telegram_id);
            const visualIndex = (data.segment_index + OFFSET) % 8;

            setDebugInfo(`🎯 ${data.prize} (индекс БД: ${data.segment_index} → визуальный: ${visualIndex})`);
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
            setDebugInfo('❌ Ошибка');
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

        if (result.prize_type?.startsWith('empty')) {
            return { emoji: '💨', text: 'Тебе ничего не выпало... Попробуй ещё раз!' };
        }
        if (result.prize_type === 'moon') {
            return { emoji: '🌙', text: 'Ты выиграл ЛУНУ! 🎉' };
        }
        if (result.prize_type === 'shard') {
            return {
                icon: <ShardIcon size={28} />,
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
                <PageOrnament />
                <h1 className="page-title">乾坤轮</h1>
                <p className="page-subtitle">Колесо Фортуны</p>

                <LiyueCard>
                    <Wheel
                        isSpinning={isSpinning}
                        resultSegmentIndex={result?.visual_index ?? null}
                        onSpinComplete={handleSpinComplete}
                    />
                </LiyueCard>

                {debugInfo && (
                    <div className="debug-info">
                        {debugInfo}
                    </div>
                )}

                <LiyueButton
                    text={isSpinning ? 'Вращается...' : 'Вращать'}
                    onClick={handleSpin}
                    disabled={isSpinning || (user?.tickets ?? 0) < 1}
                    icon={!isSpinning ? <TicketIcon size={18} /> : undefined}
                />

                {showResult && resultDisplay && (
                    <div className="spin-result">
                        <div className="spin-result-content">
                            {resultDisplay.icon ? (
                                <span className="spin-result-emoji">{resultDisplay.icon}</span>
                            ) : (
                                <span className="spin-result-emoji">{resultDisplay.emoji}</span>
                            )}
                            <p>{resultDisplay.text}</p>
                        </div>
                    </div>
                )}

                {error && <div className="spin-error"><p>❌ {error}</p></div>}
            </div>
        </div>
    );
}