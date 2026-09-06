import React from 'react';

interface GoldButtonProps {
    text: string;
    onClick: () => void;
    outline?: boolean;
    disabled?: boolean;
    icon?: React.ReactNode;
    className?: string;
}

export default function GoldButton({
    text,
    onClick,
    outline = false,
    disabled = false,
    icon,
    className = '',
}: GoldButtonProps) {
    return (
        <button
            className={`gold-button ${outline ? 'outline' : ''} ${className}`}
            onClick={onClick}
            disabled={disabled}
        >
            {icon && <span className="gold-button-icon">{icon}</span>}
            <span className="gold-button-text">{text}</span>
        </button>
    );
}