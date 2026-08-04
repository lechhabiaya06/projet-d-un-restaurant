// ----- Traduction -----
const btnLang = document.getElementById('lang');
const langues = ['fr', 'en', 'es'];
let indexLangue = 0;

btnLang.addEventListener('click', function() {
    indexLangue = (indexLangue + 1) % langues.length;
    const langueCourrante = langues[indexLangue];
    btnLang.textContent = langueCourrante.toUpperCase();
    const elements = document.querySelectorAll('[data-fr]');
    elements.forEach(function(el) {
        el.innerHTML = el.getAttribute('data-' + langueCourrante);
    });
});

// ----- Panier -----
let panier = [];

function afficherPanier() {
    const zone = document.getElementById('cart-items');
    const totalZone = document.getElementById('cart-total');
    zone.innerHTML = '';
    let total = 0;

    if (panier.length === 0) {
        zone.innerHTML = '<p>Votre panier est vide.</p>';
    }

    for (let i = 0; i < panier.length; i++) {
        const plat = panier[i];
        total = total + plat.prix;

        const ligne = document.createElement('div');
        ligne.className = 'cart-row';
        ligne.innerHTML =
            '<span>' + plat.nom + '</span>' +
            '<span>' + plat.prix.toFixed(2) + ' Dhs</span>' +
            '<button class="btn-remove" data-index="' + i + '">✕</button>';
        zone.appendChild(ligne);
    }

    totalZone.textContent = 'Total : ' + total.toFixed(2) + ' Dhs';
    document.getElementById('cart-count').textContent = panier.length;

    document.querySelectorAll('.btn-remove').forEach(function(bouton) {
        bouton.addEventListener('click', function() {
            const index = parseInt(bouton.getAttribute('data-index'));
            panier.splice(index, 1);
            afficherPanier();
        });
    });
}

document.querySelectorAll('.btn-add-cart').forEach(function(bouton) {
    bouton.addEventListener('click', function() {
        const plat = {
            id: bouton.getAttribute('data-id'),
            nom: bouton.getAttribute('data-nom'),
            prix: parseFloat(bouton.getAttribute('data-prix'))
        };
        panier.push(plat);
        afficherPanier();
    });
});
// Ouvrir/fermer la carte panier
const cartToggle = document.getElementById('cart-toggle');
const cartDropdown = document.getElementById('cart-dropdown');

cartToggle.addEventListener('click', function() {
    cartDropdown.classList.toggle('open');
});

// Valider la commande -> envoie au serveur Flask
const btnCommander = document.getElementById('btn-commander');
btnCommander.addEventListener('click', function() {
    if (panier.length === 0) {
        alert('Votre panier est vide.');
        return;
    }

    const formulaire = document.createElement('form');
    formulaire.method = 'POST';
    formulaire.action = '/commander';

    for (let i = 0; i < panier.length; i++) {
        const champ = document.createElement('input');
        champ.type = 'hidden';
        champ.name = 'plat_id';
        champ.value = panier[i].id;
        formulaire.appendChild(champ);
    }

    document.body.appendChild(formulaire);
    formulaire.submit();
});

afficherPanier();