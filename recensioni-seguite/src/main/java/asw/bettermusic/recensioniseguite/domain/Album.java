package asw.bettermusic.recensioniseguite.domain;

import jakarta.persistence.*;
import lombok.*;
import java.util.*;

@Entity
@Data @NoArgsConstructor @AllArgsConstructor
public class Album {
    @Id
    private Long id;
    private String titolo;
    private String artista;

    @ElementCollection(fetch = FetchType.EAGER)
    private Set<String> generi;
}
