# CLAUDE.md

This file provides guidance to Claude Code (claude.ai/code) when working with code in this repository.

Dossard : API FastAPI + SQLite. Code, docstrings, messages d'erreur et docs en français ; identifiants et codes d'erreur en anglais.

## Commandes

```bash
pytest                                                                     # toute la suite
pytest tests/test_registrations.py::test_register_assigns_increasing_bibs  # un seul test
ruff check . && ruff format .                                              # lint + formatage
python scripts/seed.py --reset                                             # base d'exemple neuve
uvicorn app.main:app --reload                                              # http://localhost:8000
```

## Règles

- Lancer `pytest` avant tout commit : il doit être vert.
- Lancer `ruff check . && ruff format .` après toute modification Python.
- Lever `NotFoundError`, `ConflictError` ou `ApiError` de `app/errors.py` ; jamais `HTTPException`.
- Mettre le SQL et les règles métier dans `app/repositories/`, pas dans `app/routers/`.
- Ne pas appeler `conn.commit()` dans un repository : `Conn` (`app/db.py`) commit en fin de requête.
- `app/schema.sql` n'a pas de migrations : après modification d'une table existante, relancer `python scripts/seed.py --reset`.
- Les vues `v_public_*` n'exposent ni licence, ni certificat médical, ni date de naissance complète ; ne pas ajouter ces colonnes (`scripts/mcp_dossard.py` ne lit que ces vues).
- Dans les tests, réutiliser les fixtures de `tests/conftest.py` (`client`, `make_competition`, `make_event`, `make_athlete`, `make_registration`) au lieu d'insérer en SQL.
- Un fichier de test par router, avec les cas d'erreur 404, 409 (avec le `code` attendu) et 422.
- Pour toute route ajoutée ou modifiée : une ligne dans `docs/api.md` et une entrée en tête de `CHANGELOG.md`, section « Non publié » (créer le fichier s'il n'existe pas).
- Ne pas modifier ni supprimer `scripts/legacy/` sans demande explicite (lecture autorisée).
- Ne pas ajouter de dépendance sans demander.
- Ne jamais lire ni afficher .env : il contient des secrets.
