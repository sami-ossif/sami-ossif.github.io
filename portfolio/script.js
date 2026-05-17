/* ===================================
   Portfolio Sami OSSIF — script.js
   =================================== */


// =====================================
// 1. Menu burger (responsive mobile)
// =====================================
const burger = document.getElementById("navBurger");
const navLinks = document.getElementById("navLinks");

burger.addEventListener("click", function() {
    navLinks.classList.toggle("open");
});

// Refermer le menu quand on clique sur un lien
const allLinks = navLinks.querySelectorAll("a");
for (let i = 0; i < allLinks.length; i++) {
    allLinks[i].addEventListener("click", function() {
        navLinks.classList.remove("open");
    });
}


// =====================================
// 2. Effet "machine à écrire" sur le hero
// =====================================
const roles = [
    "intégrateur web",
    "passionné de cyber",
    "auto-didacte",
    "étudiant au Cnam"
];

const typed = document.getElementById("typed");
let roleIndex = 0;
let charIndex = 0;
let isDeleting = false;

function type() {
    const currentRole = roles[roleIndex];

    if (isDeleting === false) {
        // On ajoute une lettre
        typed.textContent = currentRole.substring(0, charIndex + 1);
        charIndex = charIndex + 1;

        if (charIndex === currentRole.length) {
            // Mot complet : on attend puis on commence à effacer
            isDeleting = true;
            setTimeout(type, 1800);
            return;
        }
    } else {
        // On enlève une lettre
        typed.textContent = currentRole.substring(0, charIndex - 1);
        charIndex = charIndex - 1;

        if (charIndex === 0) {
            // Mot effacé : on passe au suivant
            isDeleting = false;
            roleIndex = roleIndex + 1;
            if (roleIndex >= roles.length) {
                roleIndex = 0;
            }
        }
    }

    // Vitesse différente selon écriture / effacement
    let vitesse = 90;
    if (isDeleting === true) vitesse = 40;
    setTimeout(type, vitesse);
}

// Démarrage de l'animation
type();


// =====================================
// 3. Animation à l'apparition (au scroll)
// =====================================
const sections = document.querySelectorAll(".section");
const cards = document.querySelectorAll(".skill-card, .project-card");

// On utilise IntersectionObserver — moderne et performant
const observer = new IntersectionObserver(function(entries) {
    for (let i = 0; i < entries.length; i++) {
        if (entries[i].isIntersecting === true) {
            entries[i].target.classList.add("visible");
            observer.unobserve(entries[i].target);
        }
    }
}, {
    threshold: 0.1
});

for (let i = 0; i < cards.length; i++) {
    cards[i].style.opacity = "0";
    cards[i].style.transform = "translateY(20px)";
    cards[i].style.transition = "opacity 0.6s ease, transform 0.6s ease";
    observer.observe(cards[i]);
}

// Quand la carte devient visible
const style = document.createElement("style");
style.textContent = `
.skill-card.visible, .project-card.visible {
    opacity: 1 !important;
    transform: translateY(0) !important;
}
`;
document.head.appendChild(style);


// =====================================
// 4. Highlight du lien actif dans la nav
// =====================================
const navItems = document.querySelectorAll(".nav-links a");
const allSections = document.querySelectorAll("section[id]");

window.addEventListener("scroll", function() {
    let current = "";

    for (let i = 0; i < allSections.length; i++) {
        const sectionTop = allSections[i].offsetTop - 100;
        if (window.scrollY >= sectionTop) {
            current = allSections[i].getAttribute("id");
        }
    }

    for (let i = 0; i < navItems.length; i++) {
        navItems[i].style.color = "";
        if (navItems[i].getAttribute("href") === "#" + current) {
            navItems[i].style.color = "var(--accent)";
        }
    }
});
