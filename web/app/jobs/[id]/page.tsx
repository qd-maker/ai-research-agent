"use client";

import { useQuery } from "@tanstack/react-query";
import { motion } from "framer-motion";
import { AlertCircle, CheckCircle2, Loader2, Terminal, Clock, Zap } from "lucide-react";
import { useRouter } from "next/navigation";
import { useEffect, useState, use } from "react";
import { api } from "@/services/api";

const steps = [
    { key: "plan", label: "规划研究维度", icon: "📋" },
    { key: "search", label: "搜索相关信息", icon: "🔍" },
    { key: "filter", label: "筛选优质来源", icon: "🎯" },
    { key: "crawl", label: "爬取网页内容", icon: "🌐" },
    { key: "extract", label: "提取结构化数据", icon: "📊" },
    { key: "compare", label: "对比分析", icon: "⚖️" },
    { key: "report", label: "生成报告", icon: "📝" },
];

export default function JobStatusPage({ params }: { params: Promise<{ id: string }> }) {
    const { id } = use(params);
    const router = useRouter();
    const [logs, setLogs] = useState<string[]>([]);

    const { data: job, error } = useQuery({
        queryKey: ["job", id],
        queryFn: () => api.getJobStatus(id),
        refetchInterval: (query) => {
            const data = query.state.data;
            return data?.status === "completed" || data?.status === "failed" ? false : 2000;
        },
    });

    useEffect(() => {
        if (job?.status === "completed") {
            setTimeout(() => {
                router.push(`/reports/${id}`);
            }, 1500);
        }
    }, [job?.status, id, router]);

    useEffect(() => {
        if (job?.progress) {
            setLogs((prev) => {
                const lastLog = prev[prev.length - 1];
                if (lastLog !== job.progress) {
                    return [...prev, job.progress];
                }
                return prev;
            });
        }
    }, [job?.progress]);

    if (error) {
        return (
            <div style={{ minHeight: '100vh', display: 'flex', alignItems: 'center', justifyContent: 'center' }}>
                <div style={{ color: '#ef4444', display: 'flex', alignItems: 'center', gap: 8 }}>
                    <AlertCircle />
                    <span>加载失败</span>
                </div>
            </div>
        );
    }

    if (!job) return null;

    const currentStep = Math.min(job.step_count, steps.length - 1);

    return (
        <main className="relative" style={{ minHeight: '100vh', padding: '60px 24px' }}>
            <div className="gradient-bg" />
            <div className="orb orb-1" />
            <div className="orb orb-2" />

            <div style={{ maxWidth: 900, margin: '0 auto', position: 'relative', zIndex: 10 }}>
                {/* Header */}
                <motion.div
                    initial={{ opacity: 0, y: 20 }}
                    animate={{ opacity: 1, y: 0 }}
                    style={{ textAlign: 'center', marginBottom: 60 }}
                >
                    <span className="status-badge" style={{
                        marginBottom: 24,
                        display: 'inline-flex',
                        alignItems: 'center',
                        gap: 8,
                        background: 'rgba(99,102,241,0.1)',
                        borderColor: 'rgba(99,102,241,0.2)',
                        color: '#a78bfa'
                    }}>
                        {job.status === "running" || job.status === "pending" ? (
                            <>
                                <Loader2 style={{ width: 16, height: 16, animation: 'spin 1s linear infinite', flexShrink: 0 }} />
                                正在研究中...
                            </>
                        ) : job.status === "completed" ? (
                            <>
                                <CheckCircle2 style={{ width: 16, height: 16 }} />
                                研究完成
                            </>
                        ) : (
                            <>
                                <AlertCircle style={{ width: 16, height: 16 }} />
                                研究失败
                            </>
                        )}
                    </span>

                    <h1 style={{ fontSize: '2rem', fontWeight: 700, marginBottom: 12 }}>
                        {job.query}
                    </h1>
                    <p style={{ color: 'rgba(255,255,255,0.5)', display: 'flex', alignItems: 'center', justifyContent: 'center', gap: 8 }}>
                        <Clock style={{ width: 16, height: 16 }} />
                        预计需要 2-3 分钟
                    </p>
                </motion.div>

                <div style={{ display: 'grid', gridTemplateColumns: '1fr 1fr', gap: 24 }}>
                    {/* Steps */}
                    <motion.div
                        initial={{ opacity: 0, x: -20 }}
                        animate={{ opacity: 1, x: 0 }}
                        transition={{ delay: 0.2 }}
                        className="glass-card"
                        style={{ padding: 32 }}
                    >
                        <h2 style={{ fontSize: 18, fontWeight: 600, marginBottom: 24, display: 'flex', alignItems: 'center', gap: 10 }}>
                            <Zap style={{ width: 20, height: 20, color: '#a78bfa' }} />
                            研究进度
                        </h2>

                        <div style={{ display: 'flex', flexDirection: 'column', gap: 16 }}>
                            {steps.map((step, i) => {
                                const isDone = job.step_count > i;
                                const isCurrent = job.step_count === i;

                                return (
                                    <div key={step.key} style={{ display: 'flex', alignItems: 'center', gap: 16 }}>
                                        <div style={{
                                            width: 40,
                                            height: 40,
                                            borderRadius: 12,
                                            display: 'flex',
                                            alignItems: 'center',
                                            justifyContent: 'center',
                                            fontSize: 20,
                                            background: isDone
                                                ? 'linear-gradient(135deg, rgba(16,185,129,0.2), rgba(52,211,153,0.2))'
                                                : isCurrent
                                                    ? 'linear-gradient(135deg, rgba(99,102,241,0.2), rgba(139,92,246,0.2))'
                                                    : 'rgba(255,255,255,0.05)',
                                            border: isDone
                                                ? '1px solid rgba(16,185,129,0.3)'
                                                : isCurrent
                                                    ? '1px solid rgba(99,102,241,0.3)'
                                                    : '1px solid rgba(255,255,255,0.1)',
                                        }}>
                                            {step.icon}
                                        </div>
                                        <div style={{ flex: 1 }}>
                                            <div style={{
                                                fontWeight: 500,
                                                color: isDone ? '#10b981' : isCurrent ? '#a78bfa' : 'rgba(255,255,255,0.4)'
                                            }}>
                                                {step.label}
                                            </div>
                                        </div>
                                        {isDone && (
                                            <CheckCircle2 style={{ width: 18, height: 18, color: '#10b981' }} />
                                        )}
                                        {isCurrent && (
                                            <div className="spinner" style={{ width: 18, height: 18, borderColor: 'rgba(167,139,250,0.3)', borderTopColor: '#a78bfa' }} />
                                        )}
                                    </div>
                                );
                            })}
                        </div>
                    </motion.div>

                    {/* Logs */}
                    <motion.div
                        initial={{ opacity: 0, x: 20 }}
                        animate={{ opacity: 1, x: 0 }}
                        transition={{ delay: 0.3 }}
                        className="glass-card"
                        style={{ padding: 32, display: 'flex', flexDirection: 'column', height: 420 }}
                    >
                        <div style={{ display: 'flex', justifyContent: 'space-between', alignItems: 'center', marginBottom: 24 }}>
                            <h2 style={{ fontSize: 18, fontWeight: 600, display: 'flex', alignItems: 'center', gap: 10 }}>
                                <Terminal style={{ width: 20, height: 20, color: '#a78bfa' }} />
                                实时日志
                            </h2>
                            <div style={{ display: 'flex', gap: 6 }}>
                                <div style={{ width: 10, height: 10, borderRadius: '50%', background: '#ef4444', opacity: 0.3 }} />
                                <div style={{ width: 10, height: 10, borderRadius: '50%', background: '#eab308', opacity: 0.3 }} />
                                <div style={{ width: 10, height: 10, borderRadius: '50%', background: '#22c55e', opacity: 0.3 }} />
                            </div>
                        </div>

                        <div style={{
                            flex: 1,
                            overflow: 'auto',
                            fontFamily: 'monospace',
                            fontSize: 13,
                            color: 'rgba(255,255,255,0.6)',
                            display: 'flex',
                            flexDirection: 'column',
                            gap: 8
                        }}>
                            {logs.length === 0 && (
                                <div style={{ color: 'rgba(255,255,255,0.3)' }}>等待日志...</div>
                            )}
                            {logs.map((log, i) => (
                                <motion.div
                                    key={i}
                                    initial={{ opacity: 0, x: -10 }}
                                    animate={{ opacity: 1, x: 0 }}
                                >
                                    <span style={{ color: '#a78bfa' }}>›</span> {log}
                                </motion.div>
                            ))}
                            {job.status === "running" && (
                                <div style={{ width: 8, height: 16, background: '#a78bfa', opacity: 0.5, animation: 'pulse 1s ease-in-out infinite' }} />
                            )}
                        </div>
                    </motion.div>
                </div>
            </div>
        </main>
    );
}
