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

DEMO_SCATTER = (
    "Poids national et effectif",
    "Ce graphique croise la part du Togo (en %) et la population absolue. "
    "Il permet de repérer les préfectures qui pèsent fortement dans le total national.",
)

DEMO_EVOL = (
    "Évolution 2010-2022",
    "Comparaison des effectifs lorsque le nom administratif est le même en 2010 et en 2022. "
    "Les préfectures non comparables (changement de découpage) sont exclues du tableau. "
    "Une hausse marquée traduit une pression accrue sur les services publics.",
)

DEMO_COMMUNES = (
    "Communes les plus et les moins peuplées",
    "Sur 117 communes, l'écart de population peut atteindre un facteur d'environ 35 "
    "entre les extrêmes. Les tableaux listent les dix communes aux deux bouts de la distribution.",
)

SERVICES_INTRO = (
    "L'électricité et la proximité des agences CEET (énergie) et TdE (eau) illustrent "
    "concrètement la présence de l'État. Nous croisons ici le taux d'accès par préfecture, "
    "la charge par agence (habitants par point de service) et la cartographie des guichets."
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
    "Plus le score est élevé, plus la préfecture mérite une action ciblée."
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
