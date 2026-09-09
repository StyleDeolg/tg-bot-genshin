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
    const OFFSET = 2;

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

        // БОЛЬШЕ ОБОРОТОВ И МЕДЛЕННЕЕ
        const extraSpins = 8 + Math.floor(Math.random() * 4);
        const totalRotation = extraSpins * 360 + targetAngle;

        console.log(`🎯 Индекс БД: ${index} → скорректированный: ${adjustedIndex} → ${segments[adjustedIndex]?.name || '???'} → угол ${Math.round(targetAngle)}°`);

        setTimeout(() => {
            setRotation(prev => prev + totalRotation);
        }, 50);

        if (spinRef.current) clearTimeout(spinRef.current);
        spinRef.current = window.setTimeout(() => {
            setIsAnimating(false);
            if (onSpinComplete) onSpinComplete();
        }, 6500); // ДОЛЬШЕ
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

    return (
        <div className="wheel-container-genshin">
            <div className={`wheel-glow-genshin ${isAnimating ? 'spinning' : ''}`}></div>
            <div className="wheel-wrapper">
                <div className="wheel-arrow-genshin">
                    <svg width="44" height="56" viewBox="0 0 44 56" fill="none">
                        <defs>
                            <linearGradient id="arrowGenshin" x1="0%" y1="0%" x2="0%" y2="100%">
                                <stop offset="0%" stopColor="#f0d060" />
                                <stop offset="100%" stopColor="#b8962e" />
                            </linearGradient>
                            <filter id="arrowShadowGenshin">
                                <feDropShadow dx="0" dy="6" stdDeviation="16" floodColor="#d4af37" floodOpacity="0.15" />
                            </filter>
                        </defs>
                        <path
                            d="M22 0 L6 44 L22 34 L38 44 L22 0Z"
                            fill="url(#arrowGenshin)"
                            filter="url(#arrowShadowGenshin)"
                            stroke="#d4af37"
                            strokeWidth="1"
                        />
                        <circle cx="22" cy="42" r="10" fill="#d4af37" opacity="0.04" />
                        <circle cx="22" cy="42" r="5" fill="#d4af37" />
                        <circle cx="22" cy="42" r="2" fill="#0b0e1a" />
                    </svg>
                </div>

                <svg
                    width={size}
                    height={size}
                    viewBox={`0 0 ${size} ${size}`}
                    style={{
                        transform: `rotate(${rotation}deg)`,
                        transition: isAnimating
                            ? 'transform 6.5s cubic-bezier(0.08, 0.82, 0.12, 1.0)'
                            : 'none',
                        filter: isAnimating ? 'drop-shadow(0 0 60px rgba(212,175,55,0.06))' : 'none',
                    }}
                >
                    {/* Внешняя обводка колеса */}
                    <circle
                        cx={center}
                        cy={center}
                        r={radius + 6}
                        fill="none"
                        stroke="url(#goldBorder)"
                        strokeWidth="3"
                        opacity="0.4"
                    />
                    <circle
                        cx={center}
                        cy={center}
                        r={radius + 2}
                        fill="none"
                        stroke="#d4af37"
                        strokeWidth="1.5"
                        opacity="0.15"
                    />
                    <circle
                        cx={center}
                        cy={center}
                        r={radius - 2}
                        fill="none"
                        stroke="rgba(212,175,55,0.04)"
                        strokeWidth="0.5"
                    />

                    <defs>
                        <linearGradient id="goldBorder" x1="0%" y1="0%" x2="100%" y2="100%">
                            <stop offset="0%" stopColor="#f0d060" />
                            <stop offset="50%" stopColor="#d4af37" />
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
                                    fill={isGold ? 'rgba(212, 175, 55, 0.05)' : 'rgba(11, 14, 26, 0.7)'}
                                    stroke="rgba(212, 175, 55, 0.02)"
                                    strokeWidth="0.5"
                                    opacity={isGold ? 0.95 : 0.9}
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
                                        fill="rgba(232, 224, 212, 0.25)"
                                        fontSize={13}
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
                                        y={labelY + 5}
                                        fill="rgba(212, 175, 55, 0.2)"
                                        fontSize={10}
                                        fontWeight="700"
                                        textAnchor="middle"
                                        transform={`rotate(${(midAngle * 180) / Math.PI + 90}, ${labelX}, ${labelY})`}
                                        letterSpacing="1"
                                    >
                                        ЛУНА
                                    </text>
                                )}

                                {isShard && (
                                    <text
                                        x={labelX}
                                        y={labelY + 5}
                                        fill="rgba(232, 224, 212, 0.08)"
                                        fontSize={9}
                                        fontWeight="600"
                                        textAnchor="middle"
                                        transform={`rotate(${(midAngle * 180) / Math.PI + 90}, ${labelX}, ${labelY})`}
                                        letterSpacing="0.3"
                                    >
                                        ОСКОЛОК
                                    </text>
                                )}
                            </g>
                        );
                    })}

                    {/* Декоративные точки по кругу */}
                    {[0, 45, 90, 135, 180, 225, 270, 315].map((deg, idx) => (
                        <circle
                            key={`dot-${idx}`}
                            cx={center + (radius + 4) * Math.cos(deg * Math.PI / 180)}
                            cy={center + (radius + 4) * Math.sin(deg * Math.PI / 180)}
                            r={2}
                            fill="rgba(212, 175, 55, 0.04)"
                        />
                    ))}

                    <circle cx={center} cy={center} r={26} fill="#0b0e1a" stroke="rgba(212,175,55,0.02)" strokeWidth="1" />
                    <circle cx={center} cy={center} r={20} fill="rgba(212,175,55,0.01)" />

                    <text
                        x={center}
                        y={center + 6}
                        textAnchor="middle"
                        fontSize="18"
                        fill="rgba(212,175,55,0.03)"
                    >
                        ✦
                    </text>

                    <circle cx={center} cy={center} r={4} fill="rgba(212,175,55,0.01)" />
                    <circle cx={center} cy={center} r={1.5} fill="rgba(212,175,55,0.02)" />
                </svg>
            </div>
        </div>
    );
}