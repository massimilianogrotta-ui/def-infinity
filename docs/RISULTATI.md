# Risultati dei test A/B

Due compiti reali, ognuno costruito due volte (DEF da solo contro DEF + questo pacchetto), stesso modello, stessi dati, poi una revisione indipendente alla cieca (senza sapere quale consegna avesse usato cosa).

## Test 1 · Circuito (confronto journal Mac/VPS)
- Pacchetto v0.1 caricato ma senza il paragrafo di aggancio alle skill: **mai usato** (0 subagent). Lezione: il pacchetto da solo è inerte, serve l'aggancio (vedi `skills/def-infinity/SKILL.md`).
- Con l'aggancio: stesso risultato corretto, ma processo più completo (spike che ha trovato un proprio errore, piano di manutenzione, pulizia finale) a +65% di costo.
- Revisione alla cieca: 20 a 19 a favore del pacchetto.
- Difetti trovati e corretti dopo questo test (v0.2): i passaggi girano solo quando un innesco reale lo richiede, il lavoro resta dentro la sessione per default (un agente separato solo se serve isolamento o parallelismo), via i percorsi assoluti della macchina e l'uso di `/tmp`.

## Test 2 · All-io v2 (registro di piattaforma, tocca SQL/RLS)
- Con il pacchetto corretto (v0.2): **costo leggermente più basso** di DEF da solo (non più alto), stessa qualità di base, copertura più ampia (ha chiuso anche un caso collegato non richiesto esplicitamente).
- Revisione alla cieca: preferenza per il pacchetto, su sicurezza del design e copertura.
- Nessuna violazione dei limiti (letture/scritture fuori dalle cartelle concesse, segreti, produzione) in nessuna delle 5 corse totali tra i due test.

## Limite onesto
Due compiti sono un segnale, non una prova statistica.
