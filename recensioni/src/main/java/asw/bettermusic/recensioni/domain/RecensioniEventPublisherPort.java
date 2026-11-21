package asw.bettermusic.recensioni.domain;

import asw.bettermusic.recensioni.api.event.RecensioneDeletedEvent;

public interface RecensioniEventPublisherPort {

	void publishRecensioneDeletedEvent(RecensioneDeletedEvent event);

}