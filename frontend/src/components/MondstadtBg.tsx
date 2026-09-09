import { useEffect } from 'react';

export default function MondstadtBg() {
    useEffect(() => {
        const container = document.querySelector('.mondstadt-bg');
        if (!container) return;

        const existing = container.querySelectorAll('.mondstadt-ornament');
        existing.forEach(el => el.remove());

        const ornaments = ['⚜', '✧', '✦', '✶'];
        for (let i = 0; i < 4; i++) {
            const el = document.createElement('div');
            el.className = 'mondstadt-ornament';
            el.textContent = ornaments[i % ornaments.length];
            el.style.top = (10 + Math.random() * 70) + '%';
            el.style.left = (5 + Math.random() * 85) + '%';
            el.style.fontSize = (40 + Math.random() * 60) + 'px';
            el.style.opacity = String(0.003 + Math.random() * 0.005);
            el.style.animation = `ornamentFloat ${25 + Math.random() * 20}s ease-in-out infinite`;
            el.style.animationDelay = Math.random() * 10 + 's';
            container.appendChild(el);
        }
    }, []);

    return (
        <div className="mondstadt-bg">
            <img
                src="/images/liyue/liyue-bg.jpg"
                alt="Mondstadt"
                className="mondstadt-bg-image"
            />
            <div className="liyue-pattern-overlay"></div>
        </div>
    );
}