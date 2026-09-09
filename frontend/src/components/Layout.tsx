import { type ReactNode } from 'react';
import Header from './Header';
import BottomNav from './BottomNav';
import MondstadtBg from './MondstadtBg.tsx';

interface LayoutProps {
    children: ReactNode;
}

export default function Layout({ children }: LayoutProps) {
    return (
        <div className="layout">
            <MondstadtBg />
            <Header />
            <main className="main-content">{children}</main>
            <BottomNav />
        </div>
    );
}