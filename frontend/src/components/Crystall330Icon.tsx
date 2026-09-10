interface Crystall330IconProps {
    size?: number;
}

export default function Crystall330Icon({ size = 28 }: Crystall330IconProps) {
    return (
        <img
            src="/images/wheel/crystall_330.png"
            alt="330 кристаллов"
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