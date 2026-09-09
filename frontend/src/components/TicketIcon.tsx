import React from 'react';

interface TicketIconProps {
    size?: number;
    className?: string;
    style?: React.CSSProperties;
}

export default function TicketIcon({ size = 24, className = '', style = {} }: TicketIconProps) {
    return (
        <svg
            width={size}
            height={size}
            viewBox="0 0 24 24"
            fill="none"
            xmlns="http://www.w3.org/2000/svg"
            className={className}
            style={style}
        >
            <path
                d="M20 8V5C20 4.44772 19.5523 4 19 4H5C4.44772 4 4 4.44772 4 5V8C5.65685 8 7 9.34315 7 11C7 12.6569 5.65685 14 4 14V19C4 19.5523 4.44772 20 5 20H19C19.5523 20 20 19.5523 20 19V14C18.3431 14 17 12.6569 17 11C17 9.34315 18.3431 8 20 8Z"
                stroke="#b83a2a"
                strokeWidth="1.8"
                fill="rgba(180, 60, 40, 0.04)"
                strokeLinecap="round"
                strokeLinejoin="round"
            />
            <path
                d="M8 11L10 13L14 9"
                stroke="#b83a2a"
                strokeWidth="1.5"
                strokeLinecap="round"
                strokeLinejoin="round"
                opacity="0.5"
            />
            <circle cx="12" cy="12" r="3" stroke="#b83a2a" strokeWidth="1.2" fill="none" opacity="0.3" />
            <path
                d="M12 10L13.5 12L12 14L10.5 12L12 10Z"
                stroke="#b83a2a"
                strokeWidth="0.8"
                fill="rgba(180, 60, 40, 0.1)"
            />
        </svg>
    );
}