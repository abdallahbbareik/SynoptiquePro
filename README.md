# README - SynoptiquePro Plugin QGIS

## Description

SynoptiquePro est un plugin QGIS pour la génération **automatique** de synoptiques de câbles FTTH. Il automatise complètement le processus d'importation, d'analyse et de représentation des réseaux de câbles à partir de fichiers KMZ.

## Fonctionnalités principales

### 1. **Import KMZ**
- Importation automatique de fichiers KMZ
- Extraction des points, lignes et polygones
- Création de couches QGIS

### 2. **Analyse topologique**
- Construction du graphe réseau (NetworkX)
- Détection automatique des éléments (NRO, PM, PBO, chambres, clients)
- Identification des chemins principaux
- Calcul des distances

### 3. **Génération de synoptiques**
- Génération d'arbres hiérarchiques
- 3 styles différents: Arborescent, Détaillé, Hiérarchique
- Affichage des distances et des fibres
- Représentation ASCII intégrée

### 4. **Export multi-formats**
- **PDF**: Rapport professionnel avec diagramme ASCII
- **SVG**: Diagramme vectoriel interactif
- **Excel**: Tableau détaillé avec synthèse
- **Draw.io**: Diagramme éditable

## Installation

### Prérequis
- QGIS 3.16 ou supérieur
- Python 3.6+

### Étapes

1. Cloner le dépôt dans le dossier des plugins QGIS:
```bash
git clone https://github.com/abdallahbbareik/SynoptiquePro.git
```

2. Installer les dépendances Python:
```bash
pip install networkx reportlab openpyxl
```

3. Redémarrer QGIS

4. Activer le plugin dans QGIS: Extensions → Installer/Gérer les extensions

## Utilisation

### Flux de travail complet

1. **Onglet 1 - Import KMZ**
   - Sélectionner votre fichier KMZ
   - Cliquer sur "Importer le KMZ"

2. **Onglet 2 - Analyse**
   - Configurer la détection automatique
   - Cliquer sur "Lancer l'analyse"

3. **Onglet 3 - Synoptique**
   - Choisir le style
   - Cliquer sur "Générer le synoptique"

4. **Onglet 4 - Export**
   - Sélectionner les formats
   - Cliquer sur "Exporter"

## Structure du projet

```
SynoptiquePro/
├── __init__.py
├── synoptique_pro.py
├── metadata.txt
├── gui/
│   ├── main_dialog.py
│   ├── import_tab.py
│   ├── analysis_tab.py
│   ├── synoptique_tab.py
│   └── export_tab.py
├── core/
│   ├── project_manager.py
│   ├── kmz_importer.py
│   ├── network_analyzer.py
│   ├── synoptique_generator.py
│   └── exporters/
│       ├── pdf_exporter.py
│       ├── svg_exporter.py
│       ├── excel_exporter.py
│       └── drawio_exporter.py
└── resources/
    └── icon.png
```

## Licence

GPL-3.0

## Auteur

Abdallah Bbareik
