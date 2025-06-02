// import tailwindcss from '@tailwindcss/postcss';

// export default {
//   plugins: [
//     tailwindcss(),
//     require('autoprefixer')
//   ]
// }
const tailwindcss = require('@tailwindcss/postcss');
const autoprefixer = require('autoprefixer');

module.exports = {
  plugins: [
    tailwindcss(),
    autoprefixer,
  ]
}
