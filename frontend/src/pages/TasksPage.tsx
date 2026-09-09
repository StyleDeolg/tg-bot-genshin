import { useEffect, useState, useRef } from 'react';
import { useAuthStore } from '../store/authStore';
import { getTasks, claimTask, checkTasks } from '../api/tasks';
import { getSponsors, checkSponsorSubscription } from '../api/sponsors';
import type { Sponsor } from '../api/sponsors';
import LiyueButton from '../components/LiyueButton';
import TicketIcon from '../components/TicketIcon';
import PageOrnament from '../components/PageOrnament';

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

    if (loading) return <div className="loading-text">Загрузка заданий...</div>;

    const sponsorTasks = tasks.filter(task => task.task_type === 'sponsor');
    const regularTasks = tasks.filter(task => task.task_type !== 'sponsor');

    const sponsorsMap = sponsors.reduce<Record<string, Sponsor>>((acc, s) => {
        acc[s.id] = s;
        return acc;
    }, {});

    return (
        <div className="page tasks-page">
            <div style={{ marginBottom: '28px' }}>
                <PageOrnament />
                <h1 className="page-title">任务</h1>
                <p className="page-subtitle">Задания</p>
            </div>

            {sponsorTasks.length > 0 && (
                <div style={{ marginBottom: '32px' }}>
                    <div style={{
                        display: 'flex',
                        alignItems: 'center',
                        gap: '12px',
                        marginBottom: '16px',
                    }}>
                        <span style={{
                            fontSize: '20px',
                            fontWeight: '600',
                            color: '#b83a2a',
                            letterSpacing: '0.5px',
                            fontFamily: "'Inter', sans-serif",
                        }}>
                            赞助商
                        </span>
                        <span style={{
                            fontSize: '12px',
                            color: 'rgba(232,221,208,0.2)',
                            background: 'rgba(180,60,40,0.04)',
                            padding: '2px 10px',
                            borderRadius: '4px',
                            border: '1px solid rgba(180,60,40,0.04)',
                        }}>
                            {sponsorTasks.filter(t => t.completed).length}/{sponsorTasks.length}
                        </span>
                    </div>

                    {sponsorTasks.map((task) => {
                        const sponsor = sponsorsMap[task.sponsor_id];
                        const isCompleted = task.completed;
                        const isChecking = checking === task.id;

                        return (
                            <div key={task.id} className="liyue-card" style={{
                                border: isCompleted
                                    ? '1px solid rgba(90, 143, 106, 0.04)'
                                    : '1px solid rgba(180,60,40,0.04)',
                                position: 'relative',
                                overflow: 'hidden',
                            }}>
                                {isCompleted && (
                                    <div style={{
                                        position: 'absolute',
                                        top: 0,
                                        right: 0,
                                        background: 'rgba(90, 143, 106, 0.04)',
                                        padding: '4px 14px',
                                        borderRadius: '0 8px 0 8px',
                                        fontSize: '11px',
                                        fontWeight: '600',
                                        color: '#5a8f6a',
                                    }}>
                                        Выполнено
                                    </div>
                                )}

                                <div style={{ marginBottom: '8px' }}>
                                    <span style={{
                                        fontSize: '15px',
                                        fontWeight: '600',
                                        color: '#e8ddd0',
                                    }}>
                                        {task.title}
                                    </span>
                                </div>

                                <p style={{
                                    fontSize: '13px',
                                    color: 'rgba(232,221,208,0.35)',
                                    marginBottom: '14px',
                                    lineHeight: 1.5,
                                }}>
                                    {task.description}
                                </p>

                                {sponsor && (
                                    <div style={{ marginBottom: '14px' }}>
                                        <a
                                            href={sponsor.link}
                                            target="_blank"
                                            rel="noopener noreferrer"
                                            style={{
                                                display: 'inline-flex',
                                                alignItems: 'center',
                                                gap: '8px',
                                                padding: '8px 18px',
                                                background: 'rgba(180,60,40,0.04)',
                                                color: '#b83a2a',
                                                borderRadius: '4px',
                                                fontSize: '13px',
                                                fontWeight: '500',
                                                textDecoration: 'none',
                                                border: '1px solid rgba(180,60,40,0.04)',
                                                transition: 'all 0.3s ease',
                                            }}
                                            onMouseEnter={(e) => {
                                                e.currentTarget.style.background = 'rgba(180,60,40,0.08)';
                                            }}
                                            onMouseLeave={(e) => {
                                                e.currentTarget.style.background = 'rgba(180,60,40,0.04)';
                                            }}
                                        >
                                            进入频道
                                        </a>
                                    </div>
                                )}

                                <div>
                                    {isCompleted ? (
                                        <div style={{
                                            padding: '10px 0',
                                            textAlign: 'center',
                                            color: 'rgba(90, 143, 106, 0.3)',
                                            fontSize: '13px',
                                            fontWeight: '500',
                                        }}>
                                            Награда получена
                                        </div>
                                    ) : (
                                        <LiyueButton
                                            text={isChecking ? 'Проверяю...' : 'Проверить подписку'}
                                            onClick={() => handleCheckSponsor(sponsor.id)}
                                            disabled={isChecking}
                                            icon={<TicketIcon size={16} />}
                                        />
                                    )}
                                </div>
                            </div>
                        );
                    })}
                </div>
            )}

            {regularTasks.length > 0 && (
                <div>
                    <div style={{
                        display: 'flex',
                        alignItems: 'center',
                        gap: '12px',
                        marginBottom: '16px',
                    }}>
                        <span style={{
                            fontSize: '20px',
                            fontWeight: '600',
                            color: '#e8ddd0',
                            letterSpacing: '0.5px',
                            fontFamily: "'Inter', sans-serif",
                        }}>
                            任务
                        </span>
                        <span style={{
                            fontSize: '12px',
                            color: 'rgba(232,221,208,0.15)',
                            background: 'rgba(255,255,255,0.02)',
                            padding: '2px 10px',
                            borderRadius: '4px',
                            border: '1px solid rgba(255,255,255,0.02)',
                        }}>
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
                            <div key={task.id} className="liyue-card" style={{
                                border: isTaskCompleted
                                    ? '1px solid rgba(90, 143, 106, 0.04)'
                                    : '1px solid rgba(180,60,40,0.04)',
                            }}>
                                <div style={{
                                    display: 'flex',
                                    justifyContent: 'space-between',
                                    alignItems: 'flex-start',
                                    marginBottom: '6px',
                                }}>
                                    <span style={{
                                        fontSize: '15px',
                                        fontWeight: '600',
                                        color: '#e8ddd0',
                                    }}>
                                        {task.title}
                                    </span>
                                    <span style={{
                                        fontSize: '11px',
                                        fontWeight: '500',
                                        color: isTaskCompleted ? '#5a8f6a' : 'rgba(232,221,208,0.15)',
                                        background: isTaskCompleted
                                            ? 'rgba(90, 143, 106, 0.04)'
                                            : 'rgba(255,255,255,0.02)',
                                        padding: '2px 12px',
                                        borderRadius: '4px',
                                        border: isTaskCompleted
                                            ? '1px solid rgba(90, 143, 106, 0.04)'
                                            : '1px solid rgba(255,255,255,0.02)',
                                        whiteSpace: 'nowrap',
                                    }}>
                                        {isTaskCompleted ? 'Готово' : 'В процессе'}
                                    </span>
                                </div>

                                <p style={{
                                    fontSize: '13px',
                                    color: 'rgba(232,221,208,0.35)',
                                    marginBottom: '12px',
                                    lineHeight: 1.5,
                                }}>
                                    {task.description}
                                </p>

                                {!isDaily && (
                                    <div style={{
                                        display: 'flex',
                                        alignItems: 'center',
                                        gap: '12px',
                                        marginBottom: '14px',
                                    }}>
                                        <div style={{
                                            flex: 1,
                                            height: '4px',
                                            background: 'rgba(255,255,255,0.04)',
                                            borderRadius: '4px',
                                            overflow: 'hidden',
                                        }}>
                                            <div style={{
                                                width: `${Math.min((progress / required) * 100, 100)}%`,
                                                height: '100%',
                                                background: progress >= required
                                                    ? 'linear-gradient(90deg, #5a8f6a, #7aaf8a)'
                                                    : 'linear-gradient(90deg, #b83a2a, #8a2a1a)',
                                                borderRadius: '4px',
                                                transition: 'width 0.5s ease',
                                            }} />
                                        </div>
                                        <span style={{
                                            fontSize: '12px',
                                            fontWeight: '500',
                                            color: progress >= required ? '#5a8f6a' : 'rgba(232,221,208,0.25)',
                                            minWidth: '45px',
                                            textAlign: 'right',
                                            fontVariantNumeric: 'tabular-nums',
                                        }}>
                                            {progress}/{required}
                                        </span>
                                    </div>
                                )}

                                <div>
                                    {buttonDisabled && !buttonText.includes('Награда получена') ? (
                                        <div style={{
                                            display: 'flex',
                                            alignItems: 'center',
                                            justifyContent: 'center',
                                            gap: '8px',
                                            padding: '12px 20px',
                                            background: 'rgba(255,255,255,0.02)',
                                            borderRadius: '4px',
                                            border: '1px solid rgba(255,255,255,0.02)',
                                            color: 'rgba(232,221,208,0.15)',
                                            fontSize: '14px',
                                            fontWeight: '500',
                                            fontFamily: 'monospace',
                                            letterSpacing: '0.5px',
                                        }}>
                                            <span>⏳</span>
                                            {buttonText}
                                        </div>
                                    ) : (
                                        <LiyueButton
                                            text={buttonText}
                                            onClick={buttonOnClick}
                                            disabled={buttonDisabled}
                                            icon={!buttonDisabled && !buttonText.includes('Награда получена') ? <TicketIcon size={16} /> : undefined}
                                        />
                                    )}
                                </div>
                            </div>
                        );
                    })}
                </div>
            )}

            {tasks.length === 0 && (
                <div style={{
                    textAlign: 'center',
                    padding: '60px 20px',
                    color: 'rgba(232,221,208,0.08)',
                }}>
                    <div style={{ fontSize: '48px', marginBottom: '16px' }}>📭</div>
                    <p style={{ fontSize: '16px' }}>Заданий пока нет</p>
                    <p style={{ fontSize: '13px', marginTop: '4px', color: 'rgba(232,221,208,0.04)' }}>
                        Загляни позже, они скоро появятся!
                    </p>
                </div>
            )}
        </div>
    );
}