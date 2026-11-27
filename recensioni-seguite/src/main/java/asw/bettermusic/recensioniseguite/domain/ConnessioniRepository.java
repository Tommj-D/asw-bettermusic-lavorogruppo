package asw.bettermusic.recensioniseguite.domain;

import org.springframework.data.repository.CrudRepository;
import java.util.Collection;

public interface ConnessioniRepository extends CrudRepository<Connessione, Long> {
    Collection<Connessione> findByUtente(String utente);
    void deleteByUtenteAndSeguitoAndRuolo(String utente, String seguito, String ruolo);
}
