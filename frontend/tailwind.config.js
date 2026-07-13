const quizColors = {
  page: '#191919',
  header: '#06061b',
  nav: '#1f1c33',
  panel: '#0d0625',
  panelAlt: '#171036',
  panelDeep: '#08001d',
  field: '#c8c1c4',
  fieldText: '#171223',
  primary: '#4420c9',
  success: '#35bf24',
  successHover: '#3ed22b',
  danger: '#c62626',
  cyan: '#94e0e5',
  text: '#d8d5d9',
  muted: '#d8d4e9',
  label: '#8fa0bf',
  heading: '#dfdce8',
  description: '#aaa6b8',
  whiteSoft: '#f6f4f5',
  timer: '#ff3b31',
  selected: '#1de22c',
  gold: '#ffd51f',
  bronze: '#d66f00',
  profileCurrent: '#403c90',
  profileCurrentText: '#d8dcff',
  modalBg: '#c8ced8',
  modalText: '#15131d',
  historyButton: '#57508e'
};

export default {
  content: ['./index.html', './src/**/*.{js,jsx}'],
  theme: {
    extend: {
      colors: {
        quiz: quizColors
      },
      fontFamily: {
        quiz: ['Trebuchet MS', 'Arial', 'sans-serif']
      },
      backgroundImage: {
        'quiz-app': 'linear-gradient(180deg, rgba(6,6,27,0.98) 0 64px, transparent 64px), linear-gradient(180deg, #1f1c33 0%, #4f4a86 55%, #6760a8 100%)'
      },
      textShadow: {
        quiz: '1px 1px 0 #11101c, -1px -1px 0 #11101c, 1px -1px 0 #11101c, -1px 1px 0 #11101c'
      }
    }
  },
  plugins: [
    function ({ addUtilities, theme }) {
      addUtilities({
        '.text-shadow-quiz': {
          textShadow: theme('textShadow.quiz')
        }
      });
    }
  ]
};
