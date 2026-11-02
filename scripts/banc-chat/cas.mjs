// Banc de non-régression du chat Daat — les cas, au format EXACT que les clients du
// site envoient (widget : profil préfixé à chaque message ; chat*.html : profil au
// premier message). Chaque cas dit ce qu'on attend du SERVEUR (événements tool_use
// « par: serveur », émis par api/_texte-primaire.js) et ce qu'il faut vérifier dans
// la réponse. Né le 18/10/2026 (siman 253 / רנ״ג : opinions inversées, « תישוי »,
// Rambam et Rif rangés côté indulgent) ; voir scripts/banc-chat/jouer.mjs.
const PROFIL = (niveau, minhag, langue, contexte) =>
  `[Profil de cette session]\n• Niveau : ${niveau}\n• Minhag : ${minhag}\n• Langue de réponse souhaitée : ${langue}\n` +
  (contexte ? `• Contexte : je consulte actuellement le ${contexte} sur daattorah.com — sauf indication contraire, mes questions portent sur ce siman.\n` : '') +
  `\n[Ma question]\n`;
const LAMDAN = 'Lamdan / Talmid Hakham — pilpoul approfondi';
const CTX253 = 'Siman 253 (Orah Haïm — Hilkhot Shabbat, page Niveau 1 — Base)';
const SRV = (ref) => ({ tool: 'sefaria_get_text', par: 'serveur', ref });
const MEHABER = (n) => `Shulchan_Arukh,_Orach_Chayim.${n}`;
const BY = (n) => `Beit_Yosef,_Orach_Chayim.${n}`;

export default [
  { id: 'L01-lamdan-253-opinions', cat: 'garde-fou ON', probe: 'Le cas du 18/10 : lamdan Habad, page 253, « résumé des opinions ». Attendu : Mehaber + Beit Yossef chargés ; opinion STRICTE (Rif/Rambam, מצטמק ורע לו) en premier ; Rif et Rambam côté strict.',
    turns: [PROFIL(LAMDAN, 'Habad / Loubavitch', 'français', CTX253) + 'Fait moi un résumé clair avec l idée des opinions'],
    expect: { serveur: [SRV(MEHABER(253)), SRV(BY(253))], ordre_253: true, strict: ['Rif', 'Rambam'], verif: ['aucun « תישוי »', 'séif 14 : pas de « bâtir le foyer »', 'HaRav 253 : séif א׳ indulgent, ט׳ strict en יש אומרים, minhag = la première'] } },
  { id: 'L02-lamdan-253-seif14-harav', cat: 'garde-fou ON + HaRav', probe: 'Lamdan demande le séif 14 du HaRav (hazara). Attendu : Mehaber chargé (pas de Beit Yossef : question de texte), puis le MODÈLE ouvre Shulchan_Arukh_HaRav,_Orach_Chayim.253.14 avant de le citer.',
    turns: [PROFIL(LAMDAN, 'Habad / Loubavitch', 'français', CTX253) + 'Dans le Choul\'han Aroukh HaRav, séif 14, quelles sont exactement les conditions de la hazara ? Cite-moi le texte.'],
    expect: { serveur: [SRV(MEHABER(253))], modele: 'Shulchan_Arukh_HaRav,_Orach_Chayim.253.14' } },
  { id: 'L03-lamdan-page253-question318', cat: 'siman de la question prime', probe: 'Page 253 ouverte, question sur le 318. Attendu : Mehaber 318, pas 253.',
    turns: [PROFIL(LAMDAN, 'Ashkénaze', 'français', CTX253) + 'Et dans le siman 318, « אין בישול אחר בישול » : où passe la limite pour un liquide refroidi ?'],
    expect: { serveur: [SRV(MEHABER(318))] } },
  { id: 'L04-debutant-253', cat: 'garde-fou OFF (niveau)', probe: 'Même question que L01, profil Débutant. Attendu : AUCUN événement serveur.',
    turns: [PROFIL('Débutant — peu ou pas de bagage', 'Séfarade', 'français', CTX253) + 'Fait moi un résumé clair avec l idée des opinions'],
    expect: { serveur: [] } },
  { id: 'L05-lamdan-sans-siman', cat: 'garde-fou OFF (pas de siman)', probe: 'Lamdan hors page siman, question conceptuelle. Attendu : AUCUN événement serveur.',
    turns: [PROFIL(LAMDAN, 'Séfarade', 'français', null) + 'Quelle est la différence de fond entre borer et meraked ?'],
    expect: { serveur: [] } },
  { id: 'L06-lamdan-urgence', cat: 'urgence prime', probe: 'Lamdan, page 253, danger vital. Attendu : AUCUN événement serveur ; réponse d\'urgence immédiate.',
    turns: [PROFIL(LAMDAN, 'Habad / Loubavitch', 'français', CTX253) + 'Mon père vient de s\'effondrer, il ne respire plus, c\'est Shabbat, est-ce que je peux appeler les secours ?'],
    expect: { serveur: [], verif: ['la réponse ouvre sur l\'appel aux secours, sans détour halakhique'] } },
  { id: 'L07-yd-lamdan-100', cat: 'Yoreh De\'ah', probe: 'Section yoreh-deah, lamdan, page Siman 100, question d\'opinions. Attendu : Mehaber YD 100 + Beit Yossef YD 100.',
    section: 'yoreh-deah',
    turns: [PROFIL(LAMDAN, 'Séfarade', 'français', 'Siman 100 (Yoreh De\'ah — Hilkhot Ta\'arovot)') + 'Pourquoi une בריה n\'est-elle pas annulée même dans mille ? Quelles opinions ?'],
    expect: { serveur: [SRV("Shulchan_Arukh,_Yoreh_De'ah.100"), SRV("Beit_Yosef,_Yoreh_De'ah.100")] } },
  { id: 'L08-lamdan-253-hebreu', cat: 'langue : hébreu', probe: 'Question en hébreu, profil lamdan (libellé français du widget), page 253.',
    turns: [PROFIL(LAMDAN, 'Habad / Loubavitch', 'hébreu', CTX253) + 'סכם לי בקצרה את הדעות בסימן 253 לגבי שהייה על גבי כירה'],
    expect: { serveur: [SRV(MEHABER(253)), SRV(BY(253))], ordre_253: true, langue: 'he' } },
  { id: 'L09-lamdan-253-anglais', cat: 'langue : anglais', probe: 'Question en anglais, profil lamdan, page 253.',
    turns: [PROFIL(LAMDAN, 'Ashkénaze', 'anglais', CTX253) + 'Give me a clear summary of the opinions in siman 253 on shehiyah.'],
    expect: { serveur: [SRV(MEHABER(253)), SRV(BY(253))], ordre_253: true, strict: ['Rif', 'Rambam'], langue: 'en' } },
  { id: 'L10-yeshiva-253', cat: 'garde-fou OFF (niveau yeshiva)', probe: 'Élève de Yeshiva, page 253. Attendu par le code : AUCUN événement serveur (à discuter : élargir ?).',
    turns: [PROFIL('Élève de Yeshiva — étude régulière', 'Séfarade', 'français', CTX253) + 'Fait moi un résumé clair avec l idée des opinions'],
    expect: { serveur: [] } },
  { id: 'L11-en-standalone-lamdan-253', cat: 'chat-en.html', probe: 'Profil du chat anglais autonome (« - Level: Lamdan »), siman 253 nommé.',
    turns: ['[Session profile]\n- Level: Lamdan\n- Minhag: Ashkenazi\n- Desired response language: English\n\nSummarize the opinions in siman 253 on shehiyah, in order.'],
    expect: { serveur: [SRV(MEHABER(253)), SRV(BY(253))], ordre_253: true, strict: ['Rif', 'Rambam'], langue: 'en' } },
  { id: 'L12-he-standalone-gematria', cat: 'chat-he.html + lettres', probe: 'Profil du chat hébreu autonome (« - רמה: Lamdan »), siman en LETTRES (סימן רנ״ג).',
    turns: ['[פרופיל סשן זה]\n- רמה: Lamdan\n- מנהג: חב״ד\n- שפת המענה המבוקשת: עברית\n\nסכם לי את הדעות בסימן רנ״ג לגבי שהייה, לפי הסדר.'],
    expect: { serveur: [SRV(MEHABER(253)), SRV(BY(253))], ordre_253: true, langue: 'he' } },
  { id: 'L13-general-yd100-section-oc', cat: 'section par défaut', probe: 'chat.html général (section orach-chaim par défaut), question explicitement Yoreh De\'ah siman 100. Attendu : Yoreh_De\'ah.100, PAS Orach_Chayim.100.',
    turns: ['[Profil de cette session]\n- Niveau : Lamdan\n- Minhag : Séfarade\n- Langue de réponse souhaitée : français\n\nPourquoi une בריה n\'est-elle pas annulée même dans mille ? Je parle du siman 100 de Yoreh De\'ah.'],
    expect: { serveur: [SRV("Shulchan_Arukh,_Yoreh_De'ah.100")], interdit: ['Shulchan_Arukh,_Orach_Chayim.100'] } },
  { id: 'L14-question-rapide-gematria', cat: 'question rapide', probe: 'La question rapide de chat.html « Explique-moi le Siman רמ״ב » avec profil Lamdan. Attendu : Mehaber 242.',
    turns: ['[Profil de cette session]\n- Niveau : Lamdan\n- Minhag : Habad\n- Langue de réponse souhaitée : français\n\nExplique-moi le Siman רמ״ב'],
    expect: { serveur: [SRV(MEHABER(242))] } },
  { id: 'L15-253-seif14-texte-seul', cat: 'question de texte', probe: '« Explique le séif 14 du HaRav et cite le texte » : pas de mot d\'opinion. Attendu : Mehaber seul, pas de Beit Yossef.',
    turns: [PROFIL(LAMDAN, 'Habad / Loubavitch', 'français', CTX253) + 'Explique-moi le séif 14 du Choul\'han Aroukh HaRav et cite-moi son texte.'],
    expect: { serveur: [SRV(MEHABER(253))], interdit: [BY(253)] } },
  { id: 'L16-yd100-richonim', cat: 'Yoreh De\'ah + Beit Yossef', probe: 'Section yoreh-deah, lamdan, « les opinions des Richonim sur la בריה ». Attendu : Mehaber + Beit Yossef YD 100 ; chaque Richon nommé l\'est par le Beit Yossef.',
    section: 'yoreh-deah',
    turns: [PROFIL(LAMDAN, 'Séfarade', 'français', 'Siman 100 (Yoreh De\'ah — Hilkhot Ta\'arovot)') + 'Quelles sont les opinions des Richonim sur la בריה qui ne s\'annule pas, et qui tient quoi ?'],
    expect: { serveur: [SRV("Shulchan_Arukh,_Yoreh_De'ah.100"), SRV("Beit_Yosef,_Yoreh_De'ah.100")] } },
];
