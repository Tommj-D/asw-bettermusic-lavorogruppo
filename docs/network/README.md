# Schemi e legenda

Gli schemi seguono il layout orizzontale `LR`, con una sola identità per container.
[overview.mmd](overview.mmd) descrive gli archi applicativi;
[docker-networks.mmd](docker-networks.mmd) rappresenta separatamente tutte le 18 reti.
Sono generati da `docker compose config --format json`, non da una seconda
configurazione della topologia. La [matrice](network-matrix.md) è generata dallo
stesso comando. Gli SVG sono rappresentazioni equivalenti esportate con Graphviz:
[panoramica](overview.svg), [reti Docker](docker-networks.svg).

- Rettangolo azzurro: container unico. Le cinque applicazioni ascoltano su 8080;
  Consul espone internamente HTTP API su 8500 e PostgreSQL ascolta su 5432.
- Ellisse gialla: bridge privata `internal: true`; ogni ellisse è una rete distinta.
- Ellisse verde: bridge `public`, collegata soltanto al Gateway.
- Collegamento senza freccia nel dettaglio: appartenenza alla rete, bidirezionale.
- Freccia continua nella panoramica: chiamata REST implementata, non policy firewall
  direzionale. Il diagramma non implica che la connessione inversa sia vietata.
- Freccia tratteggiata verso Consul: registrazione/query; Consul effettua gli
  healthcheck HTTP nella direzione inversa sulla stessa rete dedicata.
- Freccia tratteggiata verso PostgreSQL: TCP 5432 predisposto tramite una rete
  interna distinta per backend; il codice Java non usa ancora queste connessioni.
  Gateway e Consul non hanno collegamenti diretti con PostgreSQL.
- Collegamento host: unico publishing applicativo, `127.0.0.1:8080:8080`.

Le reti separano connettività diretta, non identità, autorizzazione o cifratura.
Il forwarding IP è disattivato nei container, ma restano percorsi applicativi
indiretti tramite Gateway e healthcheck amministrativi Consul. I diagrammi non
certificano l'isolamento di un workload compromesso. Vedere [DOCKER.md](../../DOCKER.md)
e il [rapporto verifiche](verification.md) per limiti e prove mancanti.

Rigenerazione: `python3 docker/scripts/generate-network-docs.py` dalla root;
aggiungere `--check` per rilevare divergenze senza modificare file. Gli SVG vengono
esportati quando è disponibile `dot`; non richiedono strumenti nei container runtime.
