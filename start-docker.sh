#!/usr/bin/env bash
set -euo pipefail

die() {
    printf 'Errore: %s\n' "$*" >&2
    exit 1
}

if [[ $# -gt 0 ]]; then
    case "$1" in
        -h|--help)
            printf '%s\n' \
                'Uso: bash start-docker.sh' \
                'Scarica le immagini, costruisce i servizi e avvia BetterMusic.' \
                'Richiede Docker avviato e Docker Compose con supporto --wait.' \
                'Usa POSTGRES_PASSWORD se esportata, altrimenti la richiede.'
            exit 0
            ;;
        *) die 'Argomento non riconosciuto. Usare --help.' ;;
    esac
fi

project_dir="$(cd -- "$(dirname -- "${BASH_SOURCE[0]}")" && pwd)"
cd -- "$project_dir"

compose() {
    docker compose --file "$project_dir/docker-compose.yml" "$@"
}

command -v docker >/dev/null 2>&1 || die \
    'Docker non trovato. Installare Docker Engine con Compose oppure Docker Desktop; vedere README.md.'
compose version || die 'Docker Compose non disponibile; installare il plugin Compose o Docker Desktop.'
compose_help="$(compose up --help)" || die 'Impossibile verificare Docker Compose.'
[[ "$compose_help" == *--wait-timeout* ]] || die 'Aggiornare Docker Compose: manca il supporto --wait-timeout.'
docker_os="$(docker info --format '{{.OSType}}' 2>/dev/null)" || die \
    'Daemon Docker non accessibile. Avviare Docker Engine/Desktop e verificare i permessi con docker info.'
[[ "$docker_os" == linux ]] || die 'Sono richiesti container Linux; selezionare Linux containers in Docker Desktop.'

if [[ -z "${POSTGRES_PASSWORD:-}" ]]; then
    [[ -t 0 ]] || die 'Input non interattivo: esportare POSTGRES_PASSWORD prima di avviare lo script.'
    printf '%s\n' 'Con un volume PostgreSQL esistente, inserire la password scelta al primo avvio.'
    if ! IFS= read -r -s -p 'Password PostgreSQL: ' POSTGRES_PASSWORD; then
        printf '\n' >&2
        die 'Lettura della password interrotta.'
    fi
    printf '\n'
    [[ -n "$POSTGRES_PASSWORD" ]] || die 'La password non puo essere vuota.'
    if ! IFS= read -r -s -p 'Ripetere la password: ' password_confirmation; then
        printf '\n' >&2
        die 'Conferma della password interrotta.'
    fi
    printf '\n'
    [[ "$POSTGRES_PASSWORD" == "$password_confirmation" ]] || die 'Le password non coincidono.'
    unset password_confirmation
fi
export POSTGRES_PASSWORD

printf '%s\n' 'Validazione della configurazione...'
compose config --quiet
printf '%s\n' 'Download delle immagini Consul e PostgreSQL...'
compose pull consul postgres
printf '%s\n' 'Build e avvio dei sette container; attesa degli healthcheck...'
if compose up -d --build --wait --wait-timeout 300; then
    compose ps
else
    startup_status=$?
    printf '%s\n' 'Avvio non completato. Stato e ultimi log:' >&2
    compose ps >&2 || true
    compose logs --tail=80 >&2 || true
    exit "$startup_status"
fi
printf '%s\n' \
    'BetterMusic disponibile su http://127.0.0.1:8080' \
    'I dati dimostrativi non vengono caricati automaticamente.' \
    'Per i comandi Compose manuali, esportare POSTGRES_PASSWORD nel proprio terminale.'
