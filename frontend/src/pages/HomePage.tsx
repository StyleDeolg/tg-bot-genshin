import { useState } from 'react';
import { useAuthStore } from '../store/authStore';
import { spinWheel } from '../api/wheel';
import { checkTasks } from '../api/tasks';
import Wheel from '../components/Wheel';
import GoldButton from '../components/GoldButton';
import GlassCard from '../components/GlassCard';
import TicketIcon from '../components/TicketIcon';
import ShardIcon from '../components/ShardIcon';

export default function HomePage() {
    const { user, updateProfile } = useAuthStore();
    const [isSpinning, setIsSpinning] = useState(false);
    const [result, setResult] = useState<any>(null);
    const [error, setError] = useState<string | null>(null);
    const [showResult, setShowResult] = useState(false);
    const [debugInfo, setDebugInfo] = useState<string>('');

    // ===== ПЕРЕОПРЕДЕЛЯЕМ ИНДЕКСЫ =====
    // Бэкенд возвращает индекс, но на колесе порядок может отличаться
    // Здесь мы задаём правильное соответствие
    const getVisualIndex = (backendIndex: number): number => {
        // Если перепутаны местами, меняем здесь
        const mapping: Record<number, number> = {
            0: 0,   // Пусто → Пусто
            1: 1,   // Осколок → 60 кристаллов (если перепутаны)
            2: 2,   // Пусто → Пусто
            3: 3,   // 60 кристаллов → Осколок (если перепутаны)
            4: 4,   // Пусто → Пусто
            5: 5,   // Луна → 330 кристаллов (если перепутаны)
            6: 6,   // Пусто → Пусто
            7: 7,   // 330 кристаллов → Луна (если перепутаны)
        };
        return mapping[backendIndex] ?? backendIndex;
    };

    const handleSpin = async () => {
        if (!user || isSpinning) return;
        if (user.tickets < 1) {
            alert('❌ Недостаточно билетиков!');
            return;
        }

        setIsSpinning(true);
        setResult(null);
        setError(null);
        setShowResult(false);
        setDebugInfo('⏳ Отправка запроса...');

        try {
            const data = await spinWheel(user.telegram_id);

            // Преобразуем индекс для визуального отображения
            const visualIndex = getVisualIndex(data.segment_index);

            setDebugInfo(`🎯 ${data.prize} (индекс БД: ${data.segment_index} → визуальный: ${visualIndex})`);
            setResult({
                ...data,
                visual_index: visualIndex,  // ← добавляем визуальный индекс
            });

            try {
                await checkTasks(user.telegram_id);
            } catch (e) {
                console.log('checkTasks error:', e);
            }

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
                <h1 className="page-title">🎡 Колесо фортуны</h1>
                <p className="page-subtitle">Крути и выигрывай призы!</p>

                <GlassCard>
                    <Wheel
                        isSpinning={isSpinning}
                        resultSegmentIndex={result?.visual_index ?? null}
                        onSpinComplete={handleSpinComplete}
                    />
                </GlassCard>

                {debugInfo && (
                    <div style={{
                        marginTop: '8px',
                        padding: '6px 12px',
                        background: 'rgba(0,0,0,0.3)',
                        borderRadius: '8px',
                        fontSize: '12px',
                        color: 'rgba(240,236,229,0.5)',
                        fontFamily: 'monospace',
                        width: '100%',
                        textAlign: 'center',
                    }}>
                        {debugInfo}
                    </div>
                )}

                <GoldButton
                    text={isSpinning ? '🔄 Крутится...' : 'Крутить'}
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