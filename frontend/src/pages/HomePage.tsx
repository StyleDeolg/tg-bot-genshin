import { useState } from 'react';
import { useAuthStore } from '../store/authStore';
import { spinWheel, checkTasks } from '../api';
import Wheel from '../components/Wheel';
import GoldButton from '../components/GoldButton';
import GlassCard from '../components/GlassCard';
import TicketIcon from '../components/TicketIcon';
import PrimogemIcon from '../components/PrimogemIcon';

export default function HomePage() {
    const { user, updateProfile } = useAuthStore();
    const [isSpinning, setIsSpinning] = useState(false);
    const [result, setResult] = useState<any>(null);
    const [error, setError] = useState<string | null>(null);
    const [showResult, setShowResult] = useState(false);

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

        try {
            const data = await spinWheel(user.telegram_id);

            console.log('🔍 ===== ВРАЩЕНИЕ КОЛЕСА =====');
            console.log('📦 Полный ответ от сервера:', JSON.stringify(data, null, 2));
            console.log('🏆 Выигрышный приз:', data.prize);
            console.log('💎 Значение:', data.prize_value);
            console.log('🎯 Должен остановиться на:', data.prize);

            setResult(data);

            await checkTasks(user.telegram_id);

            setTimeout(async () => {
                await updateProfile();
                setIsSpinning(false);
                setShowResult(true);
            }, 1000);

        } catch (err: any) {
            console.error('❌ Ошибка:', err);
            setError(err.response?.data?.detail || 'Ошибка при вращении');
            setIsSpinning(false);
        }
    };

    return (
        <div className="page home-page">
            <div className="home-content">
                <h1 className="page-title">🎡 Колесо фортуны</h1>
                <p className="page-subtitle">Крути и выигрывай примогемы!</p>

                <GlassCard>
                    <Wheel isSpinning={isSpinning} resultPrize={result?.prize || null} />
                </GlassCard>

                <GoldButton
                    text={isSpinning ? '🔄 Крутится...' : 'Крутить'}
                    onClick={handleSpin}
                    disabled={isSpinning || (user?.tickets ?? 0) < 1}
                    icon={!isSpinning ? <TicketIcon size={18} /> : undefined}
                />

                {showResult && result && (
                    <div className="spin-result">
                        <div className="spin-result-content">
                            {result.emoji === '💨' ? (
                                <span className="spin-result-emoji">💨</span>
                            ) : (
                                <PrimogemIcon size={28} className="spin-result-icon" />
                            )}
                            <p>
                                {result.emoji === '💨'
                                    ? ' Тебе ничего не выпало... Попробуй ещё раз!'
                                    : ` Ты выиграл ${result.prize}! (+${result.prize_value} 💎)`
                                }
                            </p>
                        </div>
                    </div>
                )}

                {error && <div className="spin-error"><p>❌ {error}</p></div>}
            </div>
        </div>
    );
}