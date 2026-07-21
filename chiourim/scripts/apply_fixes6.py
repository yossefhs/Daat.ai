# -*- coding: utf-8 -*-
# Applique les corrections du panel de vérification, ciblées par fichier + start time.
import json, re

# (fichier, start, old_substr_or_None, new_full_text_or_None, regex_sub_or_None)
# Si new_full_text fourni -> remplace tout le texte du cue. Sinon old->new substring.
fixes = [
    # 1. profitation -> fait de profiter
    ('chiour6_part_1.json', 53.8, 'de la profitation [d\'une melakha]', 'du fait de profiter [d\'une melakha]'),
    # 2. CRITIQUE: borer "possible/permis", pas "interdit"
    ('chiour6_part_1.json', 177.0, 'pour que le borer soit [interdit] ;', 'pour que le borer soit possible [permis] ;'),
    # 3. CRITIQUE: "heure et quart" mal entendu "Rabbenou Yerou'ham" (747.5 + 751.6)
    ('chiour6_part_2.json', 747.5, '__FULL__', 'il écrit la mesure de digestion du Birkat HaMazon : une'),
    ('chiour6_part_2.json', 751.6, '__FULL__', 'heure et quart, soit 72 minutes — quoi, ils ne savent pas dire 60'),
    # 4. "blesser les noix" -> "fendre les noix" + poter -> potzéa
    ('chiour6_part_3.json', 1350.3, '« blesser les noix » (poter egozim)', '« fendre les noix » (potzéa egozim)'),
    ('chiour6_part_3.json', 1619.0, '« blesser les noix »', '« fendre les noix »'),
    # 5. CRITIQUE: cyrillique lekanoув -> lekanev
    ('chiour6_part_3.json', 1630.5, '__REGEX__', r'\(lekano[^)]*\)|lekanev'),  # handled specially below
    # 6. CRITIQUE: misattribution Beit Yossef (1925 + 1934)
    ('chiour6_part_3.json', 1925.0, 'Rabbenou Yerou\'ham, qui parle de cela', 'le Beit Yossef, qui parle de cela'),
    ('chiour6_part_3.json', 1934.0, 'Rabbenou Yossef [Yerou\'ham] dit', 'Le Beit Yossef dit'),
    # 7. moutarde: retirer le crochet erroné [un œuf]
    ('chiour6_part_4.json', 2274.4, 'en fait de la moutarde [un œuf] —', 'en fait, de la moutarde —'),
    # 8. CRITIQUE: accord "ceci sont" -> "celles-ci sont"
    ('chiour6_part_6.json', 3340.4, 'et ceci sont les klipot impures', 'et celles-ci sont les klipot impures'),
    # 9. élision "le Or" -> "l'Or"
    ('chiour6_part_7.json', 4199.8, 'que le Or', 'que l\'Or'),
    # 10. CRITIQUE: cohérence olives (oignon/riz -> olives)
    ('chiour6_part_7.json', 3901.1, '__FULL__', 'Mais ce n\'est pas le débat ici. Ici, je parle d\'une personne qui n\'aime pas les olives : elle en a dans son riz.'),
    ('chiour6_part_7.json', 3908.3, '__FULL__', 'Alors disons qu\'il y a une olive ici, une olive là, une olive là — donc j\'en retire, disons,'),
    ('chiour6_part_7.json', 3918.4, '__FULL__', 'car il me reste encore quelques olives, mais j\'en ai déjà retiré quelques-unes.'),
]

by_file = {}
for fx in fixes:
    by_file.setdefault(fx[0], []).append(fx)

for f, lst in by_file.items():
    data = json.load(open(f, encoding='utf-8'))
    idx = {round(c['start'], 2): c for c in data}
    for (_, start, old, new) in lst:
        c = idx.get(round(start, 2))
        if c is None:
            # closest fallback
            c = min(data, key=lambda x: abs(x['start'] - start))
        before = c['text']
        if old == '__REGEX__':
            c['text'] = re.sub(r'\(lekano[^)]*\)', '(lekanev)', c['text'])
        elif old == '__FULL__':
            c['text'] = new
        else:
            assert old in c['text'], f'NON TROUVÉ dans {f}@{start}: {old!r} | texte={before!r}'
            c['text'] = c['text'].replace(old, new)
        status = 'OK' if c['text'] != before else 'INCHANGÉ'
        print(f'{f} @{start}: {status}')
    json.dump(data, open(f, 'w', encoding='utf-8'), ensure_ascii=False, indent=0)

print('--- corrections appliquées ---')
