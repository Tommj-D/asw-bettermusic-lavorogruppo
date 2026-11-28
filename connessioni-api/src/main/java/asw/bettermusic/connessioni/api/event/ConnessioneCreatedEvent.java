package asw.bettermusic.connessioni.api.event;

import lombok.*;

@Data @NoArgsConstructor @AllArgsConstructor
public class ConnessioneCreatedEvent {
    private Long id;
    private String utente;
    private String seguito;
    private String ruolo;
}
