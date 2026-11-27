package asw.bettermusic.recensioniseguite.domain;

import org.springframework.data.repository.CrudRepository;
import java.util.Collection;

public interface RecensioniRepository extends CrudRepository<Recensione, Long> {
    Collection<Recensione> findByRecensore(String recensore);
    Collection<Recensione> findByIdAlbum(Long idAlbum);
}
