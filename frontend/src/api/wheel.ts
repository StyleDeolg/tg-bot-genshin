import apiClient from './client';

export interface SpinResult {
    prize: string;
    prize_value: number;
    prize_type: string;
    emoji: string;
    tickets_left: number;
    shards: number;
    has_moon: boolean;
    segment_index: number;
}

export interface Prize {
    name: string;
    value: number;
    emoji: string;
    prize_type: string;
    color: string;
}

export const spinWheel = async (telegramId: string): Promise<SpinResult> => {
    const response = await apiClient.post('/api/wheel/spin', {
        telegram_id: telegramId,
    });
    return response.data;
};

export const getPrizes = async (): Promise<Prize[]> => {
    const response = await apiClient.get('/api/wheel/prizes');
    return response.data;
};