import apiClient from './client';

// --- ПРОФИЛЬ ---
export const getProfile = async (telegramId: string) => {
    const response = await apiClient.get(`/api/profile/${telegramId}`);
    return response.data;
};

// --- РЕФЕРАЛЫ ---
export const getReferral = async (telegramId: string) => {
    const response = await apiClient.get(`/api/referral/${telegramId}`);
    return response.data;
};

export const getReferralLink = async (telegramId: string) => {
    const response = await apiClient.get(`/api/referral/link/${telegramId}`);
    return response.data;
};

export const getReferralStats = async (telegramId: string) => {
    const response = await apiClient.get(`/api/referral/stats/${telegramId}`);
    return response.data;
};

// --- ЗАДАНИЯ ---
export const getTasks = async (telegramId: string) => {
    const response = await apiClient.get(`/api/tasks/${telegramId}`);
    return response.data;
};

export const claimTask = async (telegramId: string, taskId: string) => {
    const response = await apiClient.post(`/api/tasks/claim/${telegramId}/${taskId}`);
    return response.data;
};

export const checkTasks = async (telegramId: string) => {
    const response = await apiClient.post(`/api/tasks/check/${telegramId}`);
    return response.data;
};

// --- КОЛЕСО ---
export const spinWheel = async (telegramId: string) => {
    const response = await apiClient.post('/api/wheel/spin', {
        telegram_id: telegramId,
    });
    return response.data;
};

export const getPrizes = async () => {
    const response = await apiClient.get('/api/wheel/prizes');
    return response.data;
};

// --- АВАТАРКА ---
export const getAvatar = async (telegramId: string) => {
    try {
        const response = await apiClient.get(`/api/auth/avatar/${telegramId}`);
        return response.data.avatar_url || null;
    } catch (error) {
        console.error('Ошибка получения аватарки:', error);
        return null;
    }
};

export { apiClient };