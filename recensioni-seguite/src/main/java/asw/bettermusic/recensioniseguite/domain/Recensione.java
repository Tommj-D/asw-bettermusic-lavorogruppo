package asw.bettermusic.recensioniseguite.domain;

import jakarta.persistence.*;
import lombok.*;

@Entity
@Data @NoArgsConstructor @AllArgsConstructor
public class Recensione implements Comparable<Recensione> {
    @Id
    @EqualsAndHashCode.Include
    private Long id;
    private String recensore;
    private Long idAlbum;
    private String sunto;

    @Override
    public int compareTo(Recensione other) {
        return this.id.compareTo(other.id);
    }
}
