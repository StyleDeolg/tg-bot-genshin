import apiClient from './client';

export interface LoginResponse {
    telegram_id: string;
    username: string | null;
    first_name: string | null;
    last_name: string | null;
    tickets: number;
    primogems: number;
    moon_shards: number;
    has_moon: boolean;
    is_donator: boolean;
}

export const login = async (data: {
    telegram_id: string;
    username?: string | null;
    first_name?: string | null;
    last_name?: string | null;
}): Promise<LoginResponse> => {
    const response = await apiClient.post('/api/auth/login', data);
    return response.data;
};

export const getAvatar = async (telegramId: string): Promise<string> => {
    const response = await apiClient.get(`/api/auth/avatar/${telegramId}`);
    return response.data.avatar_url;
};