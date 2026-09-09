interface ShardIconProps {
    size?: number;
    className?: string;
    style?: React.CSSProperties;
}

export default function ShardIcon({ size = 24, className = '', style = {} }: ShardIconProps) {
    return (
        <img
            src="/images/wheel/shard.jpg"
            alt="Осколок луны"
            className={className}
            style={{
                width: size,
                height: size,
                objectFit: 'contain',
                display: 'inline-block',
                ...style,
            }}
        />
    );
}