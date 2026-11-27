package asw.bettermusic.recensioni.albumclient;

import asw.bettermusic.recensioni.domain.Album;
import asw.bettermusic.recensioni.domain.AlbumClientPort;
import asw.bettermusic.recensioni.domain.AlbumRepository;
import org.springframework.beans.factory.annotation.Autowired;
import org.springframework.boot.autoconfigure.condition.ConditionalOnProperty;
import org.springframework.stereotype.Service;

@Service
@ConditionalOnProperty(name = "asw.recensioni.albumclient.implementation", havingValue = "kafka")
public class AlbumLocalAdapter implements AlbumClientPort {

    @Autowired
    private AlbumRepository albumRepository;

    @Override
    public Album getAlbum(String titoloAlbum, String artistaAlbum) {
        return albumRepository.findByTitoloAndArtista(titoloAlbum, artistaAlbum).orElse(null);
    }
}
