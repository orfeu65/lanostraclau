-- =============================================================
-- La Nostra Clau — Dades inicials
-- Supabase / PostgreSQL
--
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
    ('Família Elisa',    '#4CAF7D'),
    ('Família Cristina', '#9B72CF'),
    ('Família Francesc', '#F5C842')
) AS d(nom, color)
WHERE NOT EXISTS (SELECT 1 FROM families);


-- -------------------------------------------------------------
-- Ítems de la llista de sortida
-- -------------------------------------------------------------

INSERT INTO checklist_items (seccio, descripcio, es_opcional, ordre)
SELECT seccio, descripcio, es_opcional, ordre FROM (VALUES
    ('El mateix dia de la sortida', 'Netejar, plegar, ordenar roba comuna (llançols, tovalloles)',                false,  10),
    ('El mateix dia de la sortida', 'Comprovar que no queda roba a l''assecadora o rentadora',                    false,  20),
    ('El mateix dia de la sortida', 'Endreçar totes les teves coses al teu armari',                               false,  30),
    ('El mateix dia de la sortida', 'Netejar el wc, la banyera, l''aigüera del lavabo',                           false,  40),
    ('El mateix dia de la sortida', 'Treure el que hi hagi al rentavaixelles i deixar-ho als armaris',            false,  50),
    ('El mateix dia de la sortida', 'Fregar i assecar olles/paelles i deixar-les endreçades',                     false,  60),
    ('El mateix dia de la sortida', 'Cuina: Netejar marbres i fogons',                                            false,  70),
    ('El mateix dia de la sortida', 'Buidar la nevera',                                                           false,  80),
    ('El mateix dia de la sortida', 'Deixar el toldo pujat i els pops a la vista al menjador',                    false,  90),
    ('El mateix dia de la sortida', 'Recollir i treure totes les escombraries',                                   false, 100),
    ('El mateix dia de la sortida', 'Passar l''escombra per tot el pis',                                          false, 110),
    ('Just abans de sortir',        'Obrir la porta de la nevera',                                                false, 120),
    ('Just abans de sortir',        'Baixar les persianes i tancar les finestres (inclòs safareig, excepte lavabo)', false, 130),
    ('Just abans de sortir',        'Totes les portes obertes',                                                   false, 140),
    ('Just abans de sortir',        'Tancar la clau de pas de l''aigua',                                          false, 150),
    ('Just abans de sortir',        'Tancar la clau de pas del gas',                                              false, 160),
    ('Just abans de sortir',        'Baixar tots els interruptors de la llum, al quadre de l''entrada',           false, 170),
    ('Just abans de sortir',        'Tancar amb clau',                                                            false, 180)
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
    ('Cristina', 'orfeu65@gmail.com',                    'Família Cristina', 'true'),
    ('Rosa',     'rosaramell@gmail.com',                  'Família Cristina', 'false'),
    ('Júlia',    'juliaperpinyaramell@gmail.com',         'Família Cristina', 'false'),
    ('Elisa',    'elisa121@martinezprocuradora.com',      'Família Elisa',    'false'),
    ('Alba',     'albamm121@gmail.com',                   'Família Elisa',    'false'),
    ('Francesc', 'francescmorama@gmail.com',              'Família Francesc', 'false'),
    ('Irina',    'nina.irina.2004@gmail.com',             'Família Francesc', 'false')
) AS u(nom, email, familia_nom, es_admin)
JOIN auth.users au ON au.email = u.email
JOIN families f    ON f.nom    = u.familia_nom
WHERE NOT EXISTS (SELECT 1 FROM usuaris WHERE usuaris.email = u.email);
