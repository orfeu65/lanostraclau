# 🔑 La Nostra Clau

Aplicació web per gestionar el pis compartit de Palamós entre tres famílies.

## Funcionalitats

- **Calendari d'estades** — visualització i gestió de les estades al pis, amb colors per família
- **Llista de sortida** — comprovació de l'estat del pis en marxar
- **Tasques pendents** — llista col·lectiva de feines i millores
- **Tauler d'avisos** — missatge compartit visible per a tothom
- **Informació útil** — enllaços, horaris i telèfons d'interès (dinàmic, gestionat des de l'app)
- **Administració** — gestió d'usuaris, famílies, checklist, subministres, acords i recursos (només administradora)

## Tecnologia

- [Streamlit](https://streamlit.io) — interfície web en Python
- [Supabase](https://supabase.com) — base de dades PostgreSQL i autenticació

## Instal·lació local

```bash
# Clona el repositori
git clone https://github.com/orfeu65/lanostraclau.git
cd lanostraclau

# Instal·la les dependències
pip install -r requirements.txt

# Configura les variables d'entorn
cp .env.example .env
# Edita .env amb les teves credencials de Supabase

# Inicialitza la base de dades a Supabase (SQL Editor)
# 1. Executa db/schema.sql
# 2. Executa db/dades.sql (còpia de dades.example.sql amb dades reals)

# Executa l'app
streamlit run app.py
```

## App

[lanostraclau.streamlit.app](https://lanostraclau.streamlit.app)

## Documentació

- [`docs/requisits.md`](docs/requisits.md) — requisits del projecte
- [`docs/arquitectura.md`](docs/arquitectura.md) — arquitectura tècnica
