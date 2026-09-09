import { useState, useEffect } from 'react';
import './LoadingScreen.css';

const characters = [
    {
        name: 'Альбедо',
        image: '/characters/Albedo.png',
        quote: 'Мои исследования — это не просто работа, это моя страсть.'
    },
    {
        name: 'Беннет',
        image: '/characters/Bennett.png',
        quote: 'Не сдавайся! Даже если всё идёт не по плану!'
    },
    {
        name: 'Дилюк',
        image: '/characters/Diluc.png',
        quote: 'Тьма не может скрыть правду, как и свет — ложь.'
    },
    {
        name: 'Фишль',
        image: '/characters/Fischl.png',
        quote: 'Я, Фишль, приветствую тебя в моём мире!'
    },
    {
        name: 'Гань Юй',
        image: '/characters/Ganyu.png',
        quote: 'Я всегда рада помочь, даже если это значит работать сверхурочно.'
    },
    {
        name: 'Ху Тао',
        image: '/characters/Hutao.png',
        quote: 'Жизнь коротка, так что давай веселиться!'
    },
    {
        name: 'Кадзуха',
        image: '/characters/Kazuha.png',
        quote: 'Ветер помнит тех, кто ушёл, но не тех, кто остался.'
    },
    {
        name: 'Кэ Цин',
        image: '/characters/Keqing.png',
        quote: 'Я, Кэ Цин, не привыкла ждать чуда. Я сама творю свою судьбу.'
    },
    {
        name: 'Кокоми',
        image: '/characters/Kokomi.png',
        quote: 'Стратегия — это искусство, и я его мастер.'
    },
    {
        name: 'Мона',
        image: '/characters/Mona.png',
        quote: 'Звёзды говорят мне, что нас ждёт великое приключение.'
    },
    {
        name: 'Нахида',
        image: '/characters/Nahida.png',
        quote: 'Знание — это свет, который ведёт нас сквозь тьму.'
    },
    {
        name: 'Ноэль',
        image: '/characters/Noel.png',
        quote: 'Я защищу вас, чего бы это ни стоило!'
    },
    {
        name: 'Рэйзор',
        image: '/characters/Razor.png',
        quote: 'Я — волк. Волк — это я. Мы вместе.'
    },
    {
        name: 'Розария',
        image: '/characters/Rosaria.png',
        quote: 'Я не люблю шумные компании, но ты — исключение.'
    },
    {
        name: 'Райдэн Эи',
        image: '/characters/Shougun.png',
        quote: 'Вечность — это не просто слово, это мой путь.'
    },
    {
        name: 'Сахароза',
        image: '/characters/Sucrose.png',
        quote: 'Я... Я просто хочу помочь тебе в твоих исследованиях.'
    },
    {
        name: 'Тарталья',
        image: '/characters/Tartaglia.png',
        quote: 'Битва — это поэзия, и я её главный поэт.'
    },
    {
        name: 'Венти',
        image: '/characters/Venti.png',
        quote: 'Ветер свободы всегда ведёт нас вперёд.'
    },
    {
        name: 'Сяо',
        image: '/characters/Xiao.png',
        quote: 'Я страж, и мой долг — защищать этот мир.'
    },
    {
        name: 'Чжун Ли',
        image: '/characters/Zhongli.png',
        quote: 'Контракты должны соблюдаться, даже если время идёт против нас.'
    },
];

const MIN_LOADING_TIME = 3000;

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
        }, 3500);

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
            <div className="loading-bg">
                <img
                    src="/images/liyue/liyue-bg.jpg"
                    alt="Genshin Impact"
                    className="loading-bg-image"
                />
                <div className="loading-glow"></div>
            </div>

            <div className="loading-content">
                <div className="loading-header">
                    <span className="loading-crest">✦</span>
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
                    <p className="loading-version">✦ v1.0.0 · Мондштадт</p>
                </div>
            </div>
        </div>
    );
}