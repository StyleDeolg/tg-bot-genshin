import { useEffect, useState, useRef } from 'react';
import { useAuthStore } from '../store/authStore';
import { getTasks, claimTask, checkTasks } from '../api/tasks';
import { getSponsors, checkSponsorSubscription } from '../api/sponsors';
import type { Sponsor } from '../api/sponsors';
import TicketIcon from '../components/TicketIcon';

export default function TasksPage() {
    const { user, updateProfile } = useAuthStore();
    const [tasks, setTasks] = useState<any[]>([]);
    const [sponsors, setSponsors] = useState<Sponsor[]>([]);
    const [loading, setLoading] = useState<boolean>(true);
    const [claiming, setClaiming] = useState<string | null>(null);
    const [checking, setChecking] = useState<string | null>(null);
    const [timeLeft, setTimeLeft] = useState<{ [key: string]: string }>({});

    const animationRef = useRef<number | undefined>(undefined);
    const prevTimeLeftRef = useRef<{ [key: string]: string }>({});

    const loadData = async () => {
        if (!user) return;
        setLoading(true);
        try {
            await checkTasks(user.telegram_id);
            const tasksData = await getTasks(user.telegram_id);
            setTasks(tasksData);
            const sponsorsData = await getSponsors(user.telegram_id);
            setSponsors(sponsorsData);
            await updateProfile();
        } catch (error) {
            console.error('Ошибка загрузки данных:', error);
        } finally {
            setLoading(false);
        }
    };

    useEffect(() => {
        loadData();
    }, [user]);

    useEffect(() => {
        const updateTimers = () => {
            const now = Date.now();
            const newTimeLeft: { [key: string]: string } = {};

            tasks.forEach((task) => {
                if (task.task_type === 'daily' && task.last_claimed_at) {
                    const lastClaimed = new Date(task.last_claimed_at).getTime();
                    const nextAvailable = lastClaimed + 24 * 60 * 60 * 1000;
                    const diff = nextAvailable - now;

                    if (diff > 0) {
                        const totalSeconds = Math.floor(diff / 1000);
                        const hours = Math.floor(totalSeconds / 3600);
                        const minutes = Math.floor((totalSeconds % 3600) / 60);
                        const seconds = totalSeconds % 60;
                        newTimeLeft[task.id] = `${String(hours).padStart(2, '0')}:${String(minutes).padStart(2, '0')}:${String(seconds).padStart(2, '0')}`;
                    } else {
                        newTimeLeft[task.id] = 'Готово!';
                    }
                } else if (task.task_type === 'daily' && !task.last_claimed_at) {
                    newTimeLeft[task.id] = 'Забрать!';
                }
            });

            const currentStr = JSON.stringify(newTimeLeft);
            const prevStr = JSON.stringify(prevTimeLeftRef.current);
            if (currentStr !== prevStr) {
                setTimeLeft(newTimeLeft);
                prevTimeLeftRef.current = newTimeLeft;
            }
        };

        updateTimers();
        const interval = setInterval(updateTimers, 1000);

        return () => {
            clearInterval(interval);
            if (animationRef.current) {
                cancelAnimationFrame(animationRef.current);
            }
        };
    }, [tasks]);

    const handleClaim = async (taskId: string) => {
        if (!user) return;
        setClaiming(taskId);
        try {
            const result = await claimTask(user.telegram_id, taskId);
            console.log('Claim result:', result);

            setTasks(prevTasks =>
                prevTasks.map(task => {
                    if (task.id === taskId) {
                        return {
                            ...task,
                            completed: true,
                            can_claim: false,
                            claimed_at: new Date().toISOString(),
                            progress: task.task_type === 'spin' ? 0 : task.progress,
                            last_claimed_at: task.task_type === 'daily' ? new Date().toISOString() : task.last_claimed_at,
                        };
                    }
                    return task;
                })
            );

            await updateProfile();
            alert(result.message);

        } catch (error: any) {
            const message = error.response?.data?.detail || 'Ошибка при получении награды';
            console.error('Claim error:', error);
            alert('❌ ' + message);
        } finally {
            setClaiming(null);
        }
    };

    const handleCheckSponsor = async (sponsorId: string) => {
        if (!user || checking) return;
        setChecking(sponsorId);
        try {
            const result = await checkSponsorSubscription(user.telegram_id, sponsorId);

            setSponsors(prevSponsors =>
                prevSponsors.map(s => {
                    if (s.id === sponsorId) {
                        return { ...s, task_completed: true };
                    }
                    return s;
                })
            );

            await loadData();
            await updateProfile();

            if (result.success) {
                alert('Подписка подтверждена! Ты получил 3 билетика!');
            } else {
                alert('❌ ' + (result.message || 'Ты ещё не подписался на канал. Подпишись и попробуй снова!'));
            }
        } catch (error: any) {
            const message = error.response?.data?.detail || 'Ошибка при проверке подписки';
            console.error('Check sponsor error:', message);
            alert('❌ ' + message);
        } finally {
            setChecking(null);
        }
    };

    if (loading) return <div className="loading-text text-light opacity-25 text-center py-5">Загрузка заданий...</div>;

    const sponsorTasks = tasks.filter(task => task.task_type === 'sponsor');
    const regularTasks = tasks.filter(task => task.task_type !== 'sponsor');

    const sponsorsMap = sponsors.reduce<Record<string, Sponsor>>((acc, s) => {
        acc[s.id] = s;
        return acc;
    }, {});

    return (
        <div className="page tasks-page">
            <div className="tasks-content">
                <div className="page-header">
                    <span className="page-title-chinese">任务</span>
                    <h1 className="page-title">Задания</h1>
                    <p className="page-subtitle">Выполняй и получай награды</p>
                </div>

                {/* СПОНСОРЫ */}
                {sponsorTasks.length > 0 && (
                    <div className="tasks-section">
                        <div className="tasks-section-header">
                            <span className="tasks-section-title">赞助商</span>
                            <span className="tasks-section-count">
                                {sponsorTasks.filter(t => t.completed).length}/{sponsorTasks.length}
                            </span>
                        </div>

                        {sponsorTasks.map((task) => {
                            const sponsor = sponsorsMap[task.sponsor_id];
                            const isCompleted = task.completed;
                            const isChecking = checking === task.id;

                            return (
                                <div key={task.id} className="task-card">
                                    {isCompleted && (
                                        <div className="task-status done">Выполнено</div>
                                    )}
                                    <div className="task-title">{task.title}</div>
                                    <div className="task-desc">{task.description}</div>

                                    {sponsor && (
                                        <a
                                            href={sponsor.link}
                                            target="_blank"
                                            rel="noopener noreferrer"
                                            className="text-decoration-none d-inline-flex align-items-center gap-2 px-3 py-2 rounded-1"
                                            style={{
                                                background: 'rgba(212, 175, 55, 0.02)',
                                                color: '#d4af37',
                                                border: '1px solid rgba(212, 175, 55, 0.02)',
                                                fontSize: '13px',
                                                fontWeight: '500',
                                                width: 'fit-content',
                                                transition: 'all 0.3s ease',
                                            }}
                                            onMouseEnter={(e) => {
                                                e.currentTarget.style.background = 'rgba(212, 175, 55, 0.04)';
                                            }}
                                            onMouseLeave={(e) => {
                                                e.currentTarget.style.background = 'rgba(212, 175, 55, 0.02)';
                                            }}
                                        >
                                            进入频道
                                        </a>
                                    )}

                                    <div className="task-actions">
                                        {isCompleted ? (
                                            <div className="text-center py-2" style={{ color: 'rgba(90, 143, 106, 0.3)', fontSize: '13px', fontWeight: '500' }}>
                                                Награда получена
                                            </div>
                                        ) : (
                                            <button
                                                className="btn-mond"
                                                onClick={() => handleCheckSponsor(sponsor.id)}
                                                disabled={isChecking}
                                            >
                                                {isChecking ? 'Проверяю...' : 'Проверить подписку'}
                                                <TicketIcon size={16} className="btn-mond-icon" />
                                            </button>
                                        )}
                                    </div>
                                </div>
                            );
                        })}
                    </div>
                )}

                {/* ОБЫЧНЫЕ ЗАДАНИЯ */}
                {regularTasks.length > 0 && (
                    <div className="tasks-section">
                        <div className="tasks-section-header">
                            <span className="tasks-section-title">任务</span>
                            <span className="tasks-section-count">
                                {regularTasks.filter(t => t.completed).length}/{regularTasks.length}
                            </span>
                        </div>

                        {regularTasks.map((task) => {
                            const isCompleted = task.completed;
                            const isClaiming = claiming === task.id;
                            const canClaim = task.can_claim;
                            const isDaily = task.task_type === 'daily';
                            const progress = task.progress;
                            const required = task.required_count;
                            const timer = timeLeft[task.id];

                            const isTaskCompleted = isCompleted || (task.task_type === 'spin' && progress >= required);

                            let buttonText = 'Забрать награду';
                            let buttonDisabled = false;
                            let buttonOnClick: () => Promise<void> = () => handleClaim(task.id);

                            if (isDaily) {
                                if (canClaim) {
                                    buttonText = isClaiming ? 'Забираю...' : 'Забрать награду';
                                    buttonDisabled = isClaiming;
                                    buttonOnClick = () => handleClaim(task.id);
                                } else if (timer && timer !== 'Готово!' && timer !== 'Забрать!') {
                                    buttonText = `⏳ ${timer}`;
                                    buttonDisabled = true;
                                    buttonOnClick = async () => { };
                                } else if (timer === 'Забрать!') {
                                    buttonText = 'Забрать награду';
                                    buttonDisabled = false;
                                    buttonOnClick = () => handleClaim(task.id);
                                } else if (timer === 'Готово!') {
                                    buttonText = 'Забрать награду';
                                    buttonDisabled = false;
                                    buttonOnClick = () => handleClaim(task.id);
                                } else {
                                    buttonText = '⏳ 24:00:00';
                                    buttonDisabled = true;
                                    buttonOnClick = async () => { };
                                }
                            } else {
                                if (isTaskCompleted && !canClaim) {
                                    buttonText = 'Награда получена';
                                    buttonDisabled = true;
                                    buttonOnClick = async () => { };
                                } else if (canClaim || progress >= required) {
                                    buttonText = isClaiming ? 'Забираю...' : 'Забрать награду';
                                    buttonDisabled = isClaiming;
                                    buttonOnClick = () => handleClaim(task.id);
                                } else {
                                    buttonText = 'Выполняется...';
                                    buttonDisabled = true;
                                    buttonOnClick = async () => { };
                                }
                            }

                            return (
                                <div key={task.id} className="task-card">
                                    <div className="task-header">
                                        <div className="task-title">{task.title}</div>
                                        <div className={`task-status ${isTaskCompleted ? 'done' : 'pending'}`}>
                                            {isTaskCompleted ? 'Готово' : 'В процессе'}
                                        </div>
                                    </div>

                                    <div className="task-desc">{task.description}</div>

                                    {!isDaily && (
                                        <div className="task-progress-wrapper">
                                            <div className="task-progress-bar">
                                                <div
                                                    className="task-progress-fill"
                                                    style={{ width: `${Math.min((progress / required) * 100, 100)}%` }}
                                                />
                                                <span className="task-progress-text">{progress}/{required}</span>
                                            </div>
                                        </div>
                                    )}

                                    <div className="task-actions">
                                        {buttonDisabled && !buttonText.includes('Награда получена') ? (
                                            <div className="d-flex align-items-center justify-content-center gap-2 py-3 px-4 rounded-1" style={{
                                                background: 'rgba(212, 175, 55, 0.01)',
                                                border: '1px solid rgba(212, 175, 55, 0.01)',
                                                color: 'rgba(232, 224, 212, 0.08)',
                                                fontSize: '14px',
                                                fontWeight: '500',
                                                fontFamily: 'monospace',
                                                letterSpacing: '0.5px',
                                            }}>
                                                <span>⏳</span>
                                                {buttonText}
                                            </div>
                                        ) : (
                                            <button
                                                className="btn-mond"
                                                onClick={buttonOnClick}
                                                disabled={buttonDisabled}
                                            >
                                                {buttonText}
                                                {!buttonDisabled && !buttonText.includes('Награда получена') && <TicketIcon size={16} className="btn-mond-icon" />}
                                            </button>
                                        )}
                                    </div>
                                </div>
                            );
                        })}
                    </div>
                )}

                {tasks.length === 0 && (
                    <div className="text-center py-5" style={{ color: 'rgba(232, 224, 212, 0.04)' }}>
                        <div style={{ fontSize: '48px', marginBottom: '16px' }}>📭</div>
                        <p style={{ fontSize: '16px' }}>Заданий пока нет</p>
                        <p style={{ fontSize: '13px', marginTop: '4px', opacity: 0.5 }}>
                            Загляни позже, они скоро появятся!
                        </p>
                    </div>
                )}
            </div>
        </div>
    );
}