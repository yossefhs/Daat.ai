#!/usr/bin/env python3
"""Confronte le texte source du NIVEAU 4 (Choul'han Aroukh HaRav) aux sources Sefaria —
verbatim, MOT POUR MOT, SÉIF PAR SÉIF, dans les trois langues — et vérifie que le lecteur le VOIT.

Usage :
  python3 scripts/verify-oh-source.py 71 72 73          # simanim nommés (1-241 : Orah Haïm, 242-365 : Chabbat)
  python3 scripts/verify-oh-source.py --tous [--bref]   # les 365
  python3 scripts/verify-oh-source.py --section shabbat [--bref]
  options : --rendu (ouvre aussi chaque page dans Chromium : voir ÉTAGE 2 ; modules playwright, pillow, numpy) ·
            --bref (une ligne par siman en défaut) · --cache (lit/écrit scripts/.cache-sefaria/saharav : un
            INSTANTANÉ, et la sortie le dit ; par défaut, la source est RE-TÉLÉCHARGÉE, comme la clause de
            vérification le demande)
  AVANT DE PUBLIER : python3 scripts/verify-oh-source.py N … --rendu   (sans --cache)

Codes de sortie : 0 tout conforme · 1 au moins une divergence · 3 Sefaria n'a pas répondu ou a répondu d'une
façon que la porte ne sait pas lire, OU le rendu est impossible (Chromium, module playwright) — rien n'est
conclu pour ce qui n'a pas été lu. Une source absente n'est jamais une source vide.

ÉTAGE 1, STATIQUE (toujours) — pour chaque siman N et ses trois pages niveau-4-daat-harav{,-he,-en}.html :
  1. nombre de blocs <details class="seif-details"> = nombre de séifim du SA HaRav sur Sefaria (0 et 0 pour un
     siman que l'Admour HaZaken n'a pas écrit : la page-pont) ; un écart de compte est nommé ;
  2. le texte de chaque .sa-he de bloc reproduit le séif de même rang MOT POUR MOT (lettres et frontières de
     mots ; nikoud et ponctuation ignorés) ;
  3. chaque « … » est à la place d'une « … » de la source ou d'une omission, et aucune « … » de la source
     n'est retirée ;
  4. chaque DESSIN de la source (<img> : 36:2 et 32:36) est dans le bloc, à sa place, et c'est LE MÊME (src
     identique octet pour octet) ;
  5. parité FR/HE/EN du texte source ;
  6. la FORME de la page. Mesurée sur les 1 095 pages niveau-4 le 9 octobre 2026, sans exception, et donc
     exigée : la chaîne details.seif-details > div.sa-block > p.sa-he ; dans le .sa-he, <br>, <b>, <small>
     (et <img> pour les dessins), sans attribut ni imbrication ; aucun style= sur la chaîne, hors celui du
     207 ; aucun élément caché (hidden, aria-hidden, popover, inert, script, template, dialog, svg…) dans un
     bloc ou autour ; aucune balise non vide écrite « /> » ; aucun attribut en double ; aucun bloc imbriqué ;
     aucun séif hors bloc (classe « seif… », titre h1-h6/summary/dt/th « סעיף X ») ; les caractères du texte :
     lettres, nikoud (sans paseq, sof pasuq ni nun hafukha), maqaf, ׳ ״, ponctuation ASCII, — – … « » “ ” ‘ ’,
     ZWJ, espace insécable. Une page-pont ne porte aucun .sa-he, sauf 304 et 322, FIGÉES par empreinte.
  L'étage statique NE SIMULE PAS LE NAVIGATEUR : il ne lit ni la CSS ni le JavaScript. C'est l'étage 2.

ÉTAGE 2, RENDU (--rendu) — ce que le lecteur VOIT. Les scripts sont fermés à l'étage 1 (ceux du site, et eux
seuls) ; ici, Chromium ouvre la page servie en local (toute requête vers un autre hôte bloquée), à 1280×900, à
390×844, et à UNE LARGEUR PAR INTERVALLE que les conditions @media de la page découpent (481, 641 et 761 px sur
les pages actuelles), mesure dans un MONDE ISOLÉ (la page ne peut pas falsifier la mesure), ouvre chaque séif
par un vrai clic sur son titre, parcourt la page, attend 1,2 s, puis :
  - lit le CSSOM par le navigateur lui-même (@import, @media, échappements, variables compris), et n'admet que
    ce que les 1 095 pages emploient (mesure du 9 octobre 2026) : des règles de style, @media et @keyframes —
    ni @supports, @container, @layer, @scope, @property, ni CSS imbriqué, ni feuille adoptée ni arbre fantôme
    (shadow DOM, dont les feuilles échappent au CSSOM du document) ; des conditions @media de largeur en
    px, d'impression et prefers-reduced-motion, et rien d'autre ; aucune police définie par la page. Sur les
    règles qui atteignent réellement le bloc, sa chaîne jusqu'au .sa-he et son contenu, OU l'un de ses ancêtres :
    aucun état (:hover, :focus…) ni pseudo-élément (::before, ::marker, ::selection…), aucune valeur qui suit
    l'écran ou le thème (vw, vh, %, calc(), min(), max(), clamp(), light-dark(), env(), attr(), color-scheme),
    aucune règle d'impression ou de mouvement réduit (elles ne sont pas rendues), aucun style en ligne ; sur la
    chaîne, des propriétés typographiques ou de boîte seulement ; aucune animation sur la chaîne ou ses ancêtres,
    ni transformation (scale, rotate, translate, zoom ; transform sur la chaîne) ;
  - PHOTOGRAPHIE CHAQUE MOT deux fois, tel quel puis avec le seul texte source rendu transparent : un mot qui ne
    change pas les pixels n'est pas vu, quelle qu'en soit la cause (voile, dégradé, couleur, contour, surlignage,
    découpe, recouvrement). L'écran est parcouru par tuiles, en hauteur ET en largeur (une page de droite à gauche
    qui déborde sur téléphone se lit en défilant vers la gauche) ; un mot qui échoue est repris seul, centré à
    l'écran, contre les éléments fixes ;
  - vérifie l'ordre visuel des mots (de droite à gauche, ligne après ligne), leur hauteur (un mot écrasé n'est
    pas lisible), que le texte et le nombre de blocs après les scripts sont ceux du fichier, et que chaque dessin
    est chargé, visible, et n'a pas été changé ;
  - tue un processus de rendu bloqué (900 s par page) : la page sort en « RENDU IMPOSSIBLE », code 3.
  Trois processus en parallèle ; ~2 h 30 pour les 1 095 pages, quelques minutes pour un lot.

CE QUE LA PORTE NE COUVRE PAS, et qui relève d'autres portes ou du relecteur :
  - les .sa-he HORS des blocs (3 752 citations des sections d'étude, dans 768 pages) : verifier-citations.py ;
  - les traductions et commentaires (.sa-fr, chidush, sections למעשה) : relecture, verifier-citations.py ;
  - du texte hébreu ajouté dans le div.sa-block hors du .sa-he, la place des <small>/<b> dans le .sa-he, un
    séif fabriqué hors bloc sous la forme d'un paragraphe ordinaire (<strong>סעיף א.</strong> sert à 60 reprises,
    légitimement, dans les explications hébraïques) ;
  - ce que les scripts DU SITE affichent depuis d'autres hôtes (bannière de dédicace, chat), bloqués au rendu ;
  - à l'intérieur d'un intervalle de largeur, une seule largeur est rendue : un élément d'une AUTRE partie de la
    page (ni la chaîne ni un ancêtre) dont la taille suit l'écran (vw, %, calc…) pourrait recouvrir le texte à
    une largeur et non à une autre ; en deçà de 320 px, rien n'est rendu ;
  - l'impression, le mouvement réduit (leurs règles sont seulement interdites sur la chaîne et ses ancêtres), le
    schéma sombre, forced-colors, la densité de pixels (aucune page n'emploie ces conditions, et l'étage 2 les
    refuse) ; le temps au-delà de 1,2 s après l'ouverture des séifs ;
  - les mots dont les seuls crochets, guillemets ou ponctuation changent (ignorés à dessein).

LES NORMALISATIONS, des deux côtés, et elles seules : NFC ; nikoud et te'amim retirés ; le maqaf est une
frontière de mot ; <br>, <p>, <div>, <li>, <tr>, <td>, <th>, <blockquote> (et « </br> », que le navigateur lit
<br>) sont des frontières, les autres balises non ; le ZWJ et les crochets éditoriaux de Kehot (« דּוֹחִ[ין] »,
« שאינ[ן] ») sont retirés — un mot mis entre crochets n'est donc pas vu ; côté source, les appels de note
<i data-commentator="Notes" …></i> sont retirés SANS espace (Sefaria en pose au milieu d'un mot). Les
guillemets, comme toute ponctuation, ne sont pas confrontés. Mesuré le 9 octobre 2026 : avec ces seules
règles, les 9 942 blocs du site ont les MÊMES frontières de mots que la source.

L'ÉDITION. Sefaria sert deux éditions hébraïques du SA HaRav, toutes deux de Kehot : « Vocalized Edition -
Kehot Publication Society » (vocalisée, l'édition PAR DÉFAUT d'api/texts, celle que les pages recopient, la
seule qui porte les dessins) et « Kehot Publication Society » (non vocalisée, abréviations NON développées).
La porte confronte à la vocalisée, et le dit. Elle vérifie que l'API v3 sert le bon siman (« ref ») et que le
nombre de séifs servis est celui que le chapeau annonce (« ובו ט״ו סעיפים » ; concordant sur les 301 chapeaux
lisibles des 302 simanim servis, le 110 écrivant « יו״ד ») : sinon, code 3.

LE CHAPEAU. Sefaria place en tête du séif 1 le titre du siman et son compte ; la page le recopie ou non, et
les deux sont conformes. Il n'est reconnu que s'il s'achève, avant le premier « : », sur « סעיף », « סעיפים »
ou « סעיף אחד », avec « ובו » dans ses quatre derniers mots, en quarante mots au plus. 301 (« השלמה לתחלת
הסמן … ») n'en a pas ; 305 et 312 n'ont pas de « : » après le leur : rien n'y est retiré. Un séif VIDE chez
Sefaria (305:33, dans les deux éditions) est signalé, non jugé.

LES LACUNES. Une lacune n'est admise que si (1) l'API v3 répond « We have no text for … » ou ne sert aucun
texte, (2) api/texts le confirme — le bon ref, aucune erreur, « he » vide —, et (3) le siman est dans
LACUNES_MESUREES de scripts/verifier-alignement.py (63 simanim mesurés le 8 octobre 2026). Sinon : code 3.

CE QUI A CHANGÉ LE 9 OCTOBRE 2026, ET POURQUOI. L'ancienne porte comparait la CONCATÉNATION des consonnes
des blocs d'un siman à celle des séifs de Sefaria :
  1. elle sortait en rouge 25 simanim d'Orah Haïm (2 4-7 9 10 15-19 21-29 33-36) sur les seuls mots du
     CHAPEAU, et noyait sous eux les vrais défauts ;
  2. un texte glissé d'un séif au suivant gardait la même concaténation ;
  3. elle s'arrêtait à la PREMIÈRE balise fermante du bloc : un .sa-he qui porte <small> ou <br> (Chabbat 301)
     n'était lu que jusqu'à elle ;
  4. son chemin était écrit en dur sous sources/orah-haim : le niveau 4 de Hilkhot Chabbat (242-365) n'était
     confronté au SA HaRav par AUCUNE porte ;
  5. elle effaçait les <img> de la source : 36:2 avait perdu ses 27 dessins de lettres, 32:36 ses deux, dans
     les trois langues, et sortait « IDENTIQUE ».
Premier balayage de la porte réécrite, sur les pages publiées : 26 simanim divergents, plus les dessins de 32
et 36. Orah Haïm 1, 3, 8, 11, 12, 13 omettaient des propositions dans les trois langues, le plus souvent sans
« … » ; 30 changeait un mot (« שסותרין » → « שסותרות ») et développait « וגו׳ », 31 développait « וגו׳ ». À
Chabbat, les pages HÉBRAÏQUES et ANGLAISES de 17 simanim — 261 (HE seule), 276, 309, 310, 311, 313, 321, 323,
324, 328, 329, 330, 355, 356, 357, 358, 360 — omettaient des propositions que la page française portait (le
lecteur hébreu ou anglais lisait un texte source tronqué) ; au 359, elles écrivaient « היא » pour « הוא ».
Restaurés le jour même. Trois arbitrages adversariaux ont ensuite trouvé, sur des témoins, une centaine de
façons de tromper les versions intermédiaires — CSS (couleur du fond, opacité, police nulle, ::first-line,
@import, variables), scripts, éléments recouvrants, balises auto-fermées, blocs hors <details>, lettres
larges, « … » déplacée, dessins permutés. Chaque tentative d'énumérer les ruses de CSS en ouvrait d'autres, et
faisait dépendre la porte de la feuille du chat (chat-widget.css, chargée par 1 056 pages) : d'où l'étage 2,
où c'est le navigateur qui dit ce que le lecteur voit. Son premier état (calculs de styles, elementFromPoint) a
été arbitré à son tour et trompé par des voiles en pointer-events:none, des dégradés, des contours de glyphes,
des minuteurs : d'où la fermeture des scripts et la mesure par PIXELS.
"""
import sys, re, json, os, unicodedata, subprocess, difflib, importlib.util, hashlib
from html.parser import HTMLParser

ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
CACHE = os.path.join(ROOT, "scripts", ".cache-sefaria", "saharav")
ED_REF = "Vocalized Edition - Kehot Publication Society"
SECTIONS = (("orah-haim", range(1, 242)), ("shabbat", range(242, 366)))
LANGS = (("FR", ""), ("HE", "-he"), ("EN", "-en"))
NIKUD = re.compile(r"[֑-ׇֽֿׁׂׅׄ]")   # sans maqaf, paseq, sof pasuq, nun hafukha
RETIRES = re.compile(r"[‍\[\]]")
POINTS = re.compile(r"…|\.(?:\s*\.)+")                                       # « … », « ... », « . . . », « .. »
MOT = re.compile(r"[א-ת]+|…")
REF = "Shulchan Arukh HaRav, Orach Chayim {n}"
ADMIS = set(" \n\t\r ,.:;()?![]'\"-—–…‍«»“”‘’־׳״/")
TAGS_SAHE = {"br", "b", "small", "img"}
# Les scripts du site, relevés le 9 octobre 2026 sur les 1 095 pages niveau-4, et eux seuls : un script qui
# n'en est pas peut tout (effacer un mot après la mesure, réagir au clic, falsifier la mesure). Les scripts
# en ligne sont reconnus par empreinte (SHA-256 de leur texte sans espaces, 16 chiffres) ; JSON-LD admis.
SCRIPTS_ADMIS = {"/assets/js/dedicace-banner.js", "../../../assets/js/chat-loader.js", "/assets/js/intra-links.js",
                 "/assets/js/pwa.js", "/assets/js/daat-copy.js", "/assets/js/share-text.js", "/_vercel/insights/script.js",
                 "../../../assets/js/daat-progress.js", "/assets/js/siman-nav.js"}
SCRIPTS_EN_LIGNE = {"1284069d37cde3df"}    # window.DAAT_CHAT_API_URL = '…/api/chat';
ON_ADMIS = {("button", "onclick", "window.print()"), ("link", "onload", "this.onload=null;this.rel='stylesheet'")}
INTERDITS = {"iframe", "object", "embed", "frame", "frameset", "portal", "base", "applet"}
TITRES = {"h1", "h2", "h3", "h4", "h5", "h6", "summary", "dt", "th", "legend", "caption"}
VIDES = {"br", "img", "hr", "meta", "link", "input", "wbr", "source", "area", "base", "col", "embed", "param", "track"}
MUETS = {"script", "style", "template", "noscript", "title", "textarea", "iframe", "noembed", "noframes", "object",
         "video", "audio", "canvas", "dialog", "select", "datalist", "svg", "math", "head", "del", "s", "strike"}
ALTS = {"dessin de la lettre (édition Kehot)", "צורת האות (מהדורת קה״ת)", "drawing of the letter (Kehot edition)"}
# le seul style= que porte un .sa-he de bloc, mesuré le 9 octobre 2026 (OH 207, trois langues)
STYLES_SAHE = {"color:var(--text-muted);font-size:15px;margin-top:14px"}

# Résidus de Sefaria, un par un, vérifiés à la main — jamais une règle. Au 294:7, l'appel de note « לז »
# (le précédent est « לו ») est coupé par Sefaria : data-label="ל"></i>ז — la seconde lettre du label tombe
# dans le texte. L'édition non vocalisée lit « אתה חונן אף אם ». Recensement du 9 octobre 2026 sur les
# 302 simanim servis : le motif « </i> + lettre isolée » ne se trouve qu'au 294:7 et au 314:4, où c'est un
# appel de note posé au milieu du mot « יד » (aucun résidu).
# Les deux pages-ponts ANCIENNES (304, 322), antérieures à la décision « page-pont sobre » de CLAUDE.md,
# portent des .sa-he qui citent d'autres textes (304 : le SA HaRav d'autres simanim ; 322 : un résumé du
# siman). La porte ne les juge pas : elle les FIGE par empreinte (SHA-256 des textes .sa-he, espaces
# normalisés, relevée le 9 octobre 2026). Toute autre page-pont ne porte AUCUN .sa-he.
PONTS_FIGES = {304: "4b79a3a5de673686", 322: "7992588b09141808"}

RESIDUS = {
    (294, 7): ('</i>ז ', '</i> ', "« ז », seconde lettre de l'appel de note « לז » que Sefaria a laissée dans le texte"),
}

try:
    _p = os.path.join(ROOT, "scripts", "verifier-alignement.py")
    _spec = importlib.util.spec_from_file_location("verifier_alignement", _p)
    _m = importlib.util.module_from_spec(_spec)
    _spec.loader.exec_module(_m)
    LACUNES = {n for (oeuvre, n) in _m.LACUNES_MESUREES if oeuvre == _m._HARAV}
    LACUNES_ERR = None
except BaseException as e:                  # SystemExit compris : jamais un code de sortie volé
    LACUNES, LACUNES_ERR = set(), f"{type(e).__name__}: {e}"


def section_de(n):
    for sec, rng in SECTIONS:
        if n in rng:
            return sec
    return None


def _curl(url):
    try:
        return subprocess.run(["curl", "-s", "--max-time", "90", url], capture_output=True,
                              text=True, timeout=120).stdout
    except subprocess.TimeoutExpired:
        raise RuntimeError("délai dépassé")


def _confirmer_lacune(n):
    try:
        d2 = json.loads(_curl(f"https://www.sefaria.org/api/texts/Shulchan_Arukh_HaRav,_Orach_Chayim.{n}?context=0&pad=0"))
    except ValueError:
        raise RuntimeError("v3 ne sert aucun texte, api/texts ne répond pas")
    if not isinstance(d2, dict) or d2.get("error") or d2.get("ref") != REF.format(n=n) or d2.get("he"):
        raise RuntimeError("v3 ne sert aucun texte, api/texts ne le confirme pas")
    if LACUNES_ERR:
        raise RuntimeError(f"liste LACUNES_MESUREES illisible ({LACUNES_ERR}) : aucune lacune ne peut être admise")
    if n not in LACUNES:
        raise RuntimeError("Sefaria ne sert aucun texte, mais le siman n'est PAS dans LACUNES_MESUREES "
                           "(scripts/verifier-alignement.py) : à vérifier à la main avant toute conclusion")
    return d2["ref"]


VAL = dict(zip("אבגדהוזחטיכלמנסעפצקרשת", [1, 2, 3, 4, 5, 6, 7, 8, 9, 10, 20, 30, 40, 50, 60, 70, 80, 90, 100, 200, 300, 400]))
VAL.update({"ך": 20, "ם": 40, "ן": 50, "ף": 80, "ץ": 90})


def compte_annonce(seg0):
    """Le nombre de séifs que le chapeau annonce, ou None s'il n'est pas lisible."""
    t = NIKUD.sub("", unicodedata.normalize("NFC", re.sub(r"<[^>]+>", "", seg0)))[:400]
    m = re.search(r"ובו\s+(?:([א-ת]+)[\"'״׳]?([א-ת]?)\s+סעיפים|סעיף\s+אחד)", t)
    if not m:
        return None
    if m.group(0).endswith("אחד"):
        return 1
    lettres = m.group(1) + m.group(2)
    if lettres == "יוד":
        return 10
    try:
        return sum(VAL[c] for c in lettres)
    except KeyError:
        return None


def _valider(n, ref):
    if not isinstance(ref, list) or not all(isinstance(s, str) for s in ref):
        raise RuntimeError("un segment de l'édition de référence n'est pas une chaîne")
    k = compte_annonce(ref[0]) if ref else None
    if k is not None and k != len(ref):
        raise RuntimeError(f"Sefaria sert {len(ref)} séifs, le chapeau en annonce {k}")
    return ref


def fetch(n, use_cache):
    """Rend (segments de l'édition de référence, titre, provenance). Lève RuntimeError sur toute réponse que
    la porte ne sait pas lire. Une réponse VIDE n'est une lacune que confirmée (voir _confirmer_lacune)."""
    f = os.path.join(CACHE, f"OH-{n}.v3.json")
    if use_cache and os.path.exists(f):
        try:
            d = json.load(open(f, encoding="utf-8"))
        except ValueError:
            d = None
        if isinstance(d, dict):
            if d.get("lacune_confirmee") == REF.format(n=n) and n in LACUNES:
                return [], "(lacune confirmée)", "cache"
            if d.get("ref") == REF.format(n=n):
                vs = {v.get("versionTitle"): v.get("text") for v in d.get("versions", []) if isinstance(v, dict)}
                ref = vs.get(ED_REF)
                if isinstance(ref, list) and any(isinstance(s, str) and s.strip() for s in ref):
                    return _valider(n, ref), ED_REF, "cache"
    raw = _curl("https://www.sefaria.org/api/v3/texts/Shulchan_Arukh_HaRav,_Orach_Chayim."
                f"{n}?version=hebrew%7Call")
    try:
        d = json.loads(raw)
    except ValueError:
        raise RuntimeError("réponse illisible")
    if not isinstance(d, dict):
        raise RuntimeError("réponse illisible")
    err = str(d.get("error", "") or "")
    vs = {v.get("versionTitle"): v.get("text") for v in d.get("versions", []) if isinstance(v, dict)}
    ref = vs.get(ED_REF)
    if isinstance(ref, str):
        ref = [ref]
    plein = isinstance(ref, list) and any(isinstance(s, str) and s.strip() for s in ref)
    if plein and not err:
        if d.get("ref") != REF.format(n=n):
            raise RuntimeError(f"l'API v3 sert « {d.get('ref')} » pour le siman {n}")
        _valider(n, ref)
        if use_cache:
            os.makedirs(CACHE, exist_ok=True)
            open(f, "w", encoding="utf-8").write(raw)
        return ref, ED_REF, "Sefaria, en direct"
    rien = not any(isinstance(x, list) and any(isinstance(s, str) and s.strip() for s in x) for x in vs.values())
    if err.startswith("We have no text for") or (not err and "versions" in d and rien and not d.get("available_versions")):
        conf = _confirmer_lacune(n)
        if use_cache:
            os.makedirs(CACHE, exist_ok=True)
            json.dump({"versions": [], "lacune_confirmee": conf}, open(f, "w", encoding="utf-8"))
        return [], "(lacune confirmée)", "Sefaria, en direct"
    if err:
        raise RuntimeError(err)
    if "versions" not in d:
        raise RuntimeError("réponse sans « versions »")
    raise RuntimeError(f"édition de référence absente ou vide ; servies : {sorted(k for k in vs if k)}"
                       + (" ; d'autres éditions existent (available_versions)" if d.get("available_versions") else ""))


# ---------------------------------------------------------------- lecture de la page

class Lecteur(HTMLParser):
    """Lit, dans l'ordre, les blocs seif-details : pour chacun, le texte de son .sa-he et ses dessins (src, place).
    Ne simule PAS le navigateur : ce qui est caché par CSS ou par script relève de l'étage de rendu (--rendu).
    Refuse, dans un bloc, tout ce qui sort de la forme mesurée (voir la docstring, point 6)."""
    FRONTIERES = {"br", "p", "div", "li", "tr", "td", "th", "blockquote"}
    SUMMARY_SEIF = re.compile(r"^סעיף\s+[א-ת]{1,4}[\"'״׳]?[א-ת]?\s*[.:]?$")

    def __init__(self):
        super().__init__(convert_charrefs=True)
        self.blocs = []          # [{"txt": str, "img": [(rang en mots, src, alt)]}]
        self.pile = []           # (balise, est_sahe, est_bloc, classes)
        self.sahe = self.bloc = 0
        self.fautes = []         # (famille, détail)
        self.tous_sahe = []      # le texte de CHAQUE .sa-he de la page, dans ou hors bloc
        self._titres = []        # [balise, texte] des titres ouverts hors bloc
        self._script = None      # le texte du script en ligne en cours de lecture

    def _faute(self, fam, det):
        if len(self.fautes) < 60:
            self.fautes.append((fam, det))

    def handle_starttag(self, tag, attrs):
        self._ouvre(tag, attrs, auto=False)

    def handle_startendtag(self, tag, attrs):
        if tag not in VIDES:
            self._faute("BALISE AUTO-FERMÉE", f"<{tag} … />")
        self._ouvre(tag, attrs, auto=True)

    def _frontiere(self):
        if self.sahe and self.bloc:
            self.blocs[-1]["txt"] += " "
        if self.sahe and self.tous_sahe:
            self.tous_sahe[-1] += " "

    def _ouvre(self, tag, attrs, auto):
        noms = [k.lower() for k, _ in attrs]
        a = {k.lower(): (v or "") for k, v in attrs}
        if tag == "script":
            if "src" in a:
                if a["src"] not in SCRIPTS_ADMIS:
                    self._faute("SCRIPT NON ADMIS", f"<script src=\"{a['src'][:80]}\">")
            elif "json" not in a.get("type", "").lower():
                self._script = ""
        for k, v in a.items():
            if k.startswith("on") and (tag, k, v) not in ON_ADMIS:
                self._faute("ATTRIBUT D'ÉVÉNEMENT NON ADMIS", f"<{tag} {k}=\"{v[:60]}\">")
            if re.sub(r"\s+", "", v).lower().startswith(("javascript:", "data:text/html")):
                self._faute("URL SCRIPTÉE", f"<{tag} {k}=\"{v[:60]}\">")
        if tag in INTERDITS:
            self._faute("ÉLÉMENT NON ADMIS", f"<{tag}>")
        # un arbre fantôme déclaratif : ses feuilles de style échappent à document.styleSheets, donc au rendu (aucune
        # page n'en porte, aucun script du site n'en crée)
        if tag == "template" and any(k.startswith("shadowroot") for k in a):
            self._faute("ÉLÉMENT NON ADMIS", "<template shadowrootmode> (arbre fantôme)")
        if tag == "meta" and a.get("http-equiv", "").lower() in ("refresh", "set-cookie", "content-security-policy"):
            self._faute("ÉLÉMENT NON ADMIS", f"<meta http-equiv=\"{a['http-equiv']}\">")
        classes = a.get("class", "").lower().split()
        if len(noms) != len(set(noms)) and (self.bloc or "seif-details" in classes or "sa-he" in classes):
            self._faute("ATTRIBUT EN DOUBLE", f"<{tag}> {noms}")
        est_bloc = "seif-details" in classes
        if est_bloc and tag != "details":
            self._faute("SÉIF HORS BLOC", f"<{tag} class=\"{a.get('class')}\">")
            est_bloc = False
        if est_bloc and self.bloc:
            self._faute("BLOC IMBRIQUÉ", "un seif-details dans un autre")
        if est_bloc and (set(a) - {"class", "open"} or set(classes) != {"seif-details"}):
            self._faute("ATTRIBUT NON ADMIS", f"<details {' '.join(noms)} class=\"{a.get('class')}\">")
        if est_bloc and any(t in MUETS or cache for t, _s, _b, _c, cache in self.pile):
            self._faute("BLOC DANS UN ÉLÉMENT NON ADMIS", " > ".join(t for t, *_ in self.pile)[-120:])
        if "seif-num" in classes and not self.bloc:
            self._faute("SÉIF HORS BLOC", "span seif-num hors d'un bloc seif-details")
        if not self.bloc and not est_bloc:
            if any(c.startswith("seif") for c in classes):
                self._faute("SÉIF HORS BLOC", f"<{tag} class=\"{a.get('class')}\"> hors d'un bloc seif-details")
            if tag in TITRES and not auto:
                self._titres.append([tag, ""])
        if self.bloc:
            if tag in MUETS or any(k in a for k in ("hidden", "aria-hidden", "popover", "inert")):
                self._faute("ÉLÉMENT NON ADMIS DANS UN BLOC", f"<{tag} {' '.join(noms)}>")
        sahe = "sa-he" in classes
        if self.sahe and self.bloc:
            if tag not in TAGS_SAHE:
                self._faute("BALISE NON ADMISE", f"<{tag}> dans le texte source")
            elif tag == "img":
                if set(a) - {"src", "alt"} or not a.get("src", "").startswith("data:image/") or a.get("alt", "") not in ALTS:
                    self._faute("ATTRIBUT NON ADMIS", "<img> dans le texte source (src data:image/…, alt de la liste)")
            elif attrs:
                self._faute("ATTRIBUT NON ADMIS", f"<{tag} {' '.join(noms)}> dans le texte source")
            if tag in ("b", "small") and any(t in ("b", "small") for t, *_ in self.pile):
                self._faute("BALISE NON ADMISE", f"<{tag}> imbriquée dans <b>/<small>")
        if sahe and self.bloc and not self.sahe:
            # la chaîne mesurée sur les 9 942 blocs : details.seif-details > div.sa-block > p.sa-he
            parent = self.pile[-1] if self.pile else None
            grand = self.pile[-2] if len(self.pile) > 1 else None
            if not (parent and parent[0] == "div" and parent[3] == ("sa-block",) and grand and grand[2]):
                self._faute("CHAÎNE NON ADMISE", "le .sa-he doit être <p> enfant de div.sa-block, enfant du bloc")
            if tag != "p" or set(a) - {"class", "style"} or set(classes) != {"sa-he"} \
                    or (a.get("style") is not None and _style_norm(a["style"]) not in STYLES_SAHE):
                self._faute("ATTRIBUT NON ADMIS", f"<{tag} {' '.join(noms)} class=\"{a.get('class')}\" style=\"{a.get('style', '')}\">")
        if self.bloc and not sahe and tag == "div" and "sa-block" in classes and a.get("style"):
            self._faute("ATTRIBUT NON ADMIS", "style= sur div.sa-block")
        if tag in self.FRONTIERES:
            self._frontiere()
        if tag == "img" and self.sahe and self.bloc:
            self.blocs[-1]["img"].append((len(sans_points(mots(self.blocs[-1]["txt"]))), a.get("src", ""), a.get("alt", "")))
        if tag in VIDES or auto:
            return
        if est_bloc:
            self.blocs.append({"txt": "", "img": []})
        if sahe:
            self.tous_sahe.append("")
        cache = any(k in a for k in ("hidden", "aria-hidden", "popover", "inert"))
        self.pile.append((tag, sahe, est_bloc, tuple(classes), cache))
        self.sahe += sahe
        self.bloc += est_bloc

    def handle_endtag(self, tag):
        if tag == "script" and self._script is not None:
            if hashlib.sha256(re.sub(r"\s+", "", self._script).encode()).hexdigest()[:16] not in SCRIPTS_EN_LIGNE:
                self._faute("SCRIPT NON ADMIS", "script en ligne : « " + re.sub(r"\s+", " ", self._script).strip()[:70] + " »")
            self._script = None
        if tag == "br":                       # « </br> » : le navigateur en fait un <br>
            self._frontiere()
            return
        if tag in VIDES or not any(t == tag for t, *_ in self.pile):
            return
        while self.pile:
            t, sahe, bloc, _c, _cache = self.pile.pop()
            self.sahe -= sahe
            self.bloc -= bloc
            if self._titres and self._titres[-1][0] == t:
                _t, txt = self._titres.pop()
                if self.SUMMARY_SEIF.match(NIKUD.sub("", txt).strip()):
                    self._faute("SÉIF HORS BLOC", f"<{t}> « {txt.strip()[:30]} » hors d'un bloc seif-details")
            if t == tag:
                break
        if tag in self.FRONTIERES:
            self._frontiere()

    def handle_data(self, data):
        if self._script is not None:
            self._script += data
            return
        if self.sahe and self.tous_sahe:
            self.tous_sahe[-1] += data
        for x in self._titres:
            x[1] += data
        if self.sahe and self.bloc:
            self.blocs[-1]["txt"] += data
            for ch in set(unicodedata.normalize("NFC", data)):
                if not ("א" <= ch <= "ת" or NIKUD.match(ch) or ch in ADMIS):
                    self._faute("CARACTÈRE NON ADMIS", f"U+{ord(ch):04X} « {ch} » dans le texte source")


def _style_norm(s):
    return ";".join(sorted(re.sub(r"\s+", "", d) for d in s.lower().split(";") if d.strip()))


def lire_page(path):
    html = open(path, encoding="utf-8").read()
    html = re.sub(r"<!---?>", "<!---->", html)          # HTML5 : « <!--> » est un commentaire vide
    lx = Lecteur()
    lx.feed(html)
    lx.close()
    lx.empreinte = hashlib.sha256("|".join(re.sub(r"\s+", " ", unicodedata.normalize("NFC", x)).strip()
                                           for x in lx.tous_sahe).encode()).hexdigest()[:16]
    return lx.blocs, list(lx.fautes), lx


# ---------------------------------------------------------------- comparaison

def _norm(s):
    s = unicodedata.normalize("NFC", s).replace("־", " ")
    s = NIKUD.sub("", s)
    s = RETIRES.sub("", s)
    return POINTS.sub(" … ", s)


def texte_source(seg):
    """Le séif de Sefaria en texte : appels de note retirés SANS espace, <br>/<p>/<div> = frontières ;
    chaque <img> devient un repère « \x00IMG\x00 »."""
    s = re.sub(r"<i\b[^>]*data-commentator[^>]*>\s*</i>", "", seg)
    s = re.sub(r"<img\b[^>]*>", " \x00IMG\x00 ", s)
    s = re.sub(r"<(?:br|/?p|/?div|/?li)\b[^>]*>", " ", s)
    return re.sub(r"<[^>]+>", "", s)


def mots(texte):
    return MOT.findall(_norm(texte))


def sans_points(ms):
    return [w for w in ms if w != "…"]


def images_source(seg, st):
    """(rang en mots, src) de chaque dessin de la source."""
    srcs = re.findall(r'<img\b[^>]*\bsrc="([^"]*)"', seg)
    out, k = [], 0
    for part, src in zip(st.split("\x00IMG\x00")[:-1], srcs):
        k += len(sans_points(mots(part)))
        out.append((k, src))
    return out


def chapeau(seg0_texte):
    """Nombre de MOTS du chapeau en tête du séif 1, ou 0."""
    k = seg0_texte.find(":")
    if k < 0:
        return 0
    ws = sans_points(mots(seg0_texte[:k]))
    if not ws or len(ws) > 40 or "ובו" not in ws[-4:]:
        return 0
    if ws[-1].startswith("סעי") or (ws[-1] == "אחד" and len(ws) > 1 and ws[-2].startswith("סעי")):
        return len(ws)
    return 0


def _rangs_points(ms):
    """Rang (en mots, « … » non comptées) de chaque « … »."""
    out, c = [], 0
    for w in ms:
        if w == "…":
            out.append(c)
        else:
            c += 1
    return out


def ecarts(sm_all, pt, decal):
    """Écarts mot à mot. sm_all : mots de la source (« … » compris) ; pt : mots de la page ; decal : nombre de
    mots de la source retirés en tête (le chapeau que la page ne recopie pas)."""
    sm = sans_points(sm_all)[decal:]
    pm = sans_points(pt)
    ell_p = _rangs_points(pt)
    ell_s = [r - decal for r in _rangs_points(sm_all) if r >= decal]
    out, page_vers_source, sites = [], {}, set()
    for op, a1, a2, b1, b2 in difflib.SequenceMatcher(None, sm, pm, autojunk=False).get_opcodes():
        if op == "equal":
            for x in range(b2 - b1 + 1):
                page_vers_source[b1 + x] = a1 + x
            continue
        a, b = " ".join(sm[a1:a2]), " ".join(pm[b1:b2])
        sites.update({b1, b2})
        page_vers_source.setdefault(b1, a1)
        page_vers_source[b2] = a2
        if op == "delete":
            out.append(("OMISSION déclarée" if b1 in ell_p else "OMISSION SILENCIEUSE", a, a2 - a1))
        elif op == "insert":
            out.append(("AJOUT", b, b2 - b1))
        elif a.replace(" ", "") == b.replace(" ", ""):
            out.append(("FRONTIÈRE DE MOT", f"{a} → {b}", max(a2 - a1, b2 - b1)))
        else:
            out.append(("MOT CHANGÉ", f"{a} → {b}", max(a2 - a1, b2 - b1)))
    # les « … » : chacune de la page à la place d'une « … » de la source ou d'une coupe ; chacune de la
    # source présente dans la page
    restant = list(ell_s)
    for r in ell_p:
        s = page_vers_source.get(r)
        if s in restant:
            restant.remove(s)
        elif r not in sites:
            ctx = " ".join(pm[max(0, r - 3):r]) + " … " + " ".join(pm[r:r + 3])
            out.append(("« … » SANS OMISSION", ctx.strip(), 1))
    for s in restant:
        if not any(f.startswith("OMISSION") for f, *_ in out):
            ctx = " ".join(sm[max(0, s - 3):s]) + " … " + " ".join(sm[s:s + 3])
            out.append(("« … » DE LA SOURCE RETIRÉE", ctx.strip(), 1))
    return out


def juger_bloc(n, i, seg, bloc, nchap):
    if (n, i + 1) in RESIDUS:
        avant, apres, _ = RESIDUS[(n, i + 1)]
        seg = unicodedata.normalize("NFC", seg)
        if avant not in seg:
            raise RuntimeError(f"résidu déclaré au séif {i + 1} introuvable : Sefaria l'a corrigé, retirer l'exception")
        seg = seg.replace(avant, apres, 1)
    st = texte_source(seg)
    sm_all = mots(st.replace("\x00IMG\x00", " "))
    sm = sans_points(sm_all)
    pt = mots(bloc["txt"])
    pm = sans_points(pt)
    decal = 0
    if i == 0 and nchap and pm != sm and (pm == sm[nchap:] or pm[:min(3, nchap)] != sm[:min(3, nchap)]):
        decal = nchap
    out = [] if (pm == sm[decal:] and _rangs_points(pt) == [r - decal for r in _rangs_points(sm_all) if r >= decal]) \
        else ecarts(sm_all, pt, decal)
    imgs_s = [(r - decal, s) for r, s in images_source(seg, st) if r >= decal]
    imgs_p = [(r, s) for r, s, _alt in bloc["img"]]
    if imgs_s != imgs_p:
        if [r for r, _ in imgs_s] != [r for r, _ in imgs_p]:
            out.append(("DESSIN OMIS OU DÉPLACÉ", f"{len(imgs_s)} dessin(s) dans la source, {len(imgs_p)} dans le bloc, ou pas au même rang", abs(len(imgs_s) - len(imgs_p)) or 1))
        else:
            k = [x for x in range(len(imgs_s)) if imgs_s[x][1] != imgs_p[x][1]]
            out.append(("DESSIN CHANGÉ", f"dessin(s) n° {', '.join(str(x + 1) for x in k)} : l'image n'est pas celle de la source", len(k)))
    return out, pm[nchap:] if (i == 0 and nchap and decal == 0) else pm, (i == 0 and nchap and decal == 0)


def aligner(B, segs):
    cle = lambda t: "".join(sans_points(mots(t)))[:60]
    a = [cle(texte_source(s)) for s in segs]
    b = [cle(x["txt"]) for x in B]
    paires = []
    for op, a1, a2, b1, b2 in difflib.SequenceMatcher(None, a, b, autojunk=False).get_opcodes():
        k = min(a2 - a1, b2 - b1) if op == "replace" else (a2 - a1 if op == "equal" else 0)
        paires += [(a1 + x, b1 + x) for x in range(k)]
        paires += [(x, None) for x in range(a1 + k, a2)]
        paires += [(None, x) for x in range(b1 + k, b2)]
    return paires


def juger(n, segs, path):
    B, fautes_page, lx = lire_page(path)
    if not segs:                             # page-pont
        if n in PONTS_FIGES:
            if lx.empreinte != PONTS_FIGES[n]:
                fautes_page.append(("PAGE-PONT MODIFIÉE", f"empreinte des .sa-he {lx.empreinte} ≠ {PONTS_FIGES[n]} (relevée le 9 octobre 2026)"))
        elif any(x.strip() for x in lx.tous_sahe):
            fautes_page.append(("TEXTE .sa-he SUR UNE PAGE-PONT", f"{sum(1 for x in lx.tous_sahe if x.strip())} élément(s) : le SA HaRav n'a pas écrit ce siman"))
    fautes = [("page", [(f, d, 1) for f, d in fautes_page])] if fautes_page else []
    nchap = chapeau(texte_source(segs[0])) if segs else 0
    paires = list(zip(range(len(segs)), range(len(B)))) if len(B) == len(segs) else aligner(B, segs)
    parite, chap_recopie, vides = [], None, []
    for i, j in paires:
        if j is None:
            fautes.append((f"séif {i + 1:>2}", [("SÉIF SANS BLOC", "aucun bloc de la page ne porte ce séif", 1)]))
            continue
        if i is None:
            fautes.append((f"bloc {j + 1:>2}", [("BLOC EN TROP", " ".join(sans_points(mots(B[j]["txt"])))[:110], 1)]))
            parite.append(("+", sans_points(mots(B[j]["txt"]))))
            continue
        if not segs[i].strip():
            vides.append(i + 1)
        out, pm, recopie = juger_bloc(n, i, segs[i], B[j], nchap)
        if i == 0 and nchap:
            chap_recopie = recopie
        parite.append((i, pm))
        if out:
            fautes.append((f"séif {i + 1:>2}", out))
    return len(B), fautes, parite, chap_recopie, vides, B


# ---------------------------------------------------------------- étage de RENDU (--rendu)
#
# L'étage statique ne simule pas le navigateur. Celui-ci OUVRE la page dans Chromium, telle que le lecteur
# la reçoit. Les scripts sont fermés à l'étage statique (SCRIPTS_ADMIS : ceux du site, et eux seuls) ; ici :
#   1. la page est servie en local ; toute requête vers un autre hôte est bloquée ;
#   2. la mesure se fait dans un MONDE ISOLÉ (CDP Page.createIsolatedWorld) : un script de la page ne peut ni
#      remplacer elementFromPoint ni getComputedStyle ;
#   3. chaque séif est ouvert par un vrai clic sur son <summary> ; la page est parcourue de haut en bas ; la
#      mesure a lieu après 1,2 s ;
#   4. le CSSOM n'admet que ce que les pages emploient (règles de style, @media, @keyframes ; conditions de
#      largeur en px, d'impression, de mouvement réduit). Les règles qui ATTEIGNENT réellement le bloc, sa chaîne
#      jusqu'au .sa-he et son contenu, ou un de ses ancêtres (évaluées par le navigateur sur le sélecteur privé
#      de ses états et pseudo-éléments, qui atteint donc plus et jamais moins) : ni état ni pseudo-élément, ni
#      valeur qui suive l'écran ou le thème, ni règle d'impression ou de mouvement réduit ; sur la chaîne, des
#      propriétés typographiques ou de boîte seulement (CSS_CHAINE) ; aucune animation ;
#   5. chaque mot est photographié deux fois, tel quel puis rendu transparent : s'il ne change pas les pixels,
#      le lecteur ne le voit pas (un voile, un dégradé, une couleur, un contour, un surlignage, une découpe —
#      quelle qu'en soit la cause) ; un mot qui échoue est repris seul, au milieu de l'écran, contre les
#      éléments fixes. L'ordre visuel des mots doit être celui du texte (droite à gauche, ligne après ligne) ;
#   6. le tout à 1280×900, à 390×844 (téléphone) et à la plus petite largeur de chaque autre intervalle que les
#      conditions @media découpent (largeurs_supplementaires) : chaque jeu de règles de largeur est rendu ;
#   7. un processus de rendu bloqué plus de DELAI secondes sur une page est tué : la page sort en « RENDU IMPOSSIBLE », code 3.

CSS_CHAINE = re.compile(r"^(font(-[a-z]+)*|line-height|color|direction|text-align|unicode-bidi|"
                        r"padding(-[a-z]+)*|margin(-[a-z]+)*|border(-[a-z]+)*|background(-[a-z]+)*|"
                        r"cursor|list-style(-type)?|box-sizing|-webkit-font-smoothing|text-rendering|"
                        r"transition(-[a-z]+)*|gap|--[\w-]+)$")
# une requête @media admise (la liste est coupée aux virgules) : un type, puis des conditions de largeur ou de
# mouvement réduit — chaque répétition exige « ( », pas de retour arrière en cascade
MEDIA_ADMIS = re.compile(r"^\s*(?:(?:only|not)\s+)?(?:screen|print|all)?(?:\s*(?:and\s+)?\(\s*(?:min-width|max-width|width|"
                         r"prefers-reduced-motion)\s*:[^)]*\))*\s*$")
LARGEURS = ((1280, 900), (390, 844))
LARGEUR_MIN = 320


def largeurs_supplementaires(coupes):
    """Les conditions @media admises ne portent que sur la largeur (en px), l'impression et le mouvement réduit.
    Leurs points de rupture découpent l'axe des largeurs en intervalles où le même jeu de règles s'applique ; rendre
    une largeur par intervalle, c'est les avoir tous vus. Rend la plus petite largeur de chaque intervalle qu'aucune
    de LARGEURS ne représente (en deçà de LARGEUR_MIN, rien n'est rendu)."""
    bornes = sorted({LARGEUR_MIN} | {c for c in coupes if c > LARGEUR_MIN})
    out = []
    for i, a in enumerate(bornes):
        b = bornes[i + 1] - 1 if i + 1 < len(bornes) else float("inf")
        if not any(a <= w <= b for w, _ in LARGEURS):
            out.append(a)
    return out

PREPARE_JS = r"""
(async () => {
  const blocs = [...document.querySelectorAll('details')].filter(d => d.classList.contains('seif-details'));
  for (const d of blocs) { const s = d.querySelector(':scope > summary'); if (!d.open && s) s.click(); }
  const H = Math.max(document.documentElement.scrollHeight, document.body ? document.body.scrollHeight : 0);
  for (let y = 0; y < H; y += Math.max(200, window.innerHeight - 100)) { window.scrollTo(0, y); await new Promise(r => setTimeout(r, 15)); }
  window.scrollTo(0, 0);
  await new Promise(r => setTimeout(r, 1200));
  return blocs.length;
})()
"""

MESURE_JS = r"""
(() => {
  const MINPX = %(minpx)s;
  const HEB = /[א-ת֑-ׇ‍\[\]]+/g;
  const out = {blocs: [], fautes: [], mots: [], imgs: []};
  const faute = (f, d) => { if (out.fautes.length < 60) out.fautes.push([f, d]); };
  const blocs = [...document.querySelectorAll('details')].filter(d => d.classList.contains('seif-details'));
  const ferme = blocs.filter(d => !d.open).length;
  if (ferme) faute('SÉIF QUI NE S\'OUVRE PAS', ferme + ' bloc(s) restés fermés après un clic sur leur titre');
  // la chaîne : chaque bloc, son div.sa-block, son .sa-he et tout ce qu'il contient ; les ancêtres des blocs
  const chaine = new Set(), anc = new Set();
  for (const d of blocs) {
    for (let e = d.parentElement; e; e = e.parentElement) anc.add(e);
    chaine.add(d);
    for (const he of d.querySelectorAll('.sa-he')) {
      for (let e = he; e && e !== d; e = e.parentElement) chaine.add(e);
      he.querySelectorAll('*').forEach(e => chaine.add(e));
    }
  }
  // 4. le CSSOM, lu par le navigateur. Mesuré le 9 octobre 2026 sur les 1 095 pages du niveau 4 : elles n'emploient
  // que des règles de style, @media et @keyframes ; aucun sélecteur qui atteint le texte source ou un ancêtre ne
  // porte de pseudo-classe d'état ni de pseudo-élément ; aucune valeur n'y dépend de la largeur (vw, %%, calc…) ;
  // aucune règle @media print ou prefers-reduced-motion ne les atteint. Tout le reste est refusé.
  const STRUCT = /^(not|is|where|has|nth-child|nth-last-child|nth-of-type|nth-last-of-type|lang|dir|root|first-child|last-child|only-child|first-of-type|last-of-type|only-of-type|empty)$/i;
  // le sélecteur sans ses états ni pseudo-éléments, aux arguments de :not/:is/:where/:has compris : il atteint
  // PLUS d'éléments que l'original, jamais moins — un argument dont un membre se vide (« :is(.x, :focus) »,
  // « :not(:hover) ») fait tomber toute la pseudo-classe ; au-delà de deux niveaux de parenthèses, le sélecteur
  // devient illisible et la porte le refuse
  const membres = s => { const r = []; let d = 0, cur = '';
    for (const ch of s) { if (ch === '(') d++; if (ch === ')') d--; if (ch === ',' && d === 0) { r.push(cur); cur = ''; } else cur += ch; }
    r.push(cur); return r; };
  const reecrire = s => s.replace(/(::?)([a-z-]+)(\((?:[^()]|\([^()]*\))*\))?/gi, (m, c, n, a) => {
    if (!(c === ':' && STRUCT.test(n))) return '';
    if (!a) return m;
    const r = membres(a.slice(1, -1)).map(x => reecrire(x).trim());
    return r.some(x => !x) ? '' : ':' + n + '(' + r.join(', ') + ')';
  });
  const nonStruct = s => [...s.matchAll(/(::?)([a-z-]+)/gi)].some(([, c, n]) => !(c === ':' && STRUCT.test(n)));
  const VARIABLE = /[\d.][sld]?v(?:w|h|i|b|min|max)\b|[\d.]cq(?:w|h|i|b|min|max)\b|%%|calc\(|min\(|max\(|clamp\(|light-dark\(|env\(|attr\(/i;
  const MEDIA = new RegExp(%(media)s);
  const coupes = new Set();
  const condition = (m, ou) => {
    if (!m || /^\s*$/.test(m)) return false;
    if (!m.split(',').every(q => MEDIA.test(q))) { faute('CONDITION @media NON ADMISE', ou + m.slice(0, 80)); return true; }
    // les points de rupture : chaque intervalle qu'ils découpent sera rendu (voir largeurs_supplementaires)
    for (const [, f, v] of m.matchAll(/\(\s*(min-width|max-width|width)\s*:\s*([^)]*)\)/gi)) {
      const x = /^\s*(\d+(?:\.\d+)?)px\s*$/i.exec(v);
      if (!x) { faute('CONDITION @media NON ADMISE', ou + m.slice(0, 80) + ' (largeur en px seulement)'); continue; }
      const w = parseFloat(x[1]);
      if (/^max/i.test(f)) coupes.add(Math.floor(w) + 1);
      else if (/^min/i.test(f)) coupes.add(Math.ceil(w));
      else { coupes.add(Math.ceil(w)); coupes.add(Math.floor(w) + 1); }
    }
    return true;
  };
  const regles = [];
  const visite = (rules, cond) => { for (const r of rules) {
    const t = r.constructor ? r.constructor.name : '?';
    if (t === 'CSSMediaRule' || t === 'CSSImportRule') {
      const m = r.media ? r.media.mediaText : '';
      const c = condition(m, '') ? cond.concat([m]) : cond;
      if (t === 'CSSMediaRule') visite(r.cssRules, c);
      else { try { visite(r.styleSheet.cssRules, c); } catch (e) { faute('FEUILLE ILLISIBLE', String(r.href)); } }
      continue;
    }
    if (t === 'CSSFontFaceRule') { faute('POLICE DÉFINIE PAR LA PAGE', '@font-face'); continue; }
    if (t === 'CSSKeyframesRule') continue;
    if (t !== 'CSSStyleRule') { faute('RÈGLE CSS NON ADMISE', t + ' : ' + String(r.cssText || '').slice(0, 70)); continue; }
    if (r.cssRules && r.cssRules.length) faute('CSS IMBRIQUÉ NON ADMIS', r.selectorText.slice(0, 80));
    regles.push([r, cond]);
  } };
  if (document.adoptedStyleSheets && document.adoptedStyleSheets.length) faute('RÈGLE CSS NON ADMISE', 'feuille adoptée (adoptedStyleSheets)');
  for (const e of document.querySelectorAll('*')) if (e.shadowRoot) { faute('RÈGLE CSS NON ADMISE', 'arbre fantôme (shadow DOM) sur <' + e.tagName.toLowerCase() + '>'); break; }
  for (const sh of document.styleSheets) {
    const m = sh.media ? sh.media.mediaText : '';
    const c = condition(m, '<' + (sh.ownerNode ? sh.ownerNode.tagName.toLowerCase() : '?') + ' media> ') ? [m] : [];
    try { visite(sh.cssRules, c); } catch (e) { faute('FEUILLE ILLISIBLE', String(sh.href)); }
  }
  for (const [r, cond] of regles) {
    // l'impression et le mouvement réduit ne sont pas rendus : leurs règles n'atteignent ni la chaîne ni un ancêtre
    const nonRendu = cond.some(m => /print|prefers-reduced-motion/i.test(m));
    const ou = cond.length ? '@media ' + cond.join(' / ') + ' ' : '';
    for (const sel0 of r.selectorText.split(',')) {
      const sel = reecrire(sel0).trim() || '*';
      let touche = false, toucheAnc = false;
      try { for (const e of document.querySelectorAll(sel)) { if (chaine.has(e)) { touche = true; break; } if (anc.has(e)) toucheAnc = true; } }
      catch (e) { faute('SÉLECTEUR QUE LA PORTE NE SAIT PAS LIRE', sel0.trim().slice(0, 80)); continue; }
      if (!touche && !toucheAnc) continue;
      const qui = touche ? 'LE TEXTE SOURCE' : 'UN ANCÊTRE DU TEXTE SOURCE';
      // un état (:hover, :focus…) : la mesure ne survole ni ne focalise ; un pseudo-élément : du texte ou un voile
      // que le DOM ne porte pas
      if (nonStruct(sel0)) { faute('PSEUDO-CLASSE OU PSEUDO-ÉLÉMENT SUR ' + qui, ou + sel0.trim().slice(0, 80)); continue; }
      if (nonRendu) { faute('RÈGLE @media NON RENDUE SUR ' + qui, ou + sel0.trim().slice(0, 60)); continue; }
      for (const p of r.style) {
        const v = r.style.getPropertyValue(p);
        const d = ou + sel0.trim().slice(0, 60) + ' { ' + p + ': ' + v.slice(0, 40) + ' }';
        // une valeur qui suit la largeur de l'écran ou son thème change ENTRE les largeurs rendues
        if (VARIABLE.test(v) || /^(color-scheme|zoom|-webkit-text-fill-color|-webkit-text-stroke.*)$/.test(p)) faute('VALEUR QUI DÉPEND DE L\'ÉCRAN OU DU THÈME SUR ' + qui, d);
        else if (touche && !new RegExp(%(chaine)s).test(p)) faute('STYLE NON ADMIS SUR LA CHAÎNE', d);
      }
    }
  }
  out.coupes = [...coupes].sort((a, b) => a - b);
  // états calculés : animation, liste, styles en ligne
  for (const e of [...chaine, ...anc]) {
    const s = getComputedStyle(e);
    if (s.animationName && s.animationName !== 'none') faute('ANIMATION SUR LE TEXTE SOURCE OU UN ANCÊTRE', e.tagName.toLowerCase() + ' : ' + s.animationName);
    if (chaine.has(e) && /list-item/.test(s.display)) faute('LISTE (::marker) SUR LE TEXTE SOURCE', e.tagName.toLowerCase());
    if (chaine.has(e) && e.getAttribute('style') && e.tagName !== 'P') faute('STYLE EN LIGNE SUR LA CHAÎNE', e.tagName.toLowerCase());
    if (anc.has(e) && e.getAttribute('style')) faute('STYLE EN LIGNE SUR UN ANCÊTRE DU TEXTE SOURCE', e.tagName.toLowerCase() + ' : ' + e.getAttribute('style').slice(0, 60));
    for (const p of ['scale', 'rotate', 'translate', 'zoom']) { const v = s[p]; if (v && v !== 'none' && v !== '1' && v !== 'normal' && v !== '0px') faute('TRANSFORMATION', e.tagName.toLowerCase() + ' ' + p + ': ' + v); }
    if (s.transform !== 'none' && chaine.has(e)) faute('TRANSFORMATION', e.tagName.toLowerCase() + ' transform: ' + s.transform);
  }
  // les mots : leur rectangle (coordonnées du document), dans l'ordre du texte
  window.scrollTo({top: 0, left: 0, behavior: 'instant'});
  window.__mots = [];
  const X = () => window.scrollX, Y = () => window.scrollY;
  blocs.forEach((d, bi) => {
    let dom = '';
    const ordre = [];
    for (const he of d.querySelectorAll('.sa-he')) {
      const w = document.createTreeWalker(he, NodeFilter.SHOW_ELEMENT | NodeFilter.SHOW_TEXT);
      for (let n = w.currentNode; n; n = w.nextNode()) {
        if (n.nodeType === 1) {
          if (n.tagName === 'BR') dom += ' ';
          if (n.tagName === 'IMG') { const r = n.getBoundingClientRect(); window.__mots.push(n);
            out.imgs.push({b: bi, i: window.__mots.length - 1, src: n.getAttribute('src') || '', ok: n.complete && n.naturalWidth > 0, r: [r.left + X(), r.top + Y(), r.width, r.height]}); }
          continue;
        }
        dom += n.data;
        for (const m of n.data.matchAll(HEB)) {
          const rg = document.createRange(); rg.setStart(n, m.index); rg.setEnd(n, m.index + m[0].length);
          const rs = [...rg.getClientRects()].filter(r => r.width >= 1 && r.height >= 1);
          const fs = parseFloat(getComputedStyle(n.parentElement).fontSize);
          let raison = null;
          if (!rs.length) raison = 'boîte vide';
          else if (rs.some(r => r.height < Math.max(MINPX, 0.6 * fs) * 0.85)) raison = 'écrasé (' + Math.round(rs[0].height) + ' px)';
          const id = out.mots.length; window.__mots.push(rg);
          out.mots.push({b: bi, i: window.__mots.length - 1, t: m[0], r: rs.map(r => [r.left + X(), r.top + Y(), r.width, r.height]), raison});
          if (rs.length) ordre.push([id, rs[0]]);
        }
      }
    }
    // ordre visuel : ligne après ligne, et de droite à gauche dans la ligne
    for (let k = 1; k < ordre.length; k++) {
      const [ia, a] = ordre[k - 1], [ib, b] = ordre[k];
      const memeLigne = Math.abs(a.top - b.top) < 0.5 * Math.min(a.height, b.height);
      if (memeLigne ? (b.left > a.left + 2) : (b.top < a.top)) { faute('ORDRE VISUEL INVERSÉ', 'séif ' + (bi + 1) + ' : « ' + out.mots[ib].t + ' » affiché avant « ' + out.mots[ia].t + ' »'); break; }
    }
    out.blocs.push({dom});
  });
  out.H = Math.max(document.documentElement.scrollHeight, document.body ? document.body.scrollHeight : 0);
  out.W = window.innerWidth; out.VH = window.innerHeight;
  return out;
})()
"""

MASQUE_JS = r"""
((on) => {
  // une feuille, posée par le monde isolé, activée puis désactivée : les GLYPHES du texte source transparents, les
  // dessins cachés. Jamais « color » : un fond, une bordure ou une ombre en currentColor changerait avec lui, et un
  // texte peint sur un fond de sa couleur paraîtrait visible (témoin R4 du quatrième arbitrage). Une règle de la page
  // plus forte mettrait la feuille en échec : le mot paraîtrait INVISIBLE (fausse alerte, jamais faux vert).
  let s = document.getElementById('porte-niveau4-masque');
  if (!s) { s = document.createElement('style'); s.id = 'porte-niveau4-masque';
    s.textContent = 'details.seif-details .sa-he, details.seif-details .sa-he * { -webkit-text-fill-color: transparent !important; -webkit-text-stroke-width: 0 !important; text-shadow: none !important; } details.seif-details .sa-he img { visibility: hidden !important; }';
    document.documentElement.appendChild(s); }
  s.disabled = !on;
  void document.body.offsetHeight;
  return true;
})(%s)
"""


def _travailleur(conn, port, root):
    """Processus de rendu : un Chromium, des pages ; reçoit (chemin, n° de blocs), rend la liste des fautes."""
    import io
    try:
        from playwright.sync_api import sync_playwright
        import numpy as np
        from PIL import Image
    except ImportError as e:
        conn.send(("ERREUR", f"module absent ({e.name}) : pip install playwright pillow numpy"))
        return
    try:
        pw = sync_playwright().start()
        nav = _chromium(pw)
    except Exception as e:  # noqa: BLE001
        conn.send(("ERREUR", str(e).splitlines()[0][:200]))
        return
    conn.send(("PRÊT", None))
    base = f"http://127.0.0.1:{port}/"

    import base64

    def capture(cdp):
        # CDP directement : l'écran tel qu'il est affiché. La capture de Playwright décale l'image d'une page
        # de droite à gauche qui déborde (de la largeur du débordement, 104 px au 14 hébreu à 390 px).
        png = base64.b64decode(cdp.send("Page.captureScreenshot", {"format": "png", "fromSurface": True, "optimizeForSpeed": True})["data"])
        return np.asarray(Image.open(io.BytesIO(png)).convert("RGB")).astype(np.int16)

    while True:
        job = conn.recv()
        if job is None:
            break
        path = job
        fautes, resultats = [], []
        largeurs, coupes, k = list(LARGEURS), set(), 0
        while k < len(largeurs):
            W, VH = largeurs[k]
            k += 1
            ctx = nav.new_context(viewport={"width": W, "height": VH}, device_scale_factor=1, color_scheme="light")
            try:
                page = ctx.new_page()
                page.route("**/*", lambda r: r.continue_() if r.request.url.startswith(base) else r.abort())
                page.goto(base + os.path.relpath(path, root), wait_until="load", timeout=45000)
                cdp = ctx.new_cdp_session(page)
                fid = cdp.send("Page.getFrameTree")["frameTree"]["frame"]["id"]
                monde = cdp.send("Page.createIsolatedWorld", {"frameId": fid, "worldName": "porte-niveau4"})["executionContextId"]

                def ev(expr, attendre=False):
                    r = cdp.send("Runtime.evaluate", {"expression": expr, "contextId": monde, "returnByValue": True,
                                                      "awaitPromise": attendre, "timeout": 120000})
                    if "exceptionDetails" in r:
                        raise RuntimeError("évaluation : " + str(r["exceptionDetails"].get("text"))[:120])
                    return r["result"].get("value")
                ev(PREPARE_JS, attendre=True)
                m = ev(MESURE_JS % {"minpx": 8, "media": json.dumps(MEDIA_ADMIS.pattern), "chaine": json.dumps(CSS_CHAINE.pattern)})
                fautes += [(f"{f} [{W} px]", d) for f, d in m["fautes"]]
                # 6. les intervalles de largeur que les conditions @media de la page découpent : un rendu par intervalle
                coupes |= set(m.get("coupes") or [])
                largeurs += [(w, 900) for w in largeurs_supplementaires(coupes) if w not in {x for x, _ in largeurs}]
                # 5. les pixels, par tuiles d'écran (verticales ET horizontales : une page de droite à gauche qui
                # déborde sur téléphone se lit en défilant vers la gauche), telles quelles puis texte transparent
                mots, imgs = m["mots"], m["imgs"]
                vis = [False] * len(mots)
                vis_img = [False] * len(imgs)
                tuiles = {}
                for i, x in enumerate(mots):
                    for (rx, ry, rw, rh) in x["r"]:
                        tuiles.setdefault((int(ry // VH), int(rx // W)), []).append(("m", i, rx, ry, rw, rh))
                for i, x in enumerate(imgs):
                    rx, ry, rw, rh = x["r"]
                    if rw > 0 and rh > 0:
                        tuiles.setdefault((int(ry // VH), int(rx // W)), []).append(("i", i, rx, ry, rw, rh))

                def ecart(a, b):
                    return np.abs(a - b).max(axis=2) > 40

                def comparer(d, vx, vy, rw, rh, seuil):
                    x0, x1 = max(0, int(vx)), min(d.shape[1], int(vx + rw) + 1)
                    y0, y1 = max(0, int(vy)), min(d.shape[0], int(vy + rh) + 1)
                    if x1 <= x0 or y1 <= y0:
                        return False
                    return int(d[y0:y1, x0:x1].sum()) >= max(seuil[0], seuil[1] * (x1 - x0) * (y1 - y0))
                for (ky, kx), objets in sorted(tuiles.items()):
                    sx, sy = ev(f"(window.scrollTo({{left: {kx * W}, top: {ky * VH}, behavior: 'instant'}}), [window.scrollX, window.scrollY])")
                    a = capture(cdp)
                    ev(MASQUE_JS % "true")
                    b = capture(cdp)
                    ev(MASQUE_JS % "false")
                    d = ecart(a, b)                     # une fois par tuile
                    for (genre, i, rx, ry, rw, rh) in objets:
                        if genre == "m" and not vis[i]:
                            vis[i] = comparer(d, rx - sx, ry - sy, rw, rh, (6, 0.03))
                        elif genre == "i" and not vis_img[i]:
                            vis_img[i] = comparer(d, rx - sx, ry - sy, rw, rh, (12, 0.02))
                # seconde chance, objet par objet, centré à l'écran (un élément fixe ne couvre pas tout l'écran)
                def centrer(k):
                    return ev(f"""(() => {{ const o = window.__mots[{k}]; const r0 = (o.getClientRects ? o.getClientRects()[0] : null) || o.getBoundingClientRect();
                        window.scrollBy({{left: r0.left + r0.width / 2 - innerWidth / 2, top: r0.top + r0.height / 2 - innerHeight * 0.4, behavior: 'instant'}});
                        const q = (o.getClientRects ? o.getClientRects()[0] : null) || o.getBoundingClientRect(); return [q.left, q.top, q.width, q.height]; }})()""")
                # trois mots d'un séif confirmés invisibles suffisent à le dire : les suivants ne sont pas repris un à un
                # (une page entièrement voilée en demanderait des milliers), ils sortent « non repris »
                echecs = {}
                for genre, liste, etat, seuil in (("m", mots, vis, (6, 0.03)), ("i", imgs, vis_img, (12, 0.02))):
                    for i, x in enumerate(liste):
                        if etat[i] or not x["r"] or x.get("raison"):
                            continue
                        if echecs.get((genre, x["b"]), 0) >= 3:
                            if genre == "m":
                                x["raison"] = "non repris un à un (trois mots du séif déjà confirmés invisibles)"
                            continue
                        vx, vy, rw, rh = centrer(x["i"])
                        if rw < 1 or rh < 1:
                            continue
                        a = capture(cdp)
                        ev(MASQUE_JS % "true")
                        b = capture(cdp)
                        ev(MASQUE_JS % "false")
                        etat[i] = comparer(ecart(a, b), vx, vy, rw, rh, seuil)
                        if not etat[i]:
                            echecs[(genre, x["b"])] = echecs.get((genre, x["b"]), 0) + 1
                resultats.append((W, m, vis, vis_img))
            except Exception as e:  # noqa: BLE001
                fautes.append(("RENDU IMPOSSIBLE", f"[{W} px] " + str(e).splitlines()[0][:160]))
            finally:
                ctx.close()
        conn.send(("FAIT", (fautes, [(W, m["blocs"], [(x["b"], x["t"], x["raison"]) for x in m["mots"]], v,
                                      [(x["b"], x["src"], x["ok"]) for x in m["imgs"]], vi) for (W, m, v, vi) in resultats])))
    try:
        nav.close()
        pw.stop()
    except Exception:  # noqa: BLE001
        pass


def _chromium(p):
    essais = [None, os.environ.get("DAAT_CHROMIUM")]
    import glob as _g
    essais += sorted(_g.glob("/opt/pw-browsers/chromium-*/chrome-linux/chrome"), reverse=True)
    err = None
    for e in essais:
        if e is False:
            continue
        try:
            return p.chromium.launch(**({"executable_path": e} if e else {}))
        except Exception as x:  # noqa: BLE001 — on essaie le suivant, et l'on rend la dernière erreur
            err = x
    raise RuntimeError(f"Chromium introuvable : {str(err).splitlines()[0] if err else '?'}")


class Rendu:
    """Un serveur HTTP local sur ROOT et PROCESSUS processus de rendu sous surveillance : un processus bloqué plus de
    DELAI secondes sur une page est tué et relancé, la page sort en « RENDU IMPOSSIBLE » (code 3)."""
    DELAI = 900
    largeurs_vues = set()
    PROCESSUS = max(1, min(3, (os.cpu_count() or 2) - 1))

    def __enter__(self):
        import threading, http.server, socketserver, functools, multiprocessing

        class _Q(http.server.SimpleHTTPRequestHandler):
            def log_message(self, *a):
                pass
        self.srv = socketserver.ThreadingTCPServer(("127.0.0.1", 0), functools.partial(_Q, directory=ROOT))
        self.port = self.srv.server_address[1]
        threading.Thread(target=self.srv.serve_forever, daemon=True).start()
        self.mp = multiprocessing.get_context("fork")
        self.ouvriers = [self._lancer() for _ in range(self.PROCESSUS)]
        return self

    def _lancer(self):
        conn, enfant = self.mp.Pipe()
        proc = self.mp.Process(target=_travailleur, args=(enfant, self.port, ROOT), daemon=True)
        proc.start()
        if not conn.poll(120):
            proc.kill()
            raise RuntimeError("Chromium ne démarre pas")
        etat, msg = conn.recv()
        if etat != "PRÊT":
            proc.kill()
            raise RuntimeError(msg)
        return [proc, conn]

    def __exit__(self, *a):
        for proc, conn in self.ouvriers:
            try:
                conn.send(None)
                proc.join(10)
            except Exception:  # noqa: BLE001
                pass
            if proc.is_alive():
                proc.kill()
        self.srv.shutdown()

    def juger_tous(self, travaux):
        """travaux : [(clé, chemin, blocs statiques)]. Rend {clé: (fautes, impossible)}."""
        import time
        from multiprocessing.connection import wait
        res, attente, actifs, fait = {}, list(travaux), {}, 0
        while attente or actifs:
            for k, ouv in enumerate(self.ouvriers):
                if k not in actifs and attente:
                    cle, path, B = attente.pop(0)
                    ouv[1].send(path)
                    actifs[k] = (cle, B, time.time() + self.DELAI)
            prets = wait([self.ouvriers[k][1] for k in actifs], timeout=2)
            for k in list(actifs):
                cle, B, limite = actifs[k]
                conn = self.ouvriers[k][1]
                if conn in prets:
                    try:
                        msg = conn.recv()
                        res[cle] = self._analyser(msg[1], B)
                    except (EOFError, OSError) as e:
                        res[cle] = ([("RENDU IMPOSSIBLE", f"processus de rendu perdu ({type(e).__name__})", 1)], True)
                        self.ouvriers[k][0].kill()
                        self.ouvriers[k] = self._lancer()
                    del actifs[k]
                    fait += 1
                elif time.time() > limite:
                    self.ouvriers[k][0].kill()
                    self.ouvriers[k] = self._lancer()
                    res[cle] = ([("RENDU IMPOSSIBLE", f"aucune réponse en {self.DELAI} s : processus de rendu tué", 1)], True)
                    del actifs[k]
                    fait += 1
            if travaux and fait and fait % 30 == 0 and prets:
                print(f"  … rendu : {fait}/{len(travaux)} pages", file=sys.stderr, flush=True)
        return res

    @staticmethod
    def _analyser(msg, blocs_statiques):
        fautes0, resultats = msg
        Rendu.largeurs_vues.update(W for (W, *_r) in resultats)
        fautes = [(f, d, 1) for f, d in fautes0]
        impossible = any(f.startswith("RENDU IMPOSSIBLE") for f, _ in fautes0)
        from collections import Counter
        for (W, blocs, mots_, vis, imgs, vis_img) in resultats:
            if len(blocs) != len(blocs_statiques):
                fautes.append((f"BLOCS CHANGÉS PAR SCRIPT [{W} px]", f"{len(blocs_statiques)} blocs dans le fichier, {len(blocs)} dans la page", 1))
                continue
            for k, (b, st) in enumerate(zip(blocs, blocs_statiques)):
                if sans_points(mots(b["dom"])) != sans_points(mots(st["txt"])):
                    fautes.append((f"TEXTE CHANGÉ PAR SCRIPT [{W} px]", f"séif {k + 1}", 1))
            invis, ex = Counter(), {}
            for (bi, t, raison), v in zip(mots_, vis):
                if raison or not v:
                    r = raison or "aucun pixel ne change quand le mot disparaît"
                    invis[(bi, r)] += 1
                    ex.setdefault((bi, r), t)
            for (bi, r), c in sorted(invis.items())[:12]:
                fautes.append((f"TEXTE SOURCE INVISIBLE AU LECTEUR [{W} px]", f"séif {bi + 1} : {c} mot(s), {r} (p. ex. « {ex[(bi, r)]} »)", c))
            for (bi, src, ok), v in zip(imgs, vis_img):
                st = [s for _r, s, _a in blocs_statiques[bi]["img"]]
                if src not in st:
                    fautes.append((f"DESSIN CHANGÉ PAR SCRIPT [{W} px]", f"séif {bi + 1}", 1))
                elif not ok:
                    fautes.append((f"DESSIN NON CHARGÉ [{W} px]", f"séif {bi + 1}", 1))
                elif not v:
                    fautes.append((f"DESSIN INVISIBLE [{W} px]", f"séif {bi + 1}", 1))
        return fautes, impossible


def main(argv):
    bref = "--bref" in argv
    use_cache = "--cache" in argv
    nums = []
    if "--tous" in argv:
        nums = list(range(1, 366))
    for i, x in enumerate(argv):
        if x == "--section" and i + 1 < len(argv):
            nums += [n for s, rng in SECTIONS if s == argv[i + 1] for n in rng]
        elif x.isdigit():
            nums.append(int(x))
    nums = sorted(set(nums))
    if not nums:
        print(__doc__.split("\n\n")[1])
        return 2
    if LACUNES_ERR:
        print(f"⛔ LACUNES_MESUREES illisible ({LACUNES_ERR}) : aucune lacune ne sera admise")
    stats = {"conformes": [], "divergents": [], "lacunes": [], "injoignables": [], "absents": [], "rendu_impossible": []}
    fam, edition_vue, provenances = {}, set(), set()
    # 1. l'étage statique, pour tous les simanim
    etats = []
    for n in nums:
        sec = section_de(n)
        if sec is None:
            etats.append((n, None, "absent", None))
            continue
        try:
            segs, titre, prov = fetch(n, use_cache)
        except RuntimeError as e:
            etats.append((n, sec, "injoignable", str(e)))
            continue
        provenances.add(prov)
        if segs:
            edition_vue.add(titre)
        par = {}
        for lang, suf in LANGS:
            p = os.path.join(ROOT, f"sources/{sec}/siman-{n}/niveau-4-daat-harav{suf}.html")
            if not os.path.exists(p):
                par[lang] = ("absent", p)
                continue
            try:
                par[lang] = ("lu", p, juger(n, segs, p))
            except RuntimeError as e:
                par[lang] = ("erreur", p, str(e))
        etats.append((n, sec, "ok", (segs, titre, prov, par)))
    # 2. l'étage de rendu, toutes les pages à la fois, réparties entre les processus
    rendus = {}
    a_rendre = "--rendu" in argv
    if a_rendre:
        travaux = [((n, lang), x[1], x[2][5]) for n, sec, k, d in etats if k == "ok" for lang, x in d[3].items() if x[0] == "lu"]
        try:
            with Rendu() as rendu:
                rendus = rendu.juger_tous(travaux)
        except RuntimeError as e:
            print(f"⛔ RENDU IMPOSSIBLE : {e} — rien n'est conclu sur ce que voit le lecteur")
            return 3
    # 3. le rapport
    for n, sec, k, d in etats:
        if k == "absent":
            print(f"=== Siman {n} : hors des sections couvertes (1-365)")
            stats["absents"].append(n)
            continue
        if k == "injoignable":
            print(f"=== Siman {n} ({sec}) — ⛔ SOURCE NON LUE : {d} — rien n'est conclu")
            stats["injoignables"].append(n)
            continue
        segs, titre, prov, par = d
        lignes, bad, par_langue, chap_par_langue, vides = [], False, {}, {}, set()
        for lang, _suf in LANGS:
            x = par.get(lang)
            if x is None:
                continue
            if x[0] == "absent":
                lignes.append(f"  {lang}: FICHIER ABSENT {os.path.relpath(x[1], ROOT)}")
                bad = True
                continue
            if x[0] == "erreur":
                lignes.append(f"  {lang}: ⛔ {x[2]}")
                bad = True
                continue
            nb, fautes, parite, chap, vd, B = x[2]
            fautes = list(fautes)
            if (n, lang) in rendus:
                fr, imposs = rendus[(n, lang)]
                if imposs:
                    stats["rendu_impossible"].append(n)
                if fr:
                    fautes.append(("rendu", fr))
            vides.update(vd)
            par_langue[lang] = parite
            chap_par_langue[lang] = chap
            cnt_ok = nb == len(segs)
            etat = "✅ IDENTIQUE" if (cnt_ok and not fautes) else "❌ DIVERGENCE"
            lignes.append(f"  {lang}: {nb} blocs seif-details [{'OK' if cnt_ok else f'≠ {len(segs)} ATTENDUS'}]"
                          f" | texte source vs Sefaria : {etat}"
                          + (f" — {len(fautes)} écart(s)" if fautes else ""))
            if not cnt_ok or fautes:
                bad = True
            for etiq, ec in fautes:
                for f_, t, k_ in ec:
                    fam.setdefault(f_, set()).add((n, lang, etiq))
                if not bref:
                    for f_, t, k_ in ec[:8]:
                        lignes.append(f"      {etiq} : {f_} ({k_} mot{'s' if k_ > 1 else ''}) « {t[:110]}{'…' if len(t) > 110 else ''} »")
                    if len(ec) > 8:
                        lignes.append(f"      {etiq} : … et {len(ec) - 8} autre(s) écart(s)")
        for (rn, rs), (_a, _b, raison) in RESIDUS.items():
            if rn == n:
                lignes.append(f"  résidu de Sefaria écarté au séif {rs} : {raison}")
        for v in sorted(vides):
            lignes.append(f"  avertissement : le séif {v} est VIDE chez Sefaria — la page ne peut que le laisser vide")
        if len(par_langue) > 1:
            ref_lang = next(iter(par_langue))
            diff = [L for L in par_langue if par_langue[L] != par_langue[ref_lang]]
            if diff:
                ou = []
                for L in diff:
                    for (a, b) in zip(par_langue[ref_lang], par_langue[L]):
                        if a != b:
                            ou.append(f"{L} ≠ {ref_lang} au séif {a[0] + 1 if isinstance(a[0], int) else '?'}")
                            break
                    else:
                        ou.append(f"{L} ≠ {ref_lang} (nombre de blocs)")
                lignes.append(f"  ⚠️  PARITÉ FR/HE/EN du texte source : DIVERGENTE — {' ; '.join(ou)}")
                fam.setdefault("PARITÉ", set()).add((n, "", ""))
                bad = True
            else:
                lignes.append("  parité FR/HE/EN du texte source : ✅ identique")
            cv = {L: c for L, c in chap_par_langue.items() if c is not None}
            if len(set(cv.values())) > 1:
                lignes.append("  avertissement : le chapeau est recopié en "
                              + ", ".join(L for L, c in cv.items() if c) + ", pas en "
                              + ", ".join(L for L, c in cv.items() if not c) + " (chaque forme est conforme)")
        if not segs:
            stats["lacunes"].append(n)
        (stats["divergents"] if bad else stats["conformes"]).append(n)
        if bref:
            if bad:
                print(f"❌ {n:>3} ({sec}) : " + " · ".join(l.strip() for l in lignes
                      if any(k in l for k in ("DIVERGENCE", "ABSENT", "PARITÉ", "ATTENDUS", "⛔"))))
        else:
            print(f"\n=== Siman {n} ({sec}) — SA HaRav : {len(segs)} séifim [{titre} ; {prov}] ===")
            print("\n".join(lignes))
    print()
    print(f"Édition confrontée : {', '.join(sorted(edition_vue)) or '—'} · source : "
          + ", ".join(sorted(provenances)) + (" (INSTANTANÉ local, non retéléchargé)" if "cache" in provenances else ""))
    print(f"CONFRONTÉ : {len(nums)} simanim · conformes {len(stats['conformes'])} (dont lacunes confirmées du SA HaRav {len(stats['lacunes'])})"
          f" · divergents {len(stats['divergents'])} · source non lue {len(stats['injoignables'])}")
    for f_ in sorted(fam):
        sims = sorted({x[0] for x in fam[f_]})
        print(f"  {f_:28s} {len(fam[f_]):4d} occurrence(s) dans {len(sims):3d} simanim : {' '.join(map(str, sims))}")
    if stats["divergents"]:
        print(f"  divergents : {' '.join(map(str, stats['divergents']))}")
    if stats["injoignables"]:
        print(f"  ⛔ source non lue : {' '.join(map(str, stats['injoignables']))}")
    if a_rendre:
        print(f"Rendu : Chromium, largeurs {', '.join(f'{w} px' for w in sorted(Rendu.largeurs_vues, reverse=True)) or 'aucune'} (une par intervalle @media), monde isolé, séifs ouverts au clic, pixels comparés, scripts du site seuls, autres hôtes bloqués"
              + (f" · RENDU IMPOSSIBLE pour {' '.join(map(str, sorted(set(stats['rendu_impossible']))))}" if stats["rendu_impossible"] else ""))
    else:
        print("RENDU NON EXÉCUTÉ : le texte est confronté, sa VISIBILITÉ ne l'est pas — avant de publier, relancer avec --rendu")
    ok = not stats["divergents"] and not stats["absents"]
    print("\n" + ("✅ VÉRIFICATION SOURCE : tout est conforme" if ok and not stats["injoignables"]
                  else "❌ VÉRIFICATION SOURCE : divergence(s) détectée(s) — NE PAS PUBLIER" if not ok
                  else "⛔ VÉRIFICATION SOURCE : source non lue pour une partie — RIEN N'EST CONCLU pour elle"))
    if stats["rendu_impossible"]:
        print(f"⛔ RENDU IMPOSSIBLE pour {' '.join(map(str, sorted(set(stats['rendu_impossible']))))} : rien n'est conclu sur ce que voit le lecteur")
    if stats["rendu_impossible"] and set(stats["divergents"]) <= set(stats["rendu_impossible"]):
        return 3
    if not ok:
        return 1
    return 3 if stats["injoignables"] else 0


if __name__ == "__main__":
    sys.exit(main(sys.argv[1:]))
