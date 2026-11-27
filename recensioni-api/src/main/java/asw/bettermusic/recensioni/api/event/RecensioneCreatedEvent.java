package asw.bettermusic.recensioni.api.event;

import lombok.*;

@Data @NoArgsConstructor @AllArgsConstructor
public class RecensioneCreatedEvent {
    private Long id;
    private String recensore;
    private Long idAlbum;
    private String sunto;
}
