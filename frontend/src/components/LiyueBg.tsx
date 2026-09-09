import { useEffect } from 'react';

export default function LiyueBg() {
    useEffect(() => {
        const container = document.querySelector('.liyue-bg');
        if (!container) return;

        const existing = container.querySelectorAll('.liyue-ornament');
        existing.forEach(el => el.remove());

        const ornaments = ['岩', '璃', '月', '港'];
        for (let i = 0; i < 4; i++) {
            const el = document.createElement('div');
            el.className = 'liyue-ornament';
            el.textContent = ornaments[i % ornaments.length];
            el.style.top = (10 + Math.random() * 70) + '%';
            el.style.left = (5 + Math.random() * 85) + '%';
            el.style.fontSize = (50 + Math.random() * 80) + 'px';
            el.style.opacity = String(0.01 + Math.random() * 0.02);
            el.style.animation = `ornamentFloat ${25 + Math.random() * 20}s ease-in-out infinite`;
            el.style.animationDelay = Math.random() * 10 + 's';
            container.appendChild(el);
        }
    }, []);

    return (
        <div className="liyue-bg">
            <img
                src="/images/liyue/liyue-bg.jpg"
                alt="Liyue"
                className="liyue-bg-image"
            />
            <div className="liyue-clouds-wrapper">
                <img
                    src="/images/liyue/oblako.png"
                    alt="Clouds"
                    className="liyue-clouds-pattern"
                />
            </div>
            <img
                src="/images/liyue/dragon.png"
                alt="Dragon"
                className="liyue-dragon-decor"
            />
            <div className="liyue-pattern-overlay"></div>
        </div>
    );
}