module.exports = {
  purge: [
    './templates/**/*.html',
    './static/js/**/*.js',
    './**/templates/**/*.html',
    './**/static/js/**/*.js',
    './node_modules/flowbite/**/*.js',
  ],
  darkMode: false, // or 'media' or 'class'
  theme: {
    extend: {},
  },
  variants: {
    extend: {},
  },
  plugins: [
    require('flowbite/plugin')
  ],
}