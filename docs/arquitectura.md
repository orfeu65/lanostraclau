# La Nostra Clau — Document d'Arquitectura

**Versió:** 1.1  
**Data:** Abril 2026  
**Estat:** Aplicació en producció  

---

## 1. Visió general

```
[Navegador mòbil]  ←→  [Streamlit Cloud]  ←→  [Supabase API]  ←→  [PostgreSQL]
   (usuari)              (frontend Python)       (autenticació        (base de
                                                  + REST API)          dades)
```

L'aplicació és una **web app** accessible des del navegador del mòbil. No és una app nativa i no requereix instal·lació. El backend i la base de dades viuen al núvol. Tot el codi és Python.

---

## 2. Tecnologia

| Component | Eina | Versió | Cost |
|---|---|---|---|
| Interfície (frontend) | Streamlit | última estable | Gratuït |
| Base de dades | Supabase (PostgreSQL) | Free tier | Gratuït |
| Autenticació | Supabase Auth (magic link per email) | — | Gratuït |
| Desplegament | Streamlit Cloud | Community | Gratuït |
| Repositori de codi | GitHub (`orfeu65/lanostraclau`) | — | Gratuït |

---

## 3. Autenticació

- Els usuaris s'autentiquen mitjançant **magic link per email** (Supabase Auth).
- L'usuari introdueix el seu email i rep un enllaç d'accés directe, sense contrasenya.
- No cal cap compte extern (GitHub, Google, etc.).
- Supabase gestiona el flux d'autenticació i els tokens de sessió.
- A cada rerun de Streamlit, la sessió es restaura al client Supabase per garantir que les polítiques RLS s'apliquen correctament.

---

## 4. Estructura de la base de dades

### `families`
| Camp | Tipus | Descripció |
|---|---|---|
| id | uuid | Clau primària |
| nom | text | Nom de la família |
| color | text | Color en format hex (#RRGGBB) per al calendari |

### `usuaris`
| Camp | Tipus | Descripció |
|---|---|---|
| id | uuid | Clau primària (lligada a Supabase Auth) |
| nom | text | Nom visible de l'usuari |
| email | text | Correu electrònic |
| familia_id | uuid | Referència a `families` |
| és_admin | boolean | Permisos d'administració |
| actiu | boolean | Permet desactivar sense eliminar |

### `estades`
| Camp | Tipus | Descripció |
|---|---|---|
| id | uuid | Clau primària |
| familia_id | uuid | Referència a `families` |
| responsable_id | uuid | Referència a `usuaris` (responsable de l'estada) |
| data_inici | date | Primer dia de l'estada |
| data_fi | date | Darrer dia de l'estada |
| comentari | text | Qui hi va, convidats, notes |
| comentari_sortida | text | Comentari deixat en fer la llista de sortida |
| creada_per | uuid | Referència a `usuaris` |
| creada_quan | timestamptz | Data i hora de creació |
| modificada_quan | timestamptz | Data i hora de darrera modificació |

### `checklist_items`
| Camp | Tipus | Descripció |
|---|---|---|
| id | uuid | Clau primària |
| seccio | text | Nom de la secció (p.ex. "Unes hores abans") |
| descripcio | text | Text de l'ítem |
| és_opcional | boolean | Si l'ítem és opcional |
| ordre | integer | Ordre de visualització |

### `checklist_respostes`
| Camp | Tipus | Descripció |
|---|---|---|
| id | uuid | Clau primària |
| estada_id | uuid | Referència a `estades` |
| item_id | uuid | Referència a `checklist_items` |
| fet | boolean | Si s'ha marcat com a fet |
| completada_per | uuid | Referència a `usuaris` |
| completada_quan | timestamptz | Data i hora de completació |

### `tasques`
| Camp | Tipus | Descripció |
|---|---|---|
| id | uuid | Clau primària |
| descripcio | text | Descripció de la tasca |
| afegida_per | uuid | Referència a `usuaris` |
| afegida_quan | timestamptz | Data i hora d'alta |
| completada | boolean | Estat de la tasca |
| completada_per | uuid | Referència a `usuaris` (pot ser null) |
| completada_quan | timestamptz | Data i hora de completació (pot ser null) |

### `avisos`
| Camp | Tipus | Descripció |
|---|---|---|
| id | uuid | Clau primària (sempre hi ha un sol registre) |
| text | text | Contingut del tauler d'avisos |
| modificat_per | uuid | Referència a `usuaris` |
| modificat_quan | timestamptz | Data i hora de darrera modificació |

---

## 5. Estructura del repositori

```
lanostraclau/
├── app.py                  # Punt d'entrada de Streamlit
├── pagines/
│   ├── inici.py
│   ├── calendari.py
│   ├── llista_sortida.py
│   ├── tasques.py
│   ├── informacio.py
│   └── administracio.py
├── serveis/
│   └── auth.py             # Autenticació (magic link, sessió)
├── static/
│   └── sarfa.pdf           # Horaris de bus BCN–Palamós
├── docs/
│   ├── requisits.md
│   └── arquitectura.md
├── .env.example            # Variables d'entorn d'exemple (sense secrets)
├── requirements.txt
└── README.md
```

---

## 6. Variables d'entorn

L'aplicació necessita les següents variables d'entorn (mai al repositori):

```
SUPABASE_URL=https://xxxx.supabase.co
SUPABASE_KEY=eyJ...
```

A Streamlit Cloud es configuren a la secció **Secrets** del projecte.

---

## 7. Desplegament

- Codi al repositori GitHub (`orfeu65/lanostraclau`).
- Streamlit Cloud connectat al repositori — redeploya automàticament en cada `git push` a `main`.
- Supabase com a base de dades i autenticació al núvol.
- URL de l'app: `https://lanostraclau.streamlit.app`

---

## 8. Estat del desenvolupament

| Pas | Descripció | Estat |
|---|---|---|
| 1 | Definició de requisits | ✅ Fet |
| 2 | Documentació (requisits + arquitectura) | ✅ Fet |
| 3 | Creació de taules a Supabase | ✅ Fet |
| 4 | Configuració autenticació magic link | ✅ Fet |
| 5 | Desenvolupament mòdul per mòdul | ✅ Fet |
| 6 | Proves i ajustos | ✅ Fet |
| 7 | Desplegament a Streamlit Cloud | ✅ Fet |

---

*Actualitzat a mesura que evoluciona el projecte.*
