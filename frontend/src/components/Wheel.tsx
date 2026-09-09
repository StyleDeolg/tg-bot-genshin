import { useEffect, useState, useRef } from 'react';
import { getPrizes, type Prize } from '../api/wheel';
import ShardIcon from './ShardIcon';

interface WheelProps {
    isSpinning?: boolean;
    resultSegmentIndex?: number | null;
    onSpinComplete?: () => void;
}

export default function Wheel({
    isSpinning = false,
    resultSegmentIndex = null,
    onSpinComplete
}: WheelProps) {
    const [segments, setSegments] = useState<Prize[]>([]);
    const [rotation, setRotation] = useState(0);
    const [isAnimating, setIsAnimating] = useState(false);

    const spinRef = useRef<number | null>(null);
    const OFFSET = -2;

    useEffect(() => {
        getPrizes().then(data => {
            console.log('📦 Призы из БД:', data.map((p, i) => `${i}: ${p.name} (${p.prize_type})`));
            setSegments(data);
        });
    }, []);

    const spinToIndex = (index: number) => {
        if (!segments.length || isAnimating) return;

        setIsAnimating(true);

        const currentAngle = rotation % 360;
        const resetAngle = -currentAngle;
        setRotation(prev => prev + resetAngle);

        const total = segments.length;
        const segmentAngle = 360 / total;

        const adjustedIndex = (index + OFFSET + total) % total;

        let targetAngle = 270 - (adjustedIndex * segmentAngle + segmentAngle / 2);
        while (targetAngle < 0) targetAngle += 360;
        while (targetAngle >= 360) targetAngle -= 360;

        const extraSpins = 6 + Math.floor(Math.random() * 3);
        const totalRotation = extraSpins * 360 + targetAngle;

        console.log(`🎯 Индекс БД: ${index} → скорректированный: ${adjustedIndex} → ${segments[adjustedIndex]?.name || '???'} → угол ${Math.round(targetAngle)}°`);

        setTimeout(() => {
            setRotation(prev => prev + totalRotation);
        }, 50);

        if (spinRef.current) clearTimeout(spinRef.current);
        spinRef.current = window.setTimeout(() => {
            setIsAnimating(false);
            if (onSpinComplete) onSpinComplete();
        }, 5500);
    };

    useEffect(() => {
        if (isSpinning && resultSegmentIndex !== null && resultSegmentIndex !== undefined && !isAnimating) {
            spinToIndex(resultSegmentIndex);
        }
    }, [isSpinning, resultSegmentIndex]);

    if (segments.length === 0) {
        return (
            <div className="wheel-container-mond">
                <div style={{ textAlign: 'center', padding: '40px', color: 'rgba(232,224,212,0.05)' }}>
                    Загрузка...
                </div>
            </div>
        );
    }

    const size = 320;
    const center = size / 2;
    const radius = size / 2 - 14;
    const angle = (2 * Math.PI) / segments.length;

    return (
        <div className="wheel-container-mond">
            <div className="wheel-wrapper">
                <div className="wheel-arrow-mond">
                    <svg width="40" height="52" viewBox="0 0 40 52" fill="none">
                        <defs>
                            <linearGradient id="arrowMond" x1="0%" y1="0%" x2="0%" y2="100%">
                                <stop offset="0%" stopColor="#d4af37" />
                                <stop offset="100%" stopColor="#b8962e" />
                            </linearGradient>
                            <filter id="arrowShadowMond">
                                <feDropShadow dx="0" dy="6" stdDeviation="16" floodColor="#d4af37" floodOpacity="0.02" />
                            </filter>
                        </defs>
                        <path
                            d="M20 0 L6 40 L20 32 L34 40 L20 0Z"
                            fill="url(#arrowMond)"
                            filter="url(#arrowShadowMond)"
                        />
                        <circle cx="20" cy="40" r="8" fill="#d4af37" opacity="0.02" />
                        <circle cx="20" cy="40" r="4" fill="#d4af37" />
                        <circle cx="20" cy="40" r="1.5" fill="#1a2a3a" />
                    </svg>
                </div>

                <svg
                    width={size}
                    height={size}
                    viewBox={`0 0 ${size} ${size}`}
                    style={{
                        transform: `rotate(${rotation}deg)`,
                        transition: isAnimating
                            ? 'transform 5.5s cubic-bezier(0.08, 0.75, 0.12, 0.98)'
                            : 'none',
                    }}
                >
                    <defs>
                        <linearGradient id="glowMond" x1="0%" y1="0%" x2="100%" y2="100%">
                            <stop offset="0%" stopColor="#d4af37" stopOpacity="0.02" />
                            <stop offset="50%" stopColor="#d4af37" stopOpacity="0.005" />
                            <stop offset="100%" stopColor="#d4af37" stopOpacity="0.02" />
                        </linearGradient>
                    </defs>

                    {/* Внешняя рамка в виде восьмиугольника */}
                    <polygon
                        points={
                            Array.from({ length: 8 }, (_, i) => {
                                const a = (i / 8) * 2 * Math.PI - Math.PI / 8;
                                const r = radius + 8;
                                return `${center + r * Math.cos(a)},${center + r * Math.sin(a)}`;
                            }).join(' ')
                        }
                        fill="none"
                        stroke="rgba(212,175,55,0.02)"
                        strokeWidth="1"
                    />

                    {/* Сектора */}
                    {segments.map((seg, i) => {
                        const startAngle = i * angle - Math.PI / 2;
                        const endAngle = startAngle + angle;
                        const x1 = center + radius * Math.cos(startAngle);
                        const y1 = center + radius * Math.sin(startAngle);
                        const x2 = center + radius * Math.cos(endAngle);
                        const y2 = center + radius * Math.sin(endAngle);
                        const midAngle = startAngle + angle / 2;

                        const iconX = center + (radius * 0.5) * Math.cos(midAngle);
                        const iconY = center + (radius * 0.5) * Math.sin(midAngle);
                        const labelX = center + (radius * 0.78) * Math.cos(midAngle);
                        const labelY = center + (radius * 0.78) * Math.sin(midAngle);

                        const isEmpty = seg.prize_type?.startsWith('empty');
                        const isMoon = seg.prize_type === 'moon';
                        const isShard = seg.prize_type === 'shard';
                        const isGold = i % 2 === 0;

                        let iconSize = 26;
                        if (isMoon) iconSize = 34;
                        if (isShard) iconSize = 28;

                        return (
                            <g key={`segment-${i}-${seg.prize_type}`}>
                                <path
                                    d={`M ${center} ${center} L ${x1} ${y1} A ${radius} ${radius} 0 0 1 ${x2} ${y2} Z`}
                                    fill={isGold ? 'rgba(212,175,55,0.06)' : 'rgba(26,42,58,0.6)'}
                                    stroke="rgba(212,175,55,0.01)"
                                    strokeWidth="0.5"
                                    opacity={isGold ? 0.9 : 0.8}
                                />

                                {/* Декоративная линия */}
                                <path
                                    d={`M ${center + radius * 0.2 * Math.cos(midAngle)} ${center + radius * 0.2 * Math.sin(midAngle)} L ${center + radius * 0.9 * Math.cos(midAngle)} ${center + radius * 0.9 * Math.sin(midAngle)}`}
                                    stroke="rgba(212,175,55,0.005)"
                                    strokeWidth="0.5"
                                    strokeDasharray="2 2"
                                />

                                {isMoon && (
                                    <image
                                        href="/images/wheel/moon.png"
                                        x={iconX - iconSize / 2}
                                        y={iconY - iconSize / 2}
                                        width={iconSize}
                                        height={iconSize}
                                        transform={`rotate(${(midAngle * 180) / Math.PI + 90}, ${iconX}, ${iconY})`}
                                        style={{ filter: 'drop-shadow(0 0 30px rgba(212,175,55,0.02))' }}
                                    />
                                )}

                                {isShard && (
                                    <foreignObject
                                        x={iconX - iconSize / 2}
                                        y={iconY - iconSize / 2}
                                        width={iconSize}
                                        height={iconSize}
                                        transform={`rotate(${(midAngle * 180) / Math.PI + 90}, ${iconX}, ${iconY})`}
                                    >
                                        <div style={{
                                            display: 'flex',
                                            alignItems: 'center',
                                            justifyContent: 'center',
                                            width: '100%',
                                            height: '100%',
                                        }}>
                                            <ShardIcon size={iconSize - 4} />
                                        </div>
                                    </foreignObject>
                                )}

                                {!isEmpty && !isMoon && !isShard && (
                                    <image
                                        href="/images/wheel/primogem.png"
                                        x={iconX - iconSize / 2}
                                        y={iconY - iconSize / 2}
                                        width={iconSize}
                                        height={iconSize}
                                        transform={`rotate(${(midAngle * 180) / Math.PI + 90}, ${iconX}, ${iconY})`}
                                    />
                                )}

                                {isEmpty && (
                                    <text
                                        x={iconX}
                                        y={iconY + 7}
                                        fill="rgba(255,255,255,0.02)"
                                        fontSize={28}
                                        fontWeight="300"
                                        textAnchor="middle"
                                        transform={`rotate(${(midAngle * 180) / Math.PI + 90}, ${iconX}, ${iconY})`}
                                    >
                                        ✦
                                    </text>
                                )}

                                {!isEmpty && !isMoon && !isShard && (
                                    <text
                                        x={labelX}
                                        y={labelY + 5}
                                        fill="rgba(255,255,255,0.08)"
                                        fontSize={13}
                                        fontWeight="700"
                                        textAnchor="middle"
                                        transform={`rotate(${(midAngle * 180) / Math.PI + 90}, ${labelX}, ${labelY})`}
                                        fontFamily="'Inter', sans-serif"
                                    >
                                        {seg.value}
                                    </text>
                                )}

                                {isMoon && (
                                    <text
                                        x={labelX}
                                        y={labelY + 5}
                                        fill="rgba(212,175,55,0.08)"
                                        fontSize={10}
                                        fontWeight="700"
                                        textAnchor="middle"
                                        transform={`rotate(${(midAngle * 180) / Math.PI + 90}, ${labelX}, ${labelY})`}
                                        fontFamily="'Cinzel', serif"
                                        letterSpacing="1"
                                    >
                                        ЛУНА
                                    </text>
                                )}

                                {isShard && (
                                    <text
                                        x={labelX}
                                        y={labelY + 5}
                                        fill="rgba(255,255,255,0.02)"
                                        fontSize={9}
                                        fontWeight="600"
                                        textAnchor="middle"
                                        transform={`rotate(${(midAngle * 180) / Math.PI + 90}, ${labelX}, ${labelY})`}
                                        fontFamily="'Inter', sans-serif"
                                        letterSpacing="0.3"
                                    >
                                        ОСКОЛОК
                                    </text>
                                )}
                            </g>
                        );
                    })}

                    {/* Центр */}
                    <circle cx={center} cy={center} r={26} fill="#0d1520" stroke="rgba(212,175,55,0.01)" strokeWidth="1" />
                    <circle cx={center} cy={center} r={20} fill="rgba(212,175,55,0.01)" />

                    {/* Герб Мондштадта */}
                    <text
                        x={center}
                        y={center + 6}
                        textAnchor="middle"
                        fontSize="16"
                        fill="rgba(212,175,55,0.02)"
                        fontFamily="'Cinzel', serif"
                    >
                        ⚜
                    </text>

                    <circle cx={center} cy={center} r={4} fill="rgba(212,175,55,0.01)" />
                    <circle cx={center} cy={center} r={1.5} fill="rgba(212,175,55,0.02)" />
                </svg>
            </div>
        </div>
    );
}