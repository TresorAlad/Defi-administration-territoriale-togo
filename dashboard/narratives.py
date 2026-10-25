"""Textes explicatifs du dashboard (français, sans markdown brut)."""

HOME_INTRO = (
    "Ce tableau de bord répond à une question simple : où vivent les Togolais, "
    "et où l'accès aux services publics (électricité, agences CEET/TdE, état civil, identité) "
    "est-il le plus inégal ? Les chiffres proviennent de données ouvertes, consolidées "
    "en couche analytique gold (39 préfectures, 117 communes)."
)

HOME_KPI = (
    "Les indicateurs ci-dessous situent l'échelle du pays : population recensée en 2022, "
    "nombre de points CEET et TdE recensés, et écart de taille entre la plus grande "
    "et la plus petite commune."
)

DEMO_INTRO = (
    "Depuis la décentralisation, le Togo compte 117 communes aux effectifs très différents. "
    "Cette page présente la population en 2022 par préfecture, son poids dans le pays, "
    "l'évolution depuis 2010 lorsque les libellés sont comparables, puis les communes "
    "aux extrêmes. Source : recensement RGPH."
)

DEMO_POP_BARS = (
    "Population 2022 par préfecture",
    "Chaque barre correspond aux résidents recensés dans une préfecture. "
    "Le littoral (Golfe, Agouè-Nyivé, Zio) concentre une large part des habitants ; "
    "l'intérieur regroupe des territoires plus petits mais essentiels pour l'équité régionale. "
    "Utilisez le filtre Région pour zoomer sur une zone.",
)

DEMO_POIDS = (
    "Préfectures les plus pesantes dans le pays",
    "Part de la population nationale (2022) pour les territoires qui concentrent le plus d'habitants. "
    "Complète le graphique précédent en mettant en évidence le déséquilibre Littoral / intérieur. "
    "Le filtre Région s'applique à toute la page.",
)

DEMO_EVOL = (
    "Évolution 2010-2022",
    "Comparaison lorsque le libellé administratif est identique en 2010 et en 2022. "
    "Les préfectures non comparables (changement de découpage) sont exclues. "
    "Le graphique met en avant les plus fortes hausses ; le tableau détaille l'ensemble.",
)

DEMO_EVOL_CHART = (
    "Pression démographique (croissance comparables)",
    "Variation en pourcentage sur les préfectures comparables. "
    "Une croissance rapide avec un accès aux services encore faible renforce la priorité d'action.",
)

DEMO_COMMUNES = (
    "Communes les plus et les moins peuplées",
    "Sur 117 communes, l'écart de population peut atteindre un facteur d'environ 35 "
    "entre les extrêmes. Les tableaux listent les dix communes aux deux bouts de la distribution.",
)

SERVICES_INTRO = (
    "L'électricité et la proximité des agences CEET (énergie) et TdE (eau) illustrent "
    "concrètement la présence de l'État. Filtrez par région pour comparer des zones homogènes : "
    "taux d'accès, charge par agence et carte des guichets se mettent à jour."
)

SERVICES_ELEC = (
    "Accès à l'électricité",
    "Taux d'accès au réseau basse tension par préfecture, avec code couleur par région. "
    "Les écarts avec le grand Lomé mettent en évidence la fracture territoriale. "
    "Certaines valeurs source dépassent 100 % : anomalie de définition à signaler en analyse.",
)

SERVICES_AGENCES = (
    "Habitants par agence",
    "Population 2022 divisée par le nombre d'agences CEET et TdE recensées. "
    "Un ratio élevé signifie que les usagers partagent peu de points d'accueil.",
)

SERVICES_MAP = (
    "Localisation des agences",
    "Points géolocalisés à partir des coordonnées publiées. "
    "Les zones densément peuplées sans point visible sont des candidats à l'ouverture de guichets.",
)

ETAT_INTRO = (
    "L'état civil et les documents d'identité reflètent la capacité de l'administration "
    "à enregistrer les naissances et à délivrer CNI, passeports et cartes professionnelles. "
    "La série 2021 est partielle sur certains types de documents : prudence de lecture."
)

ETAT_NAISSANCES = (
    "Naissances enregistrées sous 45 jours",
    "Évolution nationale du nombre d'enregistrements dans les délais légaux. "
    "Les variations peuvent mêler tendance réelle et changement de collecte.",
)

ETAT_IDENTITE = (
    "Production de documents d'identité",
    "Volumes annuels par type de document. "
    "La demande de passeports peut refléter la mobilité, pas seulement la démographie.",
)

RECO_INTRO = (
    "Les recommandations s'appuient sur un score calculé en gold : faible accès à l'électricité, "
    "peu d'agences, croissance démographique 2010-2022. "
    "Utilisez le filtre Région pour isoler les priorités d'une zone ; les fiches dépliables détaillent chaque territoire."
)

LIMITES_ANALYSE = (
    "Limites et prudence de lecture",
    "Homonymes RGPH gérés en silver ; évolution 2010-2022 partielle si le découpage a changé ; "
    "série identité 2021 incomplète ; certains taux d'électricité source dépassent 100 % (définition statistique). "
    "Les scores de priorité orientent l'action, ils ne remplacent pas une étude de terrain.",
)

CONCLUSIONS_CLE = (
    "Trois enseignements",
    "1) Le territoire est très inégal : communes et préfectures littoral vs intérieur. "
    "2) L'accès électricité et guichets CEET/TdE reste disjoint de la densité de population. "
    "3) Des actions ciblées par préfecture sont proposées dans mart_recommandations, alimentées par le pipeline reproductible.",
)

RECO_CHART = (
    "Territoires prioritaires",
    "Classement des préfectures où les signaux de tension se cumulent le plus. "
    "Les fiches détaillées précisent les mesures suggérées.",
)

RECO_FICHES = (
    "Actions par préfecture",
    "Synthèse population, électricité et agences, avec recommandation rédigée pour chaque territoire en tête de liste.",
)

RECO_PLAN = (
    "Orientations nationales",
    "Synthèse pour décideurs : complète les fiches locales sans les remplacer.",
)
