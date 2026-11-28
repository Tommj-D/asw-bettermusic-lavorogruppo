package asw.bettermusic.connessioni.domain;

public interface ConnessioniEventPublisherPort {
    void publishConnessioneCreated(Connessione connessione);
    void publishConnessioneDeleted(Connessione connessione);
}
