import { useEffect, useState, useRef } from 'react';
import { useAuthStore } from '../store/authStore';
import { getTasks, claimTask, checkTasks } from '../api/tasks';
import { getSponsors, checkSponsorSubscription } from '../api/sponsors';
import type { Sponsor } from '../api/sponsors';
import TicketIcon from '../components/TicketIcon';
import ButtonGenshin from '../components/ButtonGenshin';

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

            await loadData();
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
                alert('✅ Подписка подтверждена! Ты получил 1 билетик!');
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

    if (loading) return <div className="loading-text text-center py-5" style={{ color: 'rgba(232,224,212,0.15)' }}>Загрузка заданий...</div>;

    // ===== КАТЕГОРИИ =====
    const sponsorTasks = tasks.filter(task => task.task_type === 'sponsor');
    const dailyTasks = tasks.filter(task => task.task_type === 'daily');
    const regularTasks = tasks.filter(task => task.task_type === 'spin' || task.task_type === 'social');

    const sponsorsMap = sponsors.reduce<Record<string, Sponsor>>((acc, s) => {
        acc[s.id] = s;
        return acc;
    }, {});

    // ===== ЕДИНЫЙ РЕНДЕР КАРТОЧКИ =====
    const renderTaskCard = (task: any) => {
        const isCompleted = task.completed;
        const isClaiming = claiming === task.id;
        const isChecking = checking === task.id;
        const canClaim = task.can_claim;
        const isDaily = task.task_type === 'daily';
        const isSponsor = task.task_type === 'sponsor';
        const progress = task.progress;
        const required = task.required_count;
        const timer = timeLeft[task.id];

        // ===== СТАТУС =====
        let statusLabel = 'В процессе';
        let statusClass = 'pending';
        if (isSponsor) {
            if (isCompleted) {
                statusLabel = 'Готово';
                statusClass = 'done';
            } else {
                statusLabel = 'В процессе';
                statusClass = 'pending';
            }
        } else if (isDaily) {
            if (canClaim) {
                statusLabel = 'Можно забрать';
                statusClass = 'done';
            } else if (timer && timer !== 'Готово!' && timer !== 'Забрать!') {
                statusLabel = 'Ожидание';
                statusClass = 'pending';
            } else {
                statusLabel = 'Можно забрать';
                statusClass = 'done';
            }
        } else {
            // spin / social
            if (isCompleted && !canClaim) {
                statusLabel = 'Готово';
                statusClass = 'done';
            } else if (canClaim || progress >= required) {
                statusLabel = 'Можно забрать';
                statusClass = 'done';
            } else {
                statusLabel = 'В процессе';
                statusClass = 'pending';
            }
        }

        // ===== КНОПКА =====
        let buttonText = 'Забрать награду';
        let buttonDisabled = false;
        let buttonOnClick: () => Promise<void> = () => handleClaim(task.id);
        let showTicketIcon = true;
        let showAsPlainText = false;

        if (isSponsor) {
            if (isCompleted) {
                buttonText = 'Награда получена';
                buttonDisabled = true;
                buttonOnClick = async () => { };
                showTicketIcon = false;
                showAsPlainText = true;
            } else {
                buttonText = isChecking ? 'Проверяю...' : 'Проверить подписку';
                buttonDisabled = isChecking;
                buttonOnClick = () => handleCheckSponsor(task.sponsor_id!);
                showTicketIcon = false;
            }
        } else if (isDaily) {
            if (canClaim) {
                buttonText = isClaiming ? 'Забираю...' : 'Забрать награду';
                buttonDisabled = isClaiming;
            } else if (timer && timer !== 'Готово!' && timer !== 'Забрать!') {
                buttonText = `⏳ ${timer}`;
                buttonDisabled = true;
                buttonOnClick = async () => { };
                showTicketIcon = false;
                showAsPlainText = true;
            } else {
                buttonText = 'Забрать награду';
                buttonDisabled = false;
            }
        } else {
            // spin / social
            if (isCompleted && !canClaim) {
                buttonText = 'Награда получена';
                buttonDisabled = true;
                buttonOnClick = async () => { };
                showTicketIcon = false;
                showAsPlainText = true;
            } else if (canClaim || progress >= required) {
                buttonText = isClaiming ? 'Забираю...' : 'Забрать награду';
                buttonDisabled = isClaiming;
            } else {
                buttonText = 'Выполняется...';
                buttonDisabled = true;
                buttonOnClick = async () => { };
                showTicketIcon = false;
                showAsPlainText = true;
            }
        }

        const sponsor = sponsorsMap[task.sponsor_id];

        return (
            <div key={task.id} className="task-card">
                <div className="task-header">
                    <div className="task-title">{task.title}</div>
                    <div className={`task-status ${statusClass}`}>{statusLabel}</div>
                </div>

                <div className="task-desc">{task.description}</div>

                {/* Прогресс-бар — только для spin / social */}
                {!isDaily && !isSponsor && (
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

                {/* Кнопка "Перейти в канал" — только для спонсоров и пока не выполнено */}
                {isSponsor && sponsor && !isCompleted && (
                    <a
                        href={sponsor.link}
                        target="_blank"
                        rel="noopener noreferrer"
                        style={{
                            display: 'inline-flex',
                            alignItems: 'center',
                            gap: '8px',
                            padding: '8px 18px',
                            background: 'rgba(212, 175, 55, 0.02)',
                            color: '#d4af37',
                            borderRadius: '8px',
                            fontSize: '13px',
                            fontWeight: '500',
                            textDecoration: 'none',
                            border: '1px solid rgba(212, 175, 55, 0.02)',
                            transition: 'all 0.3s ease',
                            width: 'fit-content',
                            marginBottom: '12px',
                        }}
                        onMouseEnter={(e) => {
                            e.currentTarget.style.background = 'rgba(212, 175, 55, 0.04)';
                        }}
                        onMouseLeave={(e) => {
                            e.currentTarget.style.background = 'rgba(212, 175, 55, 0.02)';
                        }}
                    >
                        Перейти в канал
                    </a>
                )}

                <div className="task-actions">
                    {showAsPlainText ? (
                        <div style={{
                            display: 'flex',
                            alignItems: 'center',
                            justifyContent: 'center',
                            gap: '8px',
                            padding: '12px 20px',
                            background: 'rgba(255,255,255,0.02)',
                            borderRadius: '8px',
                            border: '1px solid rgba(212, 175, 55, 0.02)',
                            color: 'rgba(232,224,212,0.15)',
                            fontSize: '14px',
                            fontWeight: '500',
                            fontFamily: buttonText.includes('⏳') ? 'monospace' : 'inherit',
                            letterSpacing: buttonText.includes('⏳') ? '0.5px' : 'normal',
                        }}>
                            {buttonText}
                        </div>
                    ) : (
                        <ButtonGenshin
                            text={buttonText}
                            onClick={buttonOnClick}
                            disabled={buttonDisabled}
                            icon={showTicketIcon ? <TicketIcon size={16} /> : undefined}
                        />
                    )}
                </div>
            </div>
        );
    };

    return (
        <div className="page tasks-page">
            <div className="tasks-content">
                <div className="page-header">
                    <h1 className="page-title">Задания</h1>
                    <p className="page-subtitle">Выполняй и получай награды</p>
                </div>

                {/* ===== 1. СПОНСОРЫ ===== */}
                {sponsorTasks.length > 0 && (
                    <div className="tasks-section">
                        <div className="tasks-section-header">
                            <span className="tasks-section-title">Спонсоры</span>
                            <span className="tasks-section-count">
                                {sponsorTasks.filter(t => t.completed).length}/{sponsorTasks.length}
                            </span>
                        </div>
                        {sponsorTasks.map(renderTaskCard)}
                    </div>
                )}

                {/* ===== 2. ЕЖЕДНЕВНЫЕ ===== */}
                {dailyTasks.length > 0 && (
                    <div className="tasks-section">
                        <div className="tasks-section-header">
                            <span className="tasks-section-title">Ежедневные</span>
                            <span className="tasks-section-count">
                                {dailyTasks.filter(t => t.can_claim).length}/{dailyTasks.length}
                            </span>
                        </div>
                        {dailyTasks.map(renderTaskCard)}
                    </div>
                )}

                {/* ===== 3. ПОСТОЯННЫЕ (spin + social) ===== */}
                {regularTasks.length > 0 && (
                    <div className="tasks-section">
                        <div className="tasks-section-header">
                            <span className="tasks-section-title">Постоянные</span>
                            <span className="tasks-section-count">
                                {regularTasks.filter(t => t.completed).length}/{regularTasks.length}
                            </span>
                        </div>
                        {regularTasks.map(renderTaskCard)}
                    </div>
                )}

                {tasks.length === 0 && (
                    <div style={{
                        textAlign: 'center',
                        padding: '60px 20px',
                        color: 'rgba(232,224,212,0.04)',
                    }}>
                        <div style={{ fontSize: '48px', marginBottom: '16px' }}>📭</div>
                        <p style={{ fontSize: '16px' }}>Заданий пока нет</p>
                        <p style={{ fontSize: '13px', marginTop: '4px', color: 'rgba(232,224,212,0.04)' }}>
                            Загляни позже, они скоро появятся!
                        </p>
                    </div>
                )}
            </div>
        </div>
    );
}