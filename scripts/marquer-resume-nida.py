#!/usr/bin/env python3
"""Bloc נדה 183-200 : cesser de présenter une condensation comme le texte source.

Les niveaux 1 de ces dix-huit simanim portent, sous `blockquote.text-source`, un texte
hébreu RETAPÉ, VOCALISÉ et ABRÉGÉ — 46 % du Choul'han Aroukh, 22 % pour le siman 190 —
rangé par familles thématiques au lieu de l'ordre du livre. Le bloc étiqueté « Seif 2-4 »
du 190 porte 311 lettres là où les séifim 2, 3 et 4 en totalisent 488, et n'en est pas
une sous-chaîne : דהינו pour דהיינו, אפלו pour אפילו.

Ce marquage est TRANSITOIRE. Il applique la convention du dépôt — une condensation
s'introduit par « résumé » / תמצית / summary et n'est pas jugée comme un verbatim — en
attendant que chaque siman soit reconstruit à partir de la source. Chaque reconstruction
le défait pour ce siman.
"""
import re, sys, os, io

ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__))) \
    if os.path.basename(os.path.dirname(os.path.abspath(__file__))) == 'scripts' \
    else '/home/user/Daat.ai'

REGLE = """  blockquote.text-resume {
    background: #f7f5f2;
    border-right: 4px dashed #b9a06a;
    direction: rtl;
    text-align: right;
    margin: 10px 0;
    padding: 10px 15px;
    font-family: 'Frank Ruhl Libre', serif;
    font-size: 12pt;
    font-style: italic;
  }

  blockquote.text-resume .resume-marque {
    display: block;
    direction: inherit;
    font-family: 'Cormorant Garamond', serif;
    font-style: normal;
    font-size: 10pt;
    color: #7a6a44;
    margin-bottom: 6px;
  }

"""

MARQUE = {
    'fr': '<span class="resume-marque"><em>résumé</em> — condensation, non le texte '
          'intégral du Choul’han Aroukh</span>',
    'he': '<span class="resume-marque"><em>תמצית</em> — קיצור, ולא לשון השולחן ערוך '
          'במלואה</span>',
    'en': '<span class="resume-marque"><em>summary</em> — a condensation, not the full '
          'text of the Shulchan Arukh</span>',
}

AVIS = {
    'fr': '<div class="key-point"><strong>Avis de lecture.</strong> Les blocs hébreux de '
          'cette section sont des <em>résumés</em>, pas le texte du Choul’han Aroukh '
          'dans sa lettre : ils en condensent la substance et n’en reprennent pas '
          'toutes les clauses. La restitution du texte intégral, séif par séif et dans '
          'l’ordre du livre, est en cours. Pour la lettre exacte, se reporter à la '
          'source.</div>',
    'he': '<div class="key-point"><strong>הערת קריאה.</strong> הקטעים העבריים שבפרק זה הם '
          '<em>תמציות</em>, ולא לשון השולחן ערוך כמות שהיא: הם מקצרים את העניין ואינם '
          'מביאים את כל הבבות. השבת הנוסח המלא, סעיף אחר סעיף וכסדר הספר, נעשית עתה. '
          'ללשון המדויקת — עיין במקור.</div>',
    'en': '<div class="key-point"><strong>A note on reading.</strong> The Hebrew blocks in '
          'this section are <em>summaries</em>, not the text of the Shulchan Arukh as it '
          'stands: they condense the substance and do not carry every clause. The full '
          'text is being restored, seif by seif and in the order of the book. For the '
          'exact wording, go to the source.</div>',
}

def langue(p):
    b = os.path.basename(p)
    return 'he' if b.endswith('-he.html') else 'en' if b.endswith('-en.html') else 'fr'

def traiter(path):
    s = io.open(path, encoding='utf-8').read()
    if 'text-resume' in s:
        return 0
    lg = langue(path)
    # 1. la règle CSS, juste avant celle de text-source
    i = s.index('  blockquote.text-source {')
    s = s[:i] + REGLE + s[i:]
    # 2. les blocs changent de classe et portent leur marque
    def swap(m):
        return ('<blockquote class="text-resume"' + m.group(1) + '>\n' + MARQUE[lg])
    s, n = re.subn(r'<blockquote class="text-source"([^>]*)>', swap, s)
    # 3. l'avis de lecture, en tête de la section du texte
    m = re.search(r'<h2 id="exp-seifim"[^>]*>.*?</h2>', s, re.S)
    if m:
        s = s[:m.end()] + '\n' + AVIS[lg] + s[m.end():]
    io.open(path, 'w', encoding='utf-8').write(s)
    return n

if __name__ == '__main__':
    tot = 0
    for n in range(183, 201):
        for suf in ('', '-he', '-en'):
            p = os.path.join(ROOT, f'sources/yoreh-deah/siman-{n}/niveau-1-base{suf}.html')
            if os.path.exists(p):
                k = traiter(p)
                tot += k
                print(f"siman {n}{suf or ' (fr)':>6} : {k} bloc(s) marqué(s)")
    print(f"\n{tot} blocs cessent de se présenter comme le texte du Choul'han Aroukh.")
