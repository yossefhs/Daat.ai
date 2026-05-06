// Templates de la séquence de bienvenue DAAT — 5 emails sur 14 jours.
// Utilisés par :
//   - /api/newsletter (envoi J0 immédiat à l'inscription)
//   - /api/cron/sequence (envoi J3 / J7 / J10 / J14 par cron quotidien)

const SITE = 'https://daattorah.com';
const LOGO = `${SITE}/assets/img/og/og-default.svg`;

function shell(title, bodyHtml, cta) {
  const ctaHtml = cta
    ? `<div style="text-align:center;margin:32px 0 16px;">
         <a href="${cta.href}" style="display:inline-block;background:#C5A55A;color:#1A1F3A;padding:14px 28px;text-decoration:none;font-family:'Inter',-apple-system,sans-serif;font-size:14px;font-weight:600;letter-spacing:1px;border-radius:3px;">${cta.label}</a>
       </div>`
    : '';
  return `<!DOCTYPE html>
<html><body style="font-family:Georgia,'Times New Roman',serif;background:#FAF6EE;margin:0;padding:24px;color:#1A1F3A;">
  <div style="max-width:560px;margin:0 auto;background:#fff;border:1px solid #E4DDD0;border-radius:8px;padding:32px;">
    <div style="display:flex;align-items:baseline;gap:12px;padding-bottom:16px;border-bottom:2px solid #C5A55A;margin-bottom:24px;">
      <span style="font-family:'Frank Ruhl Libre',serif;font-size:32px;font-weight:700;color:#C5A55A;">דעת</span>
      <span style="font-family:'Inter',-apple-system,sans-serif;font-size:13px;font-weight:600;color:#1A1F3A;letter-spacing:4px;">DAAT</span>
    </div>
    <h1 style="font-family:Georgia,serif;color:#1A1F3A;font-size:22px;margin:0 0 16px;line-height:1.3;">${title}</h1>
    <div style="color:#3D4266;font-size:15px;line-height:1.75;">${bodyHtml}</div>
    ${ctaHtml}
    <p style="color:#aaa;font-size:11px;line-height:1.6;margin-top:32px;padding-top:16px;border-top:1px solid #E4DDD0;text-align:center;">
      דעת DAAT · <a href="${SITE}/" style="color:#C5A55A;">daattorah.com</a> · initié par le Rav Yossef Haim Samama
    </p>
  </div>
</body></html>`.trim();
}

// Chaque step a : dayOffset (jours depuis subscription), subject, build(html, text)
export const SEQUENCE = [
  {
    id: 'j0',
    dayOffset: 0,
    subject: 'Barukh haba dans la communauté Daat',
    build() {
      const body = `
        <p>Tu viens de rejoindre la newsletter Daat — Barukh haba, on est heureux de t'avoir.</p>
        <p>Chaque dimanche, tu recevras un siman du <strong>Choulhan Aroukh, Orah Haïm</strong> en français : texte hébreu intégral, traduction, et sources des Rishonim et Acharonim.</p>
        <p>Pour te lancer dès maintenant : commence par le <strong>Siman 242 — Kavod et Oneg Shabbat</strong>. C'est le premier siman des Hilkhot Shabbat, et il pose le cadre : pourquoi le Shabbat est central, comment l'honorer, ce que disent les poskim.</p>
      `;
      return {
        subject: 'Barukh haba dans la communauté Daat',
        html: shell('Barukh haba dans la communauté Daat', body, {
          href: `${SITE}/sources/shabbat/siman-242/`,
          label: 'Étudier le Siman 242 →',
        }),
        text:
          'Barukh haba dans la communauté Daat.\n\n' +
          'Tu recevras chaque dimanche un siman du Choulhan Aroukh — texte hébreu, traduction, sources.\n\n' +
          'Pour commencer : Siman 242 — Kavod et Oneg Shabbat\n' +
          `${SITE}/sources/shabbat/siman-242/\n\n— DAAT דעת`,
      };
    },
  },
  {
    id: 'j3',
    dayOffset: 3,
    subject: 'Comment lire un siman Daat — les 3 niveaux',
    build() {
      const body = `
        <p>Tu as peut-être commencé le Siman 242. Si oui, tu as vu que chaque siman est étudié à <strong>3 niveaux</strong>. Voici ce que ça signifie :</p>
        <p style="background:#FAF6EE;border-left:3px solid #C5A55A;padding:14px 18px;margin:16px 0;">
          <strong style="color:#2E7D52;">Niveau 1 — Base.</strong><br>
          Initiation pédagogique. Texte hébreu, traduction française fluide, explication des concepts. À étudier d'abord, sans pression.
        </p>
        <p style="background:#FAF6EE;border-left:3px solid #6B3FA0;padding:14px 18px;margin:16px 0;">
          <strong style="color:#6B3FA0;">Niveau 2 — Lamdan.</strong><br>
          Pilpoul approfondi. <em>Hakirat haYesod</em>, débats des Acharonim, sougyot du Talmud. Pour celui qui veut creuser.
        </p>
        <p style="background:#FFF8E5;border-left:3px solid #C5A55A;padding:14px 18px;margin:16px 0;">
          <strong style="color:#C5A55A;">Niveau 3 — Synthèse Magistrale.</strong><br>
          Récap pour révision : axiomes, mnémoniques, arbres de décision, cas pratiques. À garder pour la mémorisation.
        </p>
        <p>Le bon ordre : <strong>Base → Lamdan → Synthèse</strong>. Mais rien ne t'empêche de sauter la Lamdan si tu veux d'abord la pratique.</p>
        <p>Et pour toute question pendant ton étude : <a href="${SITE}/chat.html" style="color:#C5A55A;font-weight:600;">l'IA Daat</a> est là, avec sources citées.</p>
      `;
      return {
        subject: 'Comment lire un siman Daat — les 3 niveaux',
        html: shell('La pédagogie Daat — 3 niveaux par siman', body, {
          href: `${SITE}/sources/shabbat/siman-242/`,
          label: 'Continuer Siman 242 →',
        }),
        text:
          'La pédagogie DAAT — 3 niveaux par siman :\n' +
          '- Niveau 1 BASE : initiation pédagogique\n' +
          '- Niveau 2 LAMDAN : pilpoul approfondi\n' +
          '- Niveau 3 SYNTHÈSE : récap pour mémoriser\n\n' +
          `Continuer Siman 242 : ${SITE}/sources/shabbat/siman-242/\n\n— DAAT`,
      };
    },
  },
  {
    id: 'j7',
    dayOffset: 7,
    subject: 'Siman 243 — Louer son champ ou son bain à un non-juif',
    build() {
      const body = `
        <p>Une semaine déjà. Si tu as fini le Siman 242 (au moins le Niveau Base), il est temps de passer au <strong>Siman 243</strong>.</p>
        <p>Le sujet est passionnant : <em>peut-on louer un champ, un bain, un four ou un moulin à un non-juif quand celui-ci va y travailler le Shabbat ?</em></p>
        <p>Le Choulhan Aroukh distingue 3 types de contrats — <strong>השכרה</strong> (location), <strong>קבלנות</strong> (forfait), <strong>אריסות</strong> (métayage) — et les conséquences halakhiques sont radicalement différentes selon ce qui est habituel pour le bien.</p>
        <p>C'est aussi la première fois que tu rencontreras les concepts de <em>mar'it ayin</em> (apparence) et d'<em>amira légoy</em> (demande à un non-juif), qui reviennent partout dans Hilkhot Shabbat.</p>
      `;
      return {
        subject: 'Siman 243 — Louer son champ ou son bain à un non-juif',
        html: shell('Siman 243 est en ligne — מרחץ, שדה, תנור, רחיים', body, {
          href: `${SITE}/sources/shabbat/siman-243/`,
          label: 'Étudier le Siman 243 →',
        }),
        text:
          'Siman 243 — Louer son champ ou son bain à un non-juif pour Shabbat.\n\n' +
          'Distinction השכרה / קבלנות / אריסות. Concepts mar\'it ayin et amira légoy.\n\n' +
          `${SITE}/sources/shabbat/siman-243/\n\n— DAAT`,
      };
    },
  },
  {
    id: 'j10',
    dayOffset: 10,
    subject: "L'IA Daat — pose tes questions de halakha",
    build() {
      const body = `
        <p>À ce stade tu as probablement rencontré une question : « Et dans MON cas, qu'est-ce qui s'applique ? »</p>
        <p>L'IA Daat est faite exactement pour ça. Tu peux lui poser des questions précises sur la halakha — elle te répond <strong>en français</strong>, en citant systématiquement ses sources (<em>Mehaber, Rama, Mishna Brura, Yabia Omer, Igrot Moshe…</em>) et en distinguant les niveaux d'autorité.</p>
        <p>Tu peux choisir ton minhag (séfarade Beit Yossef, ashkénaze Rama, Habad…) et l'IA ajustera sa présentation des positions divergentes.</p>
        <p style="background:#FFF3E0;border:1px solid #C5A55A;padding:14px 18px;margin:16px 0;color:#8C6F1E;">
          <strong>Important.</strong> L'IA Daat présente les positions des poskim — elle ne tranche pas la halakha lemaasseh. Pour toute décision pratique : consulte ton Rav.
        </p>
        <p>Quelques exemples de questions à essayer :</p>
        <ul style="color:#3D4266;line-height:1.8;">
          <li>« Peut-on louer une voiture à un non-juif pour Shabbat ? »</li>
          <li>« Quelle est la différence entre <em>oneg</em> et <em>kavod</em> Shabbat ? »</li>
          <li>« Le Mishna Brura suit-il le Rama ou le Choulhan Aroukh sur Y ? »</li>
        </ul>
      `;
      return {
        subject: "L'IA Daat — pose tes questions de halakha",
        html: shell("L'IA Daat répond avec sources citées", body, {
          href: `${SITE}/chat.html`,
          label: 'Ouvrir l\'IA Daat →',
        }),
        text:
          'L\'IA Daat — pose tes questions de halakha en français, sources citées.\n\n' +
          'Choisis ton minhag, pose ta question, l\'IA présente les positions.\n' +
          'Pour la halakha lemaasseh : consulte ton Rav.\n\n' +
          `${SITE}/chat.html\n\n— DAAT`,
      };
    },
  },
  {
    id: 'j14',
    dayOffset: 14,
    subject: 'Issachar et Zévouloun — la part de chacun',
    build() {
      const body = `
        <p>Voilà deux semaines que tu reçois Daat. Si tu lis encore — c'est que la plateforme te sert. Et c'est précisément le moment de te parler de ce qui la fait vivre.</p>
        <p style="font-family:'Georgia',serif;font-style:italic;background:#FAF6EE;border-left:3px solid #C5A55A;padding:18px 22px;margin:18px 0;color:#1A1F3A;">
          « שְׂמַח זְבוּלֻן בְּצֵאתֶךָ, וְיִשָּׂשכָר בְּאֹהָלֶיךָ »<br>
          <span style="font-size:13px;color:#7A7F9A;font-style:normal;letter-spacing:1px;">Devarim 33:18 — « Réjouis-toi, Zévouloun, dans tes sorties — et toi, Issachar, dans tes tentes. »</span>
        </p>
        <p>La tradition rapporte que Zévouloun travaillait le commerce et soutenait Issachar pour qu'il puisse étudier la Torah à plein temps. Et le mérite de l'étude était <strong>partagé</strong> entre les deux frères. Sans Zévouloun, pas d'Issachar — sans Issachar, pas de Torah qui descend dans le monde.</p>
        <p>DAAT existe parce que des bâtisseurs ont choisi de prendre cette part. Le contenu est et restera <strong>gratuit</strong> — l'étude de la Torah ne se vend pas. Mais sa diffusion a un coût : serveurs, IA, recherche, rédaction.</p>
        <p>Si tu peux soutenir, à toute hauteur — un don ponctuel, une dédicace d'étude, ou un mécénat mensuel (<em>Tomeh Adaat</em>) — ton nom rejoint le Mur des Bâtisseurs et ta part est inscrite dans chaque page étudiée.</p>
      `;
      return {
        subject: 'Issachar et Zévouloun — la part de chacun',
        html: shell('Issachar & Zévouloun — la part de chacun', body, {
          href: `${SITE}/soutenir.html`,
          label: 'Devenir bâtisseur →',
        }),
        text:
          'Issachar & Zévouloun — la tradition de la part partagée.\n\n' +
          'DAAT est gratuit pour rester accessible à tous. Il vit grâce à ses bâtisseurs.\n' +
          'Don libre, dédicace d\'étude, ou Tomeh Adaat (mensuel) :\n' +
          `${SITE}/soutenir.html\n\n— DAAT`,
      };
    },
  },
];

export function getStepById(id) {
  return SEQUENCE.find((s) => s.id === id);
}

export function getDueSteps(subscribedAtIso, sentSteps = []) {
  if (!subscribedAtIso) return [];
  const subscribedAt = new Date(subscribedAtIso);
  if (isNaN(subscribedAt.getTime())) return [];
  const now = new Date();
  const days = Math.floor((now.getTime() - subscribedAt.getTime()) / 86400000);
  return SEQUENCE.filter(
    (s) => days >= s.dayOffset && !sentSteps.includes(s.id)
  );
}
