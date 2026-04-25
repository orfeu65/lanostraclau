-- =============================================================
-- La Nostra Clau — Esquema de la base de dades
-- Supabase / PostgreSQL
--
-- Script idempotent: es pot executar més d'una vegada sense error.
-- Les taules, polítiques i índexs s'ometen si ja existeixen.
-- =============================================================


-- -------------------------------------------------------------
-- 1. TAULES
-- -------------------------------------------------------------

-- Famílies propietàries del pis
CREATE TABLE IF NOT EXISTS families (
    id    uuid PRIMARY KEY DEFAULT gen_random_uuid(),
    nom   text NOT NULL,
    color text NOT NULL DEFAULT '#cccccc'
);

-- Usuaris de l'aplicació
CREATE TABLE IF NOT EXISTS usuaris (
    id         uuid PRIMARY KEY REFERENCES auth.users(id) ON DELETE CASCADE,
    nom        text NOT NULL,
    email      text NOT NULL UNIQUE,
    familia_id uuid REFERENCES families(id),
    es_admin   boolean NOT NULL DEFAULT false,
    actiu      boolean NOT NULL DEFAULT true
);

-- Estades al pis
CREATE TABLE IF NOT EXISTS estades (
    id                uuid PRIMARY KEY DEFAULT gen_random_uuid(),
    familia_id        uuid NOT NULL REFERENCES families(id),
    responsable_id    uuid NOT NULL REFERENCES usuaris(id),
    data_inici        date NOT NULL,
    data_fi           date NOT NULL,
    comentari         text,
    comentari_sortida text,                    -- comentari de la llista de sortida
    creada_per        uuid NOT NULL REFERENCES usuaris(id),
    creada_quan       timestamptz NOT NULL DEFAULT now(),
    modificada_quan   timestamptz NOT NULL DEFAULT now(),
    CONSTRAINT dates_correctes CHECK (data_fi >= data_inici)
);

-- Ítems de la llista de sortida
CREATE TABLE IF NOT EXISTS checklist_items (
    id          uuid PRIMARY KEY DEFAULT gen_random_uuid(),
    seccio      text NOT NULL,
    descripcio  text NOT NULL,
    es_opcional boolean NOT NULL DEFAULT false,
    ordre       integer NOT NULL DEFAULT 0
);

-- Respostes de la llista de sortida per estada
CREATE TABLE IF NOT EXISTS checklist_respostes (
    id              uuid PRIMARY KEY DEFAULT gen_random_uuid(),
    estada_id       uuid NOT NULL REFERENCES estades(id) ON DELETE CASCADE,
    item_id         uuid NOT NULL REFERENCES checklist_items(id),
    fet             boolean NOT NULL DEFAULT false,
    completada_per  uuid REFERENCES usuaris(id),
    completada_quan timestamptz,
    UNIQUE (estada_id, item_id)
);

-- Tasques pendents del pis
CREATE TABLE IF NOT EXISTS tasques (
    id              uuid PRIMARY KEY DEFAULT gen_random_uuid(),
    descripcio      text NOT NULL,
    afegida_per     uuid NOT NULL REFERENCES usuaris(id),
    afegida_quan    timestamptz NOT NULL DEFAULT now(),
    completada      boolean NOT NULL DEFAULT false,
    completada_per  uuid REFERENCES usuaris(id),
    completada_quan timestamptz
);

-- Tauler d'avisos (registre únic)
CREATE TABLE IF NOT EXISTS avisos (
    id             uuid PRIMARY KEY DEFAULT gen_random_uuid(),
    text           text NOT NULL DEFAULT '',
    modificat_per  uuid REFERENCES usuaris(id),
    modificat_quan timestamptz NOT NULL DEFAULT now()
);

-- Recursos i enllaços d'interès
CREATE TABLE IF NOT EXISTS recursos (
    id        uuid PRIMARY KEY DEFAULT gen_random_uuid(),
    titol     text NOT NULL,
    url       text NOT NULL,
    categoria text NOT NULL,
    ordre     integer NOT NULL DEFAULT 0
);


-- -------------------------------------------------------------
-- 2. ROW LEVEL SECURITY (RLS)
-- -------------------------------------------------------------

ALTER TABLE families            ENABLE ROW LEVEL SECURITY;
ALTER TABLE usuaris             ENABLE ROW LEVEL SECURITY;
ALTER TABLE estades             ENABLE ROW LEVEL SECURITY;
ALTER TABLE checklist_items     ENABLE ROW LEVEL SECURITY;
ALTER TABLE checklist_respostes ENABLE ROW LEVEL SECURITY;
ALTER TABLE tasques             ENABLE ROW LEVEL SECURITY;
ALTER TABLE avisos              ENABLE ROW LEVEL SECURITY;
ALTER TABLE recursos            ENABLE ROW LEVEL SECURITY;

-- Lectura: qualsevol usuari autenticat pot llegir-ho tot
DROP POLICY IF EXISTS "usuaris autenticats poden llegir families"            ON families;
DROP POLICY IF EXISTS "usuaris autenticats poden llegir usuaris"             ON usuaris;
DROP POLICY IF EXISTS "usuaris autenticats poden llegir estades"             ON estades;
DROP POLICY IF EXISTS "usuaris autenticats poden llegir checklist_items"     ON checklist_items;
DROP POLICY IF EXISTS "usuaris autenticats poden llegir checklist_respostes" ON checklist_respostes;
DROP POLICY IF EXISTS "usuaris autenticats poden llegir tasques"             ON tasques;
DROP POLICY IF EXISTS "usuaris autenticats poden llegir avisos"              ON avisos;
DROP POLICY IF EXISTS "usuaris autenticats podem llegir recursos"            ON recursos;

CREATE POLICY "usuaris autenticats poden llegir families"
    ON families FOR SELECT TO authenticated USING (true);

CREATE POLICY "usuaris autenticats poden llegir usuaris"
    ON usuaris FOR SELECT TO authenticated USING (true);

CREATE POLICY "usuaris autenticats poden llegir estades"
    ON estades FOR SELECT TO authenticated USING (true);

CREATE POLICY "usuaris autenticats poden llegir checklist_items"
    ON checklist_items FOR SELECT TO authenticated USING (true);

CREATE POLICY "usuaris autenticats poden llegir checklist_respostes"
    ON checklist_respostes FOR SELECT TO authenticated USING (true);

CREATE POLICY "usuaris autenticats poden llegir tasques"
    ON tasques FOR SELECT TO authenticated USING (true);

CREATE POLICY "usuaris autenticats poden llegir avisos"
    ON avisos FOR SELECT TO authenticated USING (true);

CREATE POLICY "usuaris autenticats podem llegir recursos"
    ON recursos FOR SELECT TO authenticated USING (true);

-- Estades: cada usuari gestiona les seves
DROP POLICY IF EXISTS "usuaris poden crear estades"               ON estades;
DROP POLICY IF EXISTS "usuaris poden modificar les seves estades" ON estades;
DROP POLICY IF EXISTS "usuaris poden eliminar les seves estades"  ON estades;

CREATE POLICY "usuaris poden crear estades"
    ON estades FOR INSERT TO authenticated
    WITH CHECK (auth.uid() = creada_per);

CREATE POLICY "usuaris poden modificar les seves estades"
    ON estades FOR UPDATE TO authenticated
    USING (
        auth.uid() = creada_per
        OR EXISTS (SELECT 1 FROM usuaris WHERE id = auth.uid() AND es_admin = true)
    );

CREATE POLICY "usuaris poden eliminar les seves estades"
    ON estades FOR DELETE TO authenticated
    USING (
        auth.uid() = creada_per
        OR EXISTS (SELECT 1 FROM usuaris WHERE id = auth.uid() AND es_admin = true)
    );

-- Checklist: qualsevol usuari autenticat pot escriure
DROP POLICY IF EXISTS "usuaris poden escriure checklist_respostes" ON checklist_respostes;

CREATE POLICY "usuaris poden escriure checklist_respostes"
    ON checklist_respostes FOR ALL TO authenticated
    USING (true) WITH CHECK (true);

-- Tasques: qualsevol usuari autenticat pot escriure
DROP POLICY IF EXISTS "usuaris poden escriure tasques" ON tasques;

CREATE POLICY "usuaris poden escriure tasques"
    ON tasques FOR ALL TO authenticated
    USING (true) WITH CHECK (true);

-- Avisos: qualsevol usuari autenticat pot inserir o modificar
DROP POLICY IF EXISTS "usuaris poden inserir avisos"   ON avisos;
DROP POLICY IF EXISTS "usuaris poden modificar avisos" ON avisos;

CREATE POLICY "usuaris poden inserir avisos"
    ON avisos FOR INSERT TO authenticated
    WITH CHECK (true);

CREATE POLICY "usuaris poden modificar avisos"
    ON avisos FOR UPDATE TO authenticated
    USING (true) WITH CHECK (true);


-- -------------------------------------------------------------
-- 3. ÍNDEXS
-- -------------------------------------------------------------

CREATE INDEX IF NOT EXISTS idx_estades_dates   ON estades (data_inici, data_fi);
CREATE INDEX IF NOT EXISTS idx_usuaris_email   ON usuaris (email);
CREATE INDEX IF NOT EXISTS idx_recursos_ordre  ON recursos (ordre);
CREATE INDEX IF NOT EXISTS idx_checklist_ordre ON checklist_items (ordre);
CREATE INDEX IF NOT EXISTS idx_estades_familia ON estades (familia_id, data_inici);
