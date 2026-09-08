import apiClient from './client';

export interface Profile {
    telegram_id: string;
    username: string | null;
    first_name: string | null;
    last_name: string | null;
    tickets: number;
    moon_shards: number;
    has_moon: boolean;
    is_donator: boolean;
    genshin_uid: string | null;
    referrals_count: number;
    tasks_completed: number;
}

export const getProfile = async (telegramId: string): Promise<Profile> => {
    const response = await apiClient.get(`/api/profile/${telegramId}`);
    return response.data;
};