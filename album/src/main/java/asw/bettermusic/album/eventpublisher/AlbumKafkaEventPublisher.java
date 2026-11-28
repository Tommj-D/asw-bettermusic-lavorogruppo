package asw.bettermusic.album.eventpublisher;

import asw.bettermusic.album.api.event.AlbumCreatedEvent;
import asw.bettermusic.album.domain.Album;
import asw.bettermusic.album.domain.AlbumEventPublisherPort;
import org.springframework.beans.factory.annotation.Autowired;
import org.springframework.kafka.core.KafkaTemplate;
import org.springframework.stereotype.Component;

@Component
public class AlbumKafkaEventPublisher implements AlbumEventPublisherPort {

    private static final String TOPIC = "album-events";

    @Autowired
    private KafkaTemplate<String, Object> kafkaTemplate;

    @Override
    public void publishAlbumCreated(Album album) {
        AlbumCreatedEvent event = new AlbumCreatedEvent(
            album.getId(), album.getTitolo(), album.getArtista(), album.getGeneri()
        );
        kafkaTemplate.send(TOPIC, String.valueOf(album.getId()), event);
    }
}
