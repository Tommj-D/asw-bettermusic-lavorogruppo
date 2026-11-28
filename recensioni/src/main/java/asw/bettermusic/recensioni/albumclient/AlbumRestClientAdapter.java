package asw.bettermusic.recensioni.albumclient;

import asw.bettermusic.recensioni.domain.*; 

import asw.bettermusic.album.api.rest.*; 

import org.springframework.stereotype.Service;
import org.springframework.beans.factory.annotation.Autowired;
import org.springframework.beans.factory.annotation.Qualifier;
import org.springframework.boot.autoconfigure.condition.ConditionalOnProperty;

import org.springframework.web.reactive.function.client.WebClient;
import org.springframework.web.reactive.function.client.WebClientException;
import reactor.core.publisher.Flux;
import reactor.core.publisher.Mono;

import java.util.*; 
import java.util.stream.*; 

@Service 
@ConditionalOnProperty(name = "asw.recensioni.albumclient.implementation", havingValue = "rest", matchIfMissing = true)
public class AlbumRestClientAdapter implements AlbumClientPort {

	@Autowired 
	@Qualifier("loadBalancedWebClient")
    private WebClient loadBalancedWebClient;

    public Album getAlbum(String titoloAlbum, String artistaAlbum) {
		Album album = null; 
        Mono<AlbumResponse> response = loadBalancedWebClient
                .get()
				.uri(builder -> builder
					.scheme("http")
					.host("album")
					.path("/cercaalbum")
					.queryParam("titolo", titoloAlbum)
					.queryParam("artista", artistaAlbum)
					.build())
                .retrieve()
                .bodyToMono(AlbumResponse.class);
        try {
            album = toAlbum(response.block());
        } catch (WebClientException e) {
            e.printStackTrace();
        }
		return album; 
    }

	private Album toAlbum(AlbumResponse response) {
		return new Album(response.getId(), response.getTitolo(), response.getArtista(), response.getGeneri());
	}

}
