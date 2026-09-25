/** @type {import('tailwindcss').Config} */
export default {
  content: ['./index.html', './src/**/*.{vue,js,ts,jsx,tsx}'],
  theme: {
    extend: {
      colors: {
        text: {
          primary: '#111827',
          secondary: '#4B5563',
          placeholder: '#9CA3AF',
          link: '#1A7FD4',
          'on-dark': '#FFFFFF',
          'sidebar-muted': '#C2DEFA',
        },

        border: {
          default: '#E2E8F0',
          brand: '#C2DEFA',
          focus: '#1A7FD4',
        },

        status: {
          delivered: '#16A34A',
          'delivered-bg': '#F0FDF4',
          'in-transit': '#1A7FD4',
          'in-transit-bg': '#EBF4FD',
          loaded: '#9CA3AF',
          'loaded-bg': '#F3F4F6',
          delayed: '#DC2626',
          'delayed-bg': '#FEF2F2',
          pending: '#D97706',
          'pending-bg': '#FFFBEB',
        },

        btn: {
          primary: {
            default: '#1A7FD4',
            hover: '#1465B0',
            pressed: '#0D4C8A',
            disabled: '#90C4F5',
          },
          secondary: {
            default: '#EBF4FD',
            hover: '#C2DEFA',
          },
        },

        chart: {
          'line-primary': '#1A7FD4',
          'area-fill': '#EBF4FD',
          'grid-line': '#E8EFF6',
          'axis-label': '#9CA3AF',
        },

        brand: {
          primary: '#1A7FD4',
          dark: '#1465B0',
          light: '#5BA5ED',
          subtle: '#EBF4FD',
        },
        bg: {
          canvas: '#FFFFFF',
          surface: '#F4F7FA',
          sidebar: '#0D4C8A',
          'sidebar-active': '#083672',
          'surface-raised': '#E8EFF6',
        },
      },
      fontFamily: {
        roboto: ['Roboto', 'sans-serif'],
      },
    },
  },
  plugins: [],
}
