import { create } from 'zustand';
import { getProfile } from '../api';

export interface User {
    public_id: string;
    telegram_id: string;
    username: string | null;
    first_name: string | null;
    last_name: string | null;
    genshin_uid: string | null;
    tickets: number;
    primogems: number;
    referrals_count?: number;
    tasks_completed?: number;
}

interface AuthState {
    user: User | null;
    isAuthenticated: boolean;
    isLoading: boolean;
    setUser: (user: User) => void;
    loadUserData: (telegramId: string) => Promise<void>;
    updateProfile: () => Promise<void>;
    logout: () => void;
}

export const useAuthStore = create<AuthState>((set, get) => ({
    user: null,
    isAuthenticated: false,
    isLoading: true,

    setUser: (user) => set({ user, isAuthenticated: true, isLoading: false }),

    loadUserData: async (telegramId: string) => {
        try {
            const profile = await getProfile(telegramId);
            const currentUser = get().user;
            if (currentUser) {
                set({
                    user: {
                        ...currentUser,
                        tickets: profile.tickets,
                        primogems: profile.primogems,
                        referrals_count: profile.referrals_count,
                        tasks_completed: profile.tasks_completed,
                    },
                    isLoading: false
                });
            }
        } catch (error) {
            console.error('Ошибка загрузки данных:', error);
            set({ isLoading: false });
        }
    },

    updateProfile: async () => {
        const { user } = get();
        if (!user) return;

        try {
            const profile = await getProfile(user.telegram_id);
            set({
                user: {
                    ...user,
                    tickets: profile.tickets,
                    primogems: profile.primogems,
                    referrals_count: profile.referrals_count,
                    tasks_completed: profile.tasks_completed,
                }
            });
        } catch (error) {
            console.error('Ошибка обновления профиля:', error);
        }
    },

    logout: () => set({ user: null, isAuthenticated: false, isLoading: false }),
}));