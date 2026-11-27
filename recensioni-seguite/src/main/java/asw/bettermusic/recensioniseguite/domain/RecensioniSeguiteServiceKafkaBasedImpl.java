package asw.bettermusic.recensioniseguite.domain;

import org.springframework.beans.factory.annotation.Autowired;
import org.springframework.stereotype.Service;

import java.util.*;
import java.util.stream.Collectors;

@Service("RecensioniSeguiteServiceKafkaBasedImpl")
public class RecensioniSeguiteServiceKafkaBasedImpl
        implements RecensioniSeguiteService {

    @Autowired
    private ConnessioniRepository connessioniRepository;

    @Autowired
    private RecensioniRepository recensioniRepository;

    @Autowired
    private AlbumRepository albumRepository;

    @Override
    public Collection<Recensione> getRecensioniSeguite(String utente) {

        Collection<Recensione> recensioniSeguite = new TreeSet<>();

        Collection<Connessione> connessioni =
                connessioniRepository.findByUtente(utente);

        /* recensioni dei recensori seguiti */
        Collection<String> recensoriSeguiti = connessioni.stream()
                .filter(c -> c.getRuolo().equals("RECENSORE"))
                .map(Connessione::getSeguito)
                .collect(Collectors.toSet());

        for (String recensore : recensoriSeguiti) {
            recensioniSeguite.addAll(
                    recensioniRepository.findByRecensore(recensore)
            );
        }

        /* recensioni degli album degli artisti seguiti */
        Collection<String> artistiSeguiti = connessioni.stream()
                .filter(c -> c.getRuolo().equals("ARTISTA"))
                .map(Connessione::getSeguito)
                .collect(Collectors.toSet());

        Set<Album> albumDiArtistiSeguiti = new HashSet<>();

        for (String artista : artistiSeguiti) {
            albumDiArtistiSeguiti.addAll(
                    albumRepository.findByArtista(artista)
            );
        }

        for (Album album : albumDiArtistiSeguiti) {
            recensioniSeguite.addAll(
                    recensioniRepository.findByIdAlbum(album.getId())
            );
        }

        /* recensioni degli album dei generi seguiti */
        Collection<String> generiSeguiti = connessioni.stream()
                .filter(c -> c.getRuolo().equals("GENERE"))
                .map(Connessione::getSeguito)
                .collect(Collectors.toSet());

        Set<Album> albumDiGeneriSeguiti = new HashSet<>();

        for (String genere : generiSeguiti) {
            albumDiGeneriSeguiti.addAll(
                    albumRepository.findByGenere(genere)
            );
        }

        for (Album album : albumDiGeneriSeguiti) {
            recensioniSeguite.addAll(
                    recensioniRepository.findByIdAlbum(album.getId())
            );
        }

        return recensioniSeguite;
    }
}
