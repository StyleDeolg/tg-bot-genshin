import { type ReactNode } from 'react';

interface LiyueCardProps {
    children: ReactNode;
    className?: string;
    style?: React.CSSProperties;
}

export default function LiyueCard({ children, className = '', style = {} }: LiyueCardProps) {
    return (
        <div className={`liyue-card ${className}`} style={style}>
            {children}
        </div>
    );
}