# Changelog

## Non publié

- Modifie `GET /events/{event_id}/ranking` : renvoie désormais la liste nue des entrées (plus d'enveloppe `{"data", "count"}`) ; l'erreur 404 passe par `NotFoundError` (`not_found`).

- Ajoute `POST /athletes/import` : importe un CSV de licenciés (`text/csv`, `;`, dates `jj/mm/aaaa`) et renvoie `created`, `skipped` et `errors` par ligne (400 `invalid_csv`, `invalid_encoding`). Remplace `scripts/legacy/import_licencies.py`, supprimé.
- Ajoute `GET /health` : vérifie que l'API répond (`{"status": "ok"}`).
- Ajoute `GET /athletes/{athlete_id}` : détail d'un athlète (404 `not_found` s'il n'existe pas).
