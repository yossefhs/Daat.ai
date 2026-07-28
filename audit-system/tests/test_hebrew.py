# -*- coding: utf-8 -*-
"""Normalisation et comparaison hébraïques (§9, §20)."""
from daat_audit.hebrew import (
    Verdict,
    compare,
    defective_letters,
    expand_abbreviations,
    letters_only,
    normalize,
    strip_nikud,
)


# ── Normalisation ────────────────────────────────────────────────────────

def test_nikoud_retire_en_mode_normalise_mais_texte_original_intact():
    original = "שַׁבָּת קֹדֶשׁ"
    # Retirer le nikoud ne CONVERTIT pas la graphie : le holam de קֹדֶשׁ était
    # porté par la lettre, pas par un vav — il ne s'en crée pas un.
    assert strip_nikud(original) == "שבת קדש"
    assert original == "שַׁבָּת קֹדֶשׁ", "l'original ne doit jamais être modifié"


def test_guillemets_et_tirets_equivalents():
    assert normalize("«שבת»") == normalize('"שבת"') == normalize("שבת")


def test_abreviations_developpees():
    assert "הקדוש ברוך הוא" in expand_abbreviations("הקב״ה")
    assert "תנו רבנן" in expand_abbreviations("ת״ר")


def test_letters_only():
    assert letters_only("שַׁבָּת, קֹדֶשׁ!") == "שבתקדש"


# ── Graphie pleine / défective ───────────────────────────────────────────

def test_graphie_pleine_contre_defective_nest_pas_un_mot_remplace():
    """Isaïe 58:13 cité mot pour mot : Sefaria vocalise en graphie défective
    (עֹנֶג, מְכֻבָּד), le site écrit en graphie pleine (עונג, מכובד). Sans
    traitement, la citation exacte ressortait en « mot remplacé »."""
    verdict, ratio, _ = compare(
        "וקראת לשבת עונג לקדוש ה׳ מכובד",
        "וְקָרָאתָ לַשַּׁבָּת עֹנֶג לִקְדוֹשׁ ה׳ מְכֻבָּד וְכִבַּדְתּוֹ",
    )
    assert verdict is Verdict.DIFF_ORTHOGRAPHE
    assert ratio == 1.0


def test_defective_ne_touche_ni_le_vav_initial_ni_le_vav_final():
    """Neutraliser ces vav effacerait la conjonction « et » et les suffixes."""
    assert defective_letters("ובא") == "ובא"      # vav initial conservé
    assert defective_letters("לו") == "לו"        # mot de 2 lettres intact
    assert defective_letters("עונג") == "ענג"     # vav médian neutralisé


def test_defective_ne_touche_pas_le_yod():
    """בית ne doit jamais se confondre avec בת : mieux vaut un faux positif
    qu'une citation fautive déclarée conforme."""
    assert defective_letters("בית") != defective_letters("בת")


# ── Comparaison : les verdicts gradués du §9 ─────────────────────────────

SOURCE = "אמר רבי יוחנן משום רבי יוסי כל המענג את השבת נותנין לו נחלה בלי מצרים"


def test_identique():
    verdict, ratio, _ = compare("כל המענג את השבת נותנין לו נחלה בלי מצרים", SOURCE)
    assert verdict is Verdict.IDENTIQUE and ratio == 1.0


def test_difference_de_nikoud_seule_nest_pas_une_erreur():
    verdict, _, _ = compare("כָּל הַמְעַנֵּג אֶת הַשַּׁבָּת", SOURCE)
    assert verdict is Verdict.IDENTIQUE, "le nikoud ne doit pas créer d'écart"


def test_ponctuation_ignoree():
    verdict, _, _ = compare("כל המענג את השבת, נותנין לו נחלה — בלי מצרים!", SOURCE)
    assert verdict is Verdict.IDENTIQUE


def test_abreviation_face_a_la_forme_developpee():
    verdict, _, _ = compare("נשמה יתירה נותן הקב״ה באדם",
                            "נשמה יתירה נותן הקדוש ברוך הוא באדם ערב שבת")
    assert verdict is Verdict.IDENTIQUE


def test_citation_tronquee_dont_les_troncons_sont_litteraux():
    verdict, _, detail = compare("אמר רבי יוחנן… נחלה בלי מצרים", SOURCE)
    assert verdict is Verdict.CITATION_TRONQUEE
    assert "littéraux" in detail


def test_mot_remplace_detecte():
    """Le cas réel du siman 68 : un verbe changé retourne le sens."""
    verdict, ratio, detail = compare(
        "ואם בא לומר בסוף כל ברכה וברכה",
        "ואם בא לשוח בסוף כל ברכה וברכה ובתחלת כל ברכה וברכה",
    )
    assert verdict in (Verdict.MOT_REMPLACE, Verdict.MOT_SUPPRIME,
                       Verdict.VARIANTE_POSSIBLE)
    assert ratio < 1.0


def test_difference_substantielle():
    verdict, ratio, _ = compare("תנו רבנן שכר אינו ראוי לקידוש כלל וכלל", SOURCE)
    assert verdict is Verdict.DIFFERENCE_SUBSTANTIELLE
    assert ratio < 0.75


def test_un_troncon_litteral_ne_masque_pas_un_troncon_douteux():
    """Le premier tronçon est mot pour mot, le second seulement orthographique :
    c'est le second qui doit être rapporté (§9 — à gravité égale de ratio, le
    verdict le plus grave l'emporte)."""
    verdict, _, _ = compare(
        "וקראת לשבת עונג… לקדוש ה׳ מכובד",
        "וְקָרָאתָ לַשַּׁבָּת עֹנֶג לִקְדוֹשׁ ה׳ מְכֻבָּד",
    )
    assert verdict is Verdict.DIFF_ORTHOGRAPHE


def test_troncon_fabrique_dans_une_citation_coupee():
    """« A… B » où B est inventé : le verdict suit le PIRE tronçon."""
    verdict, _, _ = compare("אמר רבי יוחנן… דבר שלא נאמר מעולם בשום מקום", SOURCE)
    assert verdict is not Verdict.IDENTIQUE
    assert verdict is not Verdict.CITATION_TRONQUEE


def test_le_diff_se_limite_au_passage_correspondant():
    """Un folio du Talmud fait des milliers de mots : comparer une citation de
    dix mots à tout le folio produisait un écart illisible au lieu du mot
    réellement changé. Cas réel du siman 242 (Beitsa 15b)."""
    source = (
        "מאי כי חדות ה' היא מעוזכם אמר רבי יוחנן משום רבי אליעזר ברבי שמעון "
        "אמר להם הקדוש ברוך הוא לישראל בני לוו עלי וקדשו קדושת היום והאמינו בי ואני פורע "
        "בני לא לכם אני אומר אלא להללו שיצאו שמניחים חיי עולם ועוסקים בחיי שעה"
    )
    verdict, _, detail = compare(
        "אמר להם הבורא לישראל בני לוו עלי וקדשו קדשת היום והאמינו בי ואני פורע",
        source,
    )
    assert verdict is Verdict.MOT_REMPLACE
    assert "« הבורא » → « הקדוש ברוך הוא »" in detail
    # La seule autre différence est une graphie pleine : elle ne doit pas être
    # présentée comme un second mot remplacé.
    assert "קדשת" not in detail
