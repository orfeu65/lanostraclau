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
-- Ítems de la llista de sortida
-- -------------------------------------------------------------

INSERT INTO checklist_items (seccio, descripcio, es_opcional, ordre)
SELECT seccio, descripcio, es_opcional, ordre FROM (VALUES
    ('El mateix dia de la sortida', 'Exemple ítem 1', false, 10),
    ('El mateix dia de la sortida', 'Exemple ítem 2', false, 20),
    ('Just abans de sortir',        'Exemple ítem 3', false, 30)
) AS t(seccio, descripcio, es_opcional, ordre)
WHERE NOT EXISTS (SELECT 1 FROM checklist_items);


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
