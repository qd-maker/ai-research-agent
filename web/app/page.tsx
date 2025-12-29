"use client";

import { motion } from "framer-motion";
import { Sparkles, ArrowRight, Zap, Search, Send } from "lucide-react";
import { useRouter } from "next/navigation";
import { useState } from "react";
import { api } from "@/services/api";

export default function Home() {
  const router = useRouter();
  const [query, setQuery] = useState("");
  const [isLoading, setIsLoading] = useState(false);
  const [isFocused, setIsFocused] = useState(false);

  const handleSubmit = async (e: React.FormEvent) => {
    e.preventDefault();
    if (!query.trim()) return;

    setIsLoading(true);
    try {
      const response = await api.createJob(query);
      router.push(`/jobs/${response.job_id}`);
    } catch (error) {
      console.error("Failed to create job:", error);
      setIsLoading(false);
    }
  };

  const suggestions = [
    { text: "飞书 vs Notion 对比", emoji: "📊" },
    { text: "2024年AI大模型市场", emoji: "🤖" },
    { text: "新能源汽车竞品分析", emoji: "🚗" }
  ];

  return (
    <main style={{
      minHeight: '100vh',
      display: 'flex',
      flexDirection: 'column',
      alignItems: 'center',
      justifyContent: 'center',
      padding: '40px 20px',
      background: 'linear-gradient(135deg, #0c0c1d 0%, #1a1a2e 50%, #16213e 100%)',
      position: 'relative',
      overflow: 'hidden'
    }}>
      {/* Animated Background Blobs */}
      <div style={{
        position: 'absolute',
        top: '-20%',
        right: '-10%',
        width: '600px',
        height: '600px',
        background: 'radial-gradient(circle, rgba(99,102,241,0.15) 0%, transparent 70%)',
        borderRadius: '50%',
        filter: 'blur(40px)',
        animation: 'pulse 8s ease-in-out infinite'
      }} />
      <div style={{
        position: 'absolute',
        bottom: '-20%',
        left: '-10%',
        width: '500px',
        height: '500px',
        background: 'radial-gradient(circle, rgba(139,92,246,0.12) 0%, transparent 70%)',
        borderRadius: '50%',
        filter: 'blur(40px)',
        animation: 'pulse 10s ease-in-out infinite reverse'
      }} />

      <style jsx global>{`
        @keyframes pulse {
          0%, 100% { transform: scale(1); opacity: 0.5; }
          50% { transform: scale(1.1); opacity: 0.7; }
        }
        @keyframes shimmer {
          0% { background-position: -200% center; }
          100% { background-position: 200% center; }
        }
      `}</style>

      {/* Content */}
      <div style={{ position: 'relative', zIndex: 10, width: '100%', maxWidth: '720px', textAlign: 'center' }}>

        {/* Badge */}
        <motion.div
          initial={{ opacity: 0, y: 20 }}
          animate={{ opacity: 1, y: 0 }}
          transition={{ duration: 0.5 }}
          style={{ marginBottom: '32px' }}
        >
          <span style={{
            display: 'inline-flex',
            alignItems: 'center',
            gap: '8px',
            padding: '10px 20px',
            background: 'linear-gradient(135deg, rgba(99,102,241,0.15), rgba(139,92,246,0.15))',
            border: '1px solid rgba(139,92,246,0.3)',
            borderRadius: '100px',
            fontSize: '14px',
            fontWeight: 500,
            color: '#a78bfa'
          }}>
            <Sparkles style={{ width: 16, height: 16 }} />
            AI 智能研究助手
          </span>
        </motion.div>

        {/* Title */}
        <motion.div
          initial={{ opacity: 0, y: 30 }}
          animate={{ opacity: 1, y: 0 }}
          transition={{ duration: 0.6, delay: 0.1 }}
          style={{ marginBottom: '48px' }}
        >
          <h1 style={{
            fontSize: 'clamp(2.5rem, 6vw, 4rem)',
            fontWeight: 700,
            lineHeight: 1.15,
            letterSpacing: '-0.03em',
            color: '#fff',
            marginBottom: '20px'
          }}>
            让深度研究
            <br />
            <span style={{
              background: 'linear-gradient(135deg, #818cf8, #a78bfa, #c084fc)',
              WebkitBackgroundClip: 'text',
              WebkitTextFillColor: 'transparent',
              backgroundClip: 'text'
            }}>
              自动化完成
            </span>
          </h1>
          <p style={{
            fontSize: '17px',
            color: 'rgba(255,255,255,0.55)',
            lineHeight: 1.7,
            maxWidth: '480px',
            margin: '0 auto'
          }}>
            输入任意主题，AI 自动规划、搜索、分析，
            <br />
            几分钟内生成专业研究报告
          </p>
        </motion.div>

        {/* Search Box - Premium Design */}
        <motion.form
          initial={{ opacity: 0, y: 30 }}
          animate={{ opacity: 1, y: 0 }}
          transition={{ duration: 0.6, delay: 0.2 }}
          onSubmit={handleSubmit}
          style={{ marginBottom: '40px' }}
        >
          <div style={{
            position: 'relative',
            background: isFocused
              ? 'linear-gradient(135deg, rgba(99,102,241,0.2), rgba(139,92,246,0.2))'
              : 'rgba(255,255,255,0.03)',
            borderRadius: '20px',
            padding: '4px',
            transition: 'all 0.4s ease',
            boxShadow: isFocused
              ? '0 0 60px rgba(99,102,241,0.2), 0 0 100px rgba(139,92,246,0.1)'
              : 'none'
          }}>
            <div style={{
              display: 'flex',
              alignItems: 'center',
              gap: '12px',
              padding: '8px 12px 8px 24px',
              background: 'rgba(15,15,35,0.9)',
              borderRadius: '16px',
              border: isFocused
                ? '1px solid rgba(139,92,246,0.4)'
                : '1px solid rgba(255,255,255,0.08)',
              transition: 'border 0.3s ease'
            }}>
              <Search style={{
                width: 22,
                height: 22,
                color: isFocused ? '#a78bfa' : 'rgba(255,255,255,0.3)',
                transition: 'color 0.3s ease'
              }} />
              <input
                type="text"
                value={query}
                onChange={(e) => setQuery(e.target.value)}
                onFocus={() => setIsFocused(true)}
                onBlur={() => setIsFocused(false)}
                placeholder="输入你想研究的主题..."
                disabled={isLoading}
                style={{
                  flex: 1,
                  background: 'transparent',
                  border: 'none',
                  outline: 'none',
                  fontSize: '17px',
                  color: '#fff',
                  padding: '16px 0',
                  fontFamily: 'inherit'
                }}
              />
              <button
                type="submit"
                disabled={isLoading || !query.trim()}
                style={{
                  display: 'flex',
                  alignItems: 'center',
                  justifyContent: 'center',
                  gap: '8px',
                  padding: '14px 28px',
                  background: query.trim()
                    ? 'linear-gradient(135deg, #6366f1, #8b5cf6)'
                    : 'rgba(255,255,255,0.1)',
                  border: 'none',
                  borderRadius: '12px',
                  color: query.trim() ? '#fff' : 'rgba(255,255,255,0.4)',
                  fontSize: '15px',
                  fontWeight: 600,
                  cursor: query.trim() && !isLoading ? 'pointer' : 'not-allowed',
                  transition: 'all 0.3s ease',
                  fontFamily: 'inherit',
                  boxShadow: query.trim()
                    ? '0 8px 30px rgba(99,102,241,0.3)'
                    : 'none'
                }}
              >
                {isLoading ? (
                  <div style={{
                    width: 20,
                    height: 20,
                    border: '2px solid rgba(255,255,255,0.3)',
                    borderTopColor: '#fff',
                    borderRadius: '50%',
                    animation: 'spin 0.8s linear infinite'
                  }} />
                ) : (
                  <>
                    开始研究
                    <Send style={{ width: 16, height: 16 }} />
                  </>
                )}
              </button>
            </div>
          </div>
        </motion.form>

        {/* Suggestions - Refined Tags */}
        <motion.div
          initial={{ opacity: 0 }}
          animate={{ opacity: 1 }}
          transition={{ duration: 0.5, delay: 0.4 }}
          style={{ marginBottom: '80px' }}
        >
          <p style={{
            fontSize: '13px',
            color: 'rgba(255,255,255,0.35)',
            marginBottom: '16px',
            textTransform: 'uppercase',
            letterSpacing: '0.1em'
          }}>
            热门研究
          </p>
          <div style={{ display: 'flex', flexWrap: 'wrap', gap: '12px', justifyContent: 'center' }}>
            {suggestions.map((item) => (
              <button
                key={item.text}
                type="button"
                onClick={() => setQuery(item.text)}
                style={{
                  display: 'flex',
                  alignItems: 'center',
                  gap: '8px',
                  padding: '12px 20px',
                  background: 'rgba(255,255,255,0.04)',
                  border: '1px solid rgba(255,255,255,0.08)',
                  borderRadius: '12px',
                  fontSize: '14px',
                  color: 'rgba(255,255,255,0.7)',
                  cursor: 'pointer',
                  transition: 'all 0.3s ease',
                  fontFamily: 'inherit'
                }}
                onMouseEnter={(e) => {
                  e.currentTarget.style.background = 'rgba(99,102,241,0.15)';
                  e.currentTarget.style.borderColor = 'rgba(99,102,241,0.3)';
                  e.currentTarget.style.color = '#fff';
                }}
                onMouseLeave={(e) => {
                  e.currentTarget.style.background = 'rgba(255,255,255,0.04)';
                  e.currentTarget.style.borderColor = 'rgba(255,255,255,0.08)';
                  e.currentTarget.style.color = 'rgba(255,255,255,0.7)';
                }}
              >
                <span>{item.emoji}</span>
                {item.text}
              </button>
            ))}
          </div>
        </motion.div>

        {/* Features Grid */}
        <motion.div
          initial={{ opacity: 0, y: 20 }}
          animate={{ opacity: 1, y: 0 }}
          transition={{ duration: 0.5, delay: 0.5 }}
          style={{
            display: 'grid',
            gridTemplateColumns: 'repeat(3, 1fr)',
            gap: '20px'
          }}
        >
          {[
            { icon: <Zap style={{ width: 24, height: 24 }} />, title: "智能规划", desc: "自动拆解研究维度", color: '#6366f1' },
            { icon: <Search style={{ width: 24, height: 24 }} />, title: "全网搜索", desc: "爬取多源数据", color: '#8b5cf6' },
            { icon: <Sparkles style={{ width: 24, height: 24 }} />, title: "AI 分析", desc: "生成结构化报告", color: '#a78bfa' }
          ].map((feature) => (
            <div
              key={feature.title}
              style={{
                padding: '28px 20px',
                background: 'rgba(255,255,255,0.02)',
                border: '1px solid rgba(255,255,255,0.06)',
                borderRadius: '20px',
                textAlign: 'center',
                transition: 'all 0.3s ease'
              }}
              onMouseEnter={(e) => {
                e.currentTarget.style.background = 'rgba(255,255,255,0.05)';
                e.currentTarget.style.borderColor = 'rgba(139,92,246,0.2)';
                e.currentTarget.style.transform = 'translateY(-4px)';
              }}
              onMouseLeave={(e) => {
                e.currentTarget.style.background = 'rgba(255,255,255,0.02)';
                e.currentTarget.style.borderColor = 'rgba(255,255,255,0.06)';
                e.currentTarget.style.transform = 'translateY(0)';
              }}
            >
              <div style={{
                width: 52,
                height: 52,
                borderRadius: 14,
                background: `rgba(${feature.color === '#6366f1' ? '99,102,241' : feature.color === '#8b5cf6' ? '139,92,246' : '167,139,250'},0.15)`,
                display: 'flex',
                alignItems: 'center',
                justifyContent: 'center',
                margin: '0 auto 16px',
                color: feature.color
              }}>
                {feature.icon}
              </div>
              <h3 style={{ fontSize: '16px', fontWeight: 600, marginBottom: '6px', color: '#fff' }}>
                {feature.title}
              </h3>
              <p style={{ fontSize: '13px', color: 'rgba(255,255,255,0.45)' }}>
                {feature.desc}
              </p>
            </div>
          ))}
        </motion.div>
      </div>
    </main>
  );
}
