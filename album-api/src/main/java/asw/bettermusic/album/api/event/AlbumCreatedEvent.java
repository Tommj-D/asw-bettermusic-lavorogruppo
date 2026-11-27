package asw.bettermusic.album.api.event;

import lombok.*;
import java.util.*;

@Data @NoArgsConstructor @AllArgsConstructor
public class AlbumCreatedEvent {
    private Long id;
    private String titolo;
    private String artista;
    private Set<String> generi;
}
