import apiClient from './client';

export interface ReferralData {
    count: number;
    link: string;
    rewards: {
        level: number;
        reward: number;
    }[];
}

export const getReferral = async (telegramId: string): Promise<ReferralData> => {
    const response = await apiClient.get(`/api/referral/${telegramId}`);
    return response.data;
};

export const getReferralLink = async (telegramId: string): Promise<{ link: string }> => {
    const response = await apiClient.get(`/api/referral/link/${telegramId}`);
    return response.data;
};

export const getReferralStats = async (telegramId: string): Promise<{ count: number; rewards: any[] }> => {
    const response = await apiClient.get(`/api/referral/stats/${telegramId}`);
    return response.data;
};