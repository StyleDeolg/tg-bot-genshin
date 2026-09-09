import { useEffect } from 'react';

export default function MondstadtBg() {
    useEffect(() => {
        const container = document.querySelector('.wind-particles');
        if (!container) return;

        const particles = ['✦', '✧', '✶', '✴', '❋', '✻'];
        // Очищаем старые частицы
        container.innerHTML = '';

        for (let i = 0; i < 14; i++) {
            const el = document.createElement('span');
            el.className = 'wind-particle';
            el.textContent = particles[i % particles.length];
            el.style.left = Math.random() * 100 + '%';
            el.style.top = Math.random() * 100 + '%';
            el.style.animationDelay = Math.random() * 25 + 's';
            el.style.animationDuration = (20 + Math.random() * 25) + 's';
            el.style.fontSize = (10 + Math.random() * 20) + 'px';
            container.appendChild(el);
        }
    }, []);

    return (
        <div className="mondstadt-bg">
            <div className="wind-particles"></div>
            <div
                className="mondstadt-crest"
                style={{ bottom: '12%', left: '3%', animationDelay: '0s' }}
            >
                ⚜️
            </div>
            <div
                className="mondstadt-crest"
                style={{ top: '20%', right: '5%', animationDelay: '2s', width: '60px', height: '60px', fontSize: '30px' }}
            >
                ⚜️
            </div>
            <div
                className="mondstadt-crest"
                style={{ bottom: '30%', left: '45%', animationDelay: '4s', width: '45px', height: '45px', fontSize: '22px' }}
            >
                ✦
            </div>
            <div
                className="mondstadt-crest"
                style={{ top: '55%', left: '80%', animationDelay: '1s', width: '35px', height: '35px', fontSize: '18px' }}
            >
                ✧
            </div>
        </div>
    );
}