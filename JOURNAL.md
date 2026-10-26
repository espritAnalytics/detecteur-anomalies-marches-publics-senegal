# Journal de décisions

Toute décision de modélisation, toute fusion d'identités arbitrée, toute limite
découverte, toute hypothèse écartée, tout changement de paramètre après un
premier lancement.

Au moment de rédiger la documentation finale, ce fichier en fournira l'essentiel.
C'est aussi lui, plus que le code, qui montre qu'il y a eu réflexion plutôt que
suivi de tutoriel.

**Format :** une entrée datée par décision. Contexte, décision, raison.

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
