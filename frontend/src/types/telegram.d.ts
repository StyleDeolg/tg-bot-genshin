interface TelegramWebApp {
    initData: string;
    initDataUnsafe: {
        user?: {
            id: number;
            first_name: string;
            last_name?: string;
            username?: string;
        };
    };
    ready: () => void;
    expand: () => void;
    close: () => void;
    disableVerticalSwipes?: () => void;
}

interface Window {
    Telegram?: {
        WebApp: TelegramWebApp;
    };
}