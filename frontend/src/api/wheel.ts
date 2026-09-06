import apiClient from './client';

export interface SpinResult {
    prize: string;
    prize_value: number;
    emoji: string | null;
    spins_left: number;
    total_spins: number;
}

export const spinWheel = async (telegramId: string): Promise<SpinResult> => {
    const response = await apiClient.post('/api/wheel/spin', {
        user_id: telegramId,
    });
    return response.data;
};