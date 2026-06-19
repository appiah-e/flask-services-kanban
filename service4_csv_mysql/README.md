# Service 4 — Chargement CSV → MySQL

## Description

API REST Flask permettant de charger des données depuis un fichier CSV dans une table MySQL.
Ce service est le **fournisseur de données** pour le Service 3.
Port : **5004**

## Installation

```bash
cd service4_csv_mysql
python -m venv venv && source venv/bin/activate  # Linux/Mac
# ou : venv\Scripts\activate                     # Windows

pip install -r requirements.txt
```

## Configuration

Copiez `.env.example` en `.env` et renseignez vos identifiants MySQL :

```bash
cp .env.example .env
```

```env
DB_HOST=localhost
DB_PORT=3306
DB_USER=flask_user
DB_PASSWORD=votre_mot_de_passe
DB_NAME=flask_stats
```

> ⚠️ **Ne jamais committer le fichier `.env` dans Git.**

## Lancement

```bash
python app.py
```

---

## Routes disponibles

### POST /upload/csv

Charge un fichier CSV dans la table MySQL `donnees`.

**Corps de la requête :** `multipart/form-data` avec la clé `file`

**Colonnes obligatoires du CSV :** `nom_serie`, `valeur`  
**Colonnes optionnelles :** `categorie`, `date_mesure`

**Exemple avec curl :**
```bash
curl -X POST http://localhost:5004/upload/csv \
     -F 'file=@data/donnees_exemple.csv'
```

**Réponse 201 (succès) :**
```json
{
  "statut": "success",
  "lignes_inserees": 22,
  "lignes_invalides_ignorees": 0,
  "message": "22 ligne(s) chargée(s) dans la table donnees"
}
```

**Erreurs possibles :**
| Code | Situation |
|------|-----------|
| 400  | Fichier manquant, extension non `.csv`, colonnes obligatoires absentes, aucune ligne valide |
| 413  | Fichier > 5 Mo |
| 500  | Erreur de connexion MySQL |

---

### GET /upload/series

Retourne la liste des séries disponibles dans la base de données.

**Exemple avec curl :**
```bash
curl http://localhost:5004/upload/series
```

**Réponse 200 :**
```json
{
  "series": [
    { "serie": "serie_A", "n_points": 10, "debut": "2024-01-15", "fin": "2024-01-24" },
    { "serie": "serie_B", "n_points": 10, "debut": "2024-01-15", "fin": "2024-01-24" }
  ],
  "total": 2
}
```

---

### GET /health

Vérifie que le service et la connexion MySQL sont opérationnels.

```bash
curl http://localhost:5004/health
```

---

## Tests

### Client HTML interactif

Ouvrez `test_client.html` dans un navigateur. Il permet de tester toutes les routes via une interface graphique.

### Tests unitaires Python

```bash
# Avec le service Flask lancé dans un autre terminal :
python test_service4.py
```

---

## Format CSV attendu

| Colonne      | Type   | Obligatoire | Exemple      |
|--------------|--------|:-----------:|--------------|
| `nom_serie`  | Texte  | ✅           | `serie_A`    |
| `valeur`     | Nombre | ✅           | `12.50`      |
| `categorie`  | Texte  | ❌           | `temperature`|
| `date_mesure`| Date   | ❌           | `2024-01-15` |

- Séparateur : `,`
- Encodage : UTF-8
- Dates au format `YYYY-MM-DD`
- Valeurs décimales avec `.` (pas de virgule)
