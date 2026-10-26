# Journal de décisions

Toute décision de modélisation, toute fusion d'identités arbitrée, toute limite
découverte, toute hypothèse écartée, tout changement de paramètre après un
premier lancement.

Au moment de rédiger la documentation finale, ce fichier en fournira l'essentiel.
C'est aussi lui, plus que le code, qui montre qu'il y a eu réflexion plutôt que
suivi de tutoriel.

**Format :** une entrée datée par décision. Contexte, décision, raison.

---

## 2026-10-26 — Inventaire du fichier source

**Fichier.** 4 842 lignes, 13 colonnes, UTF-8, séparateur virgule.
SHA-256 `38d87d71…6866a6`. Période réelle 2010-01-04 à 2013-03-29.

**Bonne nouvelle.** Le fichier est bien plus riche qu'attendu : `code` est un
identifiant unique (4 842 / 4 842), `type` couvre exactement les quatre
catégories des seuils réglementaires, `entité` porte l'autorité contractante,
`mode` distingue seize procédures de passation, et `annee` donne l'exercice
budgétaire indépendamment de la date d'attribution.

**Trois découvertes qui modifient le plan.**

1. *Base fiscale mixte.* La colonne `taxes` vaut TTC pour 3 525 marchés,
   HD-HT pour 1 162, HT pour 146, HT/HD pour 7 et HD pour 2. Les seuils légaux
   s'expriment hors taxes. Comparer un montant TTC à un seuil HT le surestime
   d'environ 18 %. **Bloquant pour le test 2 tant que la règle de
   normalisation n'est pas arrêtée.**

2. *735 avenants (15,2 %).* `mode` contient « Avenant » et « Avenant de
   renouvellement ». Ce ne sont pas des marchés initiaux : leur montant n'est
   pas soumis au seuil de passation de la même façon. À exclure des tests 1, 2
   et 4. Ils constituent en revanche un sujet d'audit à part entière.

3. *L'exercice n'est pas l'année de la date.* L'exercice 2010 compte 958
   attributions datées de 2010, 201 de 2011 et 18 de 2012. Le décalage entre
   exercice et date d'attribution est lui-même un indicateur. Reste à décider
   lequel des deux définit la « fin d'exercice » du test 4.

**Autres constats.**
- 198 montants à exactement zéro, dont 188 avenants. Aucun montant négatif.
  À exclure de Benford (logarithme indéfini).
- Exercices complets exploitables : 2010, 2011, 2012. 2009 (115 marchés) et
  2013 (229) sont tronqués aux bornes du fichier.
- Médiane des montants : 48 055 525 FCFA, soit exactement la zone des seuils
  de 50 et 70 millions. La population est donc bien placée pour le test 2.
- Le préfixe de `code` encode le type (F, T, S, C). Six lignes présentent une
  incohérence préfixe / type : contrôle qualité gratuit.
- Deux formats de code coexistent : `F0009/10` jusqu'en 2012, `F/0001/13/SL`
  en 2013.
- 20 lignes sans devise, toutes de 2013, toutes avec un montant renseigné.
- Écart de 21 lignes entre les 4 863 annoncées et les 4 842 lues.
- La colonne `titre` contient des initiales de personnes physiques
  (« Mr T.L », « M. M.F et M.D.Y »). À ne pas republier telle quelle.

**Décisions prises.** `encodage` et `separateur` reportés dans
`config/params.yaml`, avec période réelle, volume réel et exercices complets.

---

## 2026-10-26 — La couche « analyse » renommée « analytique »

**Contexte.** `CREATE SCHEMA analyse` échoue : erreur de syntaxe.

**Cause.** `ANALYSE` (et `ANALYZE`) est un mot-clé réservé de PostgreSQL — c'est
la commande qui met à jour les statistiques du planificateur de requêtes.

**Décision.** Renommer la couche en `analytique` plutôt que de la mettre entre
guillemets doubles partout. Un identifiant entre guillemets devient sensible à
la casse et doit être cité dans chaque requête, chaque script et chaque
connexion d'outil — une nuisance permanente pour éviter un renommage de cinq
minutes.

**Portée.** `sql/00_schemas.sql` et `README.md`. Aucune donnée chargée à ce stade.

---

## 2026-10-26 — Mise en place de l'environnement

**Contexte.** Démarrage du projet.

**Décisions.**
- Architecture en trois couches (`brut`, `propre`, `analyse`), nommées dans
  l'esprit de dbt pour permettre une conversion ultérieure sans réécriture.
- Paramètres centralisés dans `config/params.yaml`, aucun seuil en dur.
- La couche brute conserve tous les champs en texte, plus le nom du fichier
  source et l'horodatage de chargement.
- Périmètre arrêté à quatre tests. Pas d'interface, pas de ML, pas de
  déploiement. Tableau de bord Power BI envisagé en extension, après publication.

**En suspens.**
- [ ] Vérifier les seuils de passation dans l'article 53 du Code des marchés
      publics et dans l'arrêté n° 007118 du 23 mars 2023. Les valeurs de
      `config/params.yaml` proviennent de sources secondaires et portent
      `verifie: false`. **Bloquant pour le test 2.**
- [ ] Confirmer la date exacte d'entrée en vigueur du relèvement des seuils de
      2014 — détermine le découpage des régimes.
- [ ] Déterminer les colonnes réellement présentes dans le fichier source, et si
      le type de marché (travaux / fournitures et services / prestations
      intellectuelles) y figure ou doit être dérivé de l'objet. **Si ce champ est
      absent, le test 2 perd sa maille principale.**
- [ ] Déterminer si un identifiant de fournisseur existe. À défaut, le
      rapprochement se fera sur le libellé, avec arbitrage manuel.

---

<!-- Nouvelles entrées au-dessus de cette ligne, les plus récentes en premier. -->
