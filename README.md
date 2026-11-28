# BETTERMUSIC

Progetto del corso di Analisi e progettazione del software per l'anno accademico 2025-2026. 


## Descrizione di questo progetto 

Questo progetto contiene il il codice di *BetterMusic*, 
un semplice social network per la condivisione di recensioni di album musicali.  
Gli utenti del sistema possono scrivere e pubblicare delle recensioni. 
Possono poi seguire le recensioni scritte da specifici recensori e quelle degli album realizzati da specifici artisti oppure di specifici generi.  
Quando un utente accede alla pagina delle recensioni che segue, gli vengono mostrate le recensioni dei recensori e degli artisti e dei generi che segue. 

L'applicazione *BetterMusic* è composta dai seguenti microservizi: 

* Il servizio *album* gestisce gli album musical. 
  Ogni album ha un titolo ed è stato realizzato da un artista, e può essere relativo a uno o più generi musicali. 
  
  Un esempio di album: 
  * id: 1
  * titolo: The Dark Side of the Moon
  * artista: Pink Floyd
  * generi: Rock, Progressive Rock 
  
  Inoltre, ogni album ha un id numerico univoco. 
  Anche titolo ed artista identificano univocamente gli album. 
  
  Operazioni: 
  * `POST /album` aggiunge un nuovo album (dati titolo, artista e una lista di generi)
  * `GET /album/{id}` trova un album, dato l'id 
  * `GET /album` trova tutti gli album
  * `GET /cercaalbum?titolo={titolo}&artista={artista}` trova un album, dati titolo e artista
  * `GET /cercaalbum/artista/{artista}` trova tutti gli album di un certo artista
  * `GET /cercaalbum/genere/{genere}` trova tutti gli album di un certo genere
  
* Il servizio *recensioni* gestisce le recensioni. 
  Ogni recensione è scritta da un recensore, si riferisce ad un album (tramite il suo id),
  e contiene il testo della recensione (che può essere molto lungo) ed un suo sunto (di solito breve). 
  
  Un esempio di recensione: 
  * id: 101
  * recensore: Woody
  * idAlbum: 1
  * testo: Bla bla bla...
  * sunto: Il lato buio dell'animo umano
  
  Una recensione in formato breve è una recensione che non contiene il testo completo della recensione, ma solo il suo sunto. 
  Per motivi di prestazioni, le operazioni che restituiscono più recensioni, le restituiscono in formato breve. 
  
  Operazioni: 
  * `POST /recensioni` aggiunge una nuova recensione (dati recensore, titolo dell'album, artista dell'album, testo e sunto della recensione)
  * `GET /recensioni/{id}` trova una recensione, dato l'id (la recensione contiene il testo completo della recensione) 
  * `GET /recensioni` trova tutte le recensioni (in formato breve) 
  * `GET /cercarecensioni/album/{idAlbum}` trova tutte le recensioni (in formato breve) di un certo album, dato il suo id
  * `GET /cercarecensioni/recensore/{recensore}` trova tutte le recensioni (in formato breve) di un certo recensore
  
* Il servizio *connessioni* gestisce le connessioni degli utenti con le recensioni che seguono, 
  e più precisamente con gli artisti, con i recensori e con i generi musicali che essi seguono. 

  Le connessioni sono delle terne *utente-seguito-ruolo*, 
  in cui l'*utente* è chi segue, 
  *seguito* è chi o che cosa è seguito (un artista oppure uno che scrive recensioni oppure un genere musicale) 
  e *ruolo* rappresenta il ruolo del seguito, e può essere *ARTISTA* oppure *RECENSORE* oppure *GENERE*. 
  Per esempio, la terna *Alice-Pink Floyd-ARTISTA* indica che *Alice* è interessata a seguire le recensioni degli album dei *Pink Floyd*. 
  Invece, la terna *Bob-OndaRock-RECENSORE* indica che *Bob* è interessato a seguire le recensioni scritte da *OndaRock*. 
  Inoltre, la terna *Carlo-Pop-GENERE* indica che *Carlo* è interessato a seguire le recensioni sugli album del genere *Pop*. 

  Operazioni: 
  * `POST /connessioni` aggiunge una nuova connessione utente-seguito-ruolo (dati utente, seguito e ruolo)
  * `GET /connessioni` trova tutte le connessioni 
  * `GET /connessioni/{utente}` trova tutte le connessioni di un certo utente
  * `GET /connessioni/{utente}/{ruolo}` trova tutte le connessioni di un certo utente relative a un certo ruolo
  * `DELETE /connessioni` cancella una connessione utente-seguito-ruolo (dati utente, seguito e ruolo)

* Il servizio *recensioni-seguite* consente a un utente di trovare le recensioni degli artisti e dei recensori e dei generi musicali che segue. 

  Operazioni: 
  * `GET /recensioniseguite/{utente}` trova tutti le recensioni seguite da un certo utente, 
    ovvero le recensioni di artisti di album e di recensori e di generi musicali seguiti da quell'utente
	(le recensioni sono in formato breve) 
  
* Il servizio *api-gateway* (esposto sulla porta *8080*) è l'API gateway dell'applicazione che: 
  * espone il servizio *album* sul path `/album` - ad esempio, `GET /album/album/{id}`
  * espone il servizio *recensioni* sul path `/recensioni` - ad esempio, `GET /recensioni/recensioni`
  * espone il servizio *connessioni* sul path `/connessioni` - ad esempio, `GET /connessioni/connessioni/{utente}`
  * espone il servizio *recensioni-seguite* sul path `/recensioni-seguite` - ad esempio, `GET /recensioni-seguite/recensioniseguite/{utente}`


## Esecuzione 

Per eseguire questo progetto: 

* per avviare *Consul*, eseguire lo script `start-consul.sh` 

* per avviare l'applicazione *BetterMusic* (che richiede *Consul*), eseguire lo script `start-bettermusic.sh` 

* per inizializzare le basi di dati con dei dati di esempio, 
  eseguire gli script `do-init-albums.sh`, `do-init-recensioni.sh` e `do-init-connessioni.sh` 
  (oppure, in modo equivalente, lo script `do-init-bettermusic-db.sh`)

Sono anche forniti alcuni script di esempio: 

* lo script `run-sample-queries.sh` esegue un insieme di interrogazioni di esempio mediante *curl*

* lo script `do-get-albums.sh` trova tutti gli album 

* lo script `do-get-album-per-id.sh` trova un album dato l'id

* lo script `do-get-album-per-titolo-e-artista.sh` trova un album dati titolo e artista

* lo script `do-get-albums-per-artista.sh` trova tutti gli album di un certo artista

* lo script `do-get-albums-per-genere.sh` trova tutti gli album di un certo genere

* lo script `do-get-recensioni.sh` trova tutte le recensioni 

* lo script `do-get-recensioni-per-id-album.sh` trova tutte le recensioni relative a un certo album 

* lo script `do-get-recensioni-per-recensore.sh` trova tutte le recensioni di un certo recensore 

* lo script `do-get-connessioni.sh` trova tutte le connessioni 

* lo script `do-get-connessioni-per-utente.sh` trova tutte le connessioni di un certo utente

* lo script `do-get-recensioni-seguite-per-utente.sh` trova tutte le recensioni seguite da un certo utente 

* lo script `do-get-recensioni-seguite.sh` trova le recensioni seguite dagli utenti Alice, Bob e Carlo

Inoltre: 

* gli script `do-update-albums.sh`, `do-update-recensioni.sh` e `do-update-connessioni.sh` 
  (oppure, in modo equivalente, lo script `do-update-bettermusic-db.sh`)
  eseguono degli aggiornamenti delle varie basi di dati, 
  utili per verificare la correttezza dell'applicazione  

Alla fine, l'applicazione può essere arrestata usando lo script `stop-bettermusic.sh`. 
*Consul* può essere arrestato usando lo script `stop-consul.sh`. 


## Test minimale 

Con riferimento agli script forniti: 

* eseguire lo script `do-init-bettermusic-db.sh`  

* eseguire lo script `run-sample-queries.sh`: 
  le recensioni seguite da Alice, Bob e Carlo (ultime risposte fornite da questo script) 
  dovrebbero essere rispettivamente 5, 6 e 5 

* eseguire lo script `do-update-albums.sh`

* eseguire di nuovo lo script `run-sample-queries.sh`: 
  ora le recensioni seguite da Alice, Bob e Carlo dovrebbero essere rispettivamente ancora 5, 6 e 5 
  (perché i nuovi album non hanno ancora recensioni)

* eseguire lo script `do-update-recensioni.sh`

* eseguire di nuovo lo script `run-sample-queries.sh`: 
  ora le recensioni seguite da Alice, Bob e Carlo dovrebbero essere rispettivamente 6, 8 e 7 

* eseguire lo script `do-update-connessioni.sh`

* eseguire di nuovo lo script `run-sample-queries.sh`: 
  ora le recensioni seguite da Alice, Bob e Carlo dovrebbero essere rispettivamente 7, 5 e 8 


## Descrizione delle attività da svolgere 

Si veda la descrizione del progetto sul sito web del corso di [Architettura dei sistemi software](https://asw.inf.uniroma3.it/).


## Utilizzo di Kafka con Docker e Kubernetes

Ecco alcune [note sull'Utilizzo di Kafka con Docker e Kubernetes](kafka/).




# BetterMusic – Progetto di Architettura dei Sistemi Software (A.A. 2026-2027)

## Componenti del gruppo
- Tommaso De Angelis 

---

## Scelte progettuali

### Gestione della cancellazione di una recensione (Punto 2)
- **Endpoint REST:** nel microservizio `recensioni` è stata aggiunta l'operazione `DELETE /recensioni/{recensioneId}` all'interno di `RecensioniController`, delegata a `RecensioniService` / `RecensioniServiceImpl`.
- **Comportamento e codici di stato HTTP:** il servizio verifica la presenza della recensione nel database HSQLDB tramite il suo identificativo. Se la recensione esiste, viene eliminata e restituita al client con stato `200 OK` (nel formato `RecensioneResponse`), coerentemente con la convenzione già adottata nel servizio `connessioni`. Se l'identificativo non corrisponde ad alcuna recensione, viene sollevata una `ResponseStatusException` con stato `404 Not Found`.
- **Instradamento tramite API Gateway:** l'API Gateway espone l'operazione all'esterno sull'URL `DELETE /recensioni/recensioni/{recensioneId}`. Non è stata necessaria alcuna modifica alla configurazione del gateway, poiché la rotta `recensioni_route` (`Path=/recensioni/**` con filtro `StripPrefix=1`) inoltra già tutti i metodi HTTP verso il servizio `recensioni`.
- **Evento di dominio (`recensioni-api`):** nel package `asw.bettermusic.recensioni.api.event` è stata definita la classe `RecensioneDeletedEvent`, contenente l'identificativo (`id`) della recensione eliminata, condivisa tra producer e consumer.
- **Pubblicazione asincrona su Kafka (`recensioni`):** seguendo l'architettura esagonale (*Porte e Adattatori*) già adottata nel progetto, è stata introdotta l'interfaccia `RecensioniEventPublisherPort` nel package `domain` e la relativa implementazione `RecensioniKafkaEventPublisher` nel package `eventpublisher`. Quando `RecensioniServiceImpl.deleteRecensione(Long id)` elimina effettivamente una recensione dal database, pubblica un `RecensioneDeletedEvent` serializzato in JSON sul topic `recensioni-service-event-channel` tramite `KafkaTemplate` (configurabile tramite `asw.kafka.channel.out` e `SPRING_KAFKA_BOOTSTRAP_SERVERS`).
- **Aggiornamento della replica locale (`recensioni-seguite`):** *(da completare in fase di integrazione con il Punto 1)* il consumer di `recensioni-seguite` intercetterà `RecensioneDeletedEvent` sullo stesso topic e rimuoverà la recensione corrispondente dalla propria replica locale HSQLDB in modo idempotente.

---

## Istruzioni per costruire ed eseguire l'applicazione

### Prerequisiti
- Java 21, Gradle, Docker / Docker Compose, `curl` e `jq`.

### Compilazione ed esecuzione in locale
1. Compilare tutti i moduli del progetto:
   ```bash
   gradle build
   ```
2. Avviare Consul e Kafka (in Docker):
   ```bash
   ./start-consul.sh
   cd kafka/docker && ./start-kafka.sh && cd ../..
   ```
3. Avviare i microservizi:
   ```bash
   ./start-bettermusic.sh
   ```
4. Per arrestare l'applicazione, Consul e Kafka:
   ```bash
   ./stop-bettermusic.sh
   ./stop-consul.sh
   cd kafka/docker && ./stop-kafka.sh && cd ../..
   ```

---

## Script di prova e conteggi attesi

### Cancellazione di una recensione (`run-test-delete-recensioni.sh`)
Sul modello del test minimale previsto dal progetto, sono stati aggiunti due script nella root del repository:
- `do-delete-recensioni.sh`: invia tramite API Gateway due richieste `DELETE` per rimuovere le recensioni con ID `2` e `6`.
- `run-test-delete-recensioni.sh`: automatizza l'intero test partendo da database appena inizializzati:
  1. Esegue `./do-init-bettermusic-db.sh` e verifica che le recensioni seguite da **Alice, Bob e Carlo** siano inizialmente **5, 6 e 5** (su un totale di **6** recensioni).
  2. Esegue `./do-delete-recensioni.sh`, rimuovendo:
     - la recensione **ID 2** (scritta da *Woody* sull'album *The Wall* dei *Pink Floyd*, genere *Progressive Rock*);
     - la recensione **ID 6** (scritta da *OndaRock* sull'album *Thriller* di *Michael Jackson*, genere *Pop*).
  3. Attende 2 secondi (`sleep 2`) per garantire la propagazione asincrona degli eventi e verifica che:
     - le recensioni totali rimaste nel sistema scendano da **6 a 4**;
     - le recensioni seguite aggiornate per **Alice, Bob e Carlo** scendano a **4, 4 e 4** (testando contemporaneamente l'aggiornamento per artista, per recensore e per genere).

---

## Limiti noti
- **Basi di dati in memoria:** ogni microservizio utilizza un database HSQLDB in-memory; al riavvio dell'applicazione tutti i dati vengono persi ed è necessario rieseguire gli script di inizializzazione.
- **Consistenza eventuale in modalità Kafka:** in seguito a una cancellazione, `recensioni-seguite` può impiegare alcuni millisecondi per riflettere l'eliminazione nella propria replica locale in attesa della consegna del messaggio da parte del broker Kafka.