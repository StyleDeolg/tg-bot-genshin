import React from 'react';

interface ButtonGenshinProps {
    text: string;
    onClick: () => void;
    outline?: boolean;
    disabled?: boolean;
    icon?: React.ReactNode;
    className?: string;
    style?: React.CSSProperties;
}

export default function ButtonGenshin({
    text,
    onClick,
    outline = false,
    disabled = false,
    icon,
    className = '',
    style = {},
}: ButtonGenshinProps) {
    return (
        <button
            className={`btn-genshin ${outline ? 'btn-genshin-outline' : ''} ${className}`}
            onClick={onClick}
            disabled={disabled}
            style={style}
        >
            {icon && <span className="btn-genshin-icon">{icon}</span>}
            <span className="btn-genshin-text">{text}</span>
        </button>
    );
}