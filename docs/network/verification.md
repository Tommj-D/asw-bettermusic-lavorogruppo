# Rapporto delle verifiche

Esecuzione nel workspace il **26 novembre 2026**, senza cambiare permessi del
socket Docker o regole firewall dell'host. Nessun container è stato avviato da
questa sessione. I PASS offline non attestano il funzionamento del deployment.

| Controllo eseguito | Esito | Evidenza / limite |
|---|---|---|
| Analisi Gradle, tutti gli application.yml, script e client REST | eseguita | Java 21, Boot 3.5.6, Cloud 2025.0.0; Wrapper assente; otto archi REST confermati |
| `docker compose config` | PASS | Compose principale normalizzato senza errori |
| Config del Compose Consul locale | PASS | file autonomo, un servizio, porta 8500 su localhost |
| `python3 docker/scripts/verify-compose.py` | PASS | sette servizi, matrice esatta di 18 bridge, 17 internal, porte e hardening dichiarati; volume PostgreSQL |
| Contratto Spring Consul offline, JDK 21 | PASS per cinque applicazioni | librerie 4.3.0 estratte dal JAR già presente: binding env, nome applicativo, hostname, instance-id, porta 8080, URL health, timeout 5s e assenza di deregistrazione critica |
| Generazione Mermaid, matrice e SVG | PASS | Compose normalizzato come sorgente; SVG esportati con Graphviz |
| Coerenza diagrammi `--check` | PASS | nessuna divergenza dal Compose |
| Sintassi Python, JSON e Bash modificato | PASS | compilazione sintattica, parsing JSON, `bash -n` |
| `git diff --check` | PASS | assenza di errori whitespace |
| `docker compose build` | BLOCCATO | `permission denied ... unix:///var/run/docker.sock`; anche buildx non disponibile, fallback al builder classico |
| `docker compose up -d` | BLOCCATO | stesso diniego di accesso al daemon |
| `docker compose ps` e log di tutti i servizi | BLOCCATO | stesso diniego di accesso al daemon |
| `python3 docker/scripts/verify-runtime.py` | BLOCCATO | validazione statica passa; `docker info` fallisce per accesso negato; nessuna prova runtime dichiarata PASS |
| Tentativo Gradle locale offline, JDK 21, cache in `/tmp` | BLOCCATO | sandbox nega socket/interfacce: `Could not determine a usable wildcard IP for this machine` |
| Healthcheck Docker e Consul, registrazioni realmente attive | NON VERIFICATI | richiedono lo stack avviato |
| Init, query, aggiornamenti e HSQLDB su Docker | NON ESEGUITI | stack non avviabile qui; conteggi 5/6/5 e successivi ancora da confermare |
| DNS/HTTP e TCP PostgreSQL consentiti e handshake TCP vietati | NON ESEGUITI | richiedono container e reti effettivi; PostgreSQL predisposto per i quattro backend, esclusi Gateway e Consul |
| UID/capabilities/NoNewPrivs/read-only effettivi | NON VERIFICATI | dichiarazioni Compose validate, ma mancano processi da ispezionare |
| Percorsi indiretti via Gateway e API Consul | LIMITE ARCHITETTURALE | identificati dall'analisi; prove controllate predisposte, non eseguite |

Il test Spring usa il JAR preesistente `album/build/libs/album.jar` per caricare le
librerie effettive: **non è una compilazione riuscita delle immagini nuove**.
La ricerca automatica dell'interfaccia predefinita viene sostituita nel solo test
con un valore in memoria; binding, oggetto di registrazione e generazione
healthcheck usano le classi Spring reali. Nessuna modifica al codice applicativo.

## Prosecuzione delle prove su un host con daemon accessibile

```bash
read -rsp 'Password PostgreSQL: ' POSTGRES_PASSWORD
echo
export POSTGRES_PASSWORD
python3 docker/scripts/verify-compose.py
docker compose config
docker compose build
docker compose up -d
docker compose up -d --wait --wait-timeout 300
docker compose ps
docker compose logs --no-color --tail=100
python3 docker/scripts/verify-functional.py
python3 docker/scripts/verify-runtime.py
# Dopo aver conservato gli output:
docker compose down
```

Eseguire il test funzionale sui database vuoti: richiama gli script originali di
init, query e aggiornamento e asserisce tutte le sequenze del README. Non lanciare
un secondo init prima dello stesso test. Il test runtime verifica matrici effettive,
porte, processi, DNS, HTTP e tutti gli IP dei target vietati; testa anche due
percorsi indiretti. Il suo codice 2 segnala proprio questi limiti e va conservato
nel verbale, senza convertirlo in una certificazione di pieno isolamento.

Le condizioni di accettazione che dipendono dal runtime restano quindi aperte.
Anche con tutte le prove di connettività diretta superate, l'isolamento contro
servizi compromessi richiederebbe ulteriori controlli di autorizzazione ed egress,
come descritto in [DOCKER.md](../../DOCKER.md).
