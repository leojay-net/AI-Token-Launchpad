/** @type {import('tailwindcss').Config} */
module.exports = {
    content: [
        './pages/**/*.{js,ts,jsx,tsx,mdx}',
        './components/**/*.{js,ts,jsx,tsx,mdx}',
        './app/**/*.{js,ts,jsx,tsx,mdx}',
    ],
    theme: {
        extend: {
            colors: {
                gold: {
                    50: '#fefdf7',
                    100: '#fef7e0',
                    200: '#fdecc4',
                    300: '#fbdb9c',
                    400: '#f8c572',
                    500: '#f5b041',
                    600: '#e89611',
                    700: '#c2760c',
                    800: '#9b5e0f',
                    900: '#7c4e10',
                    950: '#472804',
                },
                neutral: {
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
                    950: '#0a0a0a',
                }
            },
            animation: {
                'fade-in': 'fadeIn 0.5s ease-in-out',
                'slide-up': 'slideUp 0.5s ease-out',
                'scale-in': 'scaleIn 0.3s ease-out',
                'float': 'float 3s ease-in-out infinite',
                'pulse-slow': 'pulse 3s cubic-bezier(0.4, 0, 0.6, 1) infinite',
            },
            keyframes: {
                fadeIn: {
                    '0%': { opacity: '0' },
                    '100%': { opacity: '1' },
                },
                slideUp: {
                    '0%': {
                        opacity: '0',
                        transform: 'translateY(20px)'
                    },
                    '100%': {
                        opacity: '1',
                        transform: 'translateY(0)'
                    },
                },
                scaleIn: {
                    '0%': {
                        opacity: '0',
                        transform: 'scale(0.95)'
                    },
                    '100%': {
                        opacity: '1',
                        transform: 'scale(1)'
                    },
                },
                float: {
                    '0%, 100%': { transform: 'translateY(0px)' },
                    '50%': { transform: 'translateY(-10px)' },
                },
            },
            boxShadow: {
                'gold': '0 4px 14px 0 rgba(245, 176, 65, 0.25)',
                'gold-lg': '0 10px 25px -3px rgba(245, 176, 65, 0.3), 0 4px 6px -2px rgba(245, 176, 65, 0.1)',
                'soft': '0 2px 8px 0 rgba(0, 0, 0, 0.05)',
                'medium': '0 4px 12px 0 rgba(0, 0, 0, 0.08)',
                'large': '0 8px 24px 0 rgba(0, 0, 0, 0.12)',
            },
        },
    },
    plugins: [],
}
