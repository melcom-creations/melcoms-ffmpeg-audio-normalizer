melcom's FFmpeg Audio Normalizer v4.1.2 - Herbstklang Edition

Analysresultat
--------------

Använd Endast analysera för att mäta filerna i kön utan att ändra eller koda ljudet. Rapporten öppnas automatiskt när omgången är klar och kan öppnas igen med "Analysresultat...". Listan visar ljudstyrka, True Peak, ljudstyrkeomfång (LRA) och PLR samt fler signalvärden för varje fil. Målen som valdes vid analysstart används endast för jämförelse; skillnaderna förutsäger inte normaliserad utdata. Kopiera ett eller alla resultat, eller exportera hela rapporten som CSV. Analys- och normaliseringsrapporter sparas separat under sessionen. En ny omgång ersätter bara rapporten av samma typ. Saknade mätningar, fel och avbrutna filer markeras tydligt. Vid filfel fortsätter analysen med återstående filer. Redan insamlade resultat finns kvar efter avbrott.

Kontroll av utdata och resultat
-------------------------------

Normaliseringsresultaten erbjuder också kopiering av ett eller alla resultat och CSV-export med original, mål, uppmätt utdata, status, bearbetningsläge och kodningsdetaljer.

Efter en slutförd analys eller normalisering öppnas motsvarande resultatfönster automatiskt. Håll muspekaren över en resultatknapp för en förklaring, även när knappen är inaktiverad. Efter avbrott finns insamlade resultat kvar via motsvarande knapp.

Ljudstyrkeomfång (LRA) beskriver variationer i ljudstyrka över tid. Sample Peak är den högsta digitala samplingsnivån; True Peak tar även hänsyn till uppskattade toppar mellan samplingarna. DC-offset är signalens likspänningskomponent.

Ljudstyrka i resultattabellerna avser filens integrerade ljudstyrka i LUFS. Relativ gatingtröskel är den relativa mättröskel som FFmpeg rapporterar för ljudstyrkemätningen, inte kompressorns tröskel eller en brusgrind i signalvägen. Min. / max. samplingsvärde visar samplingsvärden med tecken, inte nivåer i dBFS. Crestfaktor jämför Sample Peak med RMS, medan PLR jämför True Peak med integrerad ljudstyrka. LRA beskriver variationer i ljudstyrka och är inte utbytbart mot något av dessa förhållanden. Uppmätt bitdjup beskriver de avkodade samplingarna, inte filformatets bitdjup.

PLR (Peak-to-Loudness Ratio)
PLR är skillnaden mellan maximal True Peak och integrerad ljudstyrka för samma fil. Värdet visas i LU och kompletterar LRA och crestfaktor. Det beräknas från den befintliga analysen utan en extra mätning. Saknade eller icke-ändliga mätvärden visas som N/A; PLR ensamt bedömer inte ljudkvaliteten.

Fönsterlayout
Dra den vågräta avdelaren ovanför processloggen för att ändra dess höjd. Den lodräta avdelaren mellan filer och inställningar ändrar deras bredd. Inställningarna kan rullas när utrymmet är mindre. Knapparna för bearbetning förblir synliga under arbetsområdena.

Fönsterstorlek, avdelarnas positioner och maximerat läge sparas automatiskt i avsnittet Layout i options.ini och återställs vid nästa start. Arkiv - Återställ fönsterlayout återställer den inbyggda layouten. Layouten är oberoende av ljudprofiler och bevaras vid byte av utformat, språk eller tema.

MP3 och M4A använder nu uttryckligen 320 kbps CBR som standard, oberoende av källans bithastighet. MP3 använder LAME-algoritmkvalitet 0. VBR aktiveras endast genom att välja en VBR-kvalitetsnivå; M4A erbjuder q2 och q1. OGG/Vorbis använder som standard 320 kbps ABR, en genomsnittlig målbithastighet och inte strikt CBR. Dess VBR-kvalitetsnivåer är separata alternativ. Äldre profiler med förlustformat och Original / Standard läser in formatets nya standard; det tidigare Vorbis-valet 320 kbps (CBR) läses in som 320 kbps (ABR). Profiler sparar det uttryckliga kvalitetsvalet. Formathjälpen under specifikationen förklarar headroom vid kodning och radbryts efter panelens bredd. Resultat och urklipp innehåller den valda kodningen.

"Headroom vid kodning (dB)" reserverar 0 till 3 dB före MP3-, M4A- eller OGG-kodning för toppar som kan uppstå vid kodning med förlust. Den interna True Peak-gränsen sänks med det angivna värdet, som lägst till FFmpegs miniminivå på -9 dBTP. Målen för ljudstyrka och slutlig True Peak ändras inte. Värdet 0 stänger av den extra marginalen. Inställningen finns under Utdataformat och sparas i profiler. Äldre profiler använder standardvärdet 0. WAV och FLAC ignorerar inställningen. Resultat och urklipp visar begärd och tillämpad marginal. Kontrollen av utdata mäter den färdigkodade filen mot de valda målen utan att ändra filen.

Aktivera "Kontrollera utdatafiler" före normalisering för att mäta de färdigkodade filerna. Alternativet är avstängt som standard och kräver extra analystid. Arkiv - Alternativ sparar standardinställningen; profiler kan spara valet. Äldre profiler läses in med kontrollen avstängd.

Öppna "Resultat..." efter bearbetningen för att jämföra original, målvärden och uppmätt utdata. Resultaten gäller den senaste normaliseringsomgången och finns i minnet tills en ny omgång startas eller programmet stängs. Det valda resultatet kan kopieras.

Skapandet av filen och kontrollen har separata statusvärden. En misslyckad eller avbruten kontroll tar inte bort en fil som har skapats. Toleransen för ljudstyrka är +/- 0,2 LU; True Peak får ligga högst 0,1 dB över den valda gränsen för en godkänd kontroll. LRA visas utan kontroll mot ett målvärde. Detta är programmets toleranser, inte en certifiering.

Mäter först och begär en fast nivåändring. FFmpeg kan växla till dynamisk bearbetning om gränser för True Peak eller ljudstyrkeomfång (LRA) förhindrar linjär bearbetning. Masteringinställningen bearbetar ljudet före normalisering och kan ändra dynamiken även när FFmpeg rapporterar linjärt läge. Om ljudstyrkan inte kan mätas hoppas ljudstyrkejusteringen över i läget med två pass, och målvärdena kan inte verifieras. Tystnad och mycket korta filer är exempel.

Antalet pass avser normaliseringen. Verifiering lägger till en mätning av den kodade filen; mastering kan också kräva en separat mätning av originalet.

Giltiga målvärden är -70 till -5 LUFS och -9 till 0 dBTP. Original / Standard bevarar de WAV-bitdjup som stöds, inklusive 64-bitars float. Om källans bithastighet inte passar utdatakodeken används dess standardvärden. Konflikter i utdatasökvägar avvisas före bearbetningen.

Ljudnormalisering med öppen källkod som använder FFmpeg med stöd för LUFS och True Peak.

Med detta program kan du enkelt normalisera ljudstyrkan på dina ljudfiler - individuellt eller i batch - med FFmpeg. De färdiga filerna sparas automatiskt i samma mapp som originalfilerna.


========================================
SNABBSTART
========================================

1. Installera FFmpeg-paketet

För detta program krävs följande kostnadsfria kommandoradsverktyg:

- ffmpeg.exe
- ffplay.exe
- ffprobe.exe

Rekommenderad nedladdningskälla:
https://github.com/BtbN/FFmpeg-Builds/releases

För Windows rekommenderas "essentials" eller "full" builds.
Leta efter en fil som:

ffmpeg-master-latest-win64-gpl.zip

Packa sedan upp arkivet på valfri plats på datorn.


2. Starta programmet och konfigurera FFmpeg-sökvägen

- Starta AudioNormalizer.exe
- Öppna i menyn: Arkiv -> Alternativ
- Välj mappen som innehåller ffmpeg.exe, ffplay.exe och ffprobe.exe

Viktigt:
Programmet kan inte fungera utan en giltig FFmpeg-sökväg.


3. Normalisera ljudfiler

- Använd "Lägg till filer" eller "Lägg till mapp"
- Välj önskad LUFS-förinställning till höger
- Välj utdataformat
- Klicka på "Starta normalisering"

Förloppet för batch-bearbetningen visas i realtid.
De färdiga filerna skapas automatiskt.


4. Förhandsgranska ljud

- Markera en fil i listan
- Tryck på knappen "Spela"

Med knapparna "Föregående" och "Nästa" kan du navigera genom din spellista.


5. Alternativ och inställningar

Under:
Arkiv -> Alternativ

kan du:

- ändra FFmpeg-sökväg
- byta programspråk
- byta apptema
- anpassa loggfilsinställningar
- aktivera eller inaktivera automatisk sökning efter uppdateringar
- välja om förhandsversioner ska inkluderas

Uppdateringskontrollen visar endast ett meddelande och en länk till motsvarande GitHub-version. Den hämtar eller installerar aldrig uppdateringar automatiskt. En manuell kontroll finns under Info -> Sök efter uppdateringar.


========================================
MASTERING-KARAKTÄRER (FÖRINSTÄLLNINGAR)
========================================

Namnen beskriver den avsedda ljudkaraktären, inte standardiserade mätvärden. Det hörbara resultatet beror på källmaterialet. Kompression och mjuk klippning sker före ljudstyrkenormaliseringen och kan ändra både anslag, täthet och signalens toppar.

Transparent
Ljudstyrkenormalisering utan extra masteringfilter. Dynamisk normalisering kan fortfarande ändra dynamiken.

Sammanhållen
Mild kompression och mjuk klippning för en mer sammanhållen mix. Kan minska dynamiken även i linjärt läge.

Punchy
Kompression och mjuk klippning med fokus på tryck och tydliga anslag. Kan ändra transienter och dynamik även i linjärt läge.

Aggressiv
Kraftigare kompression och mjuk klippning för ett tätare ljud. Kan minska dynamiken även i linjärt läge.


========================================
VIKTIG INFORMATION
========================================

FFmpeg-sökväg
Se till att sökvägen till ffmpeg.exe, ffplay.exe och ffprobe.exe är korrekt konfigurerad.

ffprobe.exe
Denna fil används för tidsvisningen i ljudspelaren.
Uppspelningen fungerar fortfarande utan den, men utan information om speltid.

LUFS-förinställningar
Förinställningarna hjälper dig att välja lämpliga ljudstyrkemål för olika plattformar.
Anpassade värden kan naturligtvis också matas in manuellt.

Utdataformat
Informationsrutan under formatvalet visar tekniska detaljer om det valda utdataformatet.


========================================
LICENS
========================================

Denna programvara är öppen källkod och släpps under MIT-licensen.
Mer information finns i filen:

LICENSE


Ha så trevligt med melcom's FFmpeg Audio Normalizer!

Med vänliga hälsningar,
melcom
