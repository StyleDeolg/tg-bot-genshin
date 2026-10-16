import apiClient from './client';

export interface Sponsor {
    id: string;
    name: string;
    link: string;
    channel: string | null;
    is_subscribed: boolean;
    task_completed: boolean;
    task_id: string | null;
}

export interface AccessStatus {
    has_access: boolean;
    missing: { id: string; name: string; link: string }[];
    total: number;
    subscribed_count: number;
    is_old?: boolean;
}

export interface SponsorLink {
    id: string;
    name: string;
    link: string;
}

/**
 * Проверка доступа к Mini App.
 * Учитывает реальную подписку + клики в боте + флаг skip_subscription_check.
 */
export const checkAccess = async (telegramId: string): Promise<AccessStatus> => {
    const response = await apiClient.get(`/api/sponsors/access/${telegramId}`);
    return response.data;
};

/**
 * Устаревший метод — оставлен для обратной совместимости.
 */
export const getSponsors = async (telegramId: string): Promise<Sponsor[]> => {
    const response = await apiClient.get(`/api/sponsors/${telegramId}`);
    return response.data;
};

/**
 * Устаревший метод — оставлен для обратной совместимости.
 */
export const checkSponsorSubscription = async (
    telegramId: string,
    sponsorId: string
): Promise<{ success: boolean; message: string }> => {
    const response = await apiClient.post(`/api/sponsors/check/${telegramId}/${sponsorId}`);
    return response.data;
};