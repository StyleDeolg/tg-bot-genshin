interface Crystall60IconProps {
    size?: number;
}

export default function Crystall60Icon({ size = 28 }: Crystall60IconProps) {
    return (
        <img
            src="/images/wheel/crystall_60.png"
            alt="60 кристаллов"
            width={size}
            height={size}
            style={{
                display: 'block',
                objectFit: 'contain',
                filter: 'drop-shadow(0 0 8px rgba(212, 175, 55, 0.35))',
                pointerEvents: 'none',
                userSelect: 'none',
            }}
            draggable={false}
        />
    );
}