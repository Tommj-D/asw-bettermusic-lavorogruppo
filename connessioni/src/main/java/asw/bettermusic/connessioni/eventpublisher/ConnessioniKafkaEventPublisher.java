package asw.bettermusic.connessioni.eventpublisher;

import asw.bettermusic.connessioni.api.event.ConnessioneCreatedEvent;
import asw.bettermusic.connessioni.api.event.ConnessioneDeletedEvent;
import asw.bettermusic.connessioni.domain.Connessione;
import asw.bettermusic.connessioni.domain.ConnessioniEventPublisherPort;
import org.springframework.beans.factory.annotation.Autowired;
import org.springframework.kafka.core.KafkaTemplate;
import org.springframework.stereotype.Component;

@Component
public class ConnessioniKafkaEventPublisher implements ConnessioniEventPublisherPort {

    private static final String TOPIC = "connessioni-events";

    @Autowired
    private KafkaTemplate<String, Object> kafkaTemplate;

    @Override
    public void publishConnessioneCreated(Connessione c) {
        ConnessioneCreatedEvent event = new ConnessioneCreatedEvent(
            c.getId(), c.getUtente(), c.getSeguito(), c.getRuolo()
        );
        kafkaTemplate.send(TOPIC, c.getUtente(), event);
    }

    @Override
    public void publishConnessioneDeleted(Connessione c) {
        ConnessioneDeletedEvent event = new ConnessioneDeletedEvent(
            c.getId(), c.getUtente(), c.getSeguito(), c.getRuolo()
        );
        kafkaTemplate.send(TOPIC, c.getUtente(), event);
    }
}
