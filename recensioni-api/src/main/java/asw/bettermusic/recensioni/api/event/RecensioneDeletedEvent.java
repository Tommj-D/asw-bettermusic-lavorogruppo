package asw.bettermusic.recensioni.api.event;

import lombok.*;

/* Evento di dominio: una recensione è stata cancellata. */
@Data @NoArgsConstructor @AllArgsConstructor
public class RecensioneDeletedEvent {

	private Long id;

}