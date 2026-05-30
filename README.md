# 🚛 NormanFleet — Plateforme de Pilotage de Flotte Industrielle

> **Digitalisation du suivi maintenance et pilotage opérationnel d'une flotte de 45 poids lourds en Normandie.**
> 
> Une stack moderne "Modern Data Stack" : **Python · dbt · DuckDB · Power BI · Power Platform**.

---

## 📝 Contexte

Une entreprise normande de transport industriel opère une flotte de **45 poids lourds** (Volvo, Renault Trucks, Mercedes, MAN, DAF) répartis sur 5 sites stratégiques : *Blainville-sur-Orne, Caen, Rouen, Le Havre, Cherbourg*.

Ce projet adresse trois enjeux majeurs :
1.  **Suivi Maintenance :** Centralisation de l'historique et alertes automatiques.
2.  **Pilotage Opérationnel :** Monitoring en temps réel de la disponibilité et de la consommation.
3.  **Saisie Terrain :** Application mobile pour la remontée d'incidents par les chauffeurs.

---

## 🏗️ Architecture du Pipeline

Le flux de données suit une logique **ELT** (Extract, Load, Transform) :

1.  **Ingestion (Python) :** 
    *   Source : Référentiel réel SDES (immatriculations PL France).
    *   Script : `pipeline/generate_data.py` (Génération via distributions Weibull/Normal).
    *   Output : 4 fichiers CSV bruts dans `data/raw/`.
2.  **Transformation (dbt + DuckDB) :**
    *   **Staging :** Nettoyage, renommage et typage des colonnes.
    *   **Marts :** Création des agrégats métier (KPIs maintenance, flotte, conso).
    *   Output : 6 fichiers CSV transformés dans `data/processed/`.
3.  **Visualisation (Power BI) :** 
    *   Dashboard 3 pages (Flotte, Maintenance, Consommation) connecté aux données traitées.
4.  **Automatisation (Power Platform) :**
    *   **Power Apps :** Mockup de saisie d'incidents (Fluent Design).
    *   **Power Automate :** Alerte email automatisée si `km_depuis_maintenance > 15 000 km`.

---

## 🛠️ Stack Technique

| Outil | Rôle |
| :--- | :--- |
| **Python 3.12** | Génération de données synthétiques (NumPy, Faker). |
| **dbt-duckdb** | Transformation, tests de qualité et documentation. |
| **DuckDB** | Base de données analytique OLAP (zéro infrastructure). |
| **Power BI** | Dataviz, modélisation en étoile et DAX. |
| **Power Platform** | Saisie mobile et alertes automatiques (Workflow). |

---

## 📊 Modèle de Données (Schéma en Étoile)

```text
Dimensions (Axes d'analyse)              Faits (Mesures)
---------------------------              ---------------

 [dim_vehicules] ------------------+     [fact_telemetrie]
 - vehicule_id (PK)                |     - telemetrie_id (PK)
 - immatriculation                 +---> - vehicule_id (FK)
 - marque / modele                 |     - km_jour / km_cumul
 - site_affectation                |     - consommation_l100
                                   |
 [dim_chauffeurs]                  |     [fact_interventions]
 - chauffeur_id (PK)               |     - intervention_id (PK)
 - nom / prenom                    +---> - vehicule_id (FK)
 - type_permis                     |     - type_intervention (Prev/Cur)
                                         - cout_eur / duree_heures
📈 KPIs Clés (Extrait du Dataset)
Indicateur	Valeur
Disponibilité Flotte	98,41% (Objectif > 95%)
Distance Totale	7,58 Millions km (sur 2 ans)
Consommation Moyenne	23,57 L/100 km
Ratio Préventif	73% (Indicateur d'une maintenance maîtrisée)
Coût Maintenance	525 244 €
🚀 Installation et Utilisation
code
Bash
# 1. Préparation de l'environnement
python -m venv .venv
source .venv/bin/activate
pip install -r requirements.txt

# 2. Génération du dataset (CSV raw)
python pipeline/generate_data.py

# 3. Exécution des transformations dbt
cd dbt_normanfleet
dbt run
dbt test
📂 Structure du Projet
code
Text
normanfleet/
├── data/
│   ├── raw/                # CSV sources bruts
│   └── processed/          # Exports dbt (consommés par PBI)
├── pipeline/
│   └── generate_data.py    # Générateur de données Python
├── dbt_normanfleet/        # Projet dbt (models staging & marts)
├── powerbi/
│   └── normanfleet.pbix    # Rapport Power BI Desktop
├── mockups/                # Fichiers Power Platform
├── docs/                   # Diagrammes BPMN, UML et Screenshots
└── README.md
👨‍💻 Auteur
Vanel Fokam
Licence Maths-Info · Université de Caen Normandie
Futur Ingénieur Data & IA · ISEN Caen (Sept. 2026)
![alt text](https://img.shields.io/badge/GitHub-Vanelfokamcode-blue?style=flat&logo=github)

