import { NavLink } from 'react-router-dom';

export default function BottomNav() {
    const navItems = [
        { path: '/', label: 'Главная', icon: '⚜' },
        { path: '/friends', label: 'Друзья', icon: '👥' },
        { path: '/tasks', label: 'Задания', icon: '📜' },
        { path: '/profile', label: 'Профиль', icon: '👤' },
    ];

    return (
        <nav className="bottom-nav">
            {navItems.map((item) => (
                <NavLink
                    key={item.path}
                    to={item.path}
                    className={({ isActive }) => `nav-item ${isActive ? 'active' : ''}`}
                >
                    <span className="nav-icon">{item.icon}</span>
                    <span className="nav-label">{item.label}</span>
                </NavLink>
            ))}
        </nav>
    );
}