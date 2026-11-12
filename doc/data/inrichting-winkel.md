# Inrichting demowinkel ROSS

Volgorde: eerst de metafield-definities, dan de product-CSV importeren, dan de collecties.

## 1. Metafield-definities (vóór de import)

Instellingen › Aangepaste gegevens › Producten › Definitie toevoegen. Namespace is telkens `custom`.

| Naam | Namespace en sleutel | Type |
| --- | --- | --- |
| Koffienaam | `custom.koffienaam` | Tekst met één regel |
| Nummer filter | `custom.nummer_filter` | Geheel getal |
| Nummer espresso | `custom.nummer_espresso` | Geheel getal |
| Regio | `custom.regio` | Tekst met één regel |
| Labelkleur | `custom.labelkleur` | Kleur |
| Smaaknotities | `custom.smaaknotities` | Tekst met één regel (notities gescheiden door ` \| `) |
| Herkomst | `custom.herkomst` | Tekst met meerdere regels |
| Variëteit en verwerking | `custom.verwerking` | Tekst met meerdere regels |
| Waarom bijzonder | `custom.waarom` | Tekst met meerdere regels |
| Oogstperiode | `custom.oogst` | Tekst met één regel |
| Tips | `custom.tips` | Tekst met meerdere regels |

Vink bij elke definitie "Storefront-toegang" aan, zodat het thema de velden kan tonen.

## 2. Product-CSV importeren

Producten › Importeren › `producten-import.csv`. Vink "Bestaande producten met dezelfde handle overschrijven" aan bij een tweede import.

## 3. Automatische collecties

Producten › Collecties › Collectie maken › Automatisch.

| Collectie | Handle | Voorwaarde |
| --- | --- | --- |
| Koffie | `koffie` | Producttype is "Single origins" OF producttype is "Blends" OF producttype is "Proefpakket" |
| Huisblends | `huisblends` | Producttype is "Blends" |
| Single origins | `single-origins` | Producttype is "Single origins" |
| Proefpakketten | `proefpakketten` | Producttype is "Proefpakket" |
| Abonnementen | `abonnementen` | Producttype is "Abonnementen" |
| Toestellen | `toestellen` | Producttype is "Toestellen" |
| Accessoires | `accessoires` | Producttype is "Attributen" |
| Thee | `thee` | Producttype is "Thee" |
| Cadeaus | `cadeaus` | Producttype is "Geschenken" OF tag is "cadeau" |
| Lekkers | `lekkers` | Producttype is "Pralines" OF producttype is "Advocaat" |

De regio-filter (bruin, oranje, rood, paars, geel) op de koffiepagina komt uit het metafield `custom.regio`, niet uit aparte collecties.
