import { type ReactNode } from 'react';
import Header from './Header';
import BottomNav from './BottomNav';
import LiyueBg from './LiyueBg';

interface LayoutProps {
    children: ReactNode;
}

export default function Layout({ children }: LayoutProps) {
    return (
        <div className="layout">
            <LiyueBg />
            <Header />
            <main className="main-content">{children}</main>
            <BottomNav />
        </div>
    );
}