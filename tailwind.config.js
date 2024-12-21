/** @type {import('tailwindcss').Config} */

const content = [
    './src/birdie_buddy/**/templates/**/*.html',
    './src/birdie_buddy/**/*.py',
    `${process.env.PYSITE_PACKAGES}/crispy_forms/**/*.html`,
    `${process.env.PYSITE_PACKAGES}/crispy_tailwind/**/*.html`,
]

console.log('watching content', content)

module.exports = {
    content,
    theme: {
        extend: {},
    },
    plugins: [
        require('@tailwindcss/forms'),
        require('@tailwindcss/typography'),
    ]
}

