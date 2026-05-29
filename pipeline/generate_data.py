"""
NormanFleet — Chapitre 01
Génération des données synthétiques cohérentes
4 tables : dim_vehicules, dim_chauffeurs, fact_telemetrie, fact_interventions
"""

import numpy as np
import csv
import os
from datetime import date, timedelta
from faker import Faker

fake = Faker('fr_FR')
rng = np.random.default_rng(seed=42)

RAW_DIR = os.path.join(os.path.dirname(__file__), '..', 'data', 'raw')
os.makedirs(RAW_DIR, exist_ok=True)

# ─── REFERENTIEL VEHICULES (ancré sur données SDES PL France) ─────────────────
MARQUES = [
    ('Volvo',    'FH 500',    18000, 'diesel'),
    ('Volvo',    'FH 460',    18000, 'diesel'),
    ('Renault',  'T 480',     18000, 'diesel'),
    ('Renault',  'T 460',     18000, 'diesel'),
    ('Mercedes', 'Actros 5',  18000, 'diesel'),
    ('MAN',      'TGX 18.510',18000, 'diesel'),
    ('DAF',      'XF 480',    18000, 'diesel'),
    ('Volvo',    'FH Electric',18000,'electrique'),
    ('Renault',  'E-Tech T',  18000, 'electrique'),
]

SITES = ['Blainville-sur-Orne', 'Caen', 'Rouen', 'Le Havre', 'Cherbourg']

def generate_dim_vehicules(n=45):
    rows = []
    for i in range(1, n+1):
        m = MARQUES[rng.integers(0, len(MARQUES))]
        annee = int(rng.integers(2016, 2024))
        immat = f"NF-{i:03d}-PL"
        rows.append({
            'vehicule_id':    f"VH{i:03d}",
            'immatriculation': immat,
            'marque':         m[0],
            'modele':         m[1],
            'ptac_tonnes':    m[2],
            'motorisation':   m[3],
            'annee_mise_service': annee,
            'site_affectation': SITES[rng.integers(0, len(SITES))],
            'km_total_depart': int(rng.integers(20000, 180000)),
        })
    return rows

def generate_dim_chauffeurs(n=20):
    rows = []
    for i in range(1, n+1):
        rows.append({
            'chauffeur_id':   f"CH{i:03d}",
            'nom':            fake.last_name(),
            'prenom':         fake.first_name(),
            'permis_ce':      True,
            'anciennete_ans': int(rng.integers(1, 22)),
            'site':           SITES[rng.integers(0, len(SITES))],
        })
    return rows

def generate_fact_telemetrie(vehicules, n_days=730):
    rows = []
    start = date(2023, 1, 1)
    for v in vehicules:
        km_cumul = v['km_total_depart']
        for d in range(n_days):
            jour = start + timedelta(days=d)
            if jour.weekday() == 6:
                continue
            if jour.weekday() == 5 and rng.random() < 0.20:
                continue
            km_jour = max(0, int(rng.normal(280, 55)))
            conso_base = 32.0 if v['motorisation'] == 'diesel' else 0.0
            conso = round(max(0, rng.normal(conso_base, 3.5)), 1)
            km_cumul += km_jour
            statut = 'immobilise' if rng.random() < 0.015 else 'actif'
            rows.append({
                'telemetrie_id':  f"{v['vehicule_id']}-{jour.isoformat()}",
                'vehicule_id':    v['vehicule_id'],
                'date':           jour.isoformat(),
                'km_jour':        km_jour,
                'km_cumul':       km_cumul,
                'consommation_L100': conso if statut == 'actif' else 0.0,
                'statut':         statut,
            })
    return rows

def generate_fact_interventions(vehicules, telemetrie_rows):
    """
    Génère des interventions basées sur km_cumul.
    Distribution Weibull k=1.8, scale=80000 km entre pannes curatives.
    Préventive tous les 15000 km environ.
    """
    rows = []
    inter_id = 1

    TYPES_CURATIF   = ['Panne moteur', 'Crevaison', 'Défaillance électrique', 'Boîte de vitesses', 'Frein']
    TYPES_PREVENTIF = ['Vidange + filtres', 'Révision 15000 km', 'Contrôle freins', 'Remplacement pneus']
    TECHNICIENS     = ['Martin L.', 'Dubois P.', 'Bernard K.', 'Lefebvre T.', 'Simon R.']

    tele_by_veh = {}
    for r in telemetrie_rows:
        tele_by_veh.setdefault(r['vehicule_id'], []).append(r)

    for v in vehicules:
        tele = tele_by_veh.get(v['vehicule_id'], [])
        if not tele:
            continue

        km_next_prev = v['km_total_depart'] + int(rng.normal(15000, 1000))
        for t in tele:
            if t['km_cumul'] >= km_next_prev:
                rows.append({
                    'intervention_id':  f"INT{inter_id:04d}",
                    'vehicule_id':      v['vehicule_id'],
                    'date_intervention': t['date'],
                    'type_intervention': 'preventif',
                    'libelle':          TYPES_PREVENTIF[rng.integers(0, len(TYPES_PREVENTIF))],
                    'technicien':       TECHNICIENS[rng.integers(0, len(TECHNICIENS))],
                    'duree_heures':     round(rng.normal(2.5, 0.5), 1),
                    'cout_eur':         int(rng.normal(420, 80)),
                    'km_compteur':      t['km_cumul'],
                })
                inter_id += 1
                km_next_prev = t['km_cumul'] + int(rng.normal(15000, 1000))

        km_since = 0
        for t in tele:
            km_since += t['km_jour']
            seuil = int(rng.weibull(1.8) * 80000)
            seuil = max(40000, min(seuil, 160000))
            if km_since >= seuil:
                rows.append({
                    'intervention_id':  f"INT{inter_id:04d}",
                    'vehicule_id':      v['vehicule_id'],
                    'date_intervention': t['date'],
                    'type_intervention': 'curatif',
                    'libelle':          TYPES_CURATIF[rng.integers(0, len(TYPES_CURATIF))],
                    'technicien':       TECHNICIENS[rng.integers(0, len(TECHNICIENS))],
                    'duree_heures':     round(rng.normal(6.5, 2.0), 1),
                    'cout_eur':         int(rng.normal(1850, 450)),
                    'km_compteur':      t['km_cumul'],
                })
                inter_id += 1
                km_since = 0

    return rows

def write_csv(path, rows, fieldnames):
    with open(path, 'w', newline='', encoding='utf-8') as f:
        w = csv.DictWriter(f, fieldnames=fieldnames)
        w.writeheader()
        w.writerows(rows)
    print(f"  ✓ {os.path.basename(path)} — {len(rows)} lignes")

if __name__ == '__main__':
    print("NormanFleet — Génération des données")
    print("─" * 40)

    vehicules   = generate_dim_vehicules(45)
    chauffeurs  = generate_dim_chauffeurs(20)
    print(f"  → {len(vehicules)} véhicules · {len(chauffeurs)} chauffeurs générés")

    telemetrie  = generate_fact_telemetrie(vehicules, n_days=730)
    print(f"  → {len(telemetrie)} lignes télémétrie générées")

    interventions = generate_fact_interventions(vehicules, telemetrie)
    print(f"  → {len(interventions)} interventions générées")

    print("\nExport CSV → data/raw/")
    write_csv(f"{RAW_DIR}/dim_vehicules.csv",     vehicules,
        ['vehicule_id','immatriculation','marque','modele','ptac_tonnes',
         'motorisation','annee_mise_service','site_affectation','km_total_depart'])

    write_csv(f"{RAW_DIR}/dim_chauffeurs.csv",    chauffeurs,
        ['chauffeur_id','nom','prenom','permis_ce','anciennete_ans','site'])

    write_csv(f"{RAW_DIR}/fact_telemetrie.csv",   telemetrie,
        ['telemetrie_id','vehicule_id','date','km_jour','km_cumul',
         'consommation_L100','statut'])

    write_csv(f"{RAW_DIR}/fact_interventions.csv", interventions,
        ['intervention_id','vehicule_id','date_intervention','type_intervention',
         'libelle','technicien','duree_heures','cout_eur','km_compteur'])

    print("\n✅ Données générées dans data/raw/")
