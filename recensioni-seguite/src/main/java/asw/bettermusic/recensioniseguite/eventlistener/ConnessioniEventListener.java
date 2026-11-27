package asw.bettermusic.recensioniseguite.eventlistener;

import asw.bettermusic.connessioni.api.event.ConnessioneCreatedEvent;
import asw.bettermusic.connessioni.api.event.ConnessioneDeletedEvent;
import asw.bettermusic.recensioniseguite.domain.Connessione;
import asw.bettermusic.recensioniseguite.domain.ConnessioniRepository;
import org.springframework.beans.factory.annotation.Autowired;
import org.springframework.kafka.annotation.KafkaHandler;
import org.springframework.kafka.annotation.KafkaListener;
import org.springframework.stereotype.Component;
import org.springframework.transaction.annotation.Transactional;

@Component
@KafkaListener(topics = "connessioni-events", groupId = "${spring.kafka.consumer.group-id}")
public class ConnessioniEventListener {

    @Autowired
    private ConnessioniRepository connessioniRepository;

    @KafkaHandler
    public void onConnessioneCreated(ConnessioneCreatedEvent event) {
        Connessione connessione = new Connessione(event.getId(), event.getUtente(), event.getSeguito(), event.getRuolo());
        connessioniRepository.save(connessione);
    }

    @KafkaHandler
    @Transactional
    public void onConnessioneDeleted(ConnessioneDeletedEvent event) {
        if (event.getId() != null) {
            connessioniRepository.deleteById(event.getId());
        } else {
            connessioniRepository.deleteByUtenteAndSeguitoAndRuolo(event.getUtente(), event.getSeguito(), event.getRuolo());
        }
    }

    @KafkaHandler(isDefault = true)
    public void ignoreUnknown(Object event) {}
}
