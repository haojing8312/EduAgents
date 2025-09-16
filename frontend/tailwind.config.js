/** @type {import('tailwindcss').Config} */
module.exports = {
  content: [
    './src/pages/**/*.{js,ts,jsx,tsx,mdx}',
    './src/components/**/*.{js,ts,jsx,tsx,mdx}',
    './src/app/**/*.{js,ts,jsx,tsx,mdx}',
  ],
  theme: {
    extend: {
      colors: {
        // 主品牌色彩 - 量子蓝系列
        primary: {
          50: '#f0f7ff',   // 极浅蓝，背景使用
          100: '#e0efff',  // 浅蓝，面板背景
          200: '#b8deff',  // 淡蓝，卡片背景
          300: '#7cc7ff',  // 中浅蓝，次要元素
          400: '#36aeff',  // 标准蓝，交互元素
          500: '#0090ff',  // 主蓝，品牌主色
          600: '#0070f3',  // 深蓝，按钮默认
          700: '#0958d9',  // 较深蓝，按钮悬停
          800: '#1d39c4',  // 深蓝，文字链接
          900: '#1e2a78',  // 最深蓝，标题文字
          950: '#0f1419'   // 极深蓝，背景
        },

        // 智能体专属色彩系统
        agents: {
          // 教育理论专家 - 智慧紫
          theorist: {
            light: '#f3e8ff',
            main: '#8b5cf6',
            dark: '#6d28d9',
            contrast: '#ffffff'
          },
          // 课程架构师 - 结构橙
          architect: {
            light: '#fff7ed',
            main: '#f97316',
            dark: '#ea580c',
            contrast: '#ffffff'
          },
          // 内容设计师 - 创意绿
          designer: {
            light: '#ecfdf5',
            main: '#10b981',
            dark: '#047857',
            contrast: '#ffffff'
          },
          // 评估专家 - 洞察红
          assessor: {
            light: '#fef2f2',
            main: '#ef4444',
            dark: '#dc2626',
            contrast: '#ffffff'
          },
          // 素材创作者 - 灵感青
          creator: {
            light: '#f0fdfa',
            main: '#14b8a6',
            dark: '#0d9488',
            contrast: '#ffffff'
          }
        },

        // 功能色彩系统
        success: {
          50: '#f0fdf4',
          500: '#22c55e',
          700: '#15803d'
        },
        warning: {
          50: '#fffbeb',
          500: '#f59e0b',
          700: '#d97706'
        },
        error: {
          50: '#fef2f2',
          500: '#ef4444',
          700: '#dc2626'
        },
        info: {
          50: '#f0f9ff',
          500: '#3b82f6',
          700: '#1d4ed8'
        },

        // 中性色系统
        neutral: {
          0: '#ffffff',
          50: '#fafafa',
          100: '#f5f5f5',
          200: '#e5e5e5',
          300: '#d4d4d4',
          400: '#a3a3a3',
          500: '#737373',
          600: '#525252',
          700: '#404040',
          800: '#262626',
          900: '#171717',
          950: '#0a0a0a'
        },

        // 背景色系统
        background: {
          primary: 'var(--bg-primary)',
          secondary: 'var(--bg-secondary)',
          tertiary: 'var(--bg-tertiary)',
          elevated: 'var(--bg-elevated)',
          overlay: 'var(--bg-overlay)'
        },

        // 文字色系统
        text: {
          primary: 'var(--text-primary)',
          secondary: 'var(--text-secondary)',
          tertiary: 'var(--text-tertiary)',
          disabled: 'var(--text-disabled)',
          inverse: 'var(--text-inverse)'
        },

        // 边框色系统
        border: {
          primary: 'var(--border-primary)',
          secondary: 'var(--border-secondary)',
          focus: 'var(--border-focus)',
          error: 'var(--border-error)'
        }
      },

      // 字体系统
      fontFamily: {
        // 标题字体 - 科技感未来字体
        display: ['Inter', 'system-ui', 'sans-serif'],
        // 正文字体 - 高可读性
        body: ['Inter', 'system-ui', 'sans-serif'],
        // 等宽字体 - 代码和数据
        mono: ['JetBrains Mono', 'Fira Code', 'monospace'],
        // 中文字体优化
        chinese: ['Inter', 'PingFang SC', 'Microsoft YaHei', 'sans-serif']
      },

      // 字体大小层级
      fontSize: {
        // 显示级别 - 大标题
        'display-2xl': ['4.5rem', { lineHeight: '1.1', letterSpacing: '-0.02em' }],
        'display-xl': ['3.75rem', { lineHeight: '1.1', letterSpacing: '-0.02em' }],
        'display-lg': ['3rem', { lineHeight: '1.2', letterSpacing: '-0.02em' }],
        'display-md': ['2.25rem', { lineHeight: '1.2', letterSpacing: '-0.01em' }],
        'display-sm': ['1.875rem', { lineHeight: '1.3', letterSpacing: '-0.01em' }],

        // 标题级别
        'heading-xl': ['1.5rem', { lineHeight: '1.4', letterSpacing: '-0.01em' }],
        'heading-lg': ['1.25rem', { lineHeight: '1.4', letterSpacing: '-0.005em' }],
        'heading-md': ['1.125rem', { lineHeight: '1.5', letterSpacing: '-0.005em' }],
        'heading-sm': ['1rem', { lineHeight: '1.5' }],

        // 正文级别
        'body-xl': ['1.125rem', { lineHeight: '1.6' }],
        'body-lg': ['1rem', { lineHeight: '1.6' }],
        'body-md': ['0.875rem', { lineHeight: '1.6' }],
        'body-sm': ['0.75rem', { lineHeight: '1.6' }],

        // 标签级别
        'label-lg': ['0.875rem', { lineHeight: '1.4', letterSpacing: '0.01em' }],
        'label-md': ['0.75rem', { lineHeight: '1.4', letterSpacing: '0.01em' }],
        'label-sm': ['0.625rem', { lineHeight: '1.4', letterSpacing: '0.05em' }]
      },

      // 间距系统 - 8px基础单位
      spacing: {
        '0.5': '0.125rem',   // 2px
        '1': '0.25rem',      // 4px
        '1.5': '0.375rem',   // 6px
        '2': '0.5rem',       // 8px - 基础单位
        '2.5': '0.625rem',   // 10px
        '3': '0.75rem',      // 12px
        '4': '1rem',         // 16px
        '5': '1.25rem',      // 20px
        '6': '1.5rem',       // 24px
        '7': '1.75rem',      // 28px
        '8': '2rem',         // 32px
        '10': '2.5rem',      // 40px
        '12': '3rem',        // 48px
        '16': '4rem',        // 64px
        '20': '5rem',        // 80px
        '24': '6rem',        // 96px
        '32': '8rem',        // 128px
        '40': '10rem',       // 160px
        '48': '12rem',       // 192px
        '56': '14rem',       // 224px
        '64': '16rem'        // 256px
      },

      // 圆角系统
      borderRadius: {
        'none': '0px',
        'xs': '0.125rem',    // 2px
        'sm': '0.25rem',     // 4px
        'md': '0.375rem',    // 6px - 默认
        'lg': '0.5rem',      // 8px
        'xl': '0.75rem',     // 12px
        '2xl': '1rem',       // 16px
        '3xl': '1.5rem',     // 24px
        'full': '9999px'
      },

      // 阴影系统
      boxShadow: {
        'xs': '0 1px 2px 0 rgba(0, 0, 0, 0.05)',
        'sm': '0 1px 3px 0 rgba(0, 0, 0, 0.1), 0 1px 2px 0 rgba(0, 0, 0, 0.06)',
        'md': '0 4px 6px -1px rgba(0, 0, 0, 0.1), 0 2px 4px -1px rgba(0, 0, 0, 0.06)',
        'lg': '0 10px 15px -3px rgba(0, 0, 0, 0.1), 0 4px 6px -2px rgba(0, 0, 0, 0.05)',
        'xl': '0 20px 25px -5px rgba(0, 0, 0, 0.1), 0 10px 10px -5px rgba(0, 0, 0, 0.04)',
        '2xl': '0 25px 50px -12px rgba(0, 0, 0, 0.25)',
        'inner': 'inset 0 2px 4px 0 rgba(0, 0, 0, 0.06)',

        // 智能体协作特效阴影
        'glow-primary': '0 0 20px rgba(0, 144, 255, 0.3)',
        'glow-theorist': '0 0 20px rgba(139, 92, 246, 0.3)',
        'glow-architect': '0 0 20px rgba(249, 115, 22, 0.3)',
        'glow-designer': '0 0 20px rgba(16, 185, 129, 0.3)',
        'glow-assessor': '0 0 20px rgba(239, 68, 68, 0.3)',
        'glow-creator': '0 0 20px rgba(20, 184, 166, 0.3)'
      },

      // 动画系统
      animation: {
        // 基础动画
        'fade-in': 'fadeIn 0.3s ease-in-out',
        'fade-out': 'fadeOut 0.3s ease-in-out',
        'slide-up': 'slideUp 0.3s ease-out',
        'slide-down': 'slideDown 0.3s ease-out',
        'slide-left': 'slideLeft 0.3s ease-out',
        'slide-right': 'slideRight 0.3s ease-out',
        'scale-in': 'scaleIn 0.2s ease-out',
        'scale-out': 'scaleOut 0.2s ease-in',

        // 智能体协作动画
        'pulse-primary': 'pulse 2s cubic-bezier(0.4, 0, 0.6, 1) infinite',
        'float': 'float 3s ease-in-out infinite',
        'glow': 'glow 2s ease-in-out infinite alternate',
        'agent-enter': 'agentEnter 0.5s ease-out',
        'collaboration': 'collaboration 1s ease-in-out infinite',

        // 数据流动画
        'data-flow': 'dataFlow 2s linear infinite',
        'progress-bar': 'progressBar 1s ease-out',
        'typing': 'typing 1.5s steps(40) infinite'
      },

      // 断点系统
      screens: {
        'xs': '475px',
        'sm': '640px',
        'md': '768px',
        'lg': '1024px',
        'xl': '1280px',
        '2xl': '1536px',
        '3xl': '1920px'
      },

      // Z-index层级
      zIndex: {
        'modal': '1000',
        'dropdown': '100',
        'tooltip': '200',
        'navigation': '50',
        'overlay': '900',
        'notification': '1100'
      }
    },
  },
  plugins: [],
}