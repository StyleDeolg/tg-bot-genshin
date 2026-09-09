import { useEffect } from 'react';

export default function MondstadtBg() {
    useEffect(() => {
        const cloudContainer = document.querySelector('.clouds');
        const leafContainer = document.querySelector('.leaves');
        const particleContainer = document.querySelector('.wind-particles');

        if (cloudContainer) {
            cloudContainer.innerHTML = '';
            for (let i = 0; i < 6; i++) {
                const el = document.createElement('span');
                el.className = 'cloud';
                el.textContent = '☁';
                el.style.left = Math.random() * 100 + '%';
                el.style.top = 10 + Math.random() * 80 + '%';
                el.style.animationDelay = Math.random() * 40 + 's';
                el.style.animationDuration = (30 + Math.random() * 30) + 's';
                el.style.fontSize = (40 + Math.random() * 60) + 'px';
                cloudContainer.appendChild(el);
            }
        }

        if (leafContainer) {
            leafContainer.innerHTML = '';
            const leafSymbols = ['✦', '✧', '❋', '✻'];
            for (let i = 0; i < 12; i++) {
                const el = document.createElement('span');
                el.className = 'leaf';
                el.textContent = leafSymbols[i % leafSymbols.length];
                el.style.left = Math.random() * 100 + '%';
                el.style.top = 10 + Math.random() * 80 + '%';
                el.style.animationDelay = Math.random() * 30 + 's';
                el.style.animationDuration = (25 + Math.random() * 25) + 's';
                el.style.fontSize = (14 + Math.random() * 18) + 'px';
                leafContainer.appendChild(el);
            }
        }

        if (particleContainer) {
            particleContainer.innerHTML = '';
            for (let i = 0; i < 20; i++) {
                const el = document.createElement('span');
                el.className = 'wind-particle';
                el.style.left = Math.random() * 100 + '%';
                el.style.top = Math.random() * 100 + '%';
                el.style.animationDelay = Math.random() * 15 + 's';
                el.style.animationDuration = (8 + Math.random() * 12) + 's';
                el.style.width = (2 + Math.random() * 4) + 'px';
                el.style.height = (2 + Math.random() * 4) + 'px';
                particleContainer.appendChild(el);
            }
        }
    }, []);

    return (
        <div className="mondstadt-bg">
            <div className="clouds"></div>
            <div className="leaves"></div>
            <div className="wind-particles"></div>
            <div className="mondstadt-crest" style={{ bottom: '10%', left: '3%' }}>⚜</div>
            <div className="mondstadt-crest" style={{ top: '15%', right: '5%', fontSize: '28px' }}>⚜</div>
            <div className="mondstadt-crest" style={{ bottom: '25%', left: '50%', fontSize: '20px' }}>✧</div>
            <div className="mondstadt-crest" style={{ top: '55%', left: '80%', fontSize: '18px' }}>✦</div>
        </div>
    );
}