# -*- coding: utf-8 -*-
"""
Lanceur du serveur Flask pour le TP 02 Blockchain (Proof of Stake).
Charge Server.py (sans modifier le fichier d'origine) et injecte
les implementations des 4 fonctions TODO requises par le protocole PoS :
    1. choisir_proposant(mises, tirage)  [R2]
    2. recompenser(nom, taux)            [R5]
    3. verifier_bloc(bloc)               [R6]
    4. route_sanctionner()               [R7]
"""
import sys
from flask import request, jsonify
import Server


def choisir_proposant_pos(mises, tirage):
    """R2 : le validateur dont l'intervalle de mise contient le tirage.
    
    Sur un segment de longueur mise_totale(mises), chaque validateur occupe
    un intervalle egal a sa mise. Avancer mise par mise jusqu'a depasser le
    tirage : le validateur sur lequel on tombe est le proposant.
    """
    cumul = 0.0
    for nom, mise in mises:
        cumul += mise
        if tirage <= cumul:
            return nom
    return mises[-1][0] if mises else None


def recompenser_pos(nom, taux):
    """R5 : un bloc de plus au compteur, et la mise augmente de mise * taux.
    
    Chercher le validateur par son nom, incrementer son champ "blocs",
    puis augmenter sa mise de mise * taux. Les autres mises ne bougent pas.
    """
    for v in Server.validateurs:
        if v["nom"] == nom:
            v["blocs"] += 1
            v["mise"] += v["mise"] * taux
            return v["mise"]
    return 0.0


def verifier_bloc_pos(bloc):
    """R6 : rejoue le tirage du bloc et compare au nom inscrit.
    
    Le bloc contient "mises" et "tirage" : rappeler choisir_proposant avec
    ces deux valeurs donne le proposant attendu. Le bloc est valide si ce
    nom est bien celui inscrit dans le bloc.
    """
    attendu = choisir_proposant_pos(bloc["mises"], bloc["tirage"])
    return bloc["proposant"] == attendu


def route_sanctionner_pos():
    """R7 : confisque une part de la mise et exclut le validateur (slashing).
    
    Chercher le validateur par son nom. La perte vaut mise * fraction
    (fraction vaut 0.5 par defaut). Retirer cette perte de sa mise, puis
    passer son champ "exclu" a True : etat_des_mises l'ignorera desormais
    et il ne sera plus jamais tire.
    """
    data = request.get_json() or {}
    nom = data.get("nom")
    fraction = data.get("fraction", 0.5)

    for v in Server.validateurs:
        if v["nom"] == nom:
            perte = v["mise"] * fraction
            v["mise"] -= perte
            v["exclu"] = True
            return jsonify({
                "perte": perte,
                "mise_restante": v["mise"],
                "exclu": True
            })

    return jsonify({"erreur": "validateur inconnu"}), 404


# Injection propre dans le module Server
Server.choisir_proposant = choisir_proposant_pos
Server.recompenser = recompenser_pos
Server.verifier_bloc = verifier_bloc_pos

# Remplacement de la route /sanctionner
Server.app.view_functions["route_sanctionner"] = route_sanctionner_pos


def run(host="0.0.0.0", port=5000, debug=False):
    print(f"Serveur PoS pret sur http://{host}:{port}")
    Server.app.run(host=host, port=port, debug=debug)


if __name__ == "__main__":
    port = int(sys.argv[1]) if len(sys.argv) > 1 else 5000
    run(port=port)
