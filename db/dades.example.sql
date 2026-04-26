-- =============================================================
-- La Nostra Clau — Dades inicials (EXEMPLE)
-- Supabase / PostgreSQL
--
-- Copia aquest fitxer com a dades.sql i omple els valors reals.
-- MAI pugis dades.sql al repositori (conté emails reals).
-- Script idempotent: cada INSERT comprova si les dades ja existeixen.
-- ATENCIÓ: cal executar schema.sql primer.
-- Per als usuaris: cal crear-los primer a Supabase Auth
--   (Authentication → Users → Add user)
-- =============================================================


-- -------------------------------------------------------------
-- Famílies
-- -------------------------------------------------------------

INSERT INTO families (nom, color)
SELECT * FROM (VALUES
    ('Família A', '#4CAF7D'),
    ('Família B', '#9B72CF'),
    ('Família C', '#F5C842')
) AS d(nom, color)
WHERE NOT EXISTS (SELECT 1 FROM families);


-- -------------------------------------------------------------
-- Seccions de la llista de sortida
-- -------------------------------------------------------------

INSERT INTO seccions_checklist (nom, icona, ordre)
SELECT nom, icona, ordre FROM (VALUES
    ('El mateix dia de la sortida', '🧹', 0),
    ('Just abans de sortir',        '👋', 1)
) AS d(nom, icona, ordre)
WHERE NOT EXISTS (SELECT 1 FROM seccions_checklist);


-- -------------------------------------------------------------
-- Ítems de la llista de sortida
-- -------------------------------------------------------------

INSERT INTO checklist_items (seccio_id, seccio, descripcio, es_opcional, ordre)
SELECT s.id, d.seccio, d.descripcio, d.es_opcional, d.ordre
FROM (VALUES
    ('El mateix dia de la sortida', 'Exemple ítem 1', false, 10),
    ('El mateix dia de la sortida', 'Exemple ítem 2', false, 20),
    ('Just abans de sortir',        'Exemple ítem 3', false, 30)
) AS d(seccio, descripcio, es_opcional, ordre)
JOIN seccions_checklist s ON s.nom = d.seccio
WHERE NOT EXISTS (SELECT 1 FROM checklist_items);

-- Migració: actualitzar seccio_id als ítems existents que no en tinguin
UPDATE checklist_items ci
SET seccio_id = sc.id
FROM seccions_checklist sc
WHERE ci.seccio = sc.nom
  AND ci.seccio_id IS NULL;


-- -------------------------------------------------------------
-- Tauler d'avisos (registre únic)
-- -------------------------------------------------------------

INSERT INTO avisos (text)
SELECT '' WHERE NOT EXISTS (SELECT 1 FROM avisos);


-- -------------------------------------------------------------
-- Usuaris
-- -------------------------------------------------------------

INSERT INTO usuaris (id, nom, email, familia_id, es_admin, actiu)
SELECT
    au.id,
    u.nom,
    u.email,
    f.id,
    u.es_admin::boolean,
    true
FROM (VALUES
    ('Admin',   'admin@example.com',   'Família A', 'true'),
    ('Usuari1', 'usuari1@example.com', 'Família A', 'false'),
    ('Usuari2', 'usuari2@example.com', 'Família B', 'false')
) AS u(nom, email, familia_nom, es_admin)
JOIN auth.users au ON au.email = u.email
JOIN families f    ON f.nom    = u.familia_nom
WHERE NOT EXISTS (SELECT 1 FROM usuaris WHERE usuaris.email = u.email);


-- -------------------------------------------------------------
-- Recursos (Drive i transport)
-- -------------------------------------------------------------

INSERT INTO recursos (titol, url, categoria, ordre)
SELECT titol, url, categoria, ordre FROM (VALUES
    ('Carpeta compartida', 'https://drive.google.com/...', 'drive', 0),
    ('Exemple transport',  'https://exemple.com',          'transport', 0)
) AS d(titol, url, categoria, ordre)
WHERE NOT EXISTS (SELECT 1 FROM recursos);


-- -------------------------------------------------------------
-- Subministres
-- -------------------------------------------------------------

INSERT INTO subministres (nom, empresa, telefon, url, notes, ordre)
SELECT nom, empresa, telefon, url, notes, ordre FROM (VALUES
    ('Aigua',       'Empresa A', '900 000 000', NULL,                   NULL, 0),
    ('Gas',         'Empresa B', '900 000 001', 'https://exemple.com',  NULL, 1),
    ('Llum',        'Empresa C', '900 000 002', 'https://exemple.com',  NULL, 2)
) AS d(nom, empresa, telefon, url, notes, ordre)
WHERE NOT EXISTS (SELECT 1 FROM subministres);


-- -------------------------------------------------------------
-- Acords entre famílies
-- -------------------------------------------------------------

INSERT INTO acords (titol, text, ordre)
SELECT titol, text, ordre FROM (VALUES
    ('Família A', 'Descripció de l''acord de la família A', 0),
    ('Família B', 'Descripció de l''acord de la família B', 1)
) AS d(titol, text, ordre)
WHERE NOT EXISTS (SELECT 1 FROM acords);
