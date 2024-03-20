/** @type {import('tailwindcss').Config} */
module.exports = {
  content: ["./src/templates/**/*.html"],
  theme: {
    extend: {
      colors: {
        whatsapp: '#25D366',
        'whatsapp-dark': '#1e9e51', // A darker shade of the whatsapp color
        'whatsapp-blue': '#34B7F1',
        'whatsapp-blue-dark': '#009FEB'
      },
    },
  },
  plugins: [
    require('@tailwindcss/forms'),
    require('@tailwindcss/aspect-ratio'),
  ],
}

