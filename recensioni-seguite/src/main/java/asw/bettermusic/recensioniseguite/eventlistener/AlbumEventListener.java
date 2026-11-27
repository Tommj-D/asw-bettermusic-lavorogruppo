package asw.bettermusic.recensioniseguite.eventlistener;

import asw.bettermusic.album.api.event.AlbumCreatedEvent;
import asw.bettermusic.recensioniseguite.domain.Album;
import asw.bettermusic.recensioniseguite.domain.AlbumRepository;
import org.springframework.beans.factory.annotation.Autowired;
import org.springframework.kafka.annotation.KafkaHandler;
import org.springframework.kafka.annotation.KafkaListener;
import org.springframework.stereotype.Component;

@Component
@KafkaListener(topics = "album-events", groupId = "${spring.kafka.consumer.group-id}")
public class AlbumEventListener {

    @Autowired
    private AlbumRepository albumRepository;

    @KafkaHandler
    public void onAlbumCreated(AlbumCreatedEvent event) {
        Album album = new Album(event.getId(), event.getTitolo(), event.getArtista(), event.getGeneri());
        albumRepository.save(album);
    }

    @KafkaHandler(isDefault = true)
    public void ignoreUnknown(Object event) {}
}
