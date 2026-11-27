# PostgreSQL in Docker

PostgreSQL è incluso nel `docker-compose.yml` principale. Dalla root del progetto:

```bash
read -rsp 'Password PostgreSQL: ' POSTGRES_PASSWORD
echo
export POSTGRES_PASSWORD
# Solo PostgreSQL:
docker compose up -d --wait postgres
# Oppure tutto lo stack:
docker compose up -d --build --wait --wait-timeout 300
```

Usa l'[immagine ufficiale PostgreSQL](https://hub.docker.com/_/postgres) versione
18 Alpine, con un volume persistente montato su `/var/lib/postgresql`, come
richiesto dall'immagine dalla versione 18.

PostgreSQL è raggiungibile dai quattro backend all'indirizzo `postgres:5432`,
utente `postgres`, database predefinito `postgres`, password scelta all'avvio.
Non pubblica porte sull'host. Per aprire una console amministrativa:

```bash
docker compose exec postgres psql -U postgres -d postgres
```

Ogni rete è una bridge con `internal: true` e due soli membri:

| Rete | Container |
|---|---|
| postgres-album | postgres, album |
| postgres-recensioni | postgres, recensioni |
| postgres-connessioni | postgres, connessioni |
| postgres-seguite | postgres, recensioni-seguite |

Gateway e Consul non condividono reti con PostgreSQL. Non viene creata una rete
`default` o una rete comune a tutti i backend. Come negli altri container,
l'inoltro IPv4 è disabilitato. Le reti bridge sono bidirezionali e separano la
connettività diretta; non sostituiscono i permessi SQL per servizio.

Il container usa UID/GID `70:70`, filesystem root in sola lettura, capabilities
rimosse e gli stessi limiti e criteri di riavvio/log dello stack. Dati persistenti
in `postgres-data`; socket e file temporanei su tmpfs. Memoria e CPU sono
configurabili con `POSTGRES_MEMORY_LIMIT` (default `512m`) e `POSTGRES_CPU_LIMIT`
(default `1.0`). La configurazione segue le directory e l'utente definiti dal
[Dockerfile ufficiale Alpine](https://github.com/docker-library/postgres/blob/master/18/alpine3.23/Dockerfile).

Non sono previsti database applicativi, tabelle, migrazioni o script SQL.
Al primo avvio l'immagine inizializza solamente il cluster e i database standard
di PostgreSQL. Le credenziali vengono impostate solo quando il volume è vuoto.
Il codice Java e i datasource restano invariati: nessuna migrazione da HSQLDB,
creazione di schemi o configurazione JDBC. Le connessioni applicative verranno
implementate successivamente; per ora sono predisposte solo le reti Docker.

```bash
# Stato e log
docker compose ps
docker compose logs --tail=100 postgres

# Arresto, conservando i dati nel volume
docker compose down
```

`docker compose down` arresta tutto lo stack e conserva il volume;
`docker compose stop postgres` arresta solo PostgreSQL. Non aggiungere `-v`
a `down` per conservare i dati.

La configurazione è validabile con `docker compose config --quiet` e
`python3 docker/scripts/verify-compose.py` dopo aver esportato la password.
L'avvio effettivo richiede l'accesso al daemon Docker.
