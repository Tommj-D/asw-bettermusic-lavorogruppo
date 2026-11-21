package asw.bettermusic.recensioni.eventpublisher;

import asw.bettermusic.recensioni.api.event.RecensioneDeletedEvent;
import asw.bettermusic.recensioni.domain.RecensioniEventPublisherPort;

import org.springframework.beans.factory.annotation.Autowired;
import org.springframework.beans.factory.annotation.Value;
import org.springframework.kafka.core.KafkaTemplate;
import org.springframework.stereotype.Component;

import java.util.logging.Logger;

@Component
public class RecensioniKafkaEventPublisher implements RecensioniEventPublisherPort {

	private final Logger logger = Logger.getLogger(this.getClass().toString());

	@Autowired
	private KafkaTemplate<String, Object> kafkaTemplate;

	@Value("${asw.kafka.channel.out:recensioni-service-event-channel}")
	private String channel;

	@Override
	public void publishRecensioneDeletedEvent(RecensioneDeletedEvent event) {
		logger.info("KAFKA EVENT PUBLISHER: publishing " + event + " on channel " + channel);
		kafkaTemplate.send(channel, event);
	}

}