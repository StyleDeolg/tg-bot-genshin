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
            <div className="wheel-container-genshin">
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

    const colorPalette = [
        ['#1a1a2e', '#2d2d5e'],
        ['#2d2d5e', '#1a1a2e'],
        ['#1a1a2e', '#2d2d5e'],
        ['#2d2d5e', '#1a1a2e'],
        ['#1a1a2e', '#2d2d5e'],
        ['#2d2d5e', '#1a1a2e'],
        ['#1a1a2e', '#2d2d5e'],
        ['#2d2d5e', '#1a1a2e'],
    ];

    return (
        <div className="wheel-container-genshin">
            <div className={`wheel-glow ${isAnimating ? 'spinning' : ''}`}>
                <div className="wheel-glow-inner"></div>
                <div className="wheel-glow-outer"></div>
            </div>

            <div className="wheel-wrapper">
                {/* Стрелка с элементами герба */}
                <div className="wheel-arrow-genshin">
                    <svg width="40" height="52" viewBox="0 0 40 52" fill="none">
                        <defs>
                            <linearGradient id="arrowGradNew" x1="0%" y1="0%" x2="0%" y2="100%">
                                <stop offset="0%" stopColor="#d4af37" />
                                <stop offset="100%" stopColor="#b8962e" />
                            </linearGradient>
                            <filter id="arrowShadowNew">
                                <feDropShadow dx="0" dy="6" stdDeviation="16" floodColor="#d4af37" floodOpacity="0.05" />
                            </filter>
                        </defs>
                        <path
                            d="M20 0 L6 40 L20 32 L34 40 L20 0Z"
                            fill="url(#arrowGradNew)"
                            filter="url(#arrowShadowNew)"
                        />
                        <circle cx="20" cy="40" r="8" fill="#d4af37" opacity="0.05" />
                        <circle cx="20" cy="40" r="4" fill="#d4af37" />
                        <circle cx="20" cy="40" r="1.5" fill="#0b0e1a" />
                    </svg>
                </div>

                {/* Колесо с декоративными элементами */}
                <svg
                    width={size}
                    height={size}
                    viewBox={`0 0 ${size} ${size}`}
                    style={{
                        transform: `rotate(${rotation}deg)`,
                        transition: isAnimating
                            ? 'transform 5.5s cubic-bezier(0.08, 0.75, 0.12, 0.98)'
                            : 'none',
                        filter: isAnimating ? 'drop-shadow(0 0 60px rgba(212,175,55,0.02))' : 'none',
                    }}
                >
                    <defs>
                        <linearGradient id="glowRing" x1="0%" y1="0%" x2="100%" y2="100%">
                            <stop offset="0%" stopColor="#d4af37" stopOpacity="0.04" />
                            <stop offset="50%" stopColor="#d4af37" stopOpacity="0.01" />
                            <stop offset="100%" stopColor="#d4af37" stopOpacity="0.04" />
                        </linearGradient>
                        <radialGradient id="centerGlow">
                            <stop offset="0%" stopColor="#d4af37" stopOpacity="0.01" />
                            <stop offset="100%" stopColor="#d4af37" stopOpacity="0" />
                        </radialGradient>
                    </defs>

                    {/* Декоративная внешняя рамка */}
                    <circle
                        cx={center}
                        cy={center}
                        r={radius + 4}
                        fill="none"
                        stroke="rgba(212,175,55,0.02)"
                        strokeWidth="1"
                    />
                    <circle
                        cx={center}
                        cy={center}
                        r={radius + 8}
                        fill="none"
                        stroke="rgba(212,175,55,0.01)"
                        strokeWidth="0.5"
                        strokeDasharray="4 4"
                    />

                    {/* Декоративные элементы по краям (арки Мондштадта) */}
                    {[0, 45, 90, 135, 180, 225, 270, 315].map((deg) => (
                        <g key={`arch-${deg}`}>
                            <path
                                d={`M ${center + (radius + 4) * Math.cos(deg * Math.PI / 180)} ${center + (radius + 4) * Math.sin(deg * Math.PI / 180)} L ${center + (radius + 8) * Math.cos(deg * Math.PI / 180)} ${center + (radius + 8) * Math.sin(deg * Math.PI / 180)}`}
                                stroke="rgba(212,175,55,0.02)"
                                strokeWidth="1"
                            />
                        </g>
                    ))}

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

                        let iconSize = 26;
                        if (isMoon) iconSize = 34;
                        if (isShard) iconSize = 28;

                        const [color1, color2] = colorPalette[i % colorPalette.length];

                        return (
                            <g key={`segment-${i}-${seg.prize_type}`}>
                                <linearGradient id={`grad-${i}`} x1="0%" y1="0%" x2="100%" y2="100%">
                                    <stop offset="0%" stopColor={color1} />
                                    <stop offset="100%" stopColor={color2} />
                                </linearGradient>
                                <path
                                    d={`M ${center} ${center} L ${x1} ${y1} A ${radius} ${radius} 0 0 1 ${x2} ${y2} Z`}
                                    fill={`url(#grad-${i})`}
                                    stroke="rgba(212,175,55,0.01)"
                                    strokeWidth="0.5"
                                    opacity={0.9}
                                />

                                {/* Декоративная линия в секторе */}
                                <path
                                    d={`M ${center + radius * 0.2 * Math.cos(midAngle)} ${center + radius * 0.2 * Math.sin(midAngle)} L ${center + radius * 0.9 * Math.cos(midAngle)} ${center + radius * 0.9 * Math.sin(midAngle)}`}
                                    stroke="rgba(255,255,255,0.01)"
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
                                        style={{ filter: 'drop-shadow(0 0 30px rgba(212,175,55,0.04))' }}
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
                                        fill="rgba(255,255,255,0.15)"
                                        fontSize={13}
                                        fontWeight="700"
                                        textAnchor="middle"
                                        transform={`rotate(${(midAngle * 180) / Math.PI + 90}, ${labelX}, ${labelY})`}
                                        fontFamily="'Montserrat', sans-serif"
                                    >
                                        {seg.value}
                                    </text>
                                )}

                                {isMoon && (
                                    <text
                                        x={labelX}
                                        y={labelY + 5}
                                        fill="rgba(212,175,55,0.2)"
                                        fontSize={10}
                                        fontWeight="700"
                                        textAnchor="middle"
                                        transform={`rotate(${(midAngle * 180) / Math.PI + 90}, ${labelX}, ${labelY})`}
                                        fontFamily="'Cormorant Garamond', serif"
                                        letterSpacing="1"
                                    >
                                        ЛУНА
                                    </text>
                                )}

                                {isShard && (
                                    <text
                                        x={labelX}
                                        y={labelY + 5}
                                        fill="rgba(255,255,255,0.05)"
                                        fontSize={9}
                                        fontWeight="600"
                                        textAnchor="middle"
                                        transform={`rotate(${(midAngle * 180) / Math.PI + 90}, ${labelX}, ${labelY})`}
                                        fontFamily="'Montserrat', sans-serif"
                                        letterSpacing="0.3"
                                    >
                                        ОСКОЛОК
                                    </text>
                                )}
                            </g>
                        );
                    })}

                    {/* Центр колеса с гербом */}
                    <circle cx={center} cy={center} r={26} fill="#0b0e1a" stroke="rgba(212,175,55,0.02)" strokeWidth="1" />
                    <circle cx={center} cy={center} r={22} fill="url(#centerGlow)" />

                    {/* Декоративные арки в центре */}
                    {[0, 45, 90, 135, 180, 225, 270, 315].map((deg, idx) => (
                        <circle
                            key={`dot-${idx}`}
                            cx={center + 16 * Math.cos(deg * Math.PI / 180)}
                            cy={center + 16 * Math.sin(deg * Math.PI / 180)}
                            r={1}
                            fill="rgba(212,175,55,0.04)"
                        />
                    ))}

                    {/* Герб в центре */}
                    <text
                        x={center}
                        y={center + 6}
                        textAnchor="middle"
                        fontSize="16"
                        fill="rgba(212,175,55,0.03)"
                        fontFamily="'Cormorant Garamond', serif"
                    >
                        ⚜
                    </text>

                    <circle cx={center} cy={center} r={4} fill="rgba(212,175,55,0.02)" />
                    <circle cx={center} cy={center} r={1.5} fill="rgba(212,175,55,0.03)" />
                </svg>
            </div>
        </div>
    );
}