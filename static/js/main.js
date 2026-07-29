const btn = document.getElementById('lang');
const langues = ['fr', 'en', 'es'];
let indexLangue = 0;

btn.addEventListener('click', function() {
    indexLangue = (indexLangue + 1) % langues.length;
    const langueCourrante = langues[indexLangue];
    btn.textContent = langueCourrante.toUpperCase();

    const elements = document.querySelectorAll('[data-fr]');
    elements.forEach(function(el) {
       el.innerHTML  = el.getAttribute('data-' + langueCourrante);
    });
});