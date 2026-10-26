-- =============================================================================
-- 00_schemas.sql — création des trois couches et des extensions
-- =============================================================================
-- À exécuter une fois, sur une base vide :
--   psql -U postgres -c "CREATE DATABASE marches_publics;"
--   psql -U postgres -d marches_publics -f sql/00_schemas.sql
-- =============================================================================

-- --- Extensions --------------------------------------------------------------
-- unaccent : suppression des accents pour normaliser les libellés
-- pg_trgm  : similarité textuelle, pour rapprocher les graphies d'un même
--            fournisseur (« ETS MAMADOU DIOP » / « Ets. M. Diop SARL »)
CREATE EXTENSION IF NOT EXISTS unaccent;
CREATE EXTENSION IF NOT EXISTS pg_trgm;


-- --- Couches -----------------------------------------------------------------
CREATE SCHEMA IF NOT EXISTS brut;
CREATE SCHEMA IF NOT EXISTS propre;
CREATE SCHEMA IF NOT EXISTS analytique;

COMMENT ON SCHEMA brut IS
  'Copie fidèle du fichier source, tous champs en texte. Jamais modifiée après '
  'chargement : c''est la piste d''audit qui permet de remonter d''un constat '
  'jusqu''à la ligne d''origine.';

COMMENT ON SCHEMA propre IS
  'Types corrigés, montants numériques, dates normalisées, libellés harmonisés. '
  'Une transformation par règle, chacune documentée dans JOURNAL.md.';

COMMENT ON SCHEMA analytique IS
  'Marchés enrichis du seuil applicable et agrégats par fournisseur et autorité. '
  'Couche consommée par les tests et par la restitution.';


-- --- Journal de chargement ---------------------------------------------------
-- Trace chaque chargement de fichier : indispensable pour la preuve
-- d'exhaustivité et pour savoir quelle version des données a produit
-- quel résultat.
CREATE TABLE IF NOT EXISTS brut.chargement (
  chargement_id     bigserial PRIMARY KEY,
  fichier           text        NOT NULL,
  empreinte_sha256  text        NOT NULL,
  charge_le         timestamptz NOT NULL DEFAULT now(),
  lignes_fichier    integer,
  lignes_inserees   integer,
  encodage          text,
  separateur        text,
  commentaire       text
);

COMMENT ON TABLE brut.chargement IS
  'Un enregistrement par chargement de fichier source. L''empreinte permet de '
  'détecter qu''une source a changé entre deux exécutions.';


-- --- Preuve d'exhaustivité ---------------------------------------------------
-- Rapprochement entre le fichier et la base, à remplir après chaque
-- chargement. Tout écart doit être expliqué par écrit : c'est la première
-- chose qu'un auditeur expérimenté vérifie.
CREATE TABLE IF NOT EXISTS brut.controle_exhaustivite (
  controle_id      bigserial PRIMARY KEY,
  chargement_id    bigint      NOT NULL REFERENCES brut.chargement(chargement_id),
  mesure           text        NOT NULL,   -- 'nombre_lignes', 'somme_montants',
                                           -- 'date_min', 'date_max'
  valeur_fichier   text,
  valeur_base      text,
  ecart            text,
  explication      text,                   -- obligatoire si écart non nul
  controle_le      timestamptz NOT NULL DEFAULT now()
);

COMMENT ON TABLE brut.controle_exhaustivite IS
  'Rapprochement fichier / base après chargement. Un écart sans explication '
  'écrite invalide l''ensemble des résultats qui en découlent.';
