import { useEffect, useState } from 'react';
import { useAuthStore } from '../store/authStore';
import { getTasks, claimTask, checkTasks } from '../api';
import GoldButton from '../components/GoldButton';
import TicketIcon from '../components/TicketIcon';

export default function TasksPage() {
    const { user, updateProfile } = useAuthStore();
    const [tasks, setTasks] = useState<any[]>([]);
    const [loading, setLoading] = useState(true);
    const [claiming, setClaiming] = useState<string | null>(null);

    const loadTasks = async () => {
        if (!user) return;
        setLoading(true);
        try {
            // Проверяем прогресс заданий перед загрузкой
            await checkTasks(user.telegram_id);
            const data = await getTasks(user.telegram_id);
            setTasks(data);
            await updateProfile();
        } catch (error) {
            console.error('Ошибка загрузки заданий:', error);
        } finally {
            setLoading(false);
        }
    };

    useEffect(() => {
        loadTasks();
    }, [user]);

    const handleClaim = async (taskId: string) => {
        if (!user) return;
        setClaiming(taskId);
        try {
            const result = await claimTask(user.telegram_id, taskId);
            await loadTasks();
            await updateProfile();
            alert(result.message);
        } catch (error: any) {
            alert(error.response?.data?.detail || 'Ошибка при получении награды');
        } finally {
            setClaiming(null);
        }
    };

    if (loading) return <div className="loading-text">Загрузка заданий...</div>;

    return (
        <div className="page tasks-page">
            <h1 className="page-title">📋 Задания</h1>
            <p className="page-subtitle">Выполняй задания и получай награды!</p>

            {tasks.length === 0 && (
                <div className="glass-card" style={{ textAlign: 'center', padding: '30px' }}>
                    <p style={{ color: 'rgba(240,236,229,0.4)' }}>Заданий пока нет. Загляни позже!</p>
                </div>
            )}

            {tasks.map((task) => {
                const isCompleted = task.completed;
                const isReady = task.can_claim || isCompleted;
                const isClaiming = claiming === task.id;

                return (
                    <div key={task.id} className={`task-card ${isReady ? 'task-ready' : ''}`}>
                        <div className="task-header">
                            <span className="task-title">{task.title}</span>
                            <span className={`task-status ${isCompleted ? 'done' : 'pending'}`}>
                                {isCompleted ? '✅ Выполнено' : '⏳ В процессе'}
                            </span>
                        </div>
                        <p className="task-desc">{task.description}</p>
                        <p className="task-progress">
                            Прогресс: {task.progress}/{task.required_count}
                        </p>
                        <div className="task-footer">
                            {isCompleted ? (
                                <div className="task-completed-badge">
                                    <span>🎉 Награда получена!</span>
                                </div>
                            ) : task.progress >= task.required_count ? (
                                <GoldButton
                                    text={isClaiming ? '⏳ Забираю...' : '🎁 Забрать награду'}
                                    onClick={() => handleClaim(task.id)}
                                    disabled={isClaiming}
                                    icon={<TicketIcon size={16} />}
                                />
                            ) : (
                                <div className="task-progress-bar">
                                    <div
                                        className="task-progress-fill"
                                        style={{ width: `${(task.progress / task.required_count) * 100}%` }}
                                    />
                                    <span className="task-progress-text">
                                        {task.progress} / {task.required_count}
                                    </span>
                                </div>
                            )}
                        </div>
                    </div>
                );
            })}
        </div>
    );
}