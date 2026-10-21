# -*- coding: utf-8 -*-
"""
TP 02 Blockchain : Preuve d'enjeu (Proof of Stake)
Script principal executant l'ensemble de la simulation et des questions du TP :
  - Etapes 1 a 10 (R1 a R7)
  - Tests approfondis du reseau (Test 1 a 4)

Usage :
  python main.py
"""

import sys
import time
import random
import threading
import requests

RESEAU = "http://127.0.0.1:5000"


# =====================================================================
#  Lancement automatique du serveur en arriere-plan si non detecte
# =====================================================================

def verifier_et_lancer_serveur():
    try:
        r = requests.get(f"{RESEAU}/validateurs", timeout=0.8)
        print("[*] Serveur PoS deja actif sur", RESEAU)
        return
    except (requests.ConnectionError, requests.Timeout):
        pass

    print("[*] Serveur non detecte sur le port 5000. Lancement automatique via run_server...")
    import run_server
    import werkzeug.serving

    server_thread = threading.Thread(
        target=werkzeug.serving.run_simple,
        kwargs={"hostname": "127.0.0.1", "port": 5000, "application": run_server.Server.app},
        daemon=True
    )
    server_thread.start()

    for _ in range(15):
        time.sleep(0.2)
        try:
            requests.get(f"{RESEAU}/validateurs", timeout=0.5)
            print("[+] Serveur demarre avec succes !")
            return
        except (requests.ConnectionError, requests.Timeout):
            pass
    raise RuntimeError("Impossible de demarrer le serveur PoS sur " + RESEAU)


# =====================================================================
#  Fonctions utilitaires et regles du participant
# =====================================================================

def choisir_proposant(mises, tirage):
    """R2, chez le participant.
    
    Sur un segment de longueur mise_totale(mises), chaque validateur occupe
    un intervalle egal a sa mise. Avancer jusqu'a depasser le tirage.
    """
    cumul = 0.0
    for nom, mise in mises:
        cumul += mise
        if tirage <= cumul:
            return nom
    return mises[-1][0] if mises else None


def verifier_bloc(bloc):
    """R6 : le nom inscrit doit etre celui que le tirage designe."""
    return bloc["proposant"] == choisir_proposant(bloc["mises"], bloc["tirage"])


def verifier_chaine(chaine):
    """R6 : applique verifier_bloc a toute la chaine."""
    return [b["numero"] for b in chaine if not verifier_bloc(b)]


def parts(mises):
    """Part de chaque validateur dans la mise totale."""
    total = sum(m for _, m in mises)
    if total == 0:
        return {nom: 0.0 for nom, _ in mises}
    return {nom: 100.0 * m / total for nom, m in mises}


def afficher_parts(validateurs, chaine):
    """Tableau part de mise / part des blocs, avec barres de '#'."""
    total = sum(v["mise"] for v in validateurs)
    print(f"taille de la chaine : {len(chaine)}")
    print(f"{'Validateur':<10} {'Part de mise':>12} {'Part des blocs':>15}")
    for v in validateurs:
        part_m = (100.0 * v["mise"] / total) if total > 0 else 0.0
        part_b = (100.0 * v["blocs"] / len(chaine)) if len(chaine) > 0 else 0.0
        barre = "#" * int(part_b / 2)
        print(f"{v['nom']:<10} {part_m:>10.1f} % {part_b:>13.1f} %  {barre}")


# =====================================================================
#  Execution des etapes pas a pas
# =====================================================================

def run_simulation():
    print("=" * 70)
    print("TP 02 Blockchain : Preuve d'enjeu (Proof of Stake)")
    print("=" * 70)

    # -------------------------------------------------------------
    # Connexion & Reset
    # -------------------------------------------------------------
    print("\n--- Connexion & Reset ---")
    rep_reset = requests.post(RESEAU + "/reset").json()
    print("POST /reset ->", rep_reset)

    # -------------------------------------------------------------
    # Etape 1 : Rejoindre (R1)
    # -------------------------------------------------------------
    print("\n--- Etape 1 : Rejoindre (R1) ---")
    participants = [
        ("Idriss", 40),
        ("Moussa", 25),
        ("Youssef", 20),
        ("Ayoub", 15)
    ]
    for nom, mise in participants:
        res = requests.post(RESEAU + "/rejoindre", json={"nom": nom, "mise": mise})
        print(f"{res.status_code} {res.json()}")

    # Test R1 : rejet si mise < 10
    res_err = requests.post(RESEAU + "/rejoindre", json={"nom": "Tricheur", "mise": 5})
    print(f"Test mise invalide (< 10) : {res_err.status_code} {res_err.json()}")

    # -------------------------------------------------------------
    # Etape 2 : Les parts (R2)
    # -------------------------------------------------------------
    print("\n--- Etape 2 : Les parts (R2) ---")
    validateurs = requests.get(RESEAU + "/validateurs").json()
    total = sum(v["mise"] for v in validateurs)
    print(f"mise totale : {total:.0f} ETH")
    for v in validateurs:
        part_pct = 100.0 * v["mise"] / total
        print(f"{v['nom']:<10} {v['mise']:>5} ETH   {part_pct:5.1f} %")

    # -------------------------------------------------------------
    # Etape 3 : Le tirage (R2)
    # -------------------------------------------------------------
    print("\n--- Etape 3 : Le tirage (R2) ---")
    mises_actuelles = [(v["nom"], v["mise"]) for v in validateurs]
    for t in [52.3, 12.0, 95.5]:
        proposant = choisir_proposant(mises_actuelles, t)
        print(f"tirage = {t:<4} -> proposant : {proposant}")

    # -------------------------------------------------------------
    # Etape 4 : Un bloc (R3, R4)
    # -------------------------------------------------------------
    print("\n--- Etape 4 : Un bloc (R3, R4) ---")
    bloc1 = requests.post(RESEAU + "/produire_bloc", json={}).json()
    print("Bloc 1 produit :", bloc1)
    recalcul = choisir_proposant(bloc1["mises"], bloc1["tirage"])
    print(f"recalcul chez moi : {recalcul} (valide = {recalcul == bloc1['proposant']})")

    # -------------------------------------------------------------
    # Etape 5 : 14 blocs de plus (R3)
    # -------------------------------------------------------------
    print("\n--- Etape 5 : 14 blocs de plus (R3) ---")
    requests.post(RESEAU + "/produire_blocs", json={"n": 14})
    chaine = requests.get(RESEAU + "/chaine").json()
    print(f"{'Bloc':>4} {'Proposant':<9} {'Tirage':>6}")
    for b in chaine:
        print(f"{b['numero']:>4} {b['proposant']:<9} {b['tirage']:>6.2f}")

    # -------------------------------------------------------------
    # Etape 6 : Proportionnalite sur 5 000 blocs (R2)
    # -------------------------------------------------------------
    print("\n--- Etape 6 : Proportionnalite sur 5 000 blocs (R2) ---")
    requests.post(RESEAU + "/produire_blocs", json={"n": 5000})
    validateurs = requests.get(RESEAU + "/validateurs").json()
    chaine = requests.get(RESEAU + "/chaine").json()
    afficher_parts(validateurs, chaine)

    # -------------------------------------------------------------
    # Etape 7 : La recompense (R5)
    # -------------------------------------------------------------
    print("\n--- Etape 7 : La recompense (R5) ---")
    requests.post(RESEAU + "/reset")
    for nom, mise in participants:
        requests.post(RESEAU + "/rejoindre", json={"nom": nom, "mise": mise})

    depart = {v["nom"]: v["mise"] for v in requests.get(RESEAU + "/validateurs").json()}
    requests.post(RESEAU + "/produire_blocs", json={"n": 1000, "taux": 0.003})
    validateurs = requests.get(RESEAU + "/validateurs").json()

    total_d = sum(depart.values())
    total_f = sum(v["mise"] for v in validateurs)

    print(f"{'Validateur':<10} {'Mise depart':>11} {'Mise fin':>10} {'Part depart':>13} {'Part fin':>10} {'Blocs':>6}")
    for v in validateurs:
        nom = v["nom"]
        p_dep = 100.0 * depart[nom] / total_d
        p_fin = 100.0 * v["mise"] / total_f
        print(f"{nom:<10} {depart[nom]:>11.1f} {v['mise']:>10.1f} {p_dep:>11.1f} % {p_fin:>8.1f} % {v['blocs']:>6}")
    print(f"{'Reseau':<10} {total_d:>11.1f} {total_f:>10.1f}")

    print("\nFacteurs de multiplication :")
    print(f"{'Validateur':<10} {'Mise x':>8} {'Part depart -> Part fin':>25}")
    for v in validateurs:
        nom = v["nom"]
        facteur = v["mise"] / depart[nom]
        p_dep = 100.0 * depart[nom] / total_d
        p_fin = 100.0 * v["mise"] / total_f
        print(f"{nom:<10} {facteur:>8.2f} {p_dep:>10.1f} % -> {p_fin:>5.1f} %")
    print(f"{'Reseau':<10} {total_f / total_d:>8.2f}")

    # -------------------------------------------------------------
    # Etape 8 : Falsifier (R6)
    # -------------------------------------------------------------
    print("\n--- Etape 8 : Falsifier (R6) ---")
    requests.post(RESEAU + "/reset")
    for nom, mise in participants:
        requests.post(RESEAU + "/rejoindre", json={"nom": nom, "mise": mise})

    requests.post(RESEAU + "/produire_blocs", json={"n": 5})
    faux = requests.post(RESEAU + "/falsifier", json={"nom": "Ayoub"}).json()
    requests.post(RESEAU + "/produire_blocs", json={"n": 3})

    recalcul_faux = choisir_proposant(faux["mises"], faux["tirage"])
    print(f"bloc {faux['numero']} signe par {faux['proposant']} | tirage {faux['tirage']}")
    print(f"recalcul : {recalcul_faux}")

    # -------------------------------------------------------------
    # Etape 9 : Detecter (R6)
    # -------------------------------------------------------------
    print("\n--- Etape 9 : Detecter (R6) ---")
    chaine = requests.get(RESEAU + "/chaine").json()
    print(f"{'Bloc':>4} {'Signe par':<9} {'Tirage':>6} {'Recalcul':<9} {'Verdict'}")
    for b in chaine:
        recalc = choisir_proposant(b["mises"], b["tirage"])
        verdict = "ok" if verifier_bloc(b) else "FALSIFIE"
        print(f"{b['numero']:>4} {b['proposant']:<9} {b['tirage']:>6.2f} {recalc:<9} {verdict}")

    rep_serveur = requests.get(RESEAU + "/verifier").json()
    falsifies_locaux = verifier_chaine(chaine)
    print("reponse du reseau :", rep_serveur["blocs_falsifies"])
    print("recalcul local    :", falsifies_locaux)

    # -------------------------------------------------------------
    # Etape 10 : Sanctionner (R7)
    # -------------------------------------------------------------
    print("\n--- Etape 10 : Sanctionner (R7) ---")
    for numero in rep_serveur["blocs_falsifies"]:
        coupable = chaine[numero - 1]["proposant"]
        r = requests.post(RESEAU + "/sanctionner", json={"nom": coupable, "fraction": 0.5}).json()
        print(f"{coupable} : {r}")

    validateurs_apres = requests.get(RESEAU + "/validateurs").json()
    total_actif = sum(v["mise"] for v in validateurs_apres if not v["exclu"])
    print(f"mise totale apres exclusion : {total_actif:.1f} ETH")

    # =============================================================
    # Section 4 : Tests du reseau
    # =============================================================
    print("\n" + "=" * 70)
    print("Section 4 : Tests du reseau")
    print("=" * 70)

    # Test 1 : Tailles d'echantillon
    print("\n--- Test 1 : Taille d'echantillon (500 blocs vs 100 000 blocs) ---")
    for n_blocs in [500, 100000]:
        requests.post(RESEAU + "/reset")
        for nom, mise in participants:
            requests.post(RESEAU + "/rejoindre", json={"nom": nom, "mise": mise})
        requests.post(RESEAU + "/produire_blocs", json={"n": n_blocs})
        v_list = requests.get(RESEAU + "/validateurs").json()
        total_m = sum(v["mise"] for v in v_list)
        print(f"\nAvec {n_blocs} blocs :")
        print(f"{'Validateur':<10} {'Part de mise':>12} {'Part des blocs':>15}")
        for v in v_list:
            p_m = 100.0 * v["mise"] / total_m
            p_b = 100.0 * v["blocs"] / n_blocs
            barre = "#" * int(p_b / 2)
            print(f"{v['nom']:<10} {p_m:>10.1f} % {p_b:>13.1f} %  {barre}")

    # Test 2 : Arrivee de 3 validateurs
    print("\n--- Test 2 : Arrivee de 3 validateurs (5000 blocs) ---")
    requests.post(RESEAU + "/reset")
    participants_7 = participants + [
        ("Aymen", 100),
        ("Timan", 50),
        ("Meryem", 50)
    ]
    for nom, mise in participants_7:
        requests.post(RESEAU + "/rejoindre", json={"nom": nom, "mise": mise})
    requests.post(RESEAU + "/produire_blocs", json={"n": 5000})
    v_list = requests.get(RESEAU + "/validateurs").json()
    total_m = sum(v["mise"] for v in v_list)
    print(f"{'Validateur':<10} {'Part de mise':>12} {'Part des blocs':>15}")
    for v in v_list:
        p_m = 100.0 * v["mise"] / total_m
        p_b = 100.0 * v["blocs"] / 5000
        barre = "#" * int(p_b / 2)
        print(f"{v['nom']:<10} {p_m:>10.1f} % {p_b:>13.1f} %  {barre}")

    # Test 3 : Recompense plus forte (taux = 0.01)
    print("\n--- Test 3 : Recompense plus forte (taux = 0.01) ---")
    requests.post(RESEAU + "/reset")
    for nom, mise in participants:
        requests.post(RESEAU + "/rejoindre", json={"nom": nom, "mise": mise})
    dep3 = {v["nom"]: v["mise"] for v in requests.get(RESEAU + "/validateurs").json()}
    requests.post(RESEAU + "/produire_blocs", json={"n": 1000, "taux": 0.01})
    v3 = requests.get(RESEAU + "/validateurs").json()
    tot_d = sum(dep3.values())
    tot_f = sum(v["mise"] for v in v3)

    print(f"{'Validateur':<10} {'Mise depart':>11} {'Mise fin':>10} {'Part depart':>13} {'Part fin':>10} {'Blocs':>6}")
    for v in v3:
        nom = v["nom"]
        p_dep = 100.0 * dep3[nom] / tot_d
        p_fin = 100.0 * v["mise"] / tot_f
        print(f"{nom:<10} {dep3[nom]:>11.1f} {v['mise']:>10.1f} {p_dep:>11.1f} % {p_fin:>8.1f} % {v['blocs']:>6}")
    print(f"{'Reseau':<10} {tot_d:>11.1f} {tot_f:>10.1f}")

    # Test 4 : Tricheur habile (tirage truque dans l'intervalle d'Ayoub [85; 100])
    print("\n--- Test 4 : Tricheur habile (Ayoub choisit un tirage dans [85; 100]) ---")
    requests.post(RESEAU + "/reset")
    for nom, mise in participants:
        requests.post(RESEAU + "/rejoindre", json={"nom": nom, "mise": mise})

    random.seed(2)
    debut = 85
    fin = 100
    for i in range(400):
        if i % 4 == 0:
            tirage_truque = round(random.uniform(debut, fin), 2)
            requests.post(RESEAU + "/falsifier", json={"nom": "Ayoub", "tirage": tirage_truque})
        else:
            requests.post(RESEAU + "/produire_bloc", json={})

    rep4 = requests.get(RESEAU + "/verifier").json()
    print("blocs falsifies :", rep4["blocs_falsifies"])
    print(f"{'Validateur':<10} {'Part de mise':>12} {'Part des blocs':>15} {'Verdict':>10}")
    for f in rep4["frequences"]:
        verdict = "SUSPECT" if f["suspect"] else "normal"
        print(f"{f['nom']:<10} {f['part_mise']:>10.1f} % {f['part_blocs']:>13.1f} % {verdict:>10}")


if __name__ == "__main__":
    verifier_et_lancer_serveur()
    run_simulation()
