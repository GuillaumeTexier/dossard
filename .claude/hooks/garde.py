#!/usr/bin/env python3
"""Hook PreToolUse : bloque les commandes shell destructrices.

Lit le JSON de Claude Code sur l'entrée standard. Pour les outils Bash et
PowerShell, refuse (code 2) les commandes contenant ``rm -rf`` (options dans
n'importe quel ordre), ``git push --force`` / ``-f`` ou ``DROP TABLE`` /
``DROP VIEW``. Dans tous les autres cas, sort avec le code 0.
"""

import json
import os
import re
import sys

OUTILS_SHELL = {"Bash", "PowerShell"}
SEPARATEURS = re.compile(r"&&|\|\||[;&|\n]")
DROP = re.compile(r"\bDROP\s+(TABLE|VIEW)\b", re.IGNORECASE)


def _options(jetons: list[str]) -> list[str]:
    """Retourne les options (jetons commençant par « - ») d'une liste."""
    return [j for j in jetons if j.startswith("-") and j != "-"]


def _rm_recursif_force(jetons: list[str]) -> bool:
    """Vrai si ``rm`` est appelé avec les options récursive et force."""
    for i, jeton in enumerate(jetons):
        if os.path.basename(jeton) != "rm":
            continue
        options = _options(jetons[i + 1 :])
        courtes = "".join(o[1:] for o in options if not o.startswith("--"))
        recursif = "r" in courtes.lower() or "--recursive" in options
        force = "f" in courtes or "--force" in options
        if recursif and force:
            return True
    return False


def _push_force(jetons: list[str]) -> bool:
    """Vrai si ``git push`` est appelé avec ``--force`` ou ``-f``."""
    if "git" not in jetons:
        return False
    debut = jetons.index("git")
    if "push" not in jetons[debut:]:
        return False
    options = _options(jetons[jetons.index("push", debut) + 1 :])
    for option in options:
        if option == "--force":
            return True
        if not option.startswith("--") and "f" in option[1:]:
            return True
    return False


def raison_blocage(commande: str) -> str | None:
    """Retourne la raison du blocage de la commande, ou None si elle passe."""
    if DROP.search(commande):
        return "DROP TABLE / DROP VIEW est interdit"
    for segment in SEPARATEURS.split(commande):
        jetons = [j.strip("\"'`()") for j in segment.split()]
        if _rm_recursif_force(jetons):
            return "rm -rf est interdit"
        if _push_force(jetons):
            return "git push --force est interdit"
    return None


def main() -> int:
    try:
        donnees = json.loads(sys.stdin.buffer.read().decode("utf-8"))
    except (ValueError, UnicodeDecodeError):
        return 0
    if not isinstance(donnees, dict) or donnees.get("tool_name") not in OUTILS_SHELL:
        return 0
    entree = donnees.get("tool_input")
    commande = entree.get("command") if isinstance(entree, dict) else None
    if not isinstance(commande, str):
        return 0
    raison = raison_blocage(commande)
    if raison is None:
        return 0
    message = f"Bloqué par le hook garde.py : {raison}\n"
    sys.stderr.buffer.write(message.encode("utf-8"))
    sys.stderr.buffer.flush()
    return 2


if __name__ == "__main__":
    sys.exit(main())
