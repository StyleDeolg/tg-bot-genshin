import { useEffect, useRef } from 'react';

const arkhonts = [
    // Венти — арфа / крылья
    <svg key="venti" viewBox="0 0 100 100" fill="none" xmlns="http://www.w3.org/2000/svg">
        <path d="M50 15 L40 35 L20 30 L35 50 L15 65 L35 65 L45 85 L55 85 L65 65 L85 65 L65 50 L80 30 L60 35 L50 15Z" stroke="currentColor" strokeWidth="1.5" />
        <path d="M35 45 L45 55 L55 45 L45 35 L35 45Z" stroke="currentColor" strokeWidth="1" />
        <circle cx="50" cy="50" r="4" stroke="currentColor" strokeWidth="1" />
    </svg>,
    // Чжун Ли — гора / копьё
    <svg key="zhongli" viewBox="0 0 100 100" fill="none" xmlns="http://www.w3.org/2000/svg">
        <path d="M50 10 L30 45 L25 40 L50 80 L75 40 L70 45 L50 10Z" stroke="currentColor" strokeWidth="1.5" />
        <path d="M40 30 L60 30 L55 45 L45 45 L40 30Z" stroke="currentColor" strokeWidth="1" />
        <rect x="45" y="50" width="10" height="25" stroke="currentColor" strokeWidth="1.5" />
    </svg>,
    // Райдэн — молния / катана
    <svg key="raiden" viewBox="0 0 100 100" fill="none" xmlns="http://www.w3.org/2000/svg">
        <path d="M50 10 L35 45 L45 40 L55 70 L45 65 L65 90 L55 55 L65 50 L50 10Z" stroke="currentColor" strokeWidth="1.5" />
        <path d="M45 35 L55 35 L50 50 L45 35Z" stroke="currentColor" strokeWidth="1" />
    </svg>,
    // Нахида — дерево / лист
    <svg key="nahida" viewBox="0 0 100 100" fill="none" xmlns="http://www.w3.org/2000/svg">
        <ellipse cx="50" cy="35" rx="25" ry="20" stroke="currentColor" strokeWidth="1.5" />
        <path d="M50 15 L50 55 L40 70 L60 70 L50 55Z" stroke="currentColor" strokeWidth="1.5" />
        <path d="M40 45 L35 55 L65 55 L60 45" stroke="currentColor" strokeWidth="1" />
        <circle cx="50" cy="50" r="3" stroke="currentColor" strokeWidth="1" />
    </svg>,
    // Фокалорс — волны / корона
    <svg key="focalors" viewBox="0 0 100 100" fill="none" xmlns="http://www.w3.org/2000/svg">
        <path d="M50 20 C65 20 70 35 65 45 C60 55 70 65 60 75 L40 75 C30 65 40 55 35 45 C30 35 35 20 50 20Z" stroke="currentColor" strokeWidth="1.5" />
        <path d="M40 35 L45 45 L55 45 L60 35" stroke="currentColor" strokeWidth="1" />
        <path d="M45 55 L50 65 L55 55" stroke="currentColor" strokeWidth="1" />
    </svg>,
];

export default function BackgroundArkhonts() {
    const containerRef = useRef<HTMLDivElement>(null);

    useEffect(() => {
        const container = containerRef.current;
        if (!container) return;
        const els = container.querySelectorAll('.arkhont-icon');
        els.forEach((el, i) => {
            const duration = 30 + i * 8;
            (el as HTMLElement).style.animationDuration = `${duration}s`;
        });
    }, []);

    return (
        <div ref={containerRef} className="arkhonts-bg">
            {arkhonts.map((arkhont, i) => (
                <div
                    key={i}
                    className="arkhont-icon"
                    style={{
                        position: 'absolute',
                        width: `${70 + i * 30}px`,
                        height: `${70 + i * 30}px`,
                        color: '#d4af37',
                        top: `${5 + i * 18}%`,
                        left: `${5 + i * 25}%`,
                        opacity: 0.03,
                        animation: `spinArkhont ${30 + i * 8}s linear infinite`,
                        transformOrigin: 'center center',
                        pointerEvents: 'none',
                        userSelect: 'none',
                    }}
                >
                    {arkhont}
                </div>
            ))}
        </div>
    );
}