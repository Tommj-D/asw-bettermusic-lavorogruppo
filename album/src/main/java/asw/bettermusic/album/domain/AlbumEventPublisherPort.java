package asw.bettermusic.album.domain;

public interface AlbumEventPublisherPort {
    void publishAlbumCreated(Album album);
}
