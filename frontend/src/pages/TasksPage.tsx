import { useEffect, useState, useRef } from 'react';
import { useAuthStore } from '../store/authStore';
import { getTasks, claimTask, checkTasks } from '../api/tasks';
import { getSponsors, checkSponsorSubscription } from '../api/sponsors';
import type { Sponsor } from '../api/sponsors';
import GoldButton from '../components/GoldButton';
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

    // ===== ОБНОВЛЕНИЕ ТАЙМЕРОВ В РЕАЛЬНОМ ВРЕМЕНИ =====
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
                        newTimeLeft[task.id] = '✅ Готово!';
                    }
                }
            });

            setTimeLeft(newTimeLeft);
        };

        // Первое обновление
        updateTimers();

        // Используем requestAnimationFrame для плавного обновления
        let lastUpdate = Date.now();

        const animate = () => {
            const now = Date.now();
            if (now - lastUpdate >= 1000) {
                updateTimers();
                lastUpdate = now;
            }
            animationRef.current = requestAnimationFrame(animate);
        };

        animationRef.current = requestAnimationFrame(animate);

        return () => {
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
            console.log('✅ Claim result:', result);

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
            console.error('❌ Claim error:', error);
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
                alert('✅ Подписка подтверждена! Ты получил 3 билетика! 🎉');
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
                <h1 className="page-title">📋 Задания</h1>
                <p className="page-subtitle">Выполняй задания и получай награды!</p>
            </div>

            {/* СПОНСОРЫ */}
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
                            color: '#d4af37',
                            letterSpacing: '0.5px',
                        }}>
                            🤝 Спонсоры
                        </span>
                        <span style={{
                            fontSize: '12px',
                            color: 'rgba(240,236,229,0.2)',
                            background: 'rgba(212,175,55,0.06)',
                            padding: '2px 10px',
                            borderRadius: '12px',
                            border: '1px solid rgba(212,175,55,0.06)',
                        }}>
                            {sponsorTasks.filter(t => t.completed).length}/{sponsorTasks.length}
                        </span>
                    </div>

                    {sponsorTasks.map((task) => {
                        const sponsor = sponsorsMap[task.sponsor_id];
                        const isCompleted = task.completed;
                        const isChecking = checking === task.id;

                        return (
                            <div key={task.id} style={{
                                background: 'rgba(255,255,255,0.02)',
                                backdropFilter: 'blur(20px)',
                                borderRadius: '14px',
                                padding: '18px 20px',
                                marginBottom: '12px',
                                border: isCompleted
                                    ? '1px solid rgba(90, 143, 106, 0.2)'
                                    : '1px solid rgba(255,255,255,0.04)',
                                transition: 'all 0.3s ease',
                                position: 'relative',
                                overflow: 'hidden',
                            }}>
                                {isCompleted && (
                                    <div style={{
                                        position: 'absolute',
                                        top: 0,
                                        right: 0,
                                        background: 'rgba(90, 143, 106, 0.08)',
                                        padding: '4px 14px',
                                        borderRadius: '0 14px 0 12px',
                                        fontSize: '11px',
                                        fontWeight: '600',
                                        color: '#5a8f6a',
                                    }}>
                                        ✅ Выполнено
                                    </div>
                                )}

                                <div style={{ marginBottom: '8px' }}>
                                    <span style={{
                                        fontSize: '15px',
                                        fontWeight: '600',
                                        color: '#f0ece5',
                                    }}>
                                        {task.title}
                                    </span>
                                </div>

                                <p style={{
                                    fontSize: '13px',
                                    color: 'rgba(240,236,229,0.4)',
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
                                                background: 'rgba(212, 175, 55, 0.06)',
                                                color: '#d4af37',
                                                borderRadius: '8px',
                                                fontSize: '13px',
                                                fontWeight: '500',
                                                textDecoration: 'none',
                                                border: '1px solid rgba(212, 175, 55, 0.06)',
                                                transition: 'all 0.3s ease',
                                            }}
                                            onMouseEnter={(e) => {
                                                e.currentTarget.style.background = 'rgba(212, 175, 55, 0.12)';
                                                e.currentTarget.style.borderColor = 'rgba(212, 175, 55, 0.15)';
                                            }}
                                            onMouseLeave={(e) => {
                                                e.currentTarget.style.background = 'rgba(212, 175, 55, 0.06)';
                                                e.currentTarget.style.borderColor = 'rgba(212, 175, 55, 0.06)';
                                            }}
                                        >
                                            <span style={{ fontSize: '16px' }}>🔗</span>
                                            Перейти в канал
                                        </a>
                                    </div>
                                )}

                                <div>
                                    {isCompleted ? (
                                        <div style={{
                                            padding: '10px 0',
                                            textAlign: 'center',
                                            color: 'rgba(90, 143, 106, 0.6)',
                                            fontSize: '13px',
                                            fontWeight: '500',
                                        }}>
                                            🎉 Награда получена!
                                        </div>
                                    ) : (
                                        <GoldButton
                                            text={isChecking ? '⏳ Проверяю...' : '✅ Проверить подписку'}
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

            {/* ОБЫЧНЫЕ ЗАДАНИЯ */}
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
                            color: '#f0ece5',
                            letterSpacing: '0.5px',
                        }}>
                            📋 Другие задания
                        </span>
                        <span style={{
                            fontSize: '12px',
                            color: 'rgba(240,236,229,0.2)',
                            background: 'rgba(255,255,255,0.03)',
                            padding: '2px 10px',
                            borderRadius: '12px',
                            border: '1px solid rgba(255,255,255,0.04)',
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

                        let buttonText = '🎁 Забрать награду';
                        let buttonDisabled = false;
                        let buttonOnClick: () => Promise<void> = () => handleClaim(task.id);

                        if (isDaily) {
                            if (canClaim) {
                                buttonText = isClaiming ? '⏳ Забираю...' : '🎁 Забрать награду';
                                buttonDisabled = isClaiming;
                                buttonOnClick = () => handleClaim(task.id);
                            } else if (timer && timer !== '✅ Готово!') {
                                buttonText = `⏳ ${timer}`;
                                buttonDisabled = true;
                                buttonOnClick = async () => { };
                            } else if (timer === '✅ Готово!') {
                                buttonText = '🎁 Забрать награду';
                                buttonDisabled = false;
                                buttonOnClick = () => handleClaim(task.id);
                            } else {
                                buttonText = '⏳ 24:00:00';
                                buttonDisabled = true;
                                buttonOnClick = async () => { };
                            }
                        } else {
                            if (isTaskCompleted && !canClaim) {
                                buttonText = '🎉 Награда получена';
                                buttonDisabled = true;
                                buttonOnClick = async () => { };
                            } else if (canClaim || progress >= required) {
                                buttonText = isClaiming ? '⏳ Забираю...' : '🎁 Забрать награду';
                                buttonDisabled = isClaiming;
                                buttonOnClick = () => handleClaim(task.id);
                            } else {
                                buttonText = '⏳ Выполняется...';
                                buttonDisabled = true;
                                buttonOnClick = async () => { };
                            }
                        }

                        return (
                            <div key={task.id} style={{
                                background: 'rgba(255,255,255,0.02)',
                                backdropFilter: 'blur(20px)',
                                borderRadius: '14px',
                                padding: '18px 20px',
                                marginBottom: '12px',
                                border: isTaskCompleted
                                    ? '1px solid rgba(90, 143, 106, 0.12)'
                                    : '1px solid rgba(255,255,255,0.04)',
                                transition: 'all 0.3s ease',
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
                                        color: '#f0ece5',
                                    }}>
                                        {task.title}
                                    </span>
                                    <span style={{
                                        fontSize: '11px',
                                        fontWeight: '500',
                                        color: isTaskCompleted ? '#5a8f6a' : 'rgba(240,236,229,0.2)',
                                        background: isTaskCompleted
                                            ? 'rgba(90, 143, 106, 0.08)'
                                            : 'rgba(255,255,255,0.03)',
                                        padding: '2px 12px',
                                        borderRadius: '12px',
                                        border: isTaskCompleted
                                            ? '1px solid rgba(90, 143, 106, 0.1)'
                                            : '1px solid rgba(255,255,255,0.04)',
                                        whiteSpace: 'nowrap',
                                    }}>
                                        {isTaskCompleted ? '✅ Готово' : '⏳ В процессе'}
                                    </span>
                                </div>

                                <p style={{
                                    fontSize: '13px',
                                    color: 'rgba(240,236,229,0.4)',
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
                                            background: 'rgba(255,255,255,0.06)',
                                            borderRadius: '4px',
                                            overflow: 'hidden',
                                        }}>
                                            <div style={{
                                                width: `${Math.min((progress / required) * 100, 100)}%`,
                                                height: '100%',
                                                background: progress >= required
                                                    ? 'linear-gradient(90deg, #5a8f6a, #7aaf8a)'
                                                    : 'linear-gradient(90deg, #d4af37, #f0d060)',
                                                borderRadius: '4px',
                                                transition: 'width 0.5s ease',
                                            }} />
                                        </div>
                                        <span style={{
                                            fontSize: '12px',
                                            fontWeight: '500',
                                            color: progress >= required ? '#5a8f6a' : 'rgba(240,236,229,0.3)',
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
                                            background: 'rgba(255,255,255,0.03)',
                                            borderRadius: '10px',
                                            border: '1px solid rgba(255,255,255,0.04)',
                                            color: 'rgba(240,236,229,0.2)',
                                            fontSize: '14px',
                                            fontWeight: '500',
                                            fontFamily: 'monospace',
                                            letterSpacing: '0.5px',
                                        }}>
                                            <span>⏳</span>
                                            {buttonText}
                                        </div>
                                    ) : (
                                        <GoldButton
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
                    color: 'rgba(240,236,229,0.2)',
                }}>
                    <div style={{ fontSize: '48px', marginBottom: '16px' }}>📭</div>
                    <p style={{ fontSize: '16px' }}>Заданий пока нет</p>
                    <p style={{ fontSize: '13px', marginTop: '4px', color: 'rgba(240,236,229,0.1)' }}>
                        Загляни позже, они скоро появятся!
                    </p>
                </div>
            )}
        </div>
    );
}