# Détecteur d'anomalies — commande publique sénégalaise

Analyse des données ouvertes d'attribution de marchés publics sénégalais :
chargement en PostgreSQL, puis application de quatre tests d'audit destinés à
faire remonter des **atypies statistiques** dans les schémas d'attribution.

---

## 1. Cadre éthique

**Cette section est en première position parce qu'elle conditionne tout le reste.**

Ce projet produit des **signaux statistiques**, pas des constats. Un écart à une
distribution attendue n'établit aucun fait et n'a aucune valeur probante.

### Ce que la version publique présente

- La **méthode** : les tests, leurs paramètres, et surtout leurs limites.
- Des **résultats agrégés** : « la méthode identifie N schémas à investiguer
  sur M marchés », par catégorie et par exercice.
- Des **exemples anonymisés** lorsqu'une illustration est nécessaire.

### Ce qu'elle ne présente jamais

- Aucun nom d'entreprise ou d'autorité contractante présenté comme suspect.
- Aucune formulation s'apparentant à une accusation.

La raison est autant professionnelle que morale : une anomalie statistique n'est
pas une preuve, et un fractionnement apparent peut avoir une explication
parfaitement légitime — achats récurrents, marché spécialisé, contrainte
budgétaire. Un auditeur sérieux le sait. C'est cette prudence qui rend le travail
crédible, bien plus qu'une révélation spectaculaire.

### Vocabulaire

| À proscrire | À employer |
|---|---|
| fraude, irrégularité, suspect, corruption | atypie statistique, signal nécessitant investigation, écart à la distribution attendue |

---

## 2. La question posée

> Peut-on détecter automatiquement des schémas d'attribution atypiques dans les
> marchés publics, à partir des seules données ouvertes ?

---

## 3. Les données

| | |
|---|---|
| **Source** | Attributions de marchés publics du Sénégal, data.gouv.fr |
| **Origine** | Moissonnage de nosdonnees.fr, extrait du portail marchespublics.sn |
| **Période** | 2010-T1 à 2013-T1 (annoncé) |
| **Volume** | ~4 863 attributions (annoncé) |
| **Licence** | Open Database License (ODbL) |

### Limites connues de la source

- **Archive, non flux.** La fiche n'a pas été alimentée depuis 2013.
- **Couverture partielle.** Seuls les marchés effectivement publiés y figurent ;
  les marchés non publiés sont absents par construction, ce qui biaise
  mécaniquement toute mesure de concentration.
- **Deux régimes réglementaires.** La période couverte est à cheval sur la
  réforme des seuils de 2014. Le seuil applicable doit être résolu par date.
- **Changement institutionnel.** L'ARMP a été dissoute par la loi n° 2022-07 du
  19 avril 2022 et remplacée par l'**ARCOP**. Le code de 2014 a été remplacé par
  le décret n° 2022-2295. Les données portent l'ancienne dénomination.

---

## 4. La méthode

Quatre tests. Pour chacun, la limite compte autant que le résultat.

### Test 1 — Loi de Benford
Compare la distribution du premier chiffre significatif des montants à la
distribution théorique. Indicateur : écart absolu moyen de Nigrini.

> **Limite.** Benford ne s'applique pas à toutes les populations : elle suppose
> des montants étalés sur plusieurs ordres de grandeur, sans borne imposée. Un
> sous-ensemble délimité par un seuil de passation viole cette hypothèse. Il faut
> par ailleurs au moins 300 observations par groupe. Un écart ne prouve rien seul :
> c'est un indicateur d'orientation, pas une preuve.

### Test 2 — Fractionnement sous les seuils
Deux volets : les marchés isolés dont le montant tombe juste sous un seuil de
passation, et les groupes de marchés d'une même autorité vers un même
fournisseur sur une courte période dont le cumul dépasse ce seuil.

> **Limite.** Juridiquement, c'est le montant *estimé* au plan de passation qui
> déclenche l'obligation de procédure, pas le montant attribué. Le test travaille
> sur l'attribution, donc sur une approximation. Par ailleurs, des achats
> récurrents légitimes produisent naturellement le motif de groupement.

C'est le test le plus parlant et le plus défendable des quatre : il ne repose sur
aucune hypothèse statistique.

### Test 3 — Concentration de fournisseurs
Part des montants captée par un même fournisseur auprès d'une même autorité,
complétée d'un indice de Herfindahl par autorité.

> **Limite.** Une concentration élevée peut être parfaitement légitime : marché
> spécialisé, faible nombre de candidats qualifiés. Les autorités comptant moins
> de dix marchés sont exclues. **Signale, n'accuse pas.**

### Test 4 — Concentration en fin d'exercice
Part du montant annuel attribuée en décembre, par autorité.

> **Limite — la plus importante du lot.** La référence n'est **pas** un douzième
> par mois. La concentration de la dépense en fin d'exercice est systémique dans
> la dépense publique : toute la population est décalée vers décembre. Comparer à
> l'uniformité théorique signalerait l'intégralité des autorités et ne
> discriminerait rien. La seule référence valide est la **distribution empirique
> des autres autorités**.

### Règle commune aux quatre tests

Chaque test est paramétré dans `config/params.yaml`, **jamais en dur dans le
code**. Les paramètres se fixent **avant** le premier lancement : les ajuster
après avoir vu les résultats revient à choisir ses conclusions. Toute
modification postérieure est datée et justifiée dans `JOURNAL.md`.

Chaque test produit, en plus de son résultat agrégé, la **liste des lignes
concernées avec leur identifiant d'origine** dans la couche brute.

---

## 5. Les résultats

*(à compléter — agrégés, chiffrés, avec graphiques)*

---

## 6. Reproduire l'analyse

### Prérequis
- PostgreSQL 15 ou supérieur
- Python 3.10 ou supérieur

### Installation

```
git clone <url>
cd detecteur-anomalies

python -m venv .venv
.venv\Scripts\activate          # Windows
pip install -r requirements.txt

copy .env.example .env           # puis renseigner les identifiants
```

### Base de données

```
psql -U postgres -c "CREATE DATABASE marches_publics;"
psql -U postgres -d marches_publics -f sql/00_schemas.sql
```

### Chaîne complète

*(à compléter au fil des sprints)*

---

## 7. Architecture

```
config/     paramètres des tests et seuils réglementaires
data/brut/  fichier source téléchargé — non versionné
data/travail/ fichiers intermédiaires — non versionné
sql/        schémas et requêtes, par couche
src/        chargement, nettoyage, tests
tests/      tests unitaires des fonctions de nettoyage et de calcul
sorties/    graphiques et rapports générés — non versionné
docs/       documentation méthodologique
```

Trois couches dans la base, dans l'esprit de dbt :

| Couche | Contenu | Règle |
|---|---|---|
| `brut` | Copie fidèle du fichier source, tout en texte | On n'y touche plus jamais. C'est la piste d'audit. |
| `propre` | Types corrigés, montants numériques, dates normalisées, noms harmonisés | Une transformation par règle, documentée |
| `analytique` | Marchés enrichis du seuil applicable, agrégats par fournisseur et autorité | Consommable par les tests et la restitution |

**Pourquoi garder la couche brute intacte :** à tout moment on doit pouvoir
remonter d'un constat jusqu'à la ligne d'origine du fichier. Sans cela aucun
résultat n'est défendable, et c'est la première chose qu'un auditeur vérifie.

---

## 8. Périmètre

**Ce que ce projet ne fait pas :** pas d'interface web, pas de machine learning,
pas de déploiement. Le sujet est déjà assez riche. L'extension naturelle, une
fois l'analyse publiée, est un tableau de bord de restitution.

---

## Licence

Code sous licence MIT. Données sous ODbL, conformément à la source.
