// Date du jour pour le modèle — bloc système NON caché, ajouté après le prompt.
//
// Ni l'ancien prompt ni la V2 ne donnaient la date au modèle, et la V2 exigeait
// pourtant qu'un calendrier vienne « de dates vérifiées ». Sans date, « ce
// Shabbat », « cette semaine », « la parasha » ou « sommes-nous à Hol HaMoed »
// n'ont aucun ancrage. Le bloc est court et change une fois par jour ; il est
// placé HORS du bloc caché (cache_control) pour ne pas invalider le cache du
// prompt système à chaque changement de date.
//
// La date hébraïque vient d'Intl (calendrier « hebrew », ICU complet dans Node
// 22). Elle est calculée en UTC : le changement de jour hébraïque (au coucher du
// soleil) et l'heure locale dépendent du lieu de l'utilisateur, ce que le bloc
// dit explicitement pour que le modèle ne tranche pas une heure de Shabbat.

function hebrewDate(d) {
  try {
    const fmt = new Intl.DateTimeFormat('en-u-ca-hebrew', {
      timeZone: 'UTC', day: 'numeric', month: 'long', year: 'numeric',
    });
    return fmt.format(d);
  } catch {
    return null;
  }
}

export function dateContextBlock(now = new Date()) {
  const civil = now.toISOString().slice(0, 10);
  const weekday = new Intl.DateTimeFormat('fr-FR', { timeZone: 'UTC', weekday: 'long' }).format(now);
  const heb = hebrewDate(now);
  return (
    `<contexte_date>Date civile du serveur (UTC) : ${weekday} ${civil}` +
    (heb ? ` · date hébraïque civile correspondante (avant le coucher du soleil) : ${heb}` : '') +
    ". L'heure locale, l'entrée et la sortie de Shabbat et le passage au jour hébraïque suivant dépendent du lieu de l'utilisateur, que tu ne connais pas : ne donne aucun horaire sans qu'il te l'indique. Utilise cette date pour situer « aujourd'hui », « ce Shabbat » et la parasha de la semaine ; dis que tu la tiens du serveur si cela compte.</contexte_date>"
  );
}
