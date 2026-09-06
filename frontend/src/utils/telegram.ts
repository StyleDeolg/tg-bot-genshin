export const isTelegramWebApp = (): boolean => {
    if (typeof window === 'undefined') return false;
    const tg = (window as any).Telegram;
    return !!(tg && tg.WebApp);
};

export const getTelegramUser = () => {
    if (!isTelegramWebApp()) return null;
    const tg = (window as any).Telegram;
    return tg.WebApp.initDataUnsafe?.user || null;
};

// ДОБАВЛЯЕМ ЭТУ ФУНКЦИЮ
export const initTelegramWebApp = () => {
    if (!isTelegramWebApp()) return;
    const tg = (window as any).Telegram;
    tg.WebApp.ready();
    tg.WebApp.expand();
    tg.WebApp.enableClosingConfirmation();
};

export const closeTelegramWebApp = () => {
    if (!isTelegramWebApp()) return;
    const tg = (window as any).Telegram;
    tg.WebApp.close();
};