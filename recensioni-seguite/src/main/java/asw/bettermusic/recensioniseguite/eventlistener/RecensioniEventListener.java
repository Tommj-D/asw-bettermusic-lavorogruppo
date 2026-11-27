package asw.bettermusic.recensioniseguite.eventlistener;

import asw.bettermusic.recensioni.api.event.RecensioneCreatedEvent;
import asw.bettermusic.recensioni.api.event.RecensioneDeletedEvent;
import asw.bettermusic.recensioniseguite.domain.Recensione;
import asw.bettermusic.recensioniseguite.domain.RecensioniRepository;
import org.springframework.beans.factory.annotation.Autowired;
import org.springframework.kafka.annotation.KafkaHandler;
import org.springframework.kafka.annotation.KafkaListener;
import org.springframework.stereotype.Component;

@Component
@KafkaListener(topics = "recensioni-events", groupId = "${spring.kafka.consumer.group-id}")
public class RecensioniEventListener {

    @Autowired
    private RecensioniRepository recensioniRepository;

    @KafkaHandler
    public void onRecensioneCreated(RecensioneCreatedEvent event) {
        Recensione recensione = new Recensione(event.getId(), event.getRecensore(), event.getIdAlbum(), event.getSunto());
        recensioniRepository.save(recensione);
    }

    @KafkaHandler
    public void onRecensioneDeleted(RecensioneDeletedEvent event) {
        if (event.getId() != null) {
            recensioniRepository.deleteById(event.getId());
        }
    }

    @KafkaHandler(isDefault = true)
    public void ignoreUnknown(Object event) {}
}
