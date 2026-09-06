import React from 'react';

interface PrimogemIconProps {
    size?: number;
    className?: string;
    style?: React.CSSProperties;
}

export default function PrimogemIcon({ size = 24, className = '', style = {} }: PrimogemIconProps) {
    return (
        <img
            src="/images/wheel/primogem.png"
            alt="Примогем"
            width={size}
            height={size}
            className={className}
            style={{ objectFit: 'contain', ...style }}
        />
    );
}