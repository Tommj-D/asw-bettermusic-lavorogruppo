package asw.bettermusic.recensioni.eventpublisher;

import asw.bettermusic.recensioni.api.event.RecensioneCreatedEvent;
import asw.bettermusic.recensioni.api.event.RecensioneDeletedEvent;
import asw.bettermusic.recensioni.domain.Recensione;
import asw.bettermusic.recensioni.domain.RecensioniEventPublisherPort;
import org.springframework.beans.factory.annotation.Autowired;
import org.springframework.kafka.core.KafkaTemplate;
import org.springframework.stereotype.Component;

@Component
public class RecensioniKafkaEventPublisher implements RecensioniEventPublisherPort {

    private static final String TOPIC = "recensioni-events";

    @Autowired
    private KafkaTemplate<String, Object> kafkaTemplate;

    @Override
    public void publishRecensioneCreated(Recensione r) {
        RecensioneCreatedEvent event = new RecensioneCreatedEvent(
            r.getId(), r.getRecensore(), r.getIdAlbum(), r.getSunto()
        );
        kafkaTemplate.send(TOPIC, String.valueOf(r.getId()), event);
    }

    @Override
    public void publishRecensioneDeleted(Long id) {
        RecensioneDeletedEvent event = new RecensioneDeletedEvent(id);
        kafkaTemplate.send(TOPIC, String.valueOf(id), event);
    }
}
