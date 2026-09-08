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

    useEffect(() => {
        getPrizes().then(data => {
            // Сохраняем порядок КАК ЕСТЬ из БД
            console.log('📦 Призы из БД:', data.map((p, i) => `${i}: ${p.name} (${p.prize_type})`));
            setSegments(data);
        });
    }, []);

    const spinToIndex = (index: number) => {
        if (!segments.length || isAnimating) return;

        setIsAnimating(true);

        // Сбрасываем текущее вращение
        const currentAngle = rotation % 360;
        const resetAngle = -currentAngle;
        setRotation(prev => prev + resetAngle);

        const total = segments.length;
        const segmentAngle = 360 / total;

        let targetAngle = 270 - (index * segmentAngle + segmentAngle / 2);
        while (targetAngle < 0) targetAngle += 360;
        while (targetAngle >= 360) targetAngle -= 360;

        const extraSpins = 5 + Math.floor(Math.random() * 2);
        const totalRotation = extraSpins * 360 + targetAngle;

        console.log(`🎯 Индекс ${index} → ${segments[index].name} → угол ${Math.round(targetAngle)}°`);

        setTimeout(() => {
            setRotation(prev => prev + totalRotation);
        }, 50);

        if (spinRef.current) clearTimeout(spinRef.current);
        spinRef.current = window.setTimeout(() => {
            setIsAnimating(false);
            if (onSpinComplete) onSpinComplete();
        }, 5000);
    };

    useEffect(() => {
        if (isSpinning && resultSegmentIndex !== null && resultSegmentIndex !== undefined && !isAnimating) {
            spinToIndex(resultSegmentIndex);
        }
    }, [isSpinning, resultSegmentIndex]);

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
                        <defs>
                            <linearGradient id="arrowGrad" x1="0%" y1="0%" x2="0%" y2="100%">
                                <stop offset="0%" stopColor="#f0d060" />
                                <stop offset="100%" stopColor="#b8962e" />
                            </linearGradient>
                            <filter id="arrowShadow">
                                <feDropShadow dx="0" dy="4" stdDeviation="8" floodColor="#d4af37" floodOpacity="0.3" />
                            </filter>
                        </defs>
                        <path
                            d="M20 0 L8 40 L20 32 L32 40 L20 0Z"
                            fill="url(#arrowGrad)"
                            stroke="#d4af37"
                            strokeWidth="2"
                            filter="url(#arrowShadow)"
                        />
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
                            ? 'transform 5s cubic-bezier(0.17, 0.67, 0.12, 0.99)'
                            : 'none',
                    }}
                >
                    <defs>
                        <linearGradient id="goldBorder" x1="0%" y1="0%" x2="100%" y2="100%">
                            <stop offset="0%" stopColor="#d4af37" />
                            <stop offset="50%" stopColor="#f0d060" />
                            <stop offset="100%" stopColor="#b8962e" />
                        </linearGradient>
                    </defs>

                    <circle
                        cx={center}
                        cy={center}
                        r={radius + 2}
                        fill="none"
                        stroke="url(#goldBorder)"
                        strokeWidth="3"
                        opacity="0.6"
                    />

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
                        const labelX = center + (radius * 0.82) * Math.cos(midAngle);
                        const labelY = center + (radius * 0.82) * Math.sin(midAngle);

                        const isEmpty = seg.prize_type?.startsWith('empty');
                        const isMoon = seg.prize_type === 'moon';
                        const isShard = seg.prize_type === 'shard';
                        const isGold = i % 2 === 0;

                        let iconSize = 26;
                        if (isMoon) iconSize = 34;
                        if (isShard) iconSize = 28;

                        return (
                            <g key={i}>
                                <path
                                    d={`M ${center} ${center} L ${x1} ${y1} A ${radius} ${radius} 0 0 1 ${x2} ${y2} Z`}
                                    fill={isGold ? '#d4af37' : '#1a1a2e'}
                                    stroke="#b8962e"
                                    strokeWidth="1.5"
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

                                {!isEmpty && !isMoon && !isShard && (
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

                                {isShard && (
                                    <text
                                        x={labelX}
                                        y={labelY + 4}
                                        fill={isGold ? '#1a1a2e' : '#f0ece5'}
                                        fontSize={8}
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

                    <circle cx={center} cy={center} r={22} fill="#d4af37" stroke="#b8962e" strokeWidth="2" />
                    <circle cx={center} cy={center} r={14} fill="#1a1a2e" stroke="#d4af37" strokeWidth="1.5" />
                    <circle cx={center} cy={center} r={5} fill="#d4af37" />
                </svg>
            </div>
        </div>
    );
}