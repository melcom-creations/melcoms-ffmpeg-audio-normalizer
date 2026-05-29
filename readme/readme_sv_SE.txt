melcom's FFmpeg Audio Normalizer v4.0.2 - Läderlappen Edition 🦇

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
- Tryck på "▶"-knappen

Med knapparna "«" och "»" kan du navigera genom din spellista.


5. Alternativ och inställningar

Under:
Arkiv -> Alternativ

kan du:

- ändra FFmpeg-sökväg
- byta programsprak
- byta apptema
- anpassa loggfilsinställningar


========================================
MASTERING-KARAKTÄRER (FÖRINSTÄLLNINGAR)
========================================

Transparent
Endast normalisering av ljudstyrka utan extra ljudbearbetning.

Cohesive
Mild bredbandskomprimering med en subtil softclip-kontur för en jämnare övergripande mix.

Punchy
Ökar närvaro och slagkraft genom starkare komprimering.

Aggressive
Det starkaste alternativet för tätt och skarpt material.


========================================
VIKTIG INFORMATION
========================================

FFmpeg-sökväg
Se till att sökvägen till ffmpeg.exe, ffplay.exe och ffprobe.exe är korrekt konfigurerad.

ffprobe.exe
Denna fil används för tidsvisningen i ljudspelaren.
Uppspelningen fungerar fortfarande utan den, men utan varaktighetsinformation.

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

LICENSE.txt


Ha så trevligt med melcom's FFmpeg Audio Normalizer!

Med vänliga hälsningar,
melcom