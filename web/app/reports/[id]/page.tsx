"use client";

import { useQuery } from "@tanstack/react-query";
import { motion } from "framer-motion";
import { ArrowLeft, Download, FileText, Table2, BookOpen } from "lucide-react";
import Link from "next/link";
import ReactMarkdown from "react-markdown";
import remarkGfm from "remark-gfm";
import { use } from "react";
import { api } from "@/services/api";

interface ComparisonTable {
    [dimension: string]: Record<string, string | number | null>;
}

interface ReportJson {
    comparison_table?: ComparisonTable;
    [key: string]: unknown;
}

export default function ReportPage({ params }: { params: Promise<{ id: string }> }) {
    const { id } = use(params);
    const { data: report, isLoading, error } = useQuery({
        queryKey: ["report", id],
        queryFn: () => api.getJobReport(id),
    });

    const downloadLinks = api.getDownloadLinks(id);
    const reportJson = report?.report_json as ReportJson | undefined;
    const comparisonTable = reportJson?.comparison_table;

    if (isLoading) {
        return (
            <div style={{ minHeight: '100vh', display: 'flex', alignItems: 'center', justifyContent: 'center' }}>
                <div className="spinner" style={{ width: 32, height: 32 }} />
            </div>
        );
    }

    if (error || !report) {
        return (
            <div style={{ minHeight: '100vh', display: 'flex', flexDirection: 'column', alignItems: 'center', justifyContent: 'center', gap: 16 }}>
                <div style={{ color: '#ef4444', fontSize: 18 }}>加载报告失败</div>
                <Link href="/" style={{ color: '#a78bfa' }}>
                    返回首页
                </Link>
            </div>
        );
    }

    return (
        <main className="relative" style={{ minHeight: '100vh', padding: '40px 24px' }}>
            <div className="gradient-bg" />

            <div style={{ maxWidth: 1100, margin: '0 auto', position: 'relative', zIndex: 10 }}>
                {/* Header */}
                <div style={{ display: 'flex', justifyContent: 'space-between', alignItems: 'center', marginBottom: 40 }}>
                    <Link
                        href="/"
                        style={{ display: 'flex', alignItems: 'center', gap: 8, color: 'rgba(255,255,255,0.6)', textDecoration: 'none', transition: 'color 0.3s' }}
                    >
                        <ArrowLeft style={{ width: 18, height: 18 }} />
                        新的研究
                    </Link>

                    <div style={{ display: 'flex', gap: 12 }}>
                        <a
                            href={downloadLinks.markdown}
                            download
                            target="_blank"
                            style={{
                                display: 'flex',
                                alignItems: 'center',
                                gap: 8,
                                padding: '10px 20px',
                                background: 'rgba(255,255,255,0.05)',
                                border: '1px solid rgba(255,255,255,0.1)',
                                borderRadius: 12,
                                color: 'white',
                                textDecoration: 'none',
                                fontSize: 14,
                                fontWeight: 500,
                                transition: 'all 0.3s'
                            }}
                        >
                            <FileText style={{ width: 16, height: 16 }} />
                            下载 Markdown
                        </a>
                        <a
                            href={downloadLinks.csv}
                            download
                            target="_blank"
                            style={{
                                display: 'flex',
                                alignItems: 'center',
                                gap: 8,
                                padding: '10px 20px',
                                background: 'rgba(255,255,255,0.05)',
                                border: '1px solid rgba(255,255,255,0.1)',
                                borderRadius: 12,
                                color: 'white',
                                textDecoration: 'none',
                                fontSize: 14,
                                fontWeight: 500,
                                transition: 'all 0.3s'
                            }}
                        >
                            <Download style={{ width: 16, height: 16 }} />
                            下载 CSV
                        </a>
                    </div>
                </div>

                {/* Title */}
                <motion.div
                    initial={{ opacity: 0, y: 20 }}
                    animate={{ opacity: 1, y: 0 }}
                    style={{ marginBottom: 48 }}
                >
                    <span className="status-badge" style={{ marginBottom: 16, display: 'inline-flex', background: 'rgba(16,185,129,0.1)', borderColor: 'rgba(16,185,129,0.2)', color: '#10b981' }}>
                        <span className="status-dot" />
                        研究完成
                    </span>
                    <h1 style={{ fontSize: '2.5rem', fontWeight: 700, lineHeight: 1.3 }}>
                        {report.query}
                    </h1>
                </motion.div>

                {/* Comparison Table */}
                {comparisonTable && Object.keys(comparisonTable).length > 0 && (
                    <motion.div
                        initial={{ opacity: 0, y: 20 }}
                        animate={{ opacity: 1, y: 0 }}
                        transition={{ delay: 0.1 }}
                        className="glass-card"
                        style={{ padding: 32, marginBottom: 32, overflow: 'hidden' }}
                    >
                        <h2 style={{ fontSize: 20, fontWeight: 600, marginBottom: 24, display: 'flex', alignItems: 'center', gap: 10 }}>
                            <Table2 style={{ width: 22, height: 22, color: '#a78bfa' }} />
                            对比矩阵
                        </h2>

                        <div style={{ overflowX: 'auto' }}>
                            <table style={{ width: '100%', borderCollapse: 'collapse', fontSize: 14 }}>
                                <thead>
                                    <tr style={{ borderBottom: '1px solid rgba(255,255,255,0.1)' }}>
                                        <th style={{ padding: 16, textAlign: 'left', color: 'rgba(255,255,255,0.5)', fontWeight: 500, width: '20%' }}>
                                            维度
                                        </th>
                                        {Object.keys(Object.values(comparisonTable)[0] || {}).map((name) => (
                                            <th key={name} style={{ padding: 16, textAlign: 'left', fontWeight: 600, fontSize: 15 }}>
                                                {name}
                                            </th>
                                        ))}
                                    </tr>
                                </thead>
                                <tbody>
                                    {Object.entries(comparisonTable).map(([dimension, data]) => (
                                        <tr key={dimension} style={{ borderBottom: '1px solid rgba(255,255,255,0.05)' }}>
                                            <td style={{ padding: 16, color: 'rgba(255,255,255,0.5)', fontWeight: 500 }}>
                                                {dimension}
                                            </td>
                                            {Object.values(data || {}).map((value, j) => (
                                                <td key={j} style={{ padding: 16, color: 'rgba(255,255,255,0.8)' }}>
                                                    {typeof value === "string" && value.length > 80 ? (
                                                        <span title={value}>{value.slice(0, 80)}...</span>
                                                    ) : (
                                                        String(value || "—")
                                                    )}
                                                </td>
                                            ))}
                                        </tr>
                                    ))}
                                </tbody>
                            </table>
                        </div>
                    </motion.div>
                )}

                {/* Report Content */}
                <motion.div
                    initial={{ opacity: 0, y: 20 }}
                    animate={{ opacity: 1, y: 0 }}
                    transition={{ delay: 0.2 }}
                    className="glass-card"
                    style={{ padding: 48 }}
                >
                    <h2 style={{ fontSize: 20, fontWeight: 600, marginBottom: 32, display: 'flex', alignItems: 'center', gap: 10 }}>
                        <BookOpen style={{ width: 22, height: 22, color: '#a78bfa' }} />
                        详细报告
                    </h2>

                    <div
                        className="markdown-content"
                        style={{
                            fontSize: 15,
                            lineHeight: 1.8,
                            color: 'rgba(255,255,255,0.85)'
                        }}
                    >
                        {report.report_md ? (
                            <ReactMarkdown
                                remarkPlugins={[remarkGfm]}
                                components={{
                                    h1: ({ children }) => <h1 style={{ fontSize: 28, fontWeight: 700, marginTop: 40, marginBottom: 16, color: '#a78bfa' }}>{children}</h1>,
                                    h2: ({ children }) => <h2 style={{ fontSize: 22, fontWeight: 600, marginTop: 32, marginBottom: 12, color: '#a78bfa' }}>{children}</h2>,
                                    h3: ({ children }) => <h3 style={{ fontSize: 18, fontWeight: 600, marginTop: 24, marginBottom: 10 }}>{children}</h3>,
                                    p: ({ children }) => <p style={{ marginBottom: 16 }}>{children}</p>,
                                    ul: ({ children }) => <ul style={{ marginBottom: 16, paddingLeft: 24 }}>{children}</ul>,
                                    li: ({ children }) => <li style={{ marginBottom: 8 }}>{children}</li>,
                                    a: ({ children, href }) => <a href={href} style={{ color: '#60a5fa', textDecoration: 'underline' }}>{children}</a>,
                                    strong: ({ children }) => <strong style={{ fontWeight: 600, color: 'white' }}>{children}</strong>,
                                    blockquote: ({ children }) => (
                                        <blockquote style={{
                                            borderLeft: '3px solid #a78bfa',
                                            paddingLeft: 20,
                                            margin: '20px 0',
                                            color: 'rgba(255,255,255,0.7)',
                                            fontStyle: 'italic'
                                        }}>
                                            {children}
                                        </blockquote>
                                    ),
                                    table: ({ children }) => (
                                        <div style={{ overflowX: 'auto', marginBottom: 24 }}>
                                            <table style={{ width: '100%', borderCollapse: 'collapse', fontSize: 14 }}>
                                                {children}
                                            </table>
                                        </div>
                                    ),
                                    thead: ({ children }) => <thead>{children}</thead>,
                                    tbody: ({ children }) => <tbody>{children}</tbody>,
                                    tr: ({ children }) => <tr style={{ borderBottom: '1px solid rgba(255,255,255,0.1)' }}>{children}</tr>,
                                    th: ({ children }) => <th style={{ padding: 12, textAlign: 'left', fontWeight: 600, color: '#a78bfa', background: 'rgba(167,139,250,0.1)' }}>{children}</th>,
                                    td: ({ children }) => <td style={{ padding: 12, textAlign: 'left', color: 'rgba(255,255,255,0.85)' }}>{children}</td>,
                                }}
                            >
                                {report.report_md}
                            </ReactMarkdown>
                        ) : (
                            <div style={{
                                textAlign: 'center',
                                padding: '40px 20px',
                                background: 'rgba(239,68,68,0.1)',
                                borderRadius: 16,
                                border: '1px solid rgba(239,68,68,0.2)'
                            }}>
                                <div style={{ fontSize: 48, marginBottom: 16 }}>⚠️</div>
                                <h3 style={{ fontSize: 18, fontWeight: 600, color: '#ef4444', marginBottom: 12 }}>
                                    研究未能生成报告
                                </h3>
                                <p style={{ color: 'rgba(255,255,255,0.6)', marginBottom: 8, lineHeight: 1.6 }}>
                                    可能的原因：
                                </p>
                                <ul style={{
                                    color: 'rgba(255,255,255,0.5)',
                                    textAlign: 'left',
                                    display: 'inline-block',
                                    lineHeight: 1.8,
                                    paddingLeft: 20
                                }}>
                                    <li>搜索引擎未返回相关结果</li>
                                    <li>网络连接问题导致搜索失败</li>
                                    <li>相关网页无法访问（被屏蔽或403错误）</li>
                                </ul>
                                <div style={{ marginTop: 24 }}>
                                    <Link
                                        href="/"
                                        style={{
                                            display: 'inline-flex',
                                            alignItems: 'center',
                                            gap: 8,
                                            padding: '12px 24px',
                                            background: 'linear-gradient(135deg, #6366f1, #8b5cf6)',
                                            borderRadius: 12,
                                            color: 'white',
                                            textDecoration: 'none',
                                            fontWeight: 500,
                                            fontSize: 14
                                        }}
                                    >
                                        ← 返回重新搜索
                                    </Link>
                                </div>
                            </div>
                        )}
                    </div>
                </motion.div>
            </div>
        </main>
    );
}
