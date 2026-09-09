import { useEffect } from 'react';

export default function MondstadtBg() {
    useEffect(() => {
        const cloudContainer = document.querySelector('.clouds');
        const leafContainer = document.querySelector('.leaves');

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
            const leafSymbols = ['🍃', '🍂', '✧', '✦'];
            for (let i = 0; i < 10; i++) {
                const el = document.createElement('span');
                el.className = 'leaf';
                el.textContent = leafSymbols[i % leafSymbols.length];
                el.style.left = Math.random() * 100 + '%';
                el.style.top = 10 + Math.random() * 80 + '%';
                el.style.animationDelay = Math.random() * 30 + 's';
                el.style.animationDuration = (25 + Math.random() * 25) + 's';
                el.style.fontSize = (14 + Math.random() * 16) + 'px';
                leafContainer.appendChild(el);
            }
        }
    }, []);

    return (
        <div className="mondstadt-bg">
            <div className="clouds"></div>
            <div className="leaves"></div>
            <div className="mondstadt-crest" style={{ bottom: '10%', left: '3%' }}>⚜</div>
            <div className="mondstadt-crest" style={{ top: '15%', right: '5%', fontSize: '28px' }}>⚜</div>
            <div className="mondstadt-crest" style={{ bottom: '25%', left: '50%', fontSize: '20px' }}>✧</div>
        </div>
    );
}