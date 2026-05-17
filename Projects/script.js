// 1. Récupération des tâches sauvegardées dans le navigateur
let donnees = localStorage.getItem("mesTaches");
let taches = [];
if (donnees !== null) {
    // JSON.parse transforme le texte sauvegardé en tableau
    taches = JSON.parse(donnees);
}
 
 
// 2. Sauvegarde du tableau dans le navigateur
function sauvegarder() {
    localStorage.setItem("mesTaches", JSON.stringify(taches));
}
 
 
// 3. Affichage de toutes les tâches
function afficherTaches() {
    let liste = document.getElementById("listeTaches");
    let html = "";
 
    for (let i = 0; i < taches.length; i++) {
        let t = taches[i];
 
        // On choisit la classe CSS selon le statut
        let classe = "statut-a-faire";
        if (t.statut === "en cours") classe = "statut-en-cours";
        if (t.statut === "terminée") classe = "statut-terminee";
 
        // On construit le HTML de la tâche en l'écrivant comme un texte
        html += "<li class='" + classe + "'>";
        html += "<strong>" + t.titre + "</strong>";
        html += "<p>" + t.description + "</p>";
        html += "<p class='date-tache'>📅 " + t.date + "</p>";
        html += "<p>Statut : " + t.statut + "</p>";
        html += "<button onclick='changerStatut(" + i + ")'>Changer statut</button> ";
        html += "<button class='btn-modifier' onclick='modifierTache(" + i + ")'>Modifier</button> ";
        html += "<button class='btn-delete' onclick='supprimerTache(" + i + ")'>Supprimer</button>";
        html += "</li>";
    }
 
    liste.innerHTML = html;
}
 
 
// 4. Changer le statut (à faire -> en cours -> terminée -> à faire ...)
function changerStatut(index) {
    if (taches[index].statut === "à faire") {
        taches[index].statut = "en cours";
    } else if (taches[index].statut === "en cours") {
        taches[index].statut = "terminée";
    } else {
        taches[index].statut = "à faire";
    }
    sauvegarder();
    afficherTaches();
}
 
 
// 5. Suppression d'une tâche
function supprimerTache(index) {
    // splice supprime 1 élément à la position "index"
    taches.splice(index, 1);
    sauvegarder();
    afficherTaches();
}
 
 
// 6. Modification d'une tâche (avec des fenêtres prompt)
function modifierTache(index) {
    let nouveauTitre = prompt("Nouveau titre :", taches[index].titre);
    if (nouveauTitre === null || nouveauTitre === "") return;
 
    let nouvelleDesc = prompt("Nouvelle description :", taches[index].description);
    if (nouvelleDesc === null) return;
 
    let nouvelleDate = prompt("Nouvelle date (AAAA-MM-JJ) :", taches[index].date);
    if (nouvelleDate === null) return;
 
    taches[index].titre = nouveauTitre;
    taches[index].description = nouvelleDesc;
    taches[index].date = nouvelleDate;
    sauvegarder();
    afficherTaches();
}
 
 
// 7. Tri des tâches (tri à bulles : on compare deux voisins et on échange si mal placés)
function trierTaches(critere) {
    for (let i = 0; i < taches.length; i++) {
        for (let j = 0; j < taches.length - 1; j++) {
            let echange = false;
            if (critere === "titre" && taches[j].titre > taches[j + 1].titre) echange = true;
            if (critere === "date" && taches[j].date > taches[j + 1].date) echange = true;
            if (critere === "statut" && taches[j].statut > taches[j + 1].statut) echange = true;
 
            if (echange === true) {
                let temp = taches[j];
                taches[j] = taches[j + 1];
                taches[j + 1] = temp;
            }
        }
    }
    sauvegarder();
    afficherTaches();
}
 
 
// 8. Bouton "Ajouter une tâche"
document.getElementById("ajouterTache").addEventListener("click", function() {
    let titre = document.getElementById("titreTache").value;
    let description = document.getElementById("taskDesc").value;
    let date = document.getElementById("dateTache").value;
 
    if (titre === "") {
        alert("Le titre est obligatoire !");
        return;
    }
 
    taches.push({
        titre: titre,
        description: description,
        date: date,
        statut: "à faire"
    });
 
    sauvegarder();
    afficherTaches();
 
    document.getElementById("titreTache").value = "";
    document.getElementById("taskDesc").value = "";
    document.getElementById("dateTache").value = "";
});
 
 
// 9. Menu de tri*
document.getElementById("triTaches").addEventListener("change", function() {
    trierTaches(this.value);
});
 
 
// 10. Affichage initial des tâches sauvegardées
afficherTaches();