# La Nostra Clau — Document de Requisits

**Versió:** 1.0  
**Data:** Abril 2025  
**Estat:** Esborrany inicial  

---

## 1. Descripció del projecte

**La Nostra Clau** és una aplicació web per a dispositius mòbils que permet gestionar de forma compartida un pis de vacances situat a Palamós (Costa Brava). L'aplicació facilita la planificació d'estades, la revisió de l'estat del pis a la sortida, i la gestió de tasques pendents.

L'app substitueix parcialment la coordinació actual per WhatsApp, mantenint però l'ús d'aquest canal per a comunicació informal i notificacions. La comptabilitat es continua gestionant a Google Drive; l'app proporciona accés ràpid als recursos existents.

Tot el projecte és en **català**: la interfície d'usuari, el codi, els comentaris i la documentació.

---

## 2. Usuaris

- **3 famílies** propietàries del pis, amb un nombre variable de membres cadascuna.
- Cada família té un **responsable de família** (compte principal).
- Cada estada pot tenir un **responsable d'estada** diferent del responsable de família (per exemple, si hi van fills o altres membres sense el cap de família).
- Hi ha una única **administradora** (cap de família d'una de les tres famílies) amb permisos especials.
- Nombre màxim d'usuaris: **10**.

---

## 3. Mòduls de l'aplicació

### 3.1 Pàgina d'inici

La primera pantalla que veu l'usuari en entrar. Conté:

- **Estat actual del pis**: qui hi és ara, o "El pis és buit" si no hi ha cap estada activa.
- **La teva propera estada**: dates i responsable de l'estada.
- **Darrera estada completada**: família, dates i comentari de sortida deixat per aquella estada.
- **Tauler d'avisos**: bloc de text únic, editable per qualsevol usuari. No és un historial, sinó un sol missatge col·lectiu que es pot modificar. Es guarda qui l'ha modificat per última vegada i quan.
- **Accessos ràpids**: enllaços a recursos externs (veure mòdul 3.5).

---

### 3.2 Calendari d'estades

Permet veure i gestionar les estades al pis.

**Visualització:**
- Vista mensual i anual del calendari.
- Cada família té un **color assignat**. Les estades es mostren amb el color de la família corresponent.
- Es pot veure d'un cop d'ull quan el pis està ocupat i per qui.

**Gestió d'estades:**
- Crear una nova estada seleccionant dies al calendari.
- Editar o eliminar una estada pròpia.
- L'administradora pot editar o eliminar estades de qualsevol família.
- **Les estades no se solapen**: el sistema ho ha d'impedir. En casos excepcionals (molt rars), es pot indicar al comentari de l'estada.

**Dades de cada estada:**
- Família
- Responsable de l'estada (persona que es fa responsable, pot no ser el cap de família)
- Data d'inici i data de fi
- Comentari lliure (qui hi va, nombre de persones, convidats, etc.)

---

### 3.3 Llista de sortida

Una llista de comprovació que el responsable de l'estada ha d'emplenar abans de marxar del pis.

- La llista és **sempre la mateixa** (versió inicial fixa; editable en versions futures).
- Els ítems estan organitzats en **seccions** (per exemple: "Unes hores abans de marxar" / "Just al marxar").
- Cada ítem pot ser **obligatori** o **opcional**.
- Hi ha un **comentari general** únic per a tota la llista de sortida d'aquella estada.
- Es guarda qui ha marcat la llista i quan.
- El comentari de la darrera llista de sortida completada es mostra a la pàgina d'inici.

**Llista de comprovació inicial:** pendent de ser facilitada pels propietaris.

---

### 3.4 Tasques pendents del pis

Llista col·lectiva de feines o millores pendents al pis.

- Qualsevol usuari pot **afegir** una tasca nova.
- Qualsevol usuari pot **marcar una tasca com a completada**.
- Les tasques completades **no s'eliminen**: es guarden amb la data de completació i qui la va completar (historial).
- La vista principal mostra les tasques pendents. Les completades es poden consultar en un historial.

**Exemples de tasques:** portar una bicicleta, arreglar la pintura de la paret, fer la lectura del gas.

---

### 3.5 Informació útil

Pàgina estàtica amb recursos i informació d'interès.

- Enllaços a la carpeta de Drive (comptabilitat, factures, contractes).
- Horaris de transport públic (PDF adjunt o enllaç extern).
- Proveïdors i números de contracte (llum, gas, aigua...).
- Telèfons d'interès (lampista, electricista, etc.).

---

### 3.6 Administració *(només administradora)*

- Gestió d'usuaris: crear, editar, desactivar comptes.
- Assignació d'usuaris a famílies.
- Editar o eliminar estades de qualsevol família.
- Futur: editar la llista de comprovació de sortida.

---

## 4. Decisions preses

| Decisió | Opció triada | Motiu |
|---|---|---|
| Tauler d'avisos | Un sol bloc editable | No cal historial; la comunicació es fa per WhatsApp |
| Solapament d'estades | No permès | Es resol per WhatsApp si és necessari |
| Notificacions | No (de moment) | Es continua usant WhatsApp |
| Llista de sortida | Una per estada, comentari general únic | Suficient per a les necessitats actuals |
| Tasques completades | Es guarden amb historial | Millor traçabilitat |
| Comptabilitat | Es manté a Google Drive | L'app només ofereix accés ràpid |
| Autenticació | Magic link per email | Accessible per a tots els membres de les famílies, sense comptes externs ni contrasenyes |
| Idioma | Català (tot: UI, codi, comentaris, docs) | Decisió de les propietàries |

---

## 5. Fora d'abast (versió inicial)

- Notificacions automàtiques (push, email, WhatsApp).
- Edició de la llista de comprovació des de l'app.
- Gestió de comptabilitat.
- App nativa (iOS / Android).
- Estadístiques d'ús del pis.

---

*Document generat durant la fase de definició del projecte. Pot ser actualitzat a mesura que evolucioni el desenvolupament.*
