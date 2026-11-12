# Overdracht: demo-webshop ROSS coffee

Lees dit eerst helemaal. Je neemt een lopend project over. Werk in het Nederlands (Vlaams), kort en zakelijk.

## Context

- **ROSS coffee** ([rosscoffee.be](https://rosscoffee.be)) is een koffiebranderij met een winkel in Kruibeke en een branderij in Melsele. De eigenaars zijn Wim en Sabrina. ROSS sponsort het triatlonteam van de gebruiker (Jeroen).
- Jeroen wil ROSS een nieuwe website aanbieden, volledig met AI gebouwd ("vibe coden"), **binnen Shopify**, zodat er aan hun verkoopplatform weinig verandert.
- **Kernboodschap voor ROSS:** ROSS blijft eigenaar van zijn huidige project. We geven het een sterke upgrade zonder aan de bestaande online winkel te raken.
- Werkwijze: we bouwen een eigen Liquid-thema op basis van Dawn, in een **Shopify Partner-ontwikkelwinkel** van Jeroen. Die winkel is de demo: hij staat achter een wachtwoord en betalingen zijn er enkel testbetalingen. Later kan ROSS het thema in zijn eigen winkel als verborgen thema bekijken.
- Jeroen werkt op twee computers (HP Omen en Samsung-laptop) en gebruikt **GitHub** in plaats van OneDrive.

## Belangrijke links

| Wat | Waar |
| --- | --- |
| Voorstel (doc) | https://claude.ai/artifact/5HwBvfjDz6cBanBFBfCMGj |
| Stappenplan (doc, met fases en tijden) | https://claude.ai/artifact/7kNEubBf5fc3xvieD5FhAp |
| Ontwerp (Design-canvas, pagina "Nieuwe richting") | https://claude.ai/artifact/VEzvWbBgs2Ard9kkUNm3sc |
| GitHub-repo | https://github.com/webchain/ROSS (branch `main`) |
| Projectbestanden | Project "Ross": `products_limit250.json` (volledige feed, 157 producten), `collections.json`, `sitemap.xml`, `news.atom.txt`, `claude/beelden-overzicht.md` en 19 foto's (logo, zakken, Wim en Sabrina, branderij, koffiebar…) |

Lees het stappenplan opnieuw voor je het bewerkt; Jeroen past het zelf ook aan.

## Repo-structuur

```
/            ← hier komt het Shopify-thema (layout/, sections/, snippets/, templates/, config/, locales/, assets/)
doc/         ← Shopify negeert deze map
  README.md
  overdracht.md           (dit bestand)
  scripts/build_import.py (bouwt de import uit products_limit250.json)
  data/producten-import.csv
  data/koffievelden.csv
  data/rapport.md
  data/inrichting-winkel.md (metafields en collecties)
```

Commits eindigen met de attributieregels die de sessie opgeeft. Doe eerst `git fetch origin main` voor je pusht.

## Waar we staan

- **Fase 0 (voorbereiden): klaar.** Er zijn een Partner-account (Datachain BV), een ontwikkelwinkel (plan Basic) en de GitHub-repo.
- **Fase 1 (productdata): CSV klaar.** De import telt 155 producten, 422 varianten en 663 afbeeldingsrijen. Voor 20 koffies zijn de koffievelden als metafields ingevuld. De testproducten "test" en "digital-product-2" zijn eruit, net als emoji's en oude HTML. Voor de koffies zijn de opties gelijkgetrokken naar **Toestel / Gewicht / Maling**. Bij Rwanda ontbreken herkomst en "waarom bijzonder".
- Foto's verwijzen naar cdn.shopify.com van de huidige winkel. Shopify haalt ze bij de import zelf op.

## Wat nu te doen, in deze volgorde

1. **Metafield-definities aanmaken in de ontwikkelwinkel**, met de ingebouwde browser. Jeroen logt zelf in; jij vult nooit wachtwoorden in. Ga naar Instellingen › Aangepaste gegevens › Producten › Definitie toevoegen, met namespace `custom` en "Storefront-toegang" aan:

   | Naam | Sleutel | Type |
   | --- | --- | --- |
   | Koffienaam | `custom.koffienaam` | Tekst met één regel |
   | Nummer filter | `custom.nummer_filter` | Geheel getal |
   | Nummer espresso | `custom.nummer_espresso` | Geheel getal |
   | Regio | `custom.regio` | Tekst met één regel |
   | Labelkleur | `custom.labelkleur` | Kleur |
   | Smaaknotities | `custom.smaaknotities` | Tekst met één regel |
   | Herkomst | `custom.herkomst` | Tekst met meerdere regels |
   | Variëteit en verwerking | `custom.verwerking` | Tekst met meerdere regels |
   | Waarom bijzonder | `custom.waarom` | Tekst met meerdere regels |
   | Oogstperiode | `custom.oogst` | Tekst met één regel |
   | Tips | `custom.tips` | Tekst met meerdere regels |

   Jeroen heeft al gevraagd om de definities op te slaan. Ze aanmaken en bewaren mag dus zonder extra akkoord.
2. **Jeroen importeert `doc/data/producten-import.csv`** via Producten › Importeren. Bestanden uploaden in de admin kan Claude niet. Controleer daarna een paar producten, bv. "10/50 Mercator": staan de metafields goed en zijn de varianten en foto's er?
3. **Automatische collecties aanmaken** volgens `doc/data/inrichting-winkel.md`: Koffie, Huisblends, Single origins, Proefpakketten, Abonnementen, Toestellen, Accessoires, Thee, Cadeaus en Lekkers. Vraag één keer akkoord voor het opslaan van de hele reeks.
4. **Fase 2: het thema.** Haal Dawn op via GitHub (`Shopify/dawn`) en zet het in de root van de repo. Bouw het in de stijl van het v3-ontwerp; zie hieronder. Laat `shopify theme check` lopen als dat lukt. Push daarna. Jeroen koppelt de repo één keer via Online Store › Thema's › Thema toevoegen › Verbinden via GitHub (webchain/ROSS, branch `main`).
5. **Fase 3:** pagina's (Ons verhaal, Workshops, Mobiele koffiebar, Zakelijk, Contact), menu, logo en nieuwsbrief. **Fase 4:** review. **Fase 5:** wachtwoord, preview-link en een rondleiding van één pagina voor ROSS die opent met de eigendomsboodschap.

## Ontwerprichting (v3, goedgekeurd door Jeroen)

- **Vertrekpunt is het eigen merk van ROSS:** het logo wit op zwart, de gekleurde koffiezakken en echte foto's van Wim, Sabrina, de branderij en de koffiebar.
- **Niet doen:** geen saaie, zakelijke look. Niet alles in koffiebeige. Niets dat er "AI-gemaakt" of als een template uitziet. Jeroen keurde eerdere versies om die redenen af.
- **Basis:** wit en zwart, met de labelkleuren als accent. Huisblend is bruin `#7B4B2A`, Afrika oranje `#F07D1F`, Midden-Amerika rood `#D3302B`, Zuid-Amerika paars `#B22A6E`, Azië geel `#CDAA21` en cafeïnevrij grijs `#6E6E6E`. Op de zakken is rood Midden-Amerika en paars Zuid-Amerika, terwijl de huidige site het omgekeerd doet. De demo volgt de zakken; ROSS moet dat nog bevestigen.
- **Typografie:** Montserrat, met Yellowtail als handschriftaccent.
- **Toon:** speels en direct, bv. "Melk en suiker? Mag. Hoeft niet."
- **Inspiratie:** illy en carantos.be.
- **Pagina's in het canvas:** Home, HomeMobiel, Koffie (collectie met kleurfilter), Mercator (product), MercatorNu (product met enkel de data die er vandaag is; dat is de basis voor de demo) en Abo.
- **Productpagina:** het nummer staat groot (espresso toont 50, filter 10), met de koffienaam, een gekleurd vlak volgens de regio, smaakchips, uitklapblokken met herkomst, verwerking, oogst en tips, en "Probeer ook eens" via Shopify-aanbevelingen.
- **Voorlopig verborgen:** smaakmeter en zetadvies, tot Wim de waarden geeft. Abonnementen, reviews en workshopboekingen hebben een app nodig.

## Praktische beperkingen

- De werkruimteproxy blokkeert rosscoffee.be en cdn.shopify.com. Haal gegevens uit de projectbestanden of gebruik de ingebouwde browser.
- Gebruik de ingebouwde browser van de computer waaraan de chat gekoppeld is. Jeroen moet daar zelf inloggen.
- `project_write` aanvaardt geen binaire bestanden. De foto's staan al in het project.

## Eerste actie in de nieuwe chat

Controleer of de ingebouwde browser ingelogd is in de admin van de ontwikkelwinkel (admin.shopify.com/store/…). Is dat zo, dan maak je stap 1 aan. Is het niet zo, dan vraag je Jeroen om in te loggen in de ingebouwde browser van de computer waaraan deze chat gekoppeld is.
