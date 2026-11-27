package asw.bettermusic.recensioni.domain;

public interface RecensioniEventPublisherPort {
    void publishRecensioneCreated(Recensione recensione);
    void publishRecensioneDeleted(Long id);
}
