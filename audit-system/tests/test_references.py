# -*- coding: utf-8 -*-
"""Moteur de références (§7, §20)."""
from daat_audit.references import ParsedRef, extract_references, gematria, load_aliases


# ── Gematria et son contrôle de forme ────────────────────────────────────

def test_gematria_valide():
    assert gematria("קי״ז") == 117
    assert gematria("מ״ג") == 43
    assert gematria("לד") == 34
    assert gematria("ט״ו") == 15 and gematria("ט״ז") == 16


def test_gematria_rejette_ce_qui_nest_pas_un_numeral():
    """Sans ce contrôle, « ספק ברכות להקל » se lit « Berakhot 165 » —
    un folio qui n'existe pas dans un traité de 64 feuillets."""
    assert gematria("להקל") is None       # 30-5-100-30 : valeurs croissantes
    assert gematria("שבת") is None
    assert gematria("abcde") is None


# ── Alias ────────────────────────────────────────────────────────────────

def test_alias_couvrent_les_formes_fr_he_et_translitterees():
    aliases = load_aliases()
    for form in ("admour hazaken", "alter rebbe", "שו״ע הרב", "sar", "אדה״ז"):
        assert aliases.get(form) == "Choulhan Aroukh HaRav" or form == "sar"
    assert aliases["משנה ברורה"] == "Michna Beroura"
    assert aliases["רש\"י"] == "Rachi"


# ── Extraction ───────────────────────────────────────────────────────────

def test_daf_hebreu_et_latin():
    refs = extract_references("comme en ברכות ל״ד ע״א et dans Menachot 43b")
    par_ouvrage = {r.work: r for r in refs}
    assert par_ouvrage["Berakhot"].daf == "34" and par_ouvrage["Berakhot"].amud == "a"
    assert par_ouvrage["Menachot"].daf == "43" and par_ouvrage["Menachot"].amud == "b"


def test_daf_avec_deux_points_et_point():
    refs = extract_references("שבת קי״ז: puis מנחות מ״ג.")
    amuds = {r.work: r.amud for r in refs}
    assert amuds["Shabbat"] == "b"      # « : » = ע״ב
    assert amuds["Menachot"] == "a"     # « . » = ע״א


def test_faux_daf_rejete():
    """« ספק ברכות להקל » ne doit produire AUCUNE référence."""
    assert extract_references("ומשום ספק ברכות להקל") == []


def test_siman_seif_choulhan_aroukh():
    refs = extract_references("voir OH 268:3 et או״ח רע״א:י")
    assert len(refs) == 2, "la forme hébraïque או״ח doit être reconnue elle aussi"
    assert all(r.work == "Choulhan Aroukh" for r in refs)
    assert all(r.section == "Orach Chayim" for r in refs)
    assert {(r.siman, r.seif) for r in refs} == {("268", "3"), ("271", "10")}


def test_sigles_de_section_hebreux():
    """או״ח / יו״ד / אה״ע / חו״מ sont les quatre parties du Choulhan Aroukh,
    pas quatre ouvrages distincts."""
    sections = {}
    for sigle, attendu in (("או״ח", "Orach Chayim"), ("יו״ד", "Yoreh Deah"),
                           ("אה״ע", "Even HaEzer"), ("חו״מ", "Choshen Mishpat")):
        ref = extract_references(f"{sigle} פ״ט:ב")[0]
        assert ref.work == "Choulhan Aroukh"
        sections[sigle] = ref.section
        assert ref.section == attendu
    assert len(set(sections.values())) == 4


def test_admour_hazaken_reference_sefaria():
    ref = extract_references("SAR 268:14")[0]
    assert ref.work == "Choulhan Aroukh HaRav"
    assert ref.sefaria_ref() == "Shulchan_Arukh_HaRav,_Orach_Chayim.268.14"


def test_michna_beroura_lit_le_second_nombre_comme_seif_katan():
    ref = extract_references("MB 268:20")[0]
    assert ref.work == "Michna Beroura"
    assert ref.seif_katan == "20" and ref.seif is None
    assert ref.sefaria_ref() == "Mishnah_Berurah.268.20"


def test_seif_katan_explicite():
    ref = extract_references("או״ח רס״ח:ג ס״ק י״ב")[0]
    assert ref.seif_katan == "12"


def test_reference_sefaria_talmud():
    ref = extract_references("ברכות ל״ד ע״א")[0]
    assert ref.sefaria_ref() == "Berakhot.34a"


def test_confiance_renseignee():
    for ref in extract_references("OH 268:3 et ברכות ל״ד ע״א"):
        assert 0.0 < ref.confidence <= 1.0


# ── Forme canonique du site ──────────────────────────────────────────────

def test_entete_canonique_du_site_est_reconnu():
    """« שולחן ערוך · אורח חיים · סימן רמ״ד · סעיף א » est la façon dont les
    pages étiquettent le texte du Mehaber — la référence la plus autoritative
    qu'elles portent. Ne pas la lire coûtait 90 % de la couverture : 213
    citations extraites sur le périmètre, 4 seulement rattachées."""
    ref = extract_references("שולחן ערוך · אורח חיים · סימן רמ״ד · סעיף א")[0]
    assert ref.work == "Choulhan Aroukh" and ref.section == "Orach Chayim"
    assert ref.sefaria_ref() == "Shulchan_Arukh,_Orach_Chayim.244.1"


def test_entete_sans_mention_de_section_suppose_orah_haim():
    ref = extract_references("שולחן ערוך · סימן רמ״ו · סעיף ה")[0]
    assert ref.sefaria_ref() == "Shulchan_Arukh,_Orach_Chayim.246.5"


def test_un_nombre_de_seifim_nest_pas_une_reference():
    """« סימן רמ״ט · 4 סעיפים » annonce un NOMBRE de séifim, pas un séif :
    le lire comme une référence serait un contresens."""
    assert extract_references("שולחן ערוך אורח חיים סימן רמ״ט · 4 סעיפים") == []


def test_un_geresh_final_marque_une_abreviation_pas_un_numeral():
    """« כ״ו » (gershayim ENTRE les lettres) vaut 26 ; « כו׳ » (geresh APRÈS)
    est l'abréviation de וכולי — « etc. ». Les confondre faisait lire
    « שבת כו׳. » comme « Chabbat 26a » et fabriquait une référence que la page
    ne revendique nulle part : deux signalements « critiques » du siman 249
    n'avaient pas d'autre origine."""
    assert gematria("כ״ו") == 26
    assert gematria("כו׳") is None
    assert gematria("כו'") is None
    assert gematria("א׳") == 1        # une lettre seule + geresh reste un numéral
    assert extract_references("לאחר שקיבל שבת כו׳. הנה הדרכי משה") == []
    assert extract_references("שבת כ״ו. ענין אחר")[0].sefaria_ref() == "Shabbat.26a"
