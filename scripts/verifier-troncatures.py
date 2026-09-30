#!/usr/bin/env python3
"""Une citation qui SAUTE un passage de sa source sans le dire — la porte née d'un cas témoin.

LE CAS TÉMOIN, 24 septembre 2026. En triant les 267 citations que
`verifier-fabrications.py` rend « introuvables » dans Hilkhot Chabbat, une d'elles
résistait à toutes les explications : « ונוהגין ללוש כדי שעור חלה בבית… »
(siman 242, niveau 4, FR et EN). C'est pourtant le Rama, mot pour mot, sur
Orah Haïm 242. Le diagnostic est tombé au caractère 45 du squelette consonantique :

    la source  …בשבת ויום טוב [סמך ממרדכי ריש מסכת ר״ה] והוא מכבוד שבת…
    la page    …בשבת ויום טוב, והוא מכבוד שבת…

La page saute le crochet de source que Sefaria place À L'INTÉRIEUR du texte du Rama,
et recolle les deux morceaux **sans points de suspension**, le tout entre guillemets.

POURQUOI AUCUNE AUTRE PORTE NE LE VOIT.
· `verifier-citations.py` cherche la citation dans la source : elle n'y est pas telle
  quelle, donc il la rend ABSENTE — le même verdict que pour une phrase inventée. Le
  lecteur du rapport ne peut pas distinguer les deux, et la pile devient inexploitable.
· `verifier-fabrications.py` demande à la recherche plein texte si la suite de mots
  existe : elle n'existe pas sous cette forme, donc « introuvable ». Même confusion.
· `verify-chabbat-source.py` et `verify-yd-source.py` jugent la RECOPIE du texte de base
  (les blockquote du niveau 1), pas les citations que les niveaux 2, 3 et 4 en tirent.

CE QUE CELLE-CI FAIT. Elle ancre la citation PAR LES DEUX BOUTS dans un même segment de
source : plus long préfixe, plus long suffixe. Quand les deux sont substantiels et que
leur somme couvre la citation, le texte existe des deux côtés d'un trou — et le trou est
imprimable. La porte dit alors ce qui a été sauté.

Une ellipse MARQUE la coupure, et la convention du dépôt le prévoit : « A… B » signifie
que A et B sont chacun verbatim. Une citation qui porte une ellipse est donc découpée à
l'ellipse et chaque morceau jugé seul, exactement comme le fait `verifier-fabrications.py`.
Ce que cette porte cherche, c'est la coupure NON MARQUÉE.

DEUX FAMILLES, ET LA SECONDE EST LA PLUS DANGEREUSE.
· LE TROU — la citation saute un passage du milieu et recolle les deux bords. C'est le cas
  témoin ci-dessus.
· LA COUPURE AVANT LA SUITE — la citation s'arrête juste avant la clause qui la retourne, et
  comme elle EST alors une sous-chaîne exacte de la source, aucune porte de citation ne peut
  la voir : elle est verbatim. Deux arbitres l'ont trouvée à la main, le même jour, sur deux
  simanim différents — le מגן אברהם רמ״ו ס״ק ו coupé sur שרי quand le mot suivant est אבל, et
  ce qui suit est le צריך עיון qui empêche d'en faire un היתר plat ; et שו״ע הרב רמ״ז:ב coupé
  sur אסור quand la source poursuit אלא אם כן יש שהות…, c'est-à-dire la condition qui le lève.
  Un correctif appliqué aux seuls cas vus n'est pas un correctif : d'où cette seconde mesure.
  Le signal est étroit à dessein — la suite doit commencer par un mot qui RETOURNE (אבל, אלא,
  ומיהו, וצ״ע, ודלא…) et la phrase ne doit pas s'être close entre-temps.

CE QU'ELLE COMPARE, ET CE QU'ELLE NE COMPARE PAS — dit en clair, parce qu'un plancher
annoncé comme un compte est l'erreur la plus coûteuse de ce dépôt. Les deux mesures
supposent que la source de la citation soit SOUS LA MAIN : elles confrontent la citation
à l'appareil du siman, téléchargé de Sefaria. Une citation dont l'ouvrage ne figure pas
dans cette table n'est donc pas « conforme » : elle n'est confrontée à RIEN. La sortie
compte désormais les deux populations séparément — CONFRONTÉES (retrouvées dans
l'appareil) et NON CONFRONTABLES (absentes de tout l'appareil) — et nomme, parmi les
secondes, celles dont le voisinage cite un daf de guemara ou un Richon : Sefaria les
indexe par folio, jamais par siman de Choul'han Aroukh, et cette porte-ci ne peut pas
les juger. Elle le DIT, au lieu de les rabattre sur l'ouvrage voisin.

ELLE REND DES CANDIDATS. Un trou peut être une variante d'édition — Sefaria n'est pas
l'édition que la page suit. Mais un crochet de source sauté, une clause retirée du milieu
d'un verbatim, une parenthèse d'attribution perdue sont chacun un défaut, et tous se
réparent de la même manière : rétablir le passage, ou écrire « … ».

╔══════════════════════════════════════════════════════════════════════════════════════╗
  L'ÉTAT MESURÉ, 29 septembre 2026 — et les chiffres d'avant sont à jeter, comme le
  furent les « 9 trous et 35 coupures » avant eux. La porte rabattait une citation
  non confrontable sur une œuvre VOISINE de l'appareil ; voir la note « L'ŒUVRE VISÉE »
  plus bas. Avant → après, à appareil et à corpus identiques :

                              Hilkhot Chabbat          Yoré Déa
    citations extraites          9 706 → 9 706      81 304 → 81 304
    jugeables                    7 128 → 7 128      70 875 → 70 875
    CONFRONTÉES                  5 917 → 5 917      60 686 → 60 686
    non confrontables            1 211 → 1 211      10 189 → 10 189
      · un daf/Richon nommé        295 →   816         809 → 8 548
      · rien ne l'explique          916 →   395       9 380 → 1 641
      · non situées dans la page    548 →     0       (non mesuré) → 1
    TROUS                           13 →     5         244 →    22
    COUPURES                        94 →    91       1 360 → 1 354

  AUCUN SIGNALEMENT NOUVEAU : les listes d'après sont des SOUS-ENSEMBLES de celles
  d'avant — zéro trou et zéro coupure ajoutés sur les deux sections. Ce tour ne
  fait que retirer, et c'est pourquoi le risque à surveiller n'était pas le bruit
  mais le MUTISME : trois corrections de ma propre correction ont été nécessaires,
  chacune trouvée en ouvrant à la main ce que je venais de faire taire (voir les
  notes du siman 342, du 318/263/287, et du siman 99 de Yoré Déa).

  DOUZE CITATIONS OUVERTES À LA MAIN contre Sefaria parmi les verdicts qui restent :
  NEUF réelles — un crochet de source sauté au milieu d'un verbatim (Chabbat 342,
  YD 99, YD 114, YD 91 Mehaber, YD 87 Chakh), une clause entière retirée
  (Chabbat 268 « וגומר אחריה ג' ברכות האחרונות », YD 91 Pit'hei Techouva
  « אין להקל », YD 109 « בין במינה בין שלא במינה »), un mot retiré (YD 190 « עליה »).
  DEUX fausses, et UNE limite.

  LES DEUX FAMILLES DE FAUX POSITIFS QUI RESTENT, déclarées et non fermées :
   1. L'ABRÉVIATION DÉVELOPPÉE. La page écrit en clair ce que la source abrège, si bien
      que les squelettes divergent sans qu'un passage ait été sauté. Mesuré : YD 118,
      la source porte « (כך דקדק התה״ד סי' ר' מאשיר״י פג״ה) » et la page
      « (כך דקדק התה״ד סימן ר׳ מאשיר״י פרק גיד הנשה) » — « סי' » et « פג״ה » développés,
      rien de sauté.
   2. LE SUFFIXE QUI S'ANCRE SUR UNE RÉPÉTITION PLUS LOIN. Mesuré : YD 89, la page écrit
      « אפילו » là où le Chakh abrège « אפי' » ; le préfixe s'ancre au bon endroit, le
      suffixe « כל היום כולו אסור » s'ancre sur la reprise de la même locution à la FIN
      du ס״ק, et le trou annoncé fait 119 consonnes pour une citation de 32.
  ELLES NE SONT PAS FERMÉES, ET C'EST UN CHOIX. Le garde-fou évident — « un trou plus
  long que la citation n'est pas un passage sauté » — écarterait YD 89 (119 pour 32)
  mais aussi YD 109 (32 pour 28), qui est RÉEL et vérifié. Poser un filtre non mesuré
  en fin de course est précisément ce qui a rendu cette porte muette quatre fois.
  Elles sont donc dites ici, pour le lecteur du relevé, et laissées au tour suivant.

  UNE LIMITE, ni vraie ni fausse : YD 141, « מכובדים אסורים · מבוזים מותרים ». C'est
  une ligne de TABLEAU de la synthèse, séparée par un « · », et le « trou » annoncé est
  la clause de motif « שודאי נעשו לשם אלילים ». Ce n'est pas un passage sauté d'une
  citation, c'est une condensation qui porte les marques d'une citation — donc un
  manquement à la convention du dépôt (`<em>résumé</em> :`), et non une troncature.
╚══════════════════════════════════════════════════════════════════════════════════════╝

Usage :
  python3 scripts/verifier-troncatures.py --path sources/shabbat/siman-242
  python3 scripts/verifier-troncatures.py --section shabbat [--bref]
  python3 scripts/verifier-troncatures.py 242 243 244
"""
import re, sys, os, json, glob, time, urllib.request, importlib.util

ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
# ⚠️ LE CACHE EST NUMÉROTÉ, et il le faut — mais il n'est PAS VERSIONNÉ, et la note qui
# tenait ici affirmait l'inverse de l'état du dépôt. Mesuré le 29 septembre 2026 :
# `.gitignore` globe `.cache-troncatures*.json` (ligne 49), le commit 2f5aa74d existe
# précisément pour garantir ce glob, et `git ls-files | grep cache` ne rend aucun des
# deux fichiers. Aucun cache de cette porte n'est suivi par git.
# CE QUI EST VRAI, et c'est la seule raison de NUMÉROTER le fichier : l'entrée gravée
# est la LISTE DES ŒUVRES téléchargées pour ce siman. Élargir APPAREIL_YD sans changer
# de nom ferait resservir l'ancien appareil — la porte élargie aurait continué de ne
# rien comparer, en silence et en vert. v2 = l'appareil du 29 septembre 2026.
CACHE = os.path.join(ROOT, ".cache-troncatures-v2.json")

# On réutilise l'extracteur de citations de la porte anti-fabrication : une porte qui
# n'extrait pas les MÊMES citations qu'une autre est une porte qui compare autre chose.
_spec = importlib.util.spec_from_file_location(
    "vf", os.path.join(ROOT, "scripts", "verifier-fabrications.py"))
_vf = importlib.util.module_from_spec(_spec)
_spec.loader.exec_module(_vf)
citations = _vf.citations

NIK = re.compile('[֑-ׇ]')
def sk(s):
    """Squelette consonantique, avec l'index de chaque consonne dans la chaîne d'origine."""
    out, idx = [], []
    for i, c in enumerate(NIK.sub(lambda m: '\u0000' * len(m.group()), s)):
        if 'א' <= c <= 'ת':
            out.append(c); idx.append(i)
    return ''.join(out), idx

def nomat_idx(chaine, idx):
    """La même chaîne sans matres lectionis, et l'index d'origine de chaque consonne.

    Le ktiv haser/malé est le faux positif dominant de tout ce dépôt : la MÊME phrase
    s'écrit מתר ou מותר, שעור ou שיעור. On neutralise donc le yod et le vav — mais en
    gardant la trace de l'index d'origine, faute de quoi le trou ne serait plus
    imprimable et la porte ne dirait pas ce qui a été sauté.
    """
    o, oi = [], []
    for c, i in zip(chaine, idx):
        if c in 'יו': continue
        o.append(c); oi.append(i)
    return ''.join(o), oi

def nomat(s): return re.sub(r'[יו]', '', s)

# L'appareil d'un siman. Le champ `ref` est contrôlé à chaque téléchargement : les formes
# X_on_Shulchan_Arukh,_Orach_Chayim.N rendent l'ŒUVRE ENTIÈRE avec un HTTP 200 et un `ref`
# sans numéro, et qui lit he[4] y lit le cinquième siman.
# Le sujet par défaut d'une page de siman : le Choul'han Aroukh de ce siman.
OEUVRES_BASE = 'Shulchan Arukh,'
OEUVRES = {
    'or': 'Shulchan_Arukh,_Orach_Chayim.{n}',
    'yd': "Shulchan_Arukh,_Yoreh_De'ah.{n}",
}
APPAREIL_OR = ['Mishnah_Berurah.{n}', 'Magen_Avraham.{n}',
               'Turei_Zahav_on_Shulchan_Arukh,_Orach_Chayim.{n}', 'Biur_Halacha.{n}',
               'Beit_Yosef,_Orach_Chaim.{n}', 'Shulchan_Arukh_HaRav,_Orach_Chayim.{n}',
               # ⚠️ AJOUTS MESURÉS, 29 septembre 2026. Sur 32 simanim de Hilkhot Chabbat,
               # 461 citations d'au moins 25 consonnes n'étaient retrouvées dans AUCUN
               # texte de cette table : elles n'étaient confrontées à rien, et la porte
               # COUPURE — qui exige la présence exacte — ne pouvait pas tourner sur
               # elles. Les quatre ouvrages ci-dessous en récupèrent 72.
               'Tur,_Orach_Chayim.{n}', 'Bach,_Orach_Chayim.{n}',
               'Arukh_HaShulchan,_Orach_Chaim.{n}',
               'Kaf_HaChayim_on_Shulchan_Arukh,_Orach_Chayim.{n}']
APPAREIL_YD = ["Siftei_Kohen_on_Shulchan_Arukh,_Yoreh_De'ah.{n}",
               "Turei_Zahav_on_Shulchan_Arukh,_Yoreh_De'ah.{n}",
               "Beit_Yosef,_Yoreh_Deah.{n}",
               # ⚠️ LE TROU MESURÉ. Cette table n'avait QUE les trois lignes ci-dessus :
               # ni le Pit'hei Techouva, ni le Baer Hetev, ni les Nekoudot HaKessef, ni
               # le Tour, ni le Bah, ni l'Aroukh HaChoul'han — c'est-à-dire l'essentiel
               # de l'appareil que les niveaux 2 et 4 de Yoré Déa citent. Mesuré sur 28
               # simanim : 4 450 citations d'au moins 25 consonnes absentes de la table,
               # dont 2 768 que ces six ouvrages retrouvent. Une citation du Pit'hei
               # Techouva était donc soit muette (la porte COUPURE ne trouvait pas la
               # phrase et passait), soit pire — elle s'ancrait par hasard sur le Beit
               # Yosef voisin et rendait un TROU imaginaire.
               "Pitchei_Teshuva_on_Shulchan_Arukh,_Yoreh_De'ah.{n}",
               "Beer_Hetev_on_Shulchan_Arukh,_Yoreh_De'ah.{n}",
               "Nekudot_HaKesef_on_Shulchan_Arukh,_Yoreh_De'ah.{n}",
               "Tur,_Yoreh_Deah.{n}", "Bach,_Yoreh_Deah.{n}",
               "Arukh_HaShulchan,_Yoreh_De'ah.{n}"]
# ÉCARTÉS, ET C'EST UNE MESURE, NON UNE OMISSION :
#  · Darkhei_Moshe (YD et OH) et Peri_Megadim…Eshel_Avraham et Kuntres_Acharon :
#    téléchargés et confrontés sur 28 simanim de Yoré Déa et 32 de Chabbat, ils
#    récupèrent ZÉRO citation. Les ajouter coûterait un appel par siman et
#    élargirait la surface d'ancrage sans rien confronter de plus.
#  · L'ALIGNEMENT DU TOUR SUR LE CHOUL'HAN AROUKH ÉTAIT SUPPOSÉ, il est maintenant
#    MESURÉ. `ref.endswith(str(n))` ne prouve que ceci : Sefaria a servi le siman
#    DEMANDÉ. Il ne prouve pas que le siman N du Tour traite la même matière que le
#    siman N du Mehaber — et c'est exactement l'écart qu'un faux ancrage produirait.
#    PREMIER ESSAI, DÉGÉNÉRÉ, et il faut le dire : comparer les fenêtres de 24 consonnes
#    partagées entre Tour N et Mehaber N donne ZÉRO partout (0 à 3 fenêtres sur 124
#    simanim). Le Choul'han Aroukh RÉÉCRIT le Tour, il ne le recopie pas : le test ne
#    mesurait rien et rendait « 52 sur la diagonale » par des égalités de zéros.
#    SECOND ESSAI, CONCLUANT — le VOCABULAIRE de fond, mots de quatre lettres et plus
#    présents dans huit simanim du compartiment au plus. Sur les 122 simanim de Hilkhot
#    Chabbat dont le Tour porte au moins dix mots rares : le recouvrement est MAXIMAL
#    sur la diagonale dans 118 cas, sur N-1 dans deux, sur N+1 dans deux. Recouvrement
#    moyen : 0,459 sur la diagonale contre 0,038 hors d'elle — un facteur douze. Les
#    quatre exceptions (simanim 256, 258, 281, 283) ont toutes un recouvrement inférieur
#    à 0,20 sur les trois positions, c'est-à-dire du bruit sur un Tour très court.
#    L'alignement tient donc, et il est mesuré ; ce n'est pas le cas du 'Hokhmat Adam
#    juste en dessous, et c'est pourquoi l'un est dans la table et l'autre non.
#  · Chokhmat_Adam.{n} est un PIÈGE : l'API rend « Chokhmat Adam 110 » avec un `ref`
#    qui finit par 110, donc la garde d'en-dessous l'accepte — mais le klal 110 du
#    'Hokhmat Adam n'a aucun rapport avec le siman 110 de Yoré Déa. Une œuvre n'entre
#    dans cette table que si son index EST le numéro de siman du Choul'han Aroukh.
#  · Kaf_HaChayim_on_Shulchan_Arukh,_Yoreh_De'ah.{n} EXISTE et est servi — l'absence de
#    cette ligne, quand Kaf_HaChayim…Orach_Chayim figure dans APPAREIL_OR, était
#    l'asymétrie de compartiment contre laquelle CLAUDE.md prévient, et elle ne
#    figurait dans NI L'UNE NI L'AUTRE des deux listes. Elle est ici, avec sa mesure.
#    Rendement, 29 septembre 2026, sur les simanim 87, 92, 99, 110, 119, 129, 160, 183,
#    200 et 234 de Yoré Déa : 610 citations non confrontables, dont Kaf HaChayim en
#    retrouve DEUX — une au siman 87, une au 99, soit 0,33 %. Et sur CINQ des dix
#    (129, 160, 183, 200, 234) Sefaria ne sert AUCUN segment : l'ouvrage s'arrête bien
#    avant la fin de Yoré Déa. Un appel de plus par siman sur 148 simanim pour deux
#    citations, et surtout une surface d'ancrage élargie de 322 segments au siman 69 —
#    or c'est exactement la surface élargie qui fabrique les faux TROUS que ce tour
#    ferme. Écarté sciemment, et non oublié.
#  · Le TALMUD n'y entre pas et ne le peut pas : son ref est « Traité.daf(a|b) », un
#    folio, et non « Œuvre,_Section.siman ». Une citation de guemara faite dans une page
#    de Yoré Déa n'est donc pas confrontable par cette porte — elle est COMPTÉE COMME
#    TELLE et imprimée à part, jamais rabattue sur un ouvrage voisin.

# Ce qui, nommé auprès d'une citation, prouve que la citation ne vient PAS du siman :
# un folio de guemara, ou un Richon que Sefaria n'indexe pas par siman de Choul'han
# Aroukh. Ces citations sont NON CONFRONTABLES par cette porte, et le dire est le
# contraire de les taire.
_MASS = ('שבת|ברכות|פסחים|עירובין|ביצה|מנחות|חולין|יבמות|נדה|סוכה|מגילה|תענית|יומא|'
         'סנהדרין|כתובות|גיטין|קידושין|קדושין|בבא קמא|בבא מציעא|בבא בתרא|מועד קטן|'
         'ראש השנה|עבודה זרה|סוטה|נדרים|שבועות|זבחים|בכורות|ערכין|תמורה|כריתות|מכות|'
         'הוריות|חגיגה')
# Le daf DOIT porter sa marque — amoud ou point. Sans elle, « שבת » est le jour de
# Chabbat, pas le traité ; c'est le même piège que la guématrie, pris par l'autre bout.
#
# ⚠️ ET CE MOTIF N'AVAIT PAS DE FRONTIÈRE DE MOT À DROITE — le piège documenté du dépôt
# pris par l'autre bout, exactement. Le nom de traité était gardé à gauche par
# `(?<![א-ת])` et par rien à droite, si bien que « ברכותיהם: » se lisait « traité
# ברכות + daf יהם + deux-points ». Et la marque de daf acceptait un simple point, ce
# qui suffisait à faire passer « שבת בבוקר. », « שבת גדול. », « סוכה נאה. » pour des
# folios. Effet MESURÉ sur Hilkhot Chabbat, 29 septembre 2026, avant correction : 226
# citations classées DAF, dont 130 par une marque d'amoud explicite et 96 par le SEUL
# point — le sous-compte « dont un daf est nommé auprès » était donc gonflé, et le
# résidu « rien n'explique l'absence » MINORÉ d'autant, c'est-à-dire flatteur.
#
# TROIS VERROUS, et chacun répond d'un faux positif observé :
#  1. LA FRONTIÈRE DE DROITE sur le nom de traité, `(?![א-ת])` — elle seule tue
#     « ברכותיהם ». Avec, à gauche, UN SEUL caractère de préfixe pris dans un ensemble
#     FERMÉ (ב ל מ ד ו כ ש ה), lui-même gardé par `(?<![א-ת])` : sans cela
#     « ביבמות (קיד ע״א) » — la forme la plus courante du dépôt — n'était pas reconnue
#     du tout, et c'est ainsi que les trois pages du siman 343 passaient pour
#     « rien n'explique l'absence » alors que la page nomme son daf.
#  2. LE NUMÉRAL EST VALIDÉ, non pas compté en lettres. Un numéral hébraïque se lit en
#     valeurs STRICTEMENT DÉCROISSANTES : כג = 20+3, קיח = 100+10+8, קמ״ה = 100+40+5.
#     « בבוקר » (2,2,6,100,200), « גדול » (3,4,6,30) et « נאה » (50,1,5) ne décroissent
#     pas, et « יהם » se termine par une finale. C'est le même raisonnement que le
#     gershayim exigé ailleurs, mais il ne dépend pas d'une marque que la source
#     n'écrit pas toujours — « שבת קמה. » est un daf sans gershayim.
#  3. LES DEUX EXCEPTIONS D'USAGE, טו et טז, qu'aucune règle de décroissance n'admet.
_VAL = {'א':1,'ב':2,'ג':3,'ד':4,'ה':5,'ו':6,'ז':7,'ח':8,'ט':9,
        'י':10,'כ':20,'ל':30,'מ':40,'נ':50,'ס':60,'ע':70,'פ':80,'צ':90,
        'ק':100,'ר':200,'ש':300,'ת':400}
FINALES = {'ך':20,'ם':40,'ן':50,'ף':80,'ץ':90}

def numeral_hebreu(t):
    """La valeur du numéral, ou None si ce n'en est pas un.

    Une finale n'est admise qu'en DERNIÈRE position, et la suite doit décroître
    strictement : c'est ce qui écarte « יהם » (10, 5, 40) autant que « בבוקר ».
    """
    lettres = [c for c in t if 'א' <= c <= 'ת']
    if not lettres or len(lettres) > 4: return None
    if ''.join(lettres) in ('טו', 'טז'):
        return 15 if lettres[1] == 'ו' else 16
    vals = []
    for k, c in enumerate(lettres):
        if c in _VAL: vals.append(_VAL[c])
        elif c in FINALES and k == len(lettres) - 1: vals.append(FINALES[c])
        else: return None
    for a, b in zip(vals, vals[1:]):
        if a <= b: return None
    return sum(vals)

_RE_DAF_BRUT = re.compile(
    r'(?<![א-ת])[בלמדוכשה]?(?:' + _MASS + r')(?![א-ת])'        # le traité, borné DES DEUX CÔTÉS
    r'[\s‏]*\(?[\s]*'
    r'(?P<num>[א-ת]{1,2}["״][א-ת]{1,2}|[א-ת]{1,3})[\'׳]?[\s]*'
    r'(?:ע["״]?[אב](?![א-ת])|[.:])')

def nomme_un_daf(ctx):
    """Un folio de guemara est-il nommé ici ? Rend le passage trouvé, ou None.

    Le motif rend des CANDIDATS ; c'est `numeral_hebreu` qui tranche. Un motif seul ne
    peut pas le faire : la marque de daf est parfois un simple point, et tout mot hébreu
    court suivi d'un point ressemble alors à un folio.
    """
    for m in _RE_DAF_BRUT.finditer(ctx):
        if numeral_hebreu(m.group('num')) is not None:
            return m
    return None

# Gardé pour l'API : `RE_DAF.search` reste appelable, mais passe par la validation.
class _DafCompat:
    def search(self, ctx): return nomme_un_daf(ctx)
RE_DAF = _DafCompat()
RE_RICHON = re.compile(r'רמב["״]ם|רמב["״]ן|רא["״]ש(?![א-ת])|רשב["״]א|ריטב["״]א|'
                       r'(?<![א-ת])ר["״]ן(?![א-ת])|(?<![א-ת])רי["״]ף(?![א-ת])|'
                       r'(?<![א-ת])רש["״]י(?![א-ת])|תוס[\'׳](?![א-ת])|תוספות|'
                       r'(?<![א-ת])מרדכי(?![א-ת])|ראב["״]ד|Rambam|Mishneh\s+Torah')

# ═══════════════════════════════════════════════════════════════════════════════════
# L'ŒUVRE VISÉE — et c'est le défaut qui a valu ce tour de correction.
#
# LE MÉCANISME, établi par un arbitre le 29 septembre 2026. Une citation absente de tout
# l'appareil était comptée NON CONFRONTABLE… puis passée à `juger()` quand même, qui
# l'ancrait par les deux bouts sur le PREMIER texte de l'appareil où les deux ancres
# tombaient. L'en-tête de cette porte affirmait « jamais rabattue sur un ouvrage
# voisin » ; le code le faisait à chaque tour.
#
# LE CAS TÉMOIN. Siman 263, niveau 2, FR et EN : « אמר רב הונא: הרגיל בנר הויין ליה
# בנים תלמידי חכמים », et la page écrit juste après « (שבת כ״ג ע״ב) ». C'est une
# guemara, citée verbatim, et elle EST dans Shabbat 23b. Le Tour d'Orah Haïm 263
# paraphrase la même guemara — « ויהא זהיר לעשות נר יפה דאמר רב הונא הרגיל בנר שבת… » —
# si bien que le préfixe de 17 consonnes de la citation y est, son suffixe de 23 y est,
# et les deux sont à VINGT consonnes l'une de l'autre : deux ancres voisines, non deux
# locutions courantes trouvées au hasard. La porte accusait donc le TOUR d'un trou pour
# une citation talmudique EXACTE. Le défaut est systématique : le Tour, le Bah et
# l'Aroukh HaChoul'han citent des guemarot constamment.
#
# LA FERMETURE. Une citation ne reçoit un verdict QUE contre l'œuvre que la page NOMME
# auprès d'elle. Trois issues, et les trois sont comptées à la sortie :
#  · l'œuvre visée est hors de portée de cette porte (un daf, un Richon) → aucun verdict ;
#  · aucune œuvre n'est nommée auprès de la citation → aucun verdict, faute de savoir
#    contre qui l'on parlerait ;
#  · une œuvre de l'appareil est nommée → verdict recevable, mais CONTRE ELLE SEULE.
#
# ⚠️ ET LA NAÏVETÉ QU'IL A FALLU ÉVITER : prendre « un Richon est nommé dans les 220
# caractères d'avant » pour « la citation vient d'un Richon ». Au siman 342 la page
# écrit « בית יוסף — … וצירף את דברי הרמב״ם … והרא״ש. השו״ע פסק בסעיף יחיד : "…" » : le
# Rambam et le Rosh y sont nommés, mais l'œuvre VISÉE est le שו״ע, nommé juste avant les
# guillemets, et le trou signalé contre lui est RÉEL — la page saute le renvoi
# « (ועיין לעיל סי' רס״א וסוף סי' ש״ז) » que Sefaria place DANS le texte du Mehaber, et
# la page cite ce renvoi à part deux phrases plus loin. Un veto posé sur la simple
# présence d'un Richon dans le voisinage aurait éteint ce défaut-là. On prend donc le
# nom le PLUS PROCHE, des deux côtés, et le plus long à égalité de distance — sans quoi
# « שו״ע הרב » se lit « שו״ע ».
# ⚠️ LE PRÉFIXE D'UN SEUL CARACTÈRE, ET IL A FAILLI ME COÛTER LE SEUL VRAI TROU DU LOT.
# Les sigles hébreux portent presque toujours l'article ou une conjonction : la page
# écrit « הַשו״ע פסק », « והמ״ב », « לפי הט״ז ». Un `(?<![א-ת])` nu REFUSE ces formes,
# puisque le caractère précédent EST une lettre hébraïque. Or les motifs de Richonim,
# eux, n'avaient pas de garde à gauche du tout et attrapaient « הרמב״ם » et « הרא״ש »
# sans difficulté. Effet observé au siman 342 : la page nomme le שו״ע juste devant les
# guillemets et le Rambam quarante caractères plus loin ; « השו״ע » étant invisible, le
# Rambam gagnait, l'œuvre visée passait pour hors de portée, et le trou RÉEL — le renvoi
# « ועיין לעיל סי' רס״א וסוף סי' ש״ז » sauté au milieu d'un verbatim du Mehaber — était
# refusé en silence. La fermeture aurait échangé trois faux TROUS contre un vrai.
# L'ensemble est FERMÉ, et gardé à sa propre gauche : c'est le même compromis que pour
# les noms de traités dans `_RE_DAF_BRUT`, et pour la même raison.
# Jusqu'à DEUX caractères : « והמ״ב » en porte deux, et un seul les manquait tous.
_PFX = r'(?<![א-ת])[הובלכמדש]{0,2}'
NOMS = [
    # (préfixe du `ref` Sefaria, ou None = HORS DE PORTÉE de cette porte, motif)
    (None,                   re.compile(r'רמב["״]ם|רמב["״]ן|רא["״]ש(?![א-ת])|רשב["״]א|'
                                        r'ריטב["״]א|' + _PFX + r'ר["״]ן(?![א-ת])|'
                                        r'' + _PFX + r'רי["״]ף(?![א-ת])|' + _PFX + r'רש["״]י(?![א-ת])|'
                                        r'תוס[\'׳](?![א-ת])|תוספות|' + _PFX + r'מרדכי(?![א-ת])|'
                                        r'ראב["״]ד|Rambam|Mishneh\s+Torah')),
    ('Shulchan Arukh HaRav',  re.compile(r'שו["״]ע\s*הרב|שוע["״]ה|אדמו["״]ר\s*הזקן|'
                                        r'אדה["״]ז|Shulchan\s+Arukh\s+HaRav|'
                                        r'Choul[\'’]?han\s+Aroukh\s+HaRav|(?<![A-Za-z])SAR(?![A-Za-z])')),
    # ⚠️ « מ״ב » EST AUSSI LA GUÉMATRIE 42, et CLAUDE.md le dit noir sur blanc : le sigle
    # ne compte que s'il n'est PAS suivi d'une marque de folio. Mesuré au siman 318 :
    # la page écrit « (שבת ל״ח:-מ״ב.) : שבת מ׳ ע״ב ומ״ב ע״א » — deux dafim de Chabbat —
    # et le « ומ״ב » y était lu « Michna Beroura », plus proche que le daf qui le
    # précède, si bien que l'œuvre visée d'une citation TALMUDIQUE devenait la Michna
    # Beroura. C'est le piège de RE_MB de verifier-citations.py, retrouvé ici.
    ('Mishnah Berurah',      re.compile(r'משנה\s*ברורה|'
                                        + _PFX + r'מ["״]ב(?![א-ת])(?![\s]*(?:ע["״]?[אב]|[.:]))|'
                                        r'Mishnah\s+Berurah|Michna\s+Beroura')),
    ('Magen Avraham',        re.compile(r'מגן\s*אברהם|' + _PFX + r'מג["״]א(?![א-ת])|Magen\s+Avraham')),
    ('Biur Halacha',         re.compile(r'ביאור\s*הלכה|באור\s*הלכה|' + _PFX + r'ביה["״]ל(?![א-ת])|'
                                        r'Biur\s+Halacha|Bi.our\s+Halakha')),
    ('Turei Zahav',          re.compile(r'טורי\s*זהב|' + _PFX + r'ט["״]ז(?![א-ת])|(?<![A-Za-z])Taz(?![A-Za-z])')),
    ('Siftei Kohen',         re.compile(r'שפתי\s*כהן|' + _PFX + r'ש["״]ך(?![א-ת])|(?<![A-Za-z])Shakh(?![A-Za-z])|'
                                        r'Siftei\s+Kohen')),
    ('Pitchei Teshuva',      re.compile(r'פתחי\s*תשובה|' + _PFX + r'פת["״]ש(?![א-ת])|Pitchei\s+Teshuva')),
    ('Beer Hetev',           re.compile(r'באר\s*היטב|Beer\s+Hetev')),
    ('Nekudot HaKesef',      re.compile(r'נקודות\s*הכסף|' + _PFX + r'נקוה["״]כ(?![א-ת])|Nekudot\s+HaKesef')),
    ('Arukh HaShulchan',     re.compile(r'ערוך\s*הש[ול]לחן|ערוך\s*השלחן|ערוך\s*השולחן|'
                                        r'' + _PFX + r'ערוה["״]ש(?![א-ת])|Arukh\s+HaShulchan|'
                                        r'Aroukh\s+HaChoul')),
    ('Kaf HaChayim',         re.compile(r'כף\s*החיים|' + _PFX + r'כה["״]ח(?![א-ת])|Kaf\s+HaChayim')),
    ('Beit Yosef',           re.compile(r'בית\s*יוסף|' + _PFX + r'ב["״]י(?![א-ת])|Beit\s+Yosef')),
    ('Bach',                 re.compile(r'בית\s*חדש|' + _PFX + r'ב["״]ח(?![א-ת])|(?<![A-Za-z])Bach(?![A-Za-z])')),
    # « טור » est gardé des deux côtés : « טורי זהב » porte un י et ne peut pas le prendre.
    ('Tur',                  re.compile(r'' + _PFX + r'ה?טור(?![א-ת])|(?<![A-Za-z])Tour(?![A-Za-z])|'
                                        r'(?<![A-Za-z])Tur(?![A-Za-z])')),
    ('Shulchan Arukh,',      re.compile(r'ש[ול]לחן\s*ערוך|שלחן\s*ערוך|שולחן\s*ערוך|'
                                        r'' + _PFX + r'שו["״]ע(?![א-ת])|' + _PFX + r'ה?מחבר(?![א-ת])|'
                                        r'' + _PFX + r'רמ["״]א(?![א-ת])|' + _PFX + r'ה?גה(?![א-ת])|'
                                        r'Choul[\'’]?han\s+Aroukh|Shulchan\s+Arukh|'
                                        r'(?<![A-Za-z])Mehaber(?![A-Za-z])|(?<![A-Za-z])Rama(?![A-Za-z])')),
]

def situer(P_sk, P_idx, s0, plaine):
    """Où la citation se trouve-t-elle DANS LA PAGE ? (début, fin) en index bruts.

    ⚠️ PAR LE SQUELETTE, ET C'EST UNE RÉPARATION. La version précédente cherchait
    `plaine.find(c[:40])` — la citation telle que l'extracteur la rend, c'est-à-dire
    DÉPOUILLÉE de son nikoud. Or les pages de ce dépôt sont largement VOCALISÉES : au
    siman 263 la page porte « אָמַר רַב הוּנָא », l'extracteur rend « אמר רב הונא », et
    `find` échouait. Mesuré sur Hilkhot Chabbat avant correction : sur 1 211 citations
    non confrontables, 548 — quarante-cinq pour cent — n'avaient AUCUN contexte examiné,
    et tombaient donc d'office dans « rien n'explique l'absence ». C'est le même piège
    que la comparaison des squelettes dans `couper_avant_la_suite`, à l'autre bout de
    la porte.

    ⚠️ ET LA FENÊTRE PART DE LA FIN DE LA CITATION, non de son début. L'ancienne prenait
    `plaine[i-220 : i+40]` : sur une citation de 150 caractères, les quarante d'après le
    DÉBUT tombent encore dans la citation, si bien que la référence qui la suit — et la
    convention du dépôt est « … » (שבת כ״ג ע״ב), la référence APRÈS les guillemets —
    n'était jamais lue.
    """
    n = len(s0)
    if n == 0: return None
    i = P_sk.find(s0)
    if i < 0:
        court = s0[:max(14, n // 2)]
        i = P_sk.find(court)
        if i < 0: return None
        n = len(court)
    j = min(i + n - 1, len(P_idx) - 1)
    return P_idx[i], min(len(plaine), P_idx[j] + 1)

def oeuvre_visee(plaine, bornes, avant=260, apres=160):
    """L'œuvre que la page NOMME le plus près de la citation.

    Rend (nom, cible) — `cible` étant le préfixe du `ref` Sefaria, ou None quand l'œuvre
    est hors de portée d'une porte indexée par siman — ou None si rien n'est nommé.
    """
    deb, fin = bornes
    gauche = plaine[max(0, deb - avant):deb]
    droite = plaine[fin:fin + apres]
    # ⚠️ LA PARENTHÈSE QUI SUIT LA CITATION PASSE AVANT TOUT LE RESTE, et c'est la
    # convention du dépôt elle-même : « citation » (ouvrage référence). Le plus proche
    # ne suffisait pas, et le siman 254 l'a montré — la page écrit, en FRANÇAIS, « il
    # ajoute que telle est aussi l'opinion du Rambam. » juste avant les guillemets, et
    # la référence réelle est « (מג״א או״ח רנ״ד ס״ק ט״ו) » juste après. Le Rambam
    # gagnait de neuf caractères, l'œuvre visée passait pour hors de portée, et une
    # coupure du Magen Avraham était tue. La prose NOMME un auteur ; la parenthèse
    # DONNE la référence. Quand la seconde existe, elle tranche.
    par = re.match(r'[\s»« ,;:.\]\[]{0,24}\(([^()]{2,90})\)', droite)
    if par:
        dedans = par.group(1)
        pris = []
        for cible, rx in NOMS:
            m = rx.search(dedans)
            if m: pris.append((m.start(), -(m.end() - m.start()), cible, m.group(0)))
        m = nomme_un_daf(dedans)
        if m: pris.append((m.start(), -(m.end() - m.start()), None, m.group(0)))
        if pris:
            pris.sort(key=lambda t: (t[0], t[1]))
            return pris[0][3], pris[0][2]
    cands = []
    for cible, rx in NOMS:
        for m in rx.finditer(gauche):
            cands.append((len(gauche) - m.end(), -(m.end() - m.start()), cible, m.group(0)))
        for m in rx.finditer(droite):
            cands.append((m.start(), -(m.end() - m.start()), cible, m.group(0)))
    m = nomme_un_daf(gauche)
    if m: cands.append((len(gauche) - m.end(), -(m.end() - m.start()), None, m.group(0)))
    m = nomme_un_daf(droite)
    if m: cands.append((m.start(), -(m.end() - m.start()), None, m.group(0)))
    if not cands: return None
    cands.sort(key=lambda t: (t[0], t[1]))
    return cands[0][3], cands[0][2]

def plat(x):
    if isinstance(x, str): return x
    if isinstance(x, list): return ' '.join(plat(y) for y in x)
    return ''

_cache = {}
if os.path.exists(CACHE):
    try: _cache = json.load(open(CACHE, encoding='utf-8'))
    except Exception: _cache = {}

def appareil(n, section):
    """[(ref, texte brut)] — le texte est gardé BRUT pour pouvoir imprimer le trou.

    ⚠️ UN CACHE NE PERSISTE JAMAIS UN RÉSULTAT INCOMPLET. La version précédente écrivait
    `_cache[cle] = out` quoi qu'il arrive : un seul 503 de Sefaria, et le siman était
    gravé à trois textes au lieu de neuf — ou à zéro — pour toujours, la porte restant
    verte et muette sur lui sans que rien ne le dise. On ne grave donc l'entrée que si
    TOUS les téléchargements ont abouti ; sinon on rend ce qu'on a et on n'écrit rien.
    Un appareil réellement vide (Sefaria ne sert rien pour ce siman) est une entrée
    légitime, mais `main` la signale à voix haute : c'est une porte qui ne compare rien.

    ⚠️ ET LA JUSTIFICATION QUI ACCOMPAGNAIT CETTE RÈGLE ÉTAIT FAUSSE. Elle donnait pour
    preuve « l'entrée yoreh-deah:169 du cache v1 est vide, donc un 503 l'a gravée ».
    Non : mesuré le 29 septembre 2026, les quatre textes de l'ancienne table pour
    Yoré Déa 169 — Mehaber, Chakh, Taz, Beit Yosef — rendent CHACUN un HTTP 200 avec
    `he = []`. C'est un appareil LÉGITIMEMENT vide, et l'entrée vide du cache v1 en est
    le reflet exact, non la trace d'une panne. La règle reste juste et reste posée ;
    ce qu'elle protège est l'échec RÉSEAU, qu'aucune entrée observée n'illustre. Une
    règle vraie adossée à une preuve fausse est une règle qu'on retirera au prochain
    doute : elle est donc adossée ici à ce qui l'exige réellement, le `continue` sur
    `not ok` quelques lignes plus bas, qui rend un appareil PARTIEL indiscernable d'un
    appareil complet une fois gravé.
    """
    cle = f'{section}:{n}'
    if cle in _cache: return _cache[cle]
    modeles = ([OEUVRES['yd']] + APPAREIL_YD) if section == 'yoreh-deah' \
              else ([OEUVRES['or']] + APPAREIL_OR)
    out, complet = [], True
    for m in modeles:
        url = f'https://www.sefaria.org/api/texts/{m.format(n=n)}?context=0&pad=0'
        ok = False
        for essai in range(3):
            try:
                with urllib.request.urlopen(url, timeout=30) as r:
                    d = json.load(r)
                ok = True
                break
            except Exception:
                time.sleep(1 + essai)
        if not ok:
            complet = False
            continue
        ref = str(d.get('ref', ''))
        if not ref.rstrip().endswith(str(n)):
            continue                      # le piège : l'œuvre entière sans dire non
        he = d.get('he')
        for b in (he if isinstance(he, list) else [he]):
            t = re.sub(r'<[^>]+>', ' ', plat(b))
            t = re.sub(r'\s+', ' ', t).strip()
            if t: out.append((ref, t))
        time.sleep(0.12)
    if complet:
        _cache[cle] = out
        # …et l'écriture est ATOMIQUE. `json.dump` sur le fichier lui-même le tronque
        # AVANT d'écrire : une interruption au milieu laisse un JSON coupé net, que la
        # lecture d'en-tête rattrape en repartant d'un cache vide — donc en retéléchargeant
        # 282 appareils. Ce n'est pas une porte fausse, mais c'est une porte qu'on ne
        # relance plus. On écrit à côté, puis on remplace.
        try:
            tmp = CACHE + '.tmp'
            with open(tmp, 'w', encoding='utf-8') as fh:
                json.dump(_cache, fh, ensure_ascii=False)
            os.replace(tmp, CACHE)
        except Exception: pass
    return out

def preparer(segs):
    """Les squelettes d'un appareil, calculés UNE FOIS par siman.

    Ils l'étaient auparavant pour CHAQUE citation et CHAQUE segment : sur Yoré Déa,
    81 000 citations contre plusieurs centaines de segments. Les précalculer ne change
    rien au verdict et rend l'élargissement de l'appareil tenable.
    """
    out = []
    for ref, brut in segs:
        b0, b0idx = sk(brut)
        b1, b1idx = nomat_idx(b0, list(range(len(b0))))
        out.append((ref, brut, b0, b0idx, b1, b1idx))
    # ⚠️ ET LA CONCATÉNATION, qui n'est pas un raffinement mais la condition pour que la
    # porte élargie tourne du tout. `presente` demandée segment par segment, c'est un
    # balayage de chaîne par segment ET par citation : sur Yoré Déa, 67 000 citations
    # contre près de mille segments une fois l'appareil complété. Le premier balayage
    # lancé ainsi avançait de six simanim par vingt-cinq minutes — une dizaine d'heures
    # pour les deux sections, c'est-à-dire une porte que personne ne lancerait. Un
    # séparateur que l'hébreu ne contient jamais interdit qu'une citation soit reconnue
    # à cheval sur deux segments : le verdict est le même, à la vitesse près.
    SEP = '\x01'
    return out, SEP.join(x[2] for x in out), SEP.join(x[4] for x in out)

def _prefixe(s, cible):
    lo, hi = 0, len(s)
    while lo < hi:
        mid = (lo + hi + 1) // 2
        if s[:mid] in cible: lo = mid
        else: hi = mid - 1
    return lo

def _suffixe(s, cible):
    lo, hi = 0, len(s)
    while lo < hi:
        mid = (lo + hi + 1) // 2
        if s[-mid:] in cible: lo = mid
        else: hi = mid - 1
    return lo

ANCRE_MIN = 12          # sous douze consonnes, un ancrage ne prouve rien
COUVERTURE_MIN = 0.85   # préfixe + suffixe doivent couvrir presque toute la citation
COUVERTURE_MAX = 1.10   # …sans la couvrir DEUX FOIS : voir ci-dessous
TROU_MIN = 4            # en deçà, c'est une variante d'orthographe, pas un passage sauté
CITATION_MIN = 25       # le seuil du dépôt : sous 25 consonnes, une coïncidence est probable
SEUIL_COUPURE = 20      # la porte COUPURE exige une présence EXACTE, non un ancrage :
                        # la coïncidence n'y est pas le risque, et son seuil est plus bas.

# ⚠️ COUVERTURE_MAX, et la mesure qui l'a imposé. Au siman 101 de Yoré Déa, la citation
# « הראויה להתכבד בה לפני האורחים » (24 consonnes) sortait avec un préfixe de 12 ET un
# suffixe de 24 — soit 36 ancrages pour 24 consonnes. Les deux ancres se recouvraient donc
# largement dans la CITATION, tout en tombant loin l'une de l'autre dans la SOURCE : ce
# n'est pas un passage sauté, c'est une locution courante qui paraît deux fois. Exiger que
# les ancres soient à peu près disjointes, et relever le seuil de longueur à celui que le
# dépôt emploie partout ailleurs, suffit à l'écarter.

def rogner_aux_mots(saute, brut, deb, fin):
    """Ramener les bords du trou sur des frontières de mot.

    La neutralisation des matres lectionis décale l'index d'une lettre ou deux, si bien
    que le trou imprimé commençait ou finissait au milieu d'un mot — « ו הכי », « יפר ב ».
    Ce n'était pas seulement laid : un trou de quatre consonnes dont deux appartiennent aux
    mots voisins n'est pas un passage sauté, c'est un artefact d'alignement. On rogne donc
    jusqu'à la première espace de chaque côté, puis le seuil TROU_MIN est appliqué à ce
    qui reste — ce qui écarte l'artefact sans écarter le mot réellement retiré.
    """
    def lettre(c): return '\u05D0' <= c <= '\u05EA'
    i, j = deb, fin
    # une espace, une virgule, un crochet ou une parenthèse sont des frontières ;
    # seule une LETTRE collée au bord prouve qu'on coupe un mot en deux.
    while i < j and i > 0 and lettre(brut[i - 1]):
        i += 1
    while j > i and j < len(brut) and lettre(brut[j]):
        j -= 1
    return brut[i:j].strip()

def presente(s0, s1, paquet):
    """La citation est-elle dans l'appareil telle quelle ? C'est LA confrontation.

    Tant qu'elle est vraie, les deux mesures de cette porte ont un texte sous la main.
    Quand elle est fausse, la porte COUPURE ne peut pas tourner du tout et la porte TROU
    ne fait qu'un ancrage aveugle sur un texte qui n'est peut-être pas le bon. `main`
    compte ces deux populations séparément : une citation non retrouvée n'est pas une
    citation confrontée, et les confondre, c'est annoncer un plancher comme un compte.
    """
    _prep, tout0, tout1 = paquet
    return s0 in tout0 or s1 in tout1

def juger(s0, s1, prep):
    """None si rien à dire ; sinon (ref, sauté, pref, suff).

    L'ancrage se fait DEUX FOIS, sur le squelette strict et sur le squelette sans matres
    lectionis. Le premier cas témoin de cette porte l'exigeait : la page écrit וְנוֹהֲגִין
    là où le Rama écrit נוהגין, si bien que le préfixe strict tombe au premier caractère
    et que le trou du milieu — le crochet [סמך ממרדכי ריש מסכת ר״ה] — reste invisible.

    L'appelant a déjà vérifié `presente` : une citation présente n'a rien à signaler.
    """
    meilleur = None
    for ref, brut, b0, b0idx, b1, b1idx in prep:
        for chaine, cible, vers_b0 in ((s0, b0, None), (s1, b1, b1idx)):
            # PRÉFILTRE, et il est SAIN : la suite exige p >= ANCRE_MIN et q >= ANCRE_MIN,
            # donc les ANCRE_MIN premières consonnes ET les ANCRE_MIN dernières doivent
            # chacune paraître dans le segment. Deux tests qui ne coûtent presque rien
            # écartent l'immense majorité des segments avant la recherche dichotomique,
            # sans qu'aucun candidat puisse être perdu : c'est une condition nécessaire.
            if chaine[:ANCRE_MIN] not in cible or chaine[-ANCRE_MIN:] not in cible:
                continue
            p, q = _prefixe(chaine, cible), _suffixe(chaine, cible)
            if p < ANCRE_MIN or q < ANCRE_MIN: continue
            if p + q < len(chaine) * COUVERTURE_MIN: continue
            if p + q > len(chaine) * COUVERTURE_MAX: continue   # ancres qui se recouvrent
            i = cible.find(chaine[:p]) + p
            j = cible.rfind(chaine[-q:])
            if j - i < TROU_MIN: continue     # chevauchement ou variante d'orthographe
            # ramener les bornes sur le squelette strict, puis sur le texte brut
            bi = i if vers_b0 is None else vers_b0[i]
            bj = j if vers_b0 is None else vers_b0[j]
            if bj >= len(b0idx): continue
            saute = brut[b0idx[bi]:b0idx[bj]]
            saute = rogner_aux_mots(saute, brut, b0idx[bi], b0idx[bj])
            if len(sk(saute)[0]) < TROU_MIN: continue
            if meilleur is None or p + q > meilleur[2] + meilleur[3]:
                meilleur = (ref, saute, p, q)
    return meilleur

# Les mots par lesquels une source RETOURNE ce qu'elle vient de dire. La liste est courte
# à dessein : elle ne cherche pas toutes les continuations, seulement celles dont l'omission
# change le sens. Une citation qui s'arrête avant un simple ו־ narratif n'est pas un défaut.
# ⚠️ « ואם » EN A ÉTÉ RETIRÉ, et la mesure qui l'a exigé mérite d'être gardée. Au premier
# balayage il rendait 83 des 201 candidats — et aucun n'était un défaut. « ואם » introduit
# presque toujours un AUTRE CAS, non un renversement : la page cite « והוא שקוצץ לו דמים
# ובלבד שלא יאמר לו שילך בשבת », le Mehaber enchaîne « ואם לא קצב… », et c'est le cas suivant,
# que la page traite ailleurs. Même chose pour ואסור, ומותר, ואינו. Une porte qui compte mal
# est pire qu'une porte absente : ne garder que ce qui RETOURNE.
RETOURNEMENT = ('אבל', 'אלא', 'ומיהו', 'מיהו', 'ואך', 'אך', 'ודלא', 'וצ״ע', 'וצ"ע', 'וצריך עיון',
                'ולפיכך', 'ולכן', 'והלכך', 'הילכך', 'ומכל מקום', 'ומ״מ', 'ומ"מ', 'ויש מתירין',
                'ויש מקילין', 'ויש חולקין', 'ויש חולקים')
# Une phrase close : la source a fini de parler, s'arrêter là n'omet rien.
CLOTURE = (':', '.', '׃')

def couper_avant_la_suite(s0, prep, page_entiere='', cible=None):
    """None, ou (ref, suite, premier_mot) — la citation s'arrête avant ce qui la retourne.

    `page_entiere` est le squelette de LA PAGE EXAMINÉE, elle seule.
    Si la clause qui retourne s'y trouve ailleurs, la page la dit à SON lecteur et il n'y a
    rien à signaler : citer une clause et traiter la suivante dans la section voisine est
    la conduite NORMALE d'une page d'étude. Sans ce filtre, la porte reprocherait à une page
    bien faite d'avoir découpé son exposé.

    ⚠️ LA PAGE, ET RIEN QU'ELLE — deux mesures l'ont imposé, l'une après l'autre.
    La première version réunissait TOUT le siman, les trois langues et les quinze fichiers.
    Au siman 247, la clause qui lève l'interdit de שו״ע הרב רמ״ז:ב venait d'être rétablie
    dans le fichier HÉBREU du niveau 2 : le filtre l'y trouvait et taisait le défaut pour
    le FRANÇAIS et pour l'ANGLAIS, qui le portaient intact. Restreindre à la langue ne
    suffisait pas : la clause vit AUSSI dans le niveau 4 français, et le filtre taisait
    encore le défaut du niveau 2. Or un lecteur du niveau 2 n'ouvre pas forcément le
    niveau 4, et jamais la page hébraïque s'il lit le français. Une clause ne couvre le
    lecteur que là où il la lit : dans la page qu'il a sous les yeux.
    """
    if len(s0) < SEUIL_COUPURE: return None
    for ref, brut, b0, b0idx, _b1, _b1idx in prep:
        # ⚠️ L'ŒUVRE VISÉE VAUT AUSSI ICI. La citation est présente quelque part dans
        # l'appareil — c'est la condition d'entrée — mais pas forcément dans l'ouvrage
        # que la page cite : le Beit Yosef reprend le Tour, l'Aroukh HaChoul'han reprend
        # le Mehaber, et « la source enchaîne sur אבל » se lisait alors dans la suite du
        # VOISIN. Quand la page nomme une œuvre de l'appareil, on ne lit que la sienne.
        if cible and not ref.startswith(cible): continue
        i = b0.find(s0)
        if i < 0: continue
        fin = b0idx[i + len(s0) - 1]
        reste = brut[fin + 1:]
        # la source s'est-elle close juste après ?
        tete = reste[:6]
        if any(c in tete for c in CLOTURE): return None
        # ⚠️ LA PONCTUATION DÉTACHÉE. La source sépare souvent la clause qui retourne par une
        # virgule, et le texte vocalisé la détache par une espace : « …בְּיוֹם רִאשׁוֹן , אֶלָּא
        # אִם כֵּן ». Prendre mots[0] puis le dépouiller rendait alors la chaîne VIDE, et le test
        # ne passait jamais — la porte ratait SON PROPRE CAS TÉMOIN, שו״ע הרב רמ״ז:ב, celui-là
        # même qu'un arbitre avait trouvé à la main. Un « 0 coupure » ne valait rien tant que
        # ce défaut vivait. On dépouille donc la TÊTE du reste avant de découper.
        mots = [m for m in reste.strip(' ,;\u05C3\u00A0\t\n-–—').split() if m.strip(',;')]
        if not mots: return None
        premier = mots[0].strip(',;')
        # ⚠️ COMPARER LES SQUELETTES, JAMAIS LES FORMES. Le Choulhan Aroukh HaRav est servi
        # VOCALISÉ : la source écrit אֶלָּא, la liste porte אלא, et « אֶלָּא ».startswith(« אלא »)
        # est FAUX — le nikoud s'intercale entre les lettres. La porte ratait ainsi son propre
        # cas témoin, שו״ע הרב רמ״ז:ב, celui-là même qu'un arbitre avait trouvé à la main et
        # que deux langues portaient intact. Un « 0 coupure » ne vaut rien tant qu'on compare
        # une forme vocalisée à une forme qui ne l'est pas.
        sp = sk(premier)[0]
        if not any(sp.startswith(sk(r)[0]) or sp == sk(r)[0] for r in RETOURNEMENT if sk(r)[0]):
            return None
        sq = sk(reste)[0]
        if len(sq) < 12: return None
        # la clause qui retourne est-elle dite ailleurs dans le siman ?
        if page_entiere and sq[:25] in page_entiere: return None
        return (ref, reste.strip(), premier)
    return None

def simanim(path):
    for d in sorted(glob.glob(os.path.join(path, 'siman-*'))):
        m = re.search(r'siman-(\d+)$', d)
        if m: yield int(m.group(1)), d

def main():
    argv = sys.argv[1:]
    bref = '--bref' in argv
    section = None
    cibles = []
    if '--path' in argv:
        p = os.path.join(ROOT, argv[argv.index('--path') + 1])
        section = 'yoreh-deah' if 'yoreh-deah' in p else ('shabbat' if 'shabbat' in p else 'orah-haim')
        if re.search(r'siman-\d+$', p):
            m = re.search(r'siman-(\d+)$', p); cibles = [(int(m.group(1)), p)]
        else:
            cibles = list(simanim(p))
    elif '--section' in argv:
        section = argv[argv.index('--section') + 1]
        cibles = list(simanim(os.path.join(ROOT, 'sources', section)))
    else:
        nums = [int(a) for a in argv if a.isdigit()]
        for n in nums:
            for sec in ('shabbat', 'orah-haim', 'yoreh-deah'):
                d = os.path.join(ROOT, 'sources', sec, f'siman-{n}')
                if os.path.isdir(d): cibles.append((n, d)); section = sec; break
    if not cibles:
        print(__doc__.strip().split('Usage :')[-1]); return 2

    total = trouve = coupe = 0
    juges = 0            # citations d'au moins SEUIL_COUPURE consonnes : les seules jugeables
    confrontees = 0      # …et RETROUVÉES dans l'appareil : les seules réellement confrontées
    hors_siman = 0       # …absentes, mais dont le voisinage nomme un daf ou un Richon
    inconnues = 0        # …absentes, et rien n'explique pourquoi
    # Ce qui a été TU, et pourquoi. Un verdict refusé en silence est un mutisme ; un
    # verdict refusé et compté est une porte qui dit ce qu'elle ne sait pas juger.
    refus_hors_portee = 0    # TROU refusé : l'œuvre visée est un daf ou un Richon
    refus_sans_visee = 0     # TROU refusé : aucune œuvre nommée auprès de la citation
    refus_rabattement = 0    # TROU refusé : l'ancrage tombait sur une œuvre VOISINE
    refus_coupure = 0        # COUPURE refusée : l'œuvre visée est hors de portée
    coupure_recadree = 0     # COUPURE lue dans l'œuvre VISÉE plutôt que dans la première
                             # de l'appareil où la citation paraissait aussi
    non_situees = 0          # citations que le repérage dans la page n'a pas situées
    # ⚠️ CES CINQ COMPTEURS NE COMPTENT QUE DES VERDICTS RÉELLEMENT PERDUS, et il a fallu
    # les reprendre pour cela. Ma première version incrémentait le refus AVANT d'appeler
    # `juger()` : elle annonçait « 741 TROUS refusés » sur Hilkhot Chabbat quand la mesure
    # — `juger()` appelé puis le veto appliqué — en donne CINQ, les seuls qui auraient
    # paru. Un facteur cent quarante-huit, et dans le sens qui grossit le silence au lieu
    # de le minorer : c'est la même faute que le plancher annoncé comme un compte, prise
    # par l'autre bout, et elle rendait la porte illisible. On juge d'abord, on refuse
    # ensuite. Le coût est nul : la version d'avant appelait déjà `juger()` là.
    vides = []           # simanim dont Sefaria ne sert AUCUN texte : la porte y est aveugle
    sans_mehaber = []    # …et ceux dont le Choul'han Aroukh lui-même est vide, ce qui est
                         # le seul signal qui compte : voir la note plus bas.

    for n, d in cibles:
        sec = 'yoreh-deah' if 'yoreh-deah' in d else ('shabbat' if 'shabbat' in d else 'orah-haim')
        prep = None
        vues = set()
        fichiers = sorted(glob.glob(os.path.join(d, '*.html')))
        for f in fichiers:
            texte = open(f, encoding='utf-8').read()
            plaine = re.sub(r'<[^>]+>', ' ', texte)
            # ⚠️ LES ENTITÉS, et ce n'est pas cosmétique. La convention du dépôt écrit
            # « &nbsp;<span class="he-q">…</span>&nbsp;» (ouvrage réf.) : une fois les
            # balises retirées, il reste « &nbsp;» (מג״א… » entre la citation et sa
            # référence. La parenthèse n'était donc jamais reconnue comme adjacente, et
            # au siman 254 l'œuvre visée retombait sur le « Rambam » de la phrase
            # française d'avant. Six caractères d'entité valaient une coupure tue.
            plaine = (plaine.replace('&nbsp;', ' ').replace('&#160;', ' ')
                            .replace('&amp;', '&').replace('&quot;', '"')
                            .replace('&#39;', "'"))
            plaine = re.sub(r'\s+', ' ', plaine)
            page_entiere, page_idx = sk(plaine)
            for c in citations(f):
                # dédoublonner PAR FICHIER : la même citation dans deux pages est deux
                # fois la même question, mais posée à deux lecteurs différents, et le
                # filtre « la clause est-elle dite ailleurs » ne leur répond pas pareil.
                if (f, c) in vues: continue
                vues.add((f, c))
                if prep is None:
                    segs = appareil(n, sec)
                    if not segs: vides.append(n)
                    # ⚠️ ET L'ÉLARGISSEMENT A FAILLI ÉTEINDRE CE SIGNAL. Au siman 169 de
                    # Yoré Déa, Sefaria ne sert RIEN — ni Mehaber, ni Chakh, ni Taz, ni
                    # Beit Yosef : l'ancienne table rendait zéro segment et l'alerte
                    # « appareil vide » partait. La table élargie y trouve UN segment, le
                    # Tour, et l'alerte se taisait — alors que la porte y est tout aussi
                    # aveugle qu'avant sur le texte du Choul'han Aroukh. On surveille donc
                    # le Mehaber lui-même, et non le total.
                    if not any(r.startswith('Shulchan Arukh,') for r, _t in segs):
                        sans_mehaber.append(n)
                    paquet = preparer(segs)
                    prep = paquet[0]
                total += 1
                s0, _ = sk(c)
                # ⚠️ DEUX SEUILS, ET ILS NE SONT PAS LE MÊME. La porte TROU exige
                # CITATION_MIN (25) consonnes — sous ce seuil, un double ancrage est une
                # coïncidence. La porte COUPURE n'en exige que 20, parce qu'elle demande
                # une présence EXACTE et non un ancrage : la coïncidence n'y est pas le
                # risque. Les confondre effacerait « כל קבוע כמחצה על מחצה דמי » (siman
                # 110, 20 consonnes), coupée juste avant le אבל qui la retourne — trois
                # pages la portent. Ce défaut-là m'a été rendu par le diff avant/après ;
                # sans lui j'aurais livré une porte qui en perd six en en gagnant deux.
                if len(s0) < SEUIL_COUPURE:
                    continue
                juges += 1
                s1, _ = nomat_idx(s0, list(range(len(s0))))
                bornes = situer(page_entiere, page_idx, s0, plaine)
                if bornes is None: non_situees += 1
                visee = oeuvre_visee(plaine, bornes) if bornes else None
                if not presente(s0, s1, paquet):
                    # NON CONFRONTABLE. On dit laquelle, et on ne la rabat sur rien —
                    # et cette fois le code le fait, au lieu de l'écrire en en-tête.
                    if visee and visee[1] is None:
                        hors_siman += 1
                    else:
                        inconnues += 1
                    r = juger(s0, s1, prep) if len(s0) >= CITATION_MIN else None
                    if r:
                        # ⚠️ QUAND RIEN N'EST NOMMÉ, L'ŒUVRE VISÉE N'EST PAS INCONNUE :
                        # c'est le Choul'han Aroukh de CE siman. Toute page de ce dépôt
                        # est la page d'un siman, et son sujet par défaut est le Mehaber
                        # et la glose du Rama de ce siman-là — un ancrage sur eux n'est
                        # donc pas « une œuvre voisine ». Refuser en bloc faute de nom
                        # m'a coûté un défaut RÉEL, mesuré : au siman 99 de Yoré Déa la
                        # page cite « (הגה: ויש מחמירים שלא לצרף עצמות…) » et saute le
                        # crochet de source « (הגהה אחת בש״ד בשם א״ז) » que Sefaria place
                        # DANS le texte du Rama. La citation s'ouvre sur « הגה: », le
                        # marqueur du Rama, et aucun nom d'ouvrage ne traîne alentour :
                        # la règle « pas de nom, pas de verdict » l'éteignait. Pour TOUTE
                        # AUTRE œuvre, l'ancrage sans nom reste spéculatif et refusé.
                        if visee is None and not r[0].startswith(OEUVRES_BASE):
                            refus_sans_visee += 1; r = None
                        elif visee and visee[1] is None:
                            refus_hors_portee += 1; r = None
                        elif visee and not r[0].startswith(visee[1]):
                            refus_rabattement += 1; r = None
                    if r:
                        trouve += 1
                        ref, saute, pf, qf = r
                        print(f"✗ TROU · siman {n} · {os.path.basename(f)}")
                        print(f"   « {c[:150]} »")
                        print(f"   {ref} : {pf} consonnes au début + {qf} à la fin, et entre les deux")
                        print(f"   la source porte — SAUTÉ SANS ELLIPSE ({len(sk(saute)[0])} consonnes) : [{saute[:160]}]")
                        if not bref: print()
                    continue
                confrontees += 1
                cible = visee[1] if visee else None
                # ⚠️ LA RÈGLE N'EST PAS LA MÊME ICI QUE POUR LE TROU, et j'ai dû défaire
                # ma propre correction pour l'apprendre. Un TROU s'appuie sur un ancrage
                # SPÉCULATIF — la citation n'est nulle part dans l'appareil, et le nom que
                # la page écrit est la seule preuve de ce dont elle parle : l'exiger est
                # juste. Une COUPURE, elle, part d'une citation PRÉSENTE MOT POUR MOT :
                # on sait déjà quel texte la porte. Le nom écrit dans la page est alors
                # le signal le PLUS FAIBLE des deux, et s'y fier rend muet.
                # MESURÉ, première version : sur Hilkhot Chabbat elle taisait NEUF
                # coupures, dont je n'ai pu justifier que trois. Les six autres étaient
                # des défauts réels — au siman 318 la page cite la Michna Beroura
                # (« היינו שאין היד סולדת בו אף שהוא קצת חם עדיין ») en écrivant
                # « le Mehaber » juste avant, et la suite qui la retourne
                # (« אבל אם היד סולדת בו… ») est bien celle de la Michna Beroura ; au
                # siman 263 la page nomme le Choul'han Aroukh HaRav et cite la glose du
                # Rama, dont la suite « אבל מי שהוא אצל אשתו » lève précisément le cas.
                # DONC : l'œuvre visée sert à CHOISIR, pas à interdire — sauf quand elle
                # est hors de portée, où elle interdit (siman 334, « מתוך שאדם בהול על
                # ממונו » est une guemara, et la suite venait du Beit Yosef qui la cite).
                if visee and cible is None:
                    if couper_avant_la_suite(s0, prep, page_entiere): refus_coupure += 1
                    continue
                r2 = couper_avant_la_suite(s0, prep, page_entiere, cible) if cible else None
                if r2:
                    if cible: coupure_recadree += 1
                else:
                    r2 = couper_avant_la_suite(s0, prep, page_entiere)
                if r2:
                    coupe += 1
                    ref, suite, premier = r2
                    print(f"✗ COUPÉE AVANT LA SUITE · siman {n} · {os.path.basename(f)}")
                    print(f"   « {c[:150] } »")
                    print(f"   {ref} — la source enchaîne sur « {premier} » sans que la phrase soit close :")
                    print(f"   [{suite[:200]}]")
                    if not bref: print()

    # ⚠️ LE COMPTE, ET NON LE PLANCHER. « Citations confrontées : 81 299 » était faux de
    # deux manières : il comptait les citations trop courtes pour être jugées, et il
    # comptait comme confrontées celles dont la source n'était même pas téléchargée.
    print(f"\nCitations extraites des pages                        : {total}")
    print(f"  · trop courtes pour être jugées (< {SEUIL_COUPURE} consonnes)   : {total - juges}")
    print(f"  · jugeables                                        : {juges}")
    print(f"CONFRONTÉES (retrouvées dans l'appareil du siman)    : {confrontees}")
    print(f"NON CONFRONTABLES (absentes de tout l'appareil)      : {hors_siman + inconnues}")
    # ⚠️ CE SOUS-COMPTE A EXPLOSÉ, ET IL FAUT DIRE POURQUOI — 295 → 816 sur Hilkhot
    # Chabbat, quand le mandat de correction attendait qu'il DIMINUE. Deux changements
    # tirent en sens inverse, et je les ai mesurés séparément sur les mêmes 1 211
    # citations non confrontables :
    #   · le MOTIF resserré seul (frontière droite + numéral validé + préfixe fermé) :
    #     295 → 308. Au niveau des occurrences dans les pages : l'ancien motif en
    #     trouvait 1 709, le nouveau 1 596. La frontière droite et la validation du
    #     numéral en ÉCARTENT 257, réparties sur 122 formes, toutes fausses —
    #     « שבת מקור: » (15 fois), « שבת בבוקר. » (8), « שבתות. », « שבתחומי: »,
    #     « תענית חלום. », « ברכות לפחות . ». Et le préfixe fermé en RÉCUPÈRE 144 sur
    #     75 formes, tous vrais — « בשבת (ג ע״א », « בעירובין (פז ע״ב », « מפסחים נ״ד ע״א ».
    #     Le sous-compte était donc gonflé de 257 ET minoré de 144 ; sur les citations
    #     qui comptent, le second effet l'emporte de treize. La prédiction était à
    #     moitié juste, et l'annoncer autrement serait annoncer une mesure non faite.
    #   · la FENÊTRE réparée (repérage par squelette, et la fenêtre qui part de la FIN
    #     de la citation) : 295 → 835 à motif inchangé. C'est elle qui domine, de loin,
    #     et pour une raison simple : 548 citations sur 1 211 n'avaient AUCUN contexte.
    # Le compte final de la porte, 816, est inférieur aux 848 de la conjonction brute :
    # elle ne demande pas « un daf paraît-il dans la fenêtre ? » mais « l'œuvre la PLUS
    # PROCHE est-elle hors de portée ? », ce qui est strictement plus exigeant.
    print(f"  · dont un daf de guemara ou un Richon est nommé auprès : {hors_siman}")
    print(f"    (ref Sefaria « Traité.daf », hors de portée d'une porte par siman)")
    print(f"  · dont rien dans la page n'explique l'absence          : {inconnues}")
    print(f"  · que le repérage n'a pas situées dans la page         : {non_situees}")
    print(f"TROUS non marqués (un passage sauté au milieu)       : {trouve}")
    print(f"COUPURES avant la suite (la clause qui retourne)      : {coupe}")
    # ⚠️ CE BLOC EST LA CONTREPARTIE DE LA FERMETURE, et il n'est pas décoratif : une
    # porte qui se tait doit dire combien de fois. Sans lui, « 0 trou » ne se distingue
    # pas de « 400 trous refusés sans qu'on sache pourquoi ».
    print(f"VERDICTS REFUSÉS — l'œuvre visée n'est pas celle de l'ancrage :")
    print(f"  · TROU refusé, l'œuvre visée est hors de portée (daf, Richon) : {refus_hors_portee}")
    print(f"  · TROU refusé, aucune œuvre nommée auprès de la citation      : {refus_sans_visee}")
    print(f"  · TROU refusé, l'ancrage tombait sur une œuvre VOISINE        : {refus_rabattement}")
    print(f"  · COUPURE refusée, l'œuvre visée est hors de portée           : {refus_coupure}")
    print(f"  · (COUPURES lues dans l'œuvre visée et non dans une voisine    : {coupure_recadree})")
    if vides:
        print(f"\n⚠️  APPAREIL VIDE — Sefaria ne sert AUCUN texte pour : "
              f"{', '.join(str(x) for x in sorted(set(vides)))}")
        print("   Sur ces simanim la porte ne compare RIEN. Ne pas lire son silence comme un feu vert.")
    if sans_mehaber:
        print(f"\n⚠️  CHOUL'HAN AROUKH ABSENT de Sefaria pour : "
              f"{', '.join(str(x) for x in sorted(set(sans_mehaber)))}")
        print("   Le texte de base n'y est pas : aucune citation du Mehaber ni du Rama n'y est")
        print("   confrontée, quoi que dise le compte des CONFRONTÉES ci-dessus.")
    if not trouve and not coupe:
        print("\nAucune citation ne saute un passage de sa source sans le dire.")
    else:
        print("\nUne ellipse marque la coupure : « A… B » dit que A et B sont chacun verbatim.")
        print("Le remède est l'un des deux — rétablir le passage, ou écrire « … ».")
    return 1 if (trouve or coupe) else 0

if __name__ == '__main__':
    sys.exit(main())
