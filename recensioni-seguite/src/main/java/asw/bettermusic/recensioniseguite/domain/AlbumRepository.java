package asw.bettermusic.recensioniseguite.domain;

import org.springframework.data.jpa.repository.Query;
import org.springframework.data.repository.CrudRepository;
import org.springframework.data.repository.query.Param;
import java.util.Collection;

public interface AlbumRepository extends CrudRepository<Album, Long> {
    Collection<Album> findByArtista(String artista);

    @Query("SELECT a FROM Album a JOIN a.generi g WHERE g = :genere")
    Collection<Album> findByGenere(@Param("genere") String genere);
}
