package asw.bettermusic.recensioni.domain;

import org.springframework.data.repository.CrudRepository;
import java.util.Optional;

public interface AlbumRepository extends CrudRepository<Album, Long> {
    Optional<Album> findByTitoloAndArtista(String titolo, String artista);
}
