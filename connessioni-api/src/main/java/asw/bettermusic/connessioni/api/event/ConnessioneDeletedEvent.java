package asw.bettermusic.connessioni.api.event;

import lombok.*;

@Data @NoArgsConstructor @AllArgsConstructor
public class ConnessioneDeletedEvent {
    private Long id;
    private String utente;
    private String seguito;
    private String ruolo;
}
