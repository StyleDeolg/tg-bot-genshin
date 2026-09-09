import { useState, useEffect } from 'react';
import './LoadingScreen.css';

const characters = [
    { name: 'Венти', image: '/characters/Venti.png', quote: 'Ветер свободы всегда ведёт нас вперёд.' },
    { name: 'Джинн', image: '/characters/Jean.png', quote: 'Я клянусь защищать Мондштадт до последнего вздоха.' },
    { name: 'Дилюк', image: '/characters/Diluc.png', quote: 'Тьма не может скрыть правду, как и свет — ложь.' },
    { name: 'Кэйа', image: '/characters/Kaeya.png', quote: 'Лёд и пламя — две стороны одной медали.' },
    { name: 'Лиза', image: '/characters/Lisa.png', quote: 'Знания — это сила, но не всегда безопасная.' },
    { name: 'Беннет', image: '/characters/Bennett.png', quote: 'Не сдавайся! Даже если всё идёт не по плану!' },
    { name: 'Фишль', image: '/characters/Fischl.png', quote: 'Я, Фишль, приветствую тебя в моём мире!' },
    { name: 'Ноэль', image: '/characters/Noel.png', quote: 'Я защищу вас, чего бы это ни стоило!' },
    { name: 'Сахароза', image: '/characters/Sucrose.png', quote: 'Я... Я просто хочу помочь тебе в твоих исследованиях.' },
    { name: 'Альбедо', image: '/characters/Albedo.png', quote: 'Мои исследования — это не просто работа, это моя страсть.' },
];

const MIN_LOADING_TIME = 5000;

export default function LoadingScreen({ onLoadingComplete }: { onLoadingComplete?: () => void }) {
    const [progress, setProgress] = useState(0);
    const [currentChar, setCurrentChar] = useState(characters[0]);

    useEffect(() => {
        const startTime = Date.now();
        const randomChar = characters[Math.floor(Math.random() * characters.length)];
        setCurrentChar(randomChar);

        const progressInterval = setInterval(() => {
            const elapsed = Date.now() - startTime;
            setProgress(Math.min((elapsed / MIN_LOADING_TIME) * 100, 100));
        }, 50);

        const charInterval = setInterval(() => {
            const randomChar = characters[Math.floor(Math.random() * characters.length)];
            setCurrentChar(randomChar);
        }, 4000);

        const timer = setTimeout(() => {
            clearInterval(progressInterval);
            clearInterval(charInterval);
            setProgress(100);
            if (onLoadingComplete) onLoadingComplete();
        }, MIN_LOADING_TIME);

        return () => {
            clearInterval(progressInterval);
            clearInterval(charInterval);
            clearTimeout(timer);
        };
    }, []);

    return (
        <div className="loading-screen">
            <div className="loading-bg"></div>
            <div className="loading-content">
                <div className="loading-header">
                    <span className="loading-crest">⚜</span>
                    <h1 className="loading-title">Genshin Pool</h1>
                    <p className="loading-sub">Мондштадт · Город Свободы</p>
                </div>

                <div className="loading-center">
                    <div className="loading-character">
                        <div className="character-circle">
                            <img src={currentChar.image} alt={currentChar.name} className="character-image" />
                        </div>
                        <p className="character-name">{currentChar.name}</p>
                    </div>

                    <div className="loading-bar-wrapper">
                        <div className="loading-bar-track">
                            <div className="loading-bar-fill" style={{ width: `${progress}%` }}>
                                <div className="loading-bar-shimmer"></div>
                            </div>
                        </div>
                        <span className="loading-percent">{Math.round(progress)}%</span>
                    </div>

                    <div className="loading-quote">
                        <p className="quote-text">«{currentChar.quote}»</p>
                    </div>
                </div>

                <div className="loading-footer">
                    <p className="loading-version">⚜ v1.0.0 · Мондштадт</p>
                </div>
            </div>
        </div>
    );
}