import { useEffect, useState, useRef } from 'react';
import { getPrizes } from '../api';

interface Prize {
    name: string;
    value: number;
    emoji: string;
    color: string;
}

interface WheelProps {
    isSpinning?: boolean;
    resultPrize?: string | null;
}

export default function Wheel({ isSpinning = false, resultPrize = null }: WheelProps) {
    const [segments, setSegments] = useState<Prize[]>([]);
    const [rotation, setRotation] = useState(0);
    const [targetRotation, setTargetRotation] = useState<number | null>(null);
    const [isAnimating, setIsAnimating] = useState(false);
    const idleIntervalRef = useRef<ReturnType<typeof setInterval> | null>(null);

    // Загружаем призы
    useEffect(() => {
        getPrizes().then((data: Prize[]) => {
            setSegments(data);
        });
    }, []);

    // Когда приходит результат — вычисляем целевой угол
    useEffect(() => {
        if (resultPrize && segments.length > 0 && !isAnimating) {
            const targetIndex = segments.findIndex(p => p.name === resultPrize);

            if (targetIndex !== -1) {
                const segmentAngle = 360 / segments.length;
                const targetAngle = 360 - (targetIndex * segmentAngle + segmentAngle / 2);
                const spins = 5 + Math.random() * 3;
                const totalRotation = spins * 360 + targetAngle;

                setTargetRotation(totalRotation);
            }
        }
    }, [resultPrize, segments]);

    // Применяем вращение
    useEffect(() => {
        if (isSpinning && targetRotation !== null && !isAnimating) {
            setIsAnimating(true);

            if (idleIntervalRef.current) {
                clearInterval(idleIntervalRef.current);
                idleIntervalRef.current = null;
            }

            setRotation(prev => prev + targetRotation);

            setTimeout(() => {
                setIsAnimating(false);
                setTargetRotation(null);
            }, 5500);
        }
    }, [isSpinning, targetRotation]);

    // После анимации — возвращаемся в idle
    useEffect(() => {
        if (!isAnimating && !isSpinning && segments.length > 0) {
            startIdleRotation();
        }
    }, [isAnimating, isSpinning, segments.length]);

    // Медленное вращение в простое
    const startIdleRotation = () => {
        if (idleIntervalRef.current) {
            clearInterval(idleIntervalRef.current);
        }
        idleIntervalRef.current = setInterval(() => {
            setRotation(prev => prev + 0.05);
        }, 16);
    };

    if (segments.length === 0) {
        return (
            <div className="wheel-container-genshin">
                <div style={{ textAlign: 'center', padding: '40px', color: 'rgba(240,236,229,0.3)' }}>
                    Загрузка...
                </div>
            </div>
        );
    }

    const size = 320;
    const center = size / 2;
    const radius = size / 2 - 12;
    const angle = (2 * Math.PI) / segments.length;

    return (
        <div className="wheel-container-genshin">
            <div className={`wheel-glow ${isAnimating ? 'spinning' : ''}`} />

            <div className="wheel-wrapper">
                <div className="wheel-arrow-genshin">
                    <svg width="40" height="50" viewBox="0 0 40 50" fill="none">
                        <path d="M20 0 L8 40 L20 32 L32 40 L20 0Z" fill="#d4af37" stroke="#b8962e" strokeWidth="2" />
                        <circle cx="20" cy="38" r="6" fill="#d4af37" stroke="#b8962e" strokeWidth="2" />
                        <circle cx="20" cy="38" r="2" fill="#1a1a2e" />
                    </svg>
                </div>

                <svg
                    width={size}
                    height={size}
                    viewBox={`0 0 ${size} ${size}`}
                    style={{
                        transform: `rotate(${rotation}deg)`,
                        transition: isAnimating
                            ? 'transform 5.5s cubic-bezier(0.17, 0.67, 0.12, 0.99)'
                            : 'none',
                        filter: isAnimating ? 'drop-shadow(0 0 40px rgba(212,175,55,0.2))' : 'none',
                    }}
                >
                    <circle
                        cx={center}
                        cy={center}
                        r={radius + 2}
                        fill="none"
                        stroke="url(#goldBorder)"
                        strokeWidth="2"
                        opacity="0.4"
                    />

                    <defs>
                        <linearGradient id="goldBorder" x1="0%" y1="0%" x2="100%" y2="100%">
                            <stop offset="0%" stopColor="#d4af37" />
                            <stop offset="50%" stopColor="#f0d060" />
                            <stop offset="100%" stopColor="#b8962e" />
                        </linearGradient>
                    </defs>

                    {segments.map((seg, i) => {
                        const startAngle = i * angle - Math.PI / 2;
                        const endAngle = startAngle + angle;
                        const x1 = center + radius * Math.cos(startAngle);
                        const y1 = center + radius * Math.sin(startAngle);
                        const x2 = center + radius * Math.cos(endAngle);
                        const y2 = center + radius * Math.sin(endAngle);
                        const midAngle = startAngle + angle / 2;

                        const iconX = center + (radius * 0.55) * Math.cos(midAngle);
                        const iconY = center + (radius * 0.55) * Math.sin(midAngle);
                        const iconSize = seg.name === "Луна Genshin" ? 34 : 26;

                        const labelX = center + (radius * 0.82) * Math.cos(midAngle);
                        const labelY = center + (radius * 0.82) * Math.sin(midAngle);

                        const isZero = seg.value === 0;
                        const isMoon = seg.name === "Луна Genshin";
                        const isGold = i % 2 === 0;

                        return (
                            <g key={i}>
                                <path
                                    d={`M ${center} ${center} L ${x1} ${y1} A ${radius} ${radius} 0 0 1 ${x2} ${y2} Z`}
                                    fill={isGold ? '#d4af37' : '#1a1a2e'}
                                    stroke="#b8962e"
                                    strokeWidth="1"
                                    opacity={0.95}
                                />

                                {isMoon && (
                                    <image
                                        href="/images/wheel/moon.png"
                                        x={iconX - iconSize / 2}
                                        y={iconY - iconSize / 2}
                                        width={iconSize}
                                        height={iconSize}
                                        transform={`rotate(${(midAngle * 180) / Math.PI + 90}, ${iconX}, ${iconY})`}
                                        style={{ filter: 'drop-shadow(0 0 20px rgba(212,175,55,0.3))' }}
                                    />
                                )}

                                {!isZero && !isMoon && (
                                    <image
                                        href="/images/wheel/primogem.png"
                                        x={iconX - iconSize / 2}
                                        y={iconY - iconSize / 2}
                                        width={iconSize}
                                        height={iconSize}
                                        transform={`rotate(${(midAngle * 180) / Math.PI + 90}, ${iconX}, ${iconY})`}
                                    />
                                )}

                                {isZero && (
                                    <text
                                        x={iconX}
                                        y={iconY + 8}
                                        fill={isGold ? '#1a1a2e' : '#f0ece5'}
                                        fontSize={28}
                                        fontWeight="300"
                                        textAnchor="middle"
                                        transform={`rotate(${(midAngle * 180) / Math.PI + 90}, ${iconX}, ${iconY})`}
                                        opacity={0.5}
                                    >
                                        ✦
                                    </text>
                                )}

                                {!isZero && !isMoon && (
                                    <text
                                        x={labelX}
                                        y={labelY + 4}
                                        fill={isGold ? '#1a1a2e' : '#f0ece5'}
                                        fontSize={12}
                                        fontWeight="700"
                                        textAnchor="middle"
                                        transform={`rotate(${(midAngle * 180) / Math.PI + 90}, ${labelX}, ${labelY})`}
                                    >
                                        {seg.value}
                                    </text>
                                )}

                                {isMoon && (
                                    <text
                                        x={labelX}
                                        y={labelY + 4}
                                        fill={isGold ? '#1a1a2e' : '#f0ece5'}
                                        fontSize={9}
                                        fontWeight="700"
                                        textAnchor="middle"
                                        transform={`rotate(${(midAngle * 180) / Math.PI + 90}, ${labelX}, ${labelY})`}
                                        letterSpacing="0.5"
                                    >
                                        ЛУНА
                                    </text>
                                )}
                            </g>
                        );
                    })}

                    <circle cx={center} cy={center} r={22} fill="#d4af37" stroke="#b8962e" strokeWidth="2" />
                    <circle cx={center} cy={center} r={14} fill="#1a1a2e" stroke="#d4af37" strokeWidth="1.5" />
                    <circle cx={center} cy={center} r={5} fill="#d4af37" />
                </svg>
            </div>
        </div>
    );
}