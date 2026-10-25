# Referentiel administratif

**39 prefectures**, **117 communes**, **5 regions** (communalisation integrale depuis 2019).

## Fichiers

| Fichier | Contenu |
|---------|---------|
| `regions.csv` | Regions (id, code ISO-like, nom) |
| `prefectures.csv` | Prefectures + lien region + `cle_normalisee` |
| `communes.csv` | Communes + lien prefecture / region |
| `mapping_libelles.csv` | Alias (agences, electricite) -> `prefecture_id` |
| `alias_open_data.csv` | Ecarts RGPH / open data (TANDJOARE, AGOE NYIVE, TOTOAL AVE) |
| `manifest.json` | Comptages et source |

## Regenerer

```bash
python3 data/ref/build_ref.py
```

Source CSV : [gausoft/Subdivision_administrative_Togo](https://github.com/gausoft/Subdivision_administrative_Togo) (mise a jour nov. 2021). A croiser avec [territoire.gouv.tg](https://territoire.gouv.tg/chiffres_cles/communes-du-togo/) pour validation officielle.

Utilise en **gold** pour joindre population, electricite et agences.
