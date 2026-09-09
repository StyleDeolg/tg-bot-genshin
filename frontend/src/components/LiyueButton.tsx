import React from 'react';

interface LiyueButtonProps {
    text: string;
    onClick: () => void;
    outline?: boolean;
    disabled?: boolean;
    icon?: React.ReactNode;
    className?: string;
    style?: React.CSSProperties;
}

export default function LiyueButton({
    text,
    onClick,
    outline = false,
    disabled = false,
    icon,
    className = '',
    style = {},
}: LiyueButtonProps) {
    return (
        <button
            className={`liyue-button ${outline ? 'outline' : ''} ${className}`}
            onClick={onClick}
            disabled={disabled}
            style={style}
        >
            {icon && <span className="liyue-button-icon">{icon}</span>}
            <span className="liyue-button-text">{text}</span>
        </button>
    );
}