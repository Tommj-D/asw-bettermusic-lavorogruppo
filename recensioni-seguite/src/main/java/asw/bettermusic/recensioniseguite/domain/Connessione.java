package asw.bettermusic.recensioniseguite.domain;

import jakarta.persistence.*;
import lombok.*;

@Entity
@Data @NoArgsConstructor @AllArgsConstructor
public class Connessione {
    @Id
    private Long id;
    private String utente;
    private String seguito;
    private String ruolo;
}
