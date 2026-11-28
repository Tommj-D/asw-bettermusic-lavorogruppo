#!/bin/bash

# Script di prova per la cancellazione delle recensioni (sul modello del test minimale)
# Nota: eseguire con l'applicazione appena avviata (db vuoti)

echo "=== 1. Inizializzazione database ==="
./do-init-bettermusic-db.sh > /dev/null

# Pausa utile per la propagazione asincrona quando si usa Kafka
sleep 2

echo "Conteggi iniziali (attesi: Alice=5, Bob=6, Carlo=5):"
for UTENTE in Alice Bob Carlo; do
    CONTEGGIO=$(curl -s localhost:8080/recensioni-seguite/recensioniseguite/$UTENTE | jq length)
    echo "  $UTENTE: $CONTEGGIO"
done
echo

echo "=== 2. Cancellazione recensioni 2 e 6 ==="
./do-delete-recensioni.sh

# Do al broker il tempo di consegnare l'evento di cancellazione a recensioni-seguite prima di leggere i conteggi (Kafka)
sleep 2

echo "=== 3. Verifica dopo la cancellazione ==="
TOTALE=$(curl -s localhost:8080/recensioni/recensioni | jq length)
echo "Recensioni totali rimaste nel sistema (atteso: 4): $TOTALE"
echo

echo "Conteggi recensioni seguite aggiornati (attesi: Alice=4, Bob=4, Carlo=4):"
for UTENTE in Alice Bob Carlo; do
    CONTEGGIO=$(curl -s localhost:8080/recensioni-seguite/recensioniseguite/$UTENTE | jq length)
    echo "  $UTENTE: $CONTEGGIO"
done
echo