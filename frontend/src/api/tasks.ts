import apiClient from './client';

export interface Task {
    id: string;
    title: string;
    description: string;
    reward: number;
    task_type: string;
    required_count: number;
    progress: number;
    completed: boolean;
    can_claim: boolean;
    sponsor_id?: string;
    last_claimed_at?: string | null;
}

export interface ClaimResponse {
    success: boolean;
    message: string;
    tickets: number;
}

export const getTasks = async (telegramId: string): Promise<Task[]> => {
    const response = await apiClient.get(`/api/tasks/${telegramId}`);
    return response.data;
};

export const claimTask = async (telegramId: string, taskId: string): Promise<ClaimResponse> => {
    const response = await apiClient.post(`/api/tasks/claim/${telegramId}/${taskId}`);
    return response.data;
};

export const checkTasks = async (telegramId: string): Promise<{ success: boolean; message: string }> => {
    const response = await apiClient.post(`/api/tasks/check/${telegramId}`);
    return response.data;
};