#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""Génère les 3 pages niveau-4 « page-passerelle » (🌉) pour les simanim oh-quotidien
dont le Choul'han Aroukh HaRav n'existe pas (lacune 132-154, etc.).
SOBRE : aucune citation reconstruite, aucun texte SA HaRav inventé.
Renvoie aux niveaux 1-3 (Mehaber/Rama) et au Siddour de l'Admour HaZaken.
"""
import sys, os
ROOT = "/home/user/Daat.ai"

STYLE = """<style>
  :root{--navy:#1A1F3A;--gold:#C5A55A;--gold-light:#D4B97A;--gold-dark:#8C6F1E;--cream:#FAF6EE;--cream-dark:#F0EAD8;--text:#1A1F3A;--text-mid:#3D4266;--text-muted:#7A7F9A;--white:#FFFFFF;--border:#E4DDD0;--habad:#3851A3;--habad-soft:#5A72C2;--habad-deep:#243669;--habad-tint:rgba(56,81,163,0.06);}
  *{margin:0;padding:0;box-sizing:border-box;}
  body{font-family:'Cormorant Garamond',Georgia,serif;background:var(--cream);color:var(--text);line-height:1.7;}
  header{background:var(--navy);padding:0 40px;display:flex;align-items:center;justify-content:space-between;height:70px;border-bottom:2px solid var(--gold);}
  .logo{display:flex;align-items:baseline;gap:12px;text-decoration:none;}
  .logo-he{font-family:'Frank Ruhl Libre',serif;font-size:26px;font-weight:700;color:var(--gold);}
  .logo-en{font-family:'Inter',sans-serif;font-size:14px;font-weight:600;color:#fff;letter-spacing:3px;}
  nav{display:flex;gap:24px;align-items:center;}
  nav a{font-family:'Inter',sans-serif;font-size:13px;color:rgba(255,255,255,0.7);text-decoration:none;letter-spacing:1px;}
  nav a:hover{color:var(--gold);}
  .breadcrumb{background:var(--navy);padding:12px 40px;border-bottom:1px solid rgba(197,165,90,0.15);}
  .breadcrumb-inner{max-width:1100px;margin:0 auto;}
  .breadcrumb a,.breadcrumb span{font-family:'Inter',sans-serif;font-size:12px;color:rgba(255,255,255,0.85);text-decoration:none;letter-spacing:0.5px;}
  .breadcrumb a:hover{color:var(--gold);}
  .breadcrumb .sep{margin:0 8px;color:rgba(255,255,255,0.85);}
  .breadcrumb .current{color:var(--gold);}
  .page-hero{background:linear-gradient(135deg,var(--habad-deep) 0%,var(--habad) 60%,var(--habad-soft) 100%);padding:56px 40px;border-bottom:3px solid var(--gold);}
  .hero-inner{max-width:1100px;margin:0 auto;}
  .hero-meta{font-family:'Inter',sans-serif;font-size:11px;letter-spacing:4px;text-transform:uppercase;color:var(--gold);margin-bottom:14px;}
  .hero-title-he{font-family:'Frank Ruhl Libre',serif;font-size:44px;font-weight:700;color:var(--gold);direction:rtl;margin-bottom:6px;letter-spacing:1px;}
  .hero-title{font-family:'Cormorant Garamond',serif;font-size:32px;font-weight:400;color:#fff;margin-bottom:8px;}
  .hero-subtitle{font-size:17px;color:rgba(255,255,255,0.78);font-style:italic;max-width:800px;}
  main{max-width:1000px;margin:0 auto;padding:50px 40px 60px;}
  .intro-block{background:var(--white);border:1px solid var(--border);border-left:4px solid var(--habad);padding:22px 26px;margin-bottom:40px;}
  .intro-block p{color:var(--text-mid);}
  .intro-block p+p{margin-top:10px;}
  .intro-block strong{color:var(--navy);}
  .section-block{margin-bottom:52px;}
  .section-num{display:inline-block;font-family:'Inter',sans-serif;font-size:11px;letter-spacing:3px;text-transform:uppercase;color:var(--habad);background:var(--habad-tint);padding:5px 12px;border-radius:2px;margin-bottom:12px;}
  .section-title-he{font-family:'Frank Ruhl Libre',serif;direction:rtl;font-size:26px;color:var(--navy);margin-bottom:6px;font-weight:700;}
  .section-title-fr{font-family:'Cormorant Garamond',serif;font-size:26px;font-weight:500;color:var(--navy);margin-bottom:18px;}
  .section-divider{width:60px;height:2px;background:var(--gold);margin-bottom:24px;}
  .missing-banner{background:linear-gradient(135deg,#fff8e5 0%,#faf0d4 100%);border:2px solid var(--gold);border-radius:4px;padding:28px 32px;margin-bottom:36px;}
  .missing-banner h2{font-family:'Cormorant Garamond',serif;font-size:26px;color:var(--gold-dark);margin-bottom:12px;}
  .missing-banner h2 .he{font-family:'Frank Ruhl Libre',serif;direction:rtl;font-size:26px;color:var(--navy);margin-right:10px;}
  .missing-banner p{color:var(--text-mid);margin-bottom:10px;}
  .missing-banner p strong{color:var(--navy);}
  .missing-banner .he-q{font-family:'Frank Ruhl Libre',serif;direction:rtl;unicode-bidi:embed;}
  .src-list{margin-left:22px;color:var(--text-mid);line-height:1.9;}
  .src-list strong{color:var(--navy);}
  .src-list a{color:var(--habad);}
  footer{background:var(--navy);border-top:2px solid var(--gold);padding:28px 40px;text-align:center;margin-top:60px;}
  footer p{font-family:'Inter',sans-serif;font-size:12px;color:rgba(255,255,255,0.85);}
  footer a{color:var(--gold);text-decoration:none;}
  .lang-switcher{display:flex;gap:6px;align-items:center;margin-left:12px;}
  .lang-switcher a{font-family:'Inter',sans-serif;font-size:11px;padding:3px 7px;border-radius:2px;letter-spacing:1px;color:rgba(255,255,255,0.85);border:1px solid rgba(255,255,255,0.15);text-decoration:none;}
  .lang-switcher a.active{color:var(--gold);border-color:var(--gold);}
  .lang-switcher a:hover{color:var(--gold);border-color:var(--gold);}
  .lang-switcher-float{position:fixed;top:12px;right:12px;z-index:9999;display:flex;gap:4px;background:rgba(255,255,255,0.95);border:1px solid #C5A55A;padding:4px 6px;border-radius:3px;box-shadow:0 2px 8px rgba(0,0,0,0.1);font-family:'Inter',sans-serif;}
  .lang-switcher-float a{font-size:11px;letter-spacing:1px;padding:3px 7px;border-radius:2px;color:#5a4a1a;text-decoration:none;border:1px solid transparent;}
  .lang-switcher-float a.active{color:#1A1F3A;background:#FFF8E5;border-color:#1A1F3A;font-weight:600;}
  .lang-switcher-float a:hover{color:#1A1F3A;border-color:#C5A55A;}
  @media print{.lang-switcher-float{display:none;}}
  .bridge-banner{background:linear-gradient(135deg,#FAF6EE 0%,#F0EAD8 100%);border:2px solid #C5A55A;border-left:6px solid #8C6F1E;border-radius:6px;padding:28px 32px;margin:0 0 36px 0;font-family:'Cormorant Garamond',Georgia,serif;}
  .bridge-banner .bridge-icon{font-size:32px;line-height:1;display:inline-block;margin-right:8px;vertical-align:middle;}
  .bridge-banner h2{font-family:'Cormorant Garamond',Georgia,serif;font-size:24px;color:#8C6F1E;margin:0 0 12px 0;font-weight:700;}
  .bridge-banner p{color:#3D4266;font-size:17px;line-height:1.7;margin:0 0 12px 0;}
  .bridge-banner .bridge-links{margin-top:16px;display:flex;flex-wrap:wrap;gap:10px;}
  .bridge-banner .bridge-links a{display:inline-block;padding:8px 16px;border-radius:3px;background:#1A1F3A;color:#C5A55A;text-decoration:none;font-family:'Inter',sans-serif;font-size:13px;letter-spacing:1px;border:1px solid #C5A55A;}
  .bridge-banner .bridge-links a:hover{background:#C5A55A;color:#1A1F3A;}
  .bridge-banner[dir="rtl"]{border-left:2px solid #C5A55A;border-right:6px solid #8C6F1E;}
  .niveau-nav{display:flex;justify-content:space-between;align-items:center;gap:1rem;padding:1.5rem 0;border-top:1px solid #d4c89a;margin:3rem 0 1.5rem;flex-wrap:wrap;font-family:'Inter','Helvetica',sans-serif;font-size:11pt;}
  .niveau-nav a{color:#1A1F3A;text-decoration:none;padding:0.5rem 1rem;border-radius:4px;}
  .niveau-nav a:hover{background:#FAF6EE;color:#1A1F3A;}
  .niveau-nav .nav-niveaux{display:flex;gap:0.5rem;}
  .niveau-nav .nav-level{border:1px solid #d4c89a;font-weight:600;letter-spacing:1px;}
  .niveau-nav .nav-level.active{background:#1A1F3A;color:#fff;border-color:#1A1F3A;}
  @media(max-width:640px){.niveau-nav{flex-direction:column;gap:0.75rem;}header,.breadcrumb,.page-hero,main,footer{padding-left:20px;padding-right:20px;}.hero-title-he{font-size:34px;}.hero-title{font-size:24px;}}
  @media print{.niveau-nav{display:none;}}
</style>"""

# Textes par langue (SOBRES — sans citation reconstruite)
TXT = {
 "fr": {
  "lang":"fr","dir":"ltr","suf":"","base":"base","lamdan":"lamdan","synthese":"synthese",
  "home":"Accueil","compart":"Orah Haïm — lois de tous les jours","level4":"Niveau 4 — Daat HaRav",
  "hero_title":lambda n:f"Daat HaRav — Siman {n} : page-passerelle",
  "title":lambda n,he:f"Siman {n} · Niveau 4 — Daat HaRav (page-passerelle) | Orah Haïm",
  "meta_desc":lambda he,subj:f"Niveau 4 (Daat HaRav) du Siman {he} — page-passerelle : l’Admour HaZaken n’a pas rédigé ce siman dans son Choul’han Aroukh (certaines portions d’Orah Haïm n’y figurent pas). Renvoi aux Niveaux 1-3 et au Siddour de l’Admour HaZaken. Sujet : {subj}.",
  "hero_sub":lambda subj:f"Ce siman — {subj} — n’a pas été rédigé par l’Admour HaZaken dans son Choul’han Aroukh. Cette page ne reconstruit aucun texte : elle oriente vers l’étude aux Niveaux 1-3 et vers le Siddour de l’Admour HaZaken.",
  "bridge_h":lambda n:f"Siman {n} — page-passerelle",
  "bridge_p":lambda he:f"<strong>Ce siman n’a pas de Niveau 4 : l’Admour HaZaken ne l’a pas rédigé dans son Choul’han Aroukh.</strong> Le Choul’han Aroukh HaRav ne couvre pas Orah Haïm de façon continue : plusieurs portions n’ont pas été écrites par le Rav, et ce siman en fait partie. Fidèlement à la règle de la maison, <strong>aucun texte du Choul’han Aroukh HaRav n’est reconstruit ni inventé ici</strong>. Étudiez ce siman aux Niveaux 1-3 (texte du Mehaber et du Rama) ; la pratique de l’Admour HaZaken est consignée dans son <strong>Siddour</strong> (Seder ha-Tefila, Seder Birkat HaNehenin et ses Piskei ha-Siddour).",
  "links":lambda n:f'<a href="/oh-quotidien/{n}/base">Niveau 1 — Base</a><a href="/oh-quotidien/{n}/lamdan">Niveau 2 — Lamdan</a><a href="/oh-quotidien/{n}/synthese">Niveau 3 — Synthèse</a><a href="/chitah-admour-hazaken.html">La chitah de l’Admour HaZaken</a>',
  "intro_h":"Pourquoi un Niveau 4 dédié à l’Admour HaZaken ?",
  "intro_p1":"Le <strong>Choul’han Aroukh de l’Admour HaZaken</strong> n’est pas un commentaire sur le Mehaber : c’est un Choul’han Aroukh autonome, qui combine la halakha, les טעמי המצוות et la dimension intérieure. Pour le Habad, l’Admour HaZaken est <strong>הפוסק האחרון</strong>.",
  "intro_p2":"Mais l’ouvrage est <strong>incomplet</strong> : l’Admour HaZaken n’a pas rédigé (ou l’on n’a pas conservé) toute la première partie d’Orah Haïm. Ce siman fait partie de ces portions manquantes. Il n’y a donc pas de texte du Rav à reproduire pour ce siman.",
  "miss_h":lambda he:f'<span class="he">סימן {he}</span> — un siman hors du Choul’han Aroukh HaRav',
  "miss_p1":"Le Choul’han Aroukh de l’Admour HaZaken couvre de larges pans d’Orah Haïm, mais pas de façon continue : plusieurs blocs n’ont pas été rédigés par le Rav, et ce siman en fait partie.",
  "miss_p2":"Là où le Rav n’a pas écrit de siman, sa <strong>conduite (מנהג) et ses pesakim</strong> se retrouvent principalement dans deux sources authentiques : son <strong>Siddour</strong> (le « Siddour de l’Admour HaZaken », avec son Seder ha-Tefila, son Seder Birkat HaNehenin et ses Piskei ha-Siddour) et le <strong>Kountress Aharon</strong> sur les simanim qu’il a effectivement rédigés.",
  "miss_note":"⚠ <strong>Note méthodologique :</strong> conformément à la règle de vérification du site, cette page ne cite ni ne reconstruit aucun texte du Choul’han Aroukh HaRav pour ce siman — puisqu’aucun n’existe. Pour la halakha de ce siman, référez-vous au Mehaber et au Rama (Niveaux 1-3) et, pour la pratique de l’Admour HaZaken, à son Siddour.",
  "src_h_he":"מקורות לעיון","src_h":"Sources pour approfondir",
  "src":lambda n:f'<li><strong>Mehaber & Rama, ce siman</strong> — <a href="/oh-quotidien/{n}/base">Niveau 1</a>, <a href="/oh-quotidien/{n}/lamdan">Niveau 2</a>, <a href="/oh-quotidien/{n}/synthese">Niveau 3</a>.</li>'
        '<li><strong>Siddour de l’Admour HaZaken</strong> — Seder ha-Tefila, Seder Birkat HaNehenin et Piskei ha-Siddour : la source directe de la conduite du Rav.</li>'
        '<li><strong>Choul’han Aroukh HaRav</strong> — les simanim voisins effectivement rédigés par le Rav.</li>'
        f'<li><strong>Préface — la chitah de l’Admour HaZaken</strong> : <a href="/chitah-admour-hazaken.html">présentation générale</a>.</li>',
  "print":"🖨️ Imprimer / Sauver en PDF","prev":lambda n:f"← Siman {n}","next":lambda n:f"Siman {n} →",
  "foot":'DAAT דעת — © 5786 / 2026 · <a href="../../../index.html">Retour à l’accueil</a> · Initié par le Rav Yossef Haim Samama',
 },
 "he": {
  "lang":"he","dir":"rtl","suf":"-he","base":"base/he","lamdan":"lamdan/he","synthese":"synthese/he",
  "home":"בית","compart":"אורח חיים — הלכות יום־יום","level4":"רמה 4 — דעת הרב",
  "hero_title":lambda n:f"דעת הרב — סימן {n}: דף־גשר",
  "title":lambda n,he:f"סימן {he} · רמה 4 — דעת הרב (דף־גשר) | אורח חיים",
  "meta_desc":lambda he,subj:f"רמה 4 (דעת הרב) לסימן {he} — דף־גשר: אדמו״ר הזקן לא כתב סימן זה בשולחן ערוך שלו (חלק מסימני אורח חיים אינם בשו״ע הרב). הפניה לרמות 1-3 ולסידור אדמו״ר הזקן. נושא: {subj}.",
  "hero_sub":lambda subj:f"סימן זה — {subj} — לא נכתב על ידי אדמו״ר הזקן בשולחן ערוך שלו. דף זה אינו משחזר שום טקסט: הוא מפנה ללימוד ברמות 1-3 ולסידור אדמו״ר הזקן.",
  "bridge_h":lambda n:f"סימן {n} — דף־גשר",
  "bridge_p":lambda he:"<strong>לסימן זה אין רמה 4: אדמו״ר הזקן לא כתבו בשולחן ערוך שלו.</strong> שולחן ערוך הרב אינו מקיף את אורח חיים ברצף: כמה מקטעים לא נכתבו על ידי הרב, וסימן זה בכללם. על פי כלל הבית, <strong>אין משחזרים ואין ממציאים כאן שום טקסט של שולחן ערוך הרב</strong>. למדו סימן זה ברמות 1-3 (לשון המחבר והרמ״א); הנהגת אדמו״ר הזקן מובאת ב<strong>סידורו</strong> (סדר התפילה, סדר ברכת הנהנין ופסקי הסידור).",
  "links":lambda n:f'<a href="/oh-quotidien/{n}/base/he">רמה 1 — בסיס</a><a href="/oh-quotidien/{n}/lamdan/he">רמה 2 — למדן</a><a href="/oh-quotidien/{n}/synthese/he">רמה 3 — סיכום</a><a href="/chitah-admour-hazaken.html">שיטת אדמו״ר הזקן</a>',
  "intro_h":"מדוע רמה 4 מוקדשת לאדמו״ר הזקן?",
  "intro_p1":"<strong>שולחן ערוך אדמו״ר הזקן</strong> אינו פירוש על המחבר, אלא שולחן ערוך עצמאי המשלב הלכה, טעמי המצוות והפנימיות. לחב״ד, אדמו״ר הזקן הוא <strong>הפוסק האחרון</strong>.",
  "intro_p2":"אך החיבור <strong>אינו שלם</strong>: אדמו״ר הזקן לא כתב (או שלא נשתמר) את כל חלקו הראשון של אורח חיים. סימן זה נמנה עם המקטעים החסרים. משום כך אין טקסט של הרב לשחזר לסימן זה.",
  "miss_h":lambda he:f'<span class="he">סימן {he}</span> — סימן שאינו בשולחן ערוך הרב',
  "miss_p1":"שולחן ערוך אדמו״ר הזקן מקיף חלקים נרחבים של אורח חיים, אך לא ברצף: כמה מקטעים לא נכתבו על ידי הרב, וסימן זה בכללם.",
  "miss_p2":"במקום שהרב לא כתב סימן, <strong>הנהגתו ופסקיו</strong> מצויים בעיקר בשני מקורות אותנטיים: <strong>סידורו</strong> (סדר התפילה, סדר ברכת הנהנין ופסקי הסידור) ו<strong>קונטרס אחרון</strong> על הסימנים שכן כתב.",
  "miss_note":"⚠ <strong>הערה מתודית:</strong> על פי כלל הבדיקה של האתר, דף זה אינו מצטט ואינו משחזר שום טקסט של שולחן ערוך הרב לסימן זה — שכן אין כזה. להלכת הסימן עיינו במחבר וברמ״א (רמות 1-3), ולהנהגת אדמו״ר הזקן — בסידורו.",
  "src_h_he":"מקורות לעיון","src_h":"מקורות לעיון",
  "src":lambda n:f'<li><strong>המחבר והרמ״א, סימן זה</strong> — <a href="/oh-quotidien/{n}/base/he">רמה 1</a>, <a href="/oh-quotidien/{n}/lamdan/he">רמה 2</a>, <a href="/oh-quotidien/{n}/synthese/he">רמה 3</a>.</li>'
        '<li><strong>סידור אדמו״ר הזקן</strong> — סדר התפילה, סדר ברכת הנהנין ופסקי הסידור: המקור הישיר להנהגת הרב.</li>'
        '<li><strong>שולחן ערוך הרב</strong> — הסימנים הסמוכים שנכתבו על ידי הרב.</li>'
        f'<li><strong>הקדמה — שיטת אדמו״ר הזקן</strong>: <a href="/chitah-admour-hazaken.html">מבוא כללי</a>.</li>',
  "print":"🖨️ הדפסה / שמירה כ־PDF","prev":lambda n:f"← סימן {n}","next":lambda n:f"סימן {n} →",
  "foot":'DAAT דעת — © 5786 / 2026 · <a href="../../../index.html">חזרה לבית</a> · ביוזמת הרב יוסף חיים סממה',
 },
 "en": {
  "lang":"en","dir":"ltr","suf":"-en","base":"base/en","lamdan":"lamdan/en","synthese":"synthese/en",
  "home":"Home","compart":"Orach Chayim — everyday laws","level4":"Level 4 — Daat HaRav",
  "hero_title":lambda n:f"Daat HaRav — Siman {n}: bridge page",
  "title":lambda n,he:f"Siman {n} · Level 4 — Daat HaRav (bridge page) | Orach Chayim",
  "meta_desc":lambda he,subj:f"Level 4 (Daat HaRav) of Siman {he} — bridge page: the Alter Rebbe did not write this siman in his Shulchan Aruch (parts of Orach Chayim are absent from Shulchan Aruch HaRav). Pointer to Levels 1-3 and to the Alter Rebbe’s Siddur. Topic: {subj}.",
  "hero_sub":lambda subj:f"This siman — {subj} — was not written by the Alter Rebbe in his Shulchan Aruch. This page reconstructs no text: it points to study at Levels 1-3 and to the Alter Rebbe’s Siddur.",
  "bridge_h":lambda n:f"Siman {n} — bridge page",
  "bridge_p":lambda he:"<strong>This siman has no Level 4: the Alter Rebbe did not write it in his Shulchan Aruch.</strong> Shulchan Aruch HaRav does not cover Orach Chayim continuously: several portions were not written by the Rav, and this siman is one of them. In keeping with the site’s rule, <strong>no Shulchan Aruch HaRav text is reconstructed or invented here</strong>. Study this siman at Levels 1-3 (the text of the Mechaber and the Rama); the Alter Rebbe’s practice is recorded in his <strong>Siddur</strong> (Seder ha-Tefillah, Seder Birkat ha-Nehenin and its Piskei Dinim).",
  "links":lambda n:f'<a href="/oh-quotidien/{n}/base/en">Level 1 — Base</a><a href="/oh-quotidien/{n}/lamdan/en">Level 2 — Lamdan</a><a href="/oh-quotidien/{n}/synthese/en">Level 3 — Synthesis</a><a href="/chitah-admour-hazaken.html">The Alter Rebbe’s approach</a>',
  "intro_h":"Why a Level 4 dedicated to the Alter Rebbe?",
  "intro_p1":"The <strong>Shulchan Aruch of the Alter Rebbe</strong> is not a commentary on the Mechaber: it is an independent Shulchan Aruch that fuses halacha, the reasons of the mitzvot and the inner dimension. For Chabad, the Alter Rebbe is <strong>ha-posek ha-acharon</strong>.",
  "intro_p2":"But the work is <strong>incomplete</strong>: the Alter Rebbe did not write (or it was not preserved) all of the first part of Orach Chayim. This siman is one of those missing portions. There is therefore no text of the Rav to reproduce for this siman.",
  "miss_h":lambda he:f'<span class="he">סימן {he}</span> — a siman outside Shulchan Aruch HaRav',
  "miss_p1":"The Alter Rebbe’s Shulchan Aruch covers large parts of Orach Chayim, but not continuously: several blocks were not written by the Rav, and this siman is one of them.",
  "miss_p2":"Where the Rav did not write a siman, his <strong>practice (minhag) and rulings</strong> are found chiefly in two authentic sources: his <strong>Siddur</strong> (Seder ha-Tefillah, Seder Birkat ha-Nehenin and Piskei ha-Siddur) and the <strong>Kuntres Acharon</strong> on the simanim he did write.",
  "miss_note":"⚠ <strong>Methodological note:</strong> in keeping with the site’s verification rule, this page neither cites nor reconstructs any Shulchan Aruch HaRav text for this siman — since none exists. For the halacha of this siman, see the Mechaber and Rama (Levels 1-3), and for the Alter Rebbe’s practice, his Siddur.",
  "src_h_he":"מקורות לעיון","src_h":"Sources for further study",
  "src":lambda n:f'<li><strong>Mechaber & Rama, this siman</strong> — <a href="/oh-quotidien/{n}/base/en">Level 1</a>, <a href="/oh-quotidien/{n}/lamdan/en">Level 2</a>, <a href="/oh-quotidien/{n}/synthese/en">Level 3</a>.</li>'
        '<li><strong>The Alter Rebbe’s Siddur</strong> — Seder ha-Tefillah, Seder Birkat ha-Nehenin and Piskei ha-Siddur: the direct source of the Rav’s practice.</li>'
        '<li><strong>Shulchan Aruch HaRav</strong> — the neighbouring simanim actually written by the Rav.</li>'
        f'<li><strong>Preface — the Alter Rebbe’s approach</strong>: <a href="/chitah-admour-hazaken.html">general introduction</a>.</li>',
  "print":"🖨️ Print / Save as PDF","prev":lambda n:f"← Siman {n}","next":lambda n:f"Siman {n} →",
  "foot":'DAAT דעת — © 5786 / 2026 · <a href="../../../index.html">Back to home</a> · Initiated by Rav Yossef Haim Samama',
 },
}

def page(lang, num, numHe, subj):
    t = TXT[lang]
    N=str(num); NM1=str(num-1); NP1=str(num+1)
    canon=f"https://daattorah.com/oh-quotidien/{N}/daat-harav"+("" if lang=="fr" else "/"+lang)
    title=t["title"](N,numHe)
    desc=t["meta_desc"](numHe,subj)
    jsonld=('<script type="application/ld+json" data-schema="niveau-jsonld">{"@context":"https://schema.org","@graph":['
      '{"@type":["Article","LearningResource"],"@id":"'+canon+'#article","headline":"'+title.replace('"','\\"')+'",'
      '"url":"'+canon+'","inLanguage":"'+("fr-FR" if lang=="fr" else lang)+'","isAccessibleForFree":true,'
      '"learningResourceType":"Page-passerelle (siman non rédigé par l\'Admour HaZaken)",'
      '"isPartOf":{"@id":"https://daattorah.com/oh-quotidien/'+N+'/#siman"},'
      '"author":{"@id":"https://daattorah.com/#rav-samama"},"publisher":{"@id":"https://daattorah.com/#organization"}},'
      '{"@type":"BreadcrumbList","itemListElement":['
      '{"@type":"ListItem","position":1,"name":"DAAT","item":"https://daattorah.com/"},'
      '{"@type":"ListItem","position":2,"name":"Orah Haïm","item":"https://daattorah.com/oh-quotidien/"},'
      '{"@type":"ListItem","position":3,"name":"Siman '+N+'","item":"https://daattorah.com/oh-quotidien/'+N+'/"},'
      '{"@type":"ListItem","position":4,"name":"'+t["level4"]+'","item":"'+canon+'"}]},'
      '{"@type":["Organization","EducationalOrganization"],"@id":"https://daattorah.com/#organization","name":"DAAT דעת","url":"https://daattorah.com/"},'
      '{"@type":"Person","@id":"https://daattorah.com/#rav-samama","name":"Rav Yossef Haim Samama"}]}</script>')
    af=' class="active"' if lang=="fr" else ''
    ah=' class="active"' if lang=="he" else ''
    ae=' class="active"' if lang=="en" else ''
    lsf=('<div class="lang-switcher-float" role="navigation" aria-label="Language">'
         f'<a href="/oh-quotidien/{N}/daat-harav"{af}>FR</a>'
         f'<a href="/oh-quotidien/{N}/daat-harav/he"{ah}>HE</a>'
         f'<a href="/oh-quotidien/{N}/daat-harav/en"{ae}>EN</a></div>')
    lss=(f'<span class="lang-switcher"><a href="/oh-quotidien/{N}/daat-harav"{af}>FR</a>'
         f'<a href="/oh-quotidien/{N}/daat-harav/he"{ah}>HE</a>'
         f'<a href="/oh-quotidien/{N}/daat-harav/en"{ae}>EN</a></span>')
    dattr=f' dir="rtl"' if lang=="he" else ""
    html=f"""<!DOCTYPE html>
<html lang="{t['lang']}" dir="{t['dir']}">
<head>
<meta charset="UTF-8">
<meta name="daat-section" content="oh-quotidien">
<link rel="icon" type="image/svg+xml" href="../../../favicon.svg">
<meta name="viewport" content="width=device-width, initial-scale=1.0">
<title>{title}</title>
<meta name="description" content="{desc}">
<meta name="author" content="Rav Yossef Haim Samama">
<link rel="canonical" href="{canon}">
  <link rel="alternate" hreflang="fr" href="https://daattorah.com/oh-quotidien/{N}/daat-harav">
  <link rel="alternate" hreflang="en" href="https://daattorah.com/oh-quotidien/{N}/daat-harav/en">
  <link rel="alternate" hreflang="he" href="https://daattorah.com/oh-quotidien/{N}/daat-harav/he">
  <link rel="alternate" hreflang="x-default" href="https://daattorah.com/oh-quotidien/{N}/daat-harav">
<meta property="og:type" content="article">
<meta property="og:site_name" content="DAAT דעת">
<meta property="og:title" content="{title}">
<meta property="og:description" content="{desc}">
<meta property="og:url" content="{canon}">
<meta property="og:image" content="https://daattorah.com/assets/img/og/siman-{N}-oh.png">
<meta property="og:locale" content="{('fr_FR' if lang=='fr' else ('he_IL' if lang=='he' else 'en_US'))}">
<meta name="twitter:card" content="summary_large_image">
<meta name="twitter:title" content="{title}">
<meta name="twitter:description" content="{desc}">
<meta name="twitter:image" content="https://daattorah.com/assets/img/og/siman-{N}-oh.png">
<link rel="preconnect" href="https://fonts.googleapis.com">
<link rel="preconnect" href="https://fonts.gstatic.com" crossorigin>
<link rel="preload" as="style" href="https://fonts.googleapis.com/css2?family=Cormorant+Garamond:ital,wght@0,400;0,500;0,600;0,700;1,400&family=Frank+Ruhl+Libre:wght@300;400;500;700;900&family=Inter:wght@300;400;500;600&display=swap" onload="this.onload=null;this.rel='stylesheet'">
<noscript><link rel="stylesheet" href="https://fonts.googleapis.com/css2?family=Cormorant+Garamond:ital,wght@0,400;0,500;0,600;0,700;1,400&family=Frank+Ruhl+Libre:wght@300;400;500;700;900&family=Inter:wght@300;400;500;600&display=swap"></noscript>
{STYLE}
{jsonld}
  <link rel="manifest" href="/manifest.webmanifest">
  <meta name="theme-color" content="#1A1F3A">
  <link rel="apple-touch-icon" href="/apple-touch-icon.png">
</head>
<body>
  <script src="/assets/js/dedicace-banner.js" defer></script>
{lsf}
<header>
  <a href="../../../index.html" class="logo"><span class="logo-he">דעת</span><span class="logo-en">DAAT</span></a>
  <nav>
    <a href="../../../index.html">{t['home']}</a>
    <a href="/oh-quotidien/">{t['compart']}</a>
    <a href="/oh-quotidien/{N}/">Siman {numHe}</a>
  {lss}</nav>
</header>
<div class="breadcrumb"><div class="breadcrumb-inner">
    <a href="../../../index.html">{t['home']}</a><span class="sep">›</span>
    <a href="/oh-quotidien/">{t['compart']}</a><span class="sep">›</span>
    <a href="/oh-quotidien/{N}/">Siman {numHe}</a><span class="sep">›</span>
    <span class="current">{t['level4']}</span>
</div></div>
<div class="page-hero"><div class="hero-inner">
    <div class="hero-meta">Orah Haïm {numHe} · {t['level4']} · שיטת אדמו״ר הזקן</div>
    <p class="hero-title-he">דעת הרב</p>
    <h1 class="hero-title" style="margin:0;">{t['hero_title'](N)}</h1>
    <p class="hero-subtitle">{t['hero_sub'](subj)}</p>
</div></div>
<main>
  <div class="bridge-banner"{dattr}>
    <h2><span class="bridge-icon">🌉</span> {t['bridge_h'](N)}</h2>
    <p>{t['bridge_p'](numHe)}</p>
    <div class="bridge-links">{t['links'](N)}</div>
  </div>
  <div class="intro-block">
    <p><strong>{t['intro_h']}</strong> {t['intro_p1']}</p>
    <p>{t['intro_p2']}</p>
  </div>
  <div class="missing-banner">
    <h2>{t['miss_h'](numHe)}</h2>
    <p>{t['miss_p1']}</p>
    <p>{t['miss_p2']}</p>
    <p style="font-size:14px;font-style:italic;padding-top:12px;border-top:1px dashed var(--gold);">{t['miss_note']}</p>
  </div>
  <section class="section-block">
    <span class="section-num">{t['src_h_he']}</span>
    <h2 class="section-title-fr">{t['src_h']}</h2>
    <div class="section-divider"></div>
    <ul class="src-list">{t['src'](N)}</ul>
  </section>
  <nav class="niveau-nav" aria-label="Navigation">
    <a href="/oh-quotidien/{NM1}/daat-harav" class="nav-prev">{t['prev'](NM1)}</a>
    <div class="nav-niveaux">
      <a href="/oh-quotidien/{N}/{t['base']}" class="nav-level">N1</a>
      <a href="/oh-quotidien/{N}/{t['lamdan']}" class="nav-level">N2</a>
      <a href="/oh-quotidien/{N}/{t['synthese']}" class="nav-level">N3</a>
      <a href="/oh-quotidien/{N}/daat-harav{t['suf'].replace('-','/') if t['suf'] else ''}" class="nav-level active">N4</a>
    </div>
    <a href="/oh-quotidien/{NP1}/daat-harav" class="nav-next">{t['next'](NP1)}</a>
  </nav>
</main>
<footer><p>{t['foot']}</p></footer>
<link rel="stylesheet" href="../../../assets/css/chat-widget.css">
<script>window.DAAT_CHAT_API_URL = 'https://daatai.vercel.app/api/chat';</script>
<script src="../../../assets/js/chat-loader.js" defer></script>
<div style="text-align:center;margin:20px 0;">
  <button onclick="window.print()" class="print-btn" style="font-family:'Inter',sans-serif;font-size:13px;font-weight:600;letter-spacing:1px;background:#1A1F3A;color:#C5A55A;padding:10px 22px;border:1px solid #C5A55A;border-radius:2px;cursor:pointer;text-transform:uppercase;">{t['print']}</button>
</div>
<style>@media print {{ .print-btn {{ display:none !important; }} }}</style>
  <script src="/assets/js/siman-nav.js" defer></script>
</body>
</html>
"""
    return html

def gen(num, numHe, subj):
    d=os.path.join(ROOT, f"sources/orah-haim/siman-{num}")
    os.makedirs(d, exist_ok=True)
    for lang in ("fr","he","en"):
        suf=TXT[lang]["suf"]
        open(os.path.join(d,f"niveau-4-daat-harav{suf}.html"),"w",encoding="utf-8").write(page(lang,num,numHe,subj))
    print(f"  siman {num} ({numHe}) : 3 pages-pont niveau-4 générées.")

# Simanim du lot courant (132-134) : (num, numHe hébreu, sujet court)
SIMANIM=[
 (169,"קס״ט","דין שמש הסעודה — le service (chamach) au cours du repas"),
 (170,"ק״ע","דברי מוסר שינהג אדם בסעודה — les règles de bonne conduite (moussar) à table"),
]
if __name__=="__main__":
    args=[int(x) for x in sys.argv[1:]]
    for num,he,subj in SIMANIM:
        if not args or num in args:
            gen(num,he,subj)
    print("OK")
