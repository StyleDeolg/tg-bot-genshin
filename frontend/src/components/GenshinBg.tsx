import { useEffect } from 'react';

export default function GenshinBg() {
    useEffect(() => {
        const container = document.querySelector('.genshin-bg');
        if (!container) return;

        const existing = container.querySelectorAll('.genshin-ornament');
        existing.forEach(el => el.remove());

        const ornaments = ['✦', '✧', '✦', '✧'];
        for (let i = 0; i < 6; i++) {
            const el = document.createElement('div');
            el.className = 'genshin-ornament';
            el.textContent = ornaments[i % ornaments.length];
            el.style.top = (5 + Math.random() * 85) + '%';
            el.style.left = (5 + Math.random() * 85) + '%';
            el.style.fontSize = (30 + Math.random() * 50) + 'px';
            el.style.opacity = String(0.01 + Math.random() * 0.02);
            el.style.animation = `ornamentFloat ${30 + Math.random() * 20}s ease-in-out infinite`;
            el.style.animationDelay = Math.random() * 15 + 's';
            container.appendChild(el);
        }
    }, []);

    return (
        <div className="genshin-bg">
            <img
                src="/images/liyue/liyue-bg.jpg"
                alt="Genshin Impact"
                className="genshin-bg-image"
            />
            <div className="genshin-glow"></div>
        </div>
    );
}