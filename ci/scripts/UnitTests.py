import os
import textwrap
from pathlib import Path

import pytest

# Title : Fichier contenant les tests unitaires pour les scripts de CI

# On importe les modules à tester pour les tests unitaires
from ci.scripts import CheckLinks
from ci.scripts import CheckDates
from ci.scripts import CheckImages
from ci.scripts import GenerateDocumentation

def test_CheckLinks_GetDomainOnly():
    """
    Permet de vérifier que GetDomainOnly extrait correctement le domaine d'une URL
    """
    url = "https://github.com/gdr-sdl/gdr-sdl/blob/dev/README.md"
    domaine = CheckLinks.GetDomainOnly(url)
    assert domaine == "https://github.com"

def test_CheckLinks_GetDomainOnly_additionnal():
    """
    Permet de tester des cas additionnels pour GetDomainOnly : port, http, url sans path
    """
    cases = {
        "http://example.com:8080/path/page.html": "http://example.com:8080",
        "https://sub.domain.example.org": "https://sub.domain.example.org",
        "https://example.com/": "https://example.com",
    }
    for url, expected in cases.items():
        assert CheckLinks.GetDomainOnly(url) == expected

def test_CheckLinks_GetLinks_and_InternalVerification(tmp_path):
    """
    Permet de vérifier que GetLinks extrait correctement les liens d'un fichier markdown
    et vérifie ces liens avec InternalVerification.

    Args:
        tmp_path : fixture pour créer des fichiers temporaires
    """
    # On crée un fichier markdown avec plusieurs types de liens
    dossier = tmp_path / "docs"
    dossier.mkdir()
    md_file = dossier / "page.md"
    target_file = dossier / "asset.pdf"

    contenu = textwrap.dedent("""
    Ceci est un test.

    Lien MD : [texte](./asset.pdf)
    Lien HTML : <a href="/static/other.png">img</a>
    <URL> : <https://example.com/page>
    Anchor : [bas](#section)
    """)
    md_file.write_text(contenu, encoding="utf-8")

    # On crée le fichier cible pour le lien relatif pour que InternalVerification puisse le trouver
    target_file.write_text("PDF content", encoding="utf-8")

    liens = CheckLinks.GetLinks(str(md_file))
    urls = [t[0] for t in liens]

    assert len(liens) >= 2
    assert any(u.endswith("asset.pdf") for u in urls)
    assert any(u.startswith("https://example.com") for u in urls)
    assert any("/static/other.png" in u for u in urls)

    relatif = "./asset.pdf"
    
    # Vérification des liens internes
    assert CheckLinks.InternalVerification(relatif, str(md_file)) is True
    assert CheckLinks.InternalVerification("nonexistent.txt", str(md_file)) is False

    try:
        CheckLinks.InternalVerification("#section", str(md_file))
    except Exception as e:
        pytest.fail(f" Erreur dans InternalVerification pour un anchor : {e}")

def test_CheckDates_FindAllMarkdown(tmp_path):
    """
    Permet de vérifier que FindAllMarkdown trouve correctement tous les fichiers markdown dans un répertoire

    Args:
        tmp_path : fixture pour créer des fichiers temporaires
    """
    root = tmp_path / "content"
    sub = root / "sub"
    sub.mkdir(parents=True)
    f1 = root / "a.md"
    f2 = sub / "b.md"
    f1.write_text("titre\n", encoding="utf-8")
    f2.write_text("titre\n", encoding="utf-8")

    found = CheckDates.FindAllMarkdown(str(root))

    # On normalise les chemins pour la comparaison
    found_set = {Path(p).resolve() for p in found}
    assert f1.resolve() in found_set
    assert f2.resolve() in found_set

def test_modules_expose_run():
    """
    Permet de vérifier que chaque module de script a une fonction run()
    """
    assert hasattr(CheckLinks, "run")
    assert hasattr(CheckDates, "run")
    assert hasattr(CheckImages, "run")
    assert hasattr(GenerateDocumentation, "run")

