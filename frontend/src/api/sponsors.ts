import apiClient from './client';

export interface Sponsor {
    id: string;
    name: string;
    link: string;
    channel: string | null;
    is_subscribed: boolean;
    task_completed: boolean;
    task_id: string | null;  // ← ДОБАВЛЯЕМ
}

export const getSponsors = async (telegramId: string): Promise<Sponsor[]> => {
    const response = await apiClient.get(`/api/sponsors/${telegramId}`);
    return response.data;
};

export const checkSponsorSubscription = async (telegramId: string, sponsorId: string): Promise<{ success: boolean; message: string }> => {
    const response = await apiClient.post(`/api/sponsors/check/${telegramId}/${sponsorId}`);
    return response.data;
};