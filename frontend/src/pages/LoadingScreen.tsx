import { useState, useEffect } from 'react';
import './LoadingScreen.css';

const characters = [
    { name: 'Чжун Ли', image: '/characters/Zhongli.png', quote: 'Контракты должны соблюдаться, даже если время идёт против нас.' },
    { name: 'Ху Тао', image: '/characters/Hutao.png', quote: 'Жизнь коротка, так что давай веселиться!' },
    { name: 'Гань Юй', image: '/characters/Ganyu.png', quote: 'Я всегда рада помочь, даже если это значит работать сверхурочно.' },
    { name: 'Сяо', image: '/characters/Xiao.png', quote: 'Я страж, и мой долг — защищать этот мир.' },
    { name: 'Кэ Цин', image: '/characters/Keqing.png', quote: 'Я, Кэ Цин, не привыкла ждать чуда. Я сама творю свою судьбу.' },
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
                    <span className="loading-crest">璃</span>
                    <h1 className="loading-title">Genshin Pool</h1>
                    <p className="loading-sub">璃月 · 契约之城</p>
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
                    <p className="loading-version">璃月 · v1.0.0</p>
                </div>
            </div>
        </div>
    );
}