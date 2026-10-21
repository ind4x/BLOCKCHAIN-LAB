# -*- coding: utf-8 -*-
"""
TP 02 Blockchain : Preuve d'enjeu (Proof of Stake)
Le reseau. Un seul noeud le lance, tous les participants s'y connectent.

    pip install flask requests
    python Server.py

Quatre fonctions sont a ecrire, marquees TODO :
    choisir_proposant(mises, tirage)     R2
    recompenser(nom, taux)               R5
    verifier_bloc(bloc)                  R6
    route_sanctionner()                  R7

Le reste du fichier est donne.
"""
from flask import Flask, request, jsonify
import random

app = Flask(__name__)

MISE_MINIMALE = 10   # R1
GRAINE = 2           # pour que la simulation soit reproductible

validateurs = []     # {"nom": "Idriss", "mise": 40, "blocs": 0, "exclu": False}
chaine = []          # {"numero": 1, "proposant": "Ayoub", "tirage": 95.6, "mises": [...]}


# =====================================================================
#  Les regles
# =====================================================================

def etat_des_mises():
    """Photographie des mises des validateurs non exclus.

    Parametres : aucun
    Retour     : liste de couples (nom, mise)
    """
    mises = []
    for v in validateurs:
        if not v["exclu"]:
            mises.append((v["nom"], v["mise"]))
    return mises


def mise_totale(mises):
    """R2 : denominateur des probabilites.

    Parametres : mises (liste de couples (nom, mise))
    Retour     : float, la somme des mises
    """
    total = 0
    for nom, mise in mises:
        total = total + mise
    return total


def choisir_proposant(mises, tirage):
    """TODO 1 -- R2 : le validateur dont l'intervalle de mise contient le tirage.

    Sur un segment de longueur mise_totale(mises), chaque validateur occupe
    un intervalle egal a sa mise. Avancer mise par mise jusqu'a depasser le
    tirage : le validateur sur lequel on tombe est le proposant.

    Cette fonction doit etre pure : memes arguments -> meme resultat. C'est
    ce qui permet de recalculer le proposant d'un bloc deja ecrit (R4).

    Parametres : mises (liste de couples (nom, mise)), tirage (float)
    Retour     : str, le nom du proposant
    """
    ...


def recompenser(nom, taux):
    """TODO 2 -- R5 : un bloc de plus au compteur, et la mise augmente de taux.

    Chercher le validateur par son nom, incrementer son champ "blocs",
    puis augmenter sa mise de mise * taux. Les autres mises ne bougent pas.

    Parametres : nom (str), taux (float, ex. 0.003)
    Retour     : float, la nouvelle mise ; 0 si le nom est inconnu
    """
    ...


def nouveau_bloc(nom, tirage, mises):
    """R3 et R4 : un seul proposant, et le bloc garde son tirage.

    Parametres : nom (str), tirage (float), mises (liste de couples)
    Retour     : dict du bloc ajoute a la chaine
    """
    bloc = {"numero": len(chaine) + 1, "proposant": nom,
            "tirage": tirage, "mises": mises}
    chaine.append(bloc)
    return bloc


def verifier_bloc(bloc):
    """TODO 3 -- R6 : rejoue le tirage du bloc et compare au nom inscrit.

    Le bloc contient "mises" et "tirage" : rappeler choisir_proposant avec
    ces deux valeurs donne le proposant attendu. Le bloc est valide si ce
    nom est bien celui inscrit dans le bloc.

    Parametres : bloc (dict : numero, proposant, tirage, mises)
    Retour     : bool, True si le bloc est valide
    """
    ...


# =====================================================================
#  Les routes
# =====================================================================

@app.route("/reset", methods=["POST"])
def route_reset():
    """Vide le reseau et reseme le generateur.

    Corps JSON : aucun
    Retour     : {"message": str}
    """
    validateurs.clear()
    chaine.clear()
    random.seed(GRAINE)
    return jsonify({"message": "reseau vide, graine " + str(GRAINE)})


@app.route("/rejoindre", methods=["POST"])
def route_rejoindre():
    """R1 : refuse une mise inferieure a MISE_MINIMALE.

    Corps JSON : {"nom": str, "mise": float}
    Retour     : {"validateur": dict, "mise_totale": float}
                 code 400 si mise < MISE_MINIMALE
    """
    data = request.get_json()
    if data["mise"] < MISE_MINIMALE:
        return jsonify({"erreur": "mise inferieure a " + str(MISE_MINIMALE)}), 400
    v = {"nom": data["nom"], "mise": data["mise"], "blocs": 0, "exclu": False}
    validateurs.append(v)
    return jsonify({"validateur": v, "mise_totale": mise_totale(etat_des_mises())})


@app.route("/validateurs", methods=["GET"])
def route_validateurs():
    """Corps JSON : aucun
    Retour       : liste de dict (nom, mise, blocs, exclu)
    """
    return jsonify(validateurs)


@app.route("/chaine", methods=["GET"])
def route_chaine():
    """Corps JSON : aucun
    Retour       : liste des blocs
    """
    return jsonify(chaine)


@app.route("/produire_bloc", methods=["POST"])
def route_produire_bloc():
    """R3 et R4 : tire, designe, enregistre, recompense.

    Corps JSON : {"taux": float}  (facultatif, defaut 0)
    Retour     : le bloc produit, tirage et mises inclus
                 code 400 si aucun validateur actif
    """
    mises = etat_des_mises()
    if len(mises) == 0:
        return jsonify({"erreur": "aucun validateur"}), 400
    taux = request.get_json().get("taux", 0)
    tirage = round(random.uniform(0, mise_totale(mises)), 2)
    nom = choisir_proposant(mises, tirage)
    bloc = nouveau_bloc(nom, tirage, mises)
    recompenser(nom, taux)
    return jsonify(bloc)


@app.route("/produire_blocs", methods=["POST"])
def route_produire_blocs():
    """Corps JSON : {"n": int, "taux": float}
    Retour       : {"blocs_produits": int, "taille_chaine": int}
    """
    data = request.get_json()
    taux = data.get("taux", 0)
    for i in range(data["n"]):
        mises = etat_des_mises()
        tirage = round(random.uniform(0, mise_totale(mises)), 2)
        nom = choisir_proposant(mises, tirage)
        nouveau_bloc(nom, tirage, mises)
        recompenser(nom, taux)
    return jsonify({"blocs_produits": data["n"], "taille_chaine": len(chaine)})


@app.route("/falsifier", methods=["POST"])
def route_falsifier():
    """R6, pour les besoins du TP : ecrit un bloc sans passer par R2.

    Sans "tirage", le reseau en tire un et le nom ne correspondra pas.
    Avec "tirage", le tricheur le choisit lui-meme.

    Corps JSON : {"nom": str, "tirage": float}  (tirage facultatif)
    Retour     : le bloc ecrit
    """
    data = request.get_json()
    mises = etat_des_mises()
    nom = data["nom"]
    tirage = data.get("tirage")
    if tirage is None:
        tirage = round(random.uniform(0, mise_totale(mises)), 2)
    bloc = nouveau_bloc(nom, tirage, mises)
    recompenser(nom, 0)
    return jsonify(bloc)


@app.route("/verifier", methods=["GET"])
def route_verifier():
    """R6 : les blocs incoherents, puis les frequences de production.

    Corps JSON : aucun
    Retour     : {"blocs_falsifies": [int],
                  "frequences": [{"nom": str, "part_mise": float,
                                  "part_blocs": float, "suspect": bool}]}
    """
    falsifies = []
    for bloc in chaine:
        if not verifier_bloc(bloc):
            falsifies.append(bloc["numero"])
    mises = etat_des_mises()
    total = mise_totale(mises)
    compte = {}
    for nom, mise in mises:
        compte[nom] = 0
    for bloc in chaine:
        if bloc["proposant"] in compte:
            compte[bloc["proposant"]] = compte[bloc["proposant"]] + 1
    frequences = []
    for nom, mise in mises:
        attendu = 100 * mise / total
        observe = 100 * compte[nom] / len(chaine)
        frequences.append({"nom": nom, "part_mise": attendu,
                           "part_blocs": observe,
                           "suspect": observe - attendu > 3.0})
    return jsonify({"blocs_falsifies": falsifies, "frequences": frequences})


@app.route("/sanctionner", methods=["POST"])
def route_sanctionner():
    """TODO 4 -- R7 : confisque une part de la mise et exclut le validateur.

    Chercher le validateur par son nom. La perte vaut mise * fraction
    (fraction vaut 0.5 par defaut). Retirer cette perte de sa mise, puis
    passer son champ "exclu" a True : etat_des_mises l'ignorera desormais
    et il ne sera plus jamais tire.

    Corps JSON : {"nom": str, "fraction": float}  (fraction facultative)
    Retour     : {"perte": float, "mise_restante": float, "exclu": True}
                 code 404 si le nom est inconnu
    """
    ...


if __name__ == "__main__":
    app.run(host="0.0.0.0", port=5000)
