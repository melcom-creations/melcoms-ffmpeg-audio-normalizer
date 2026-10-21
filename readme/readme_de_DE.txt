melcom's FFmpeg Audio Normalizer v4.1.2 - Herbstklang Edition

Ausgabeprüfung und Ergebnisse
-----------------------------

PLR (Peak-to-Loudness Ratio)
PLR ist die Differenz zwischen maximalem True Peak und integrierter Lautheit derselben Datei. Der Wert wird in LU angezeigt und ergänzt LRA und Crest-Faktor. Er wird ohne weiteren Messdurchlauf aus der vorhandenen Analyse berechnet. Fehlende oder nicht endliche Messwerte erscheinen als N/A; PLR allein bewertet keine Klangqualität.

Fensteraufteilung
Die waagerechte Trennlinie über dem Prozessprotokoll verändert dessen Höhe. Die senkrechte Trennlinie zwischen Dateien und Einstellungen verändert deren Breite. Bei wenig Platz lassen sich die Einstellungen scrollen. Die Schaltflächen zur Verarbeitung bleiben unter den Arbeitsbereichen sichtbar.

Fenstergröße, Positionen der Trennlinien und maximierter Zustand werden automatisch im Abschnitt Layout der options.ini gespeichert und beim nächsten Start wiederhergestellt. Datei - Fensteraufteilung zurücksetzen stellt die eingebaute Standardaufteilung wieder her. Die Aufteilung ist unabhängig von Audioprofilen und bleibt beim Wechsel von Ausgabeformat, Sprache oder Theme erhalten.

MP3 und M4A starten jetzt ausdrücklich mit 320 kbps CBR, unabhängig von der Quellbitrate. MP3 verwendet LAME-Algorithmusqualität 0. VBR wird nur durch Auswahl einer VBR-Qualitätsstufe aktiviert; M4A bietet q2 und q1. OGG/Vorbis startet mit 320 kbps ABR, einer durchschnittlichen Zielbitrate und keinem strikten CBR. Seine VBR-Qualitätsstufen bleiben ausdrücklich wählbare Alternativen. Ältere verlustbehaftete Profile mit Original / Default laden den neuen Formatstandard; die frühere Vorbis-Option 320 kbps (CBR) wird als 320 kbps (ABR) geladen. Profile speichern die ausdrückliche Qualitätsauswahl. Die Formathilfe unter Specs erklärt den Encoder-Headroom und passt ihren Zeilenumbruch an die Feldbreite an. Ergebnisse und Zwischenablage enthalten die gewählte Codierung.

"Encoder-Headroom (dB)" reserviert vor der MP3-, M4A- oder OGG-Codierung 0 bis 3 dB für Signalspitzen, die bei verlustbehafteter Codierung entstehen können. Die interne True-Peak-Grenze wird um den eingestellten Wert abgesenkt, höchstens bis zu FFmpegs Untergrenze von -9 dBTP. Lautheitsziel und endgültiger True-Peak-Zielwert bleiben unverändert. 0 deaktiviert die zusätzliche Reserve. Die Einstellung steht unter Ausgabeformat und wird in Profilen gespeichert. Ältere Profile verwenden den Standardwert 0. WAV und FLAC ignorieren die Einstellung. Ergebnisse und Zwischenablage zeigen angeforderte und angewendete Reserve. Die Ausgabeprüfung misst die fertig codierte Datei gegen die gewählten Zielwerte, ohne sie zu verändern.

Aktiviere "Ausgabedateien prüfen" vor der Normalisierung, um die fertig codierten Dateien zu messen. Die Option ist standardmäßig ausgeschaltet und benötigt zusätzliche Analysezeit. Datei - Optionen speichert die Voreinstellung; Profile können die Auswahl übernehmen. Ältere Profile werden ohne Ausgabeprüfung geladen.

Öffne nach der Verarbeitung "Ergebnisse...", um Original, Ziel und gemessene Ausgabe zu vergleichen. Die Ergebnisse gehören zum letzten Normalisierungslauf und bleiben bis zum nächsten Normalisierungslauf oder Programmende im Arbeitsspeicher. Das ausgewählte Ergebnis lässt sich kopieren.

Dateierstellung und Prüfung haben getrennte Zustände. Eine fehlgeschlagene oder abgebrochene Prüfung verwirft keine erfolgreich erstellte Datei. Die Lautheit wird mit +/- 0,2 LU geprüft; True Peak darf für eine bestandene Prüfung höchstens 0,1 dB über der gewählten Grenze liegen. LRA wird ohne Zielprüfung angezeigt. Dies sind Anwendungstoleranzen und keine Zertifizierung.

Misst zuerst und fordert eine feste Pegeländerung an. FFmpeg kann dynamisch arbeiten, wenn True-Peak- oder Lautheitsspanne-Grenzen die lineare Verarbeitung verhindern. Das Mastering-Preset bearbeitet das Audio vor der Normalisierung und kann die Dynamik auch dann verändern, wenn FFmpeg Linear meldet. Ist die Lautheit nicht messbar, entfällt im Verfahren mit zwei Durchgängen die Lautheitsanpassung; eine erfolgreiche Zielprüfung ist dann nicht möglich. Beispiele sind Stille und sehr kurze Dateien.

Die Zahl der Durchgänge bezieht sich auf die Normalisierung. Die Ausgabeprüfung ergänzt eine Messung der codierten Datei; bei Mastering kann zusätzlich eine separate Messung des Originals nötig sein.

Gültige Ziele liegen zwischen -70 und -5 LUFS sowie -9 und 0 dBTP. Original / Default erhält unterstützte WAV-Bittiefen einschließlich 64-Bit-Float. Ist die Quellbitrate für den Ausgabecodec ungeeignet, werden dessen Standardwerte verwendet. Widersprüchliche Ausgabepfade werden vor der Verarbeitung abgelehnt.

Open-Source Audio-Normalisierung mit FFmpeg sowie LUFS- und True-Peak-Unterstützung.

Mit diesem Programm kannst Du die Lautstärke Deiner Audiodateien - einzeln oder stapelweise - komfortabel mit FFmpeg normalisieren. Die fertigen Dateien werden automatisch im gleichen Ordner wie die Originaldateien gespeichert.


========================================
SCHNELLSTART
========================================

1. FFmpeg-Suite installieren

Für dieses Programm benötigst Du die kostenlosen Kommandozeilen-Tools:

- ffmpeg.exe
- ffplay.exe
- ffprobe.exe

Empfohlene Downloadquelle:
https://github.com/BtbN/FFmpeg-Builds/releases

Für Windows empfehlen sich die "essentials" oder "full" Builds.
Halte Ausschau nach einer Datei wie:

ffmpeg-master-latest-win64-gpl.zip

Entpacke das Archiv anschließend an einen beliebigen Ort auf Deinem Computer.


2. Programm starten und FFmpeg-Pfad festlegen

- Starte AudioNormalizer.exe
- Öffne im Menü: Datei -> Optionen
- Wähle den Ordner aus, der ffmpeg.exe, ffplay.exe und ffprobe.exe enthält

Wichtig:
Ohne korrekt gesetzten FFmpeg-Pfad kann das Programm nicht arbeiten.


3. Audiodateien normalisieren

- Nutze "Dateien hinzufügen" oder "Ordner hinzufügen"
- Stelle rechts Dein gewünschtes LUFS-Preset ein
- Wähle das Ausgabeformat
- Klicke auf "Normalisierung starten"

Der Fortschritt der Stapelverarbeitung wird live angezeigt.
Die fertigen Dateien werden automatisch erstellt.


4. Audio-Vorschau

- Datei in der Liste markieren
- Den "Play"-Button drücken

Mit den Buttons "Zurück" und "Weiter" kannst Du wie in einer Playlist durch Deine Dateiliste springen.


5. Optionen und Einstellungen

Unter:
Datei -> Optionen

kannst Du:

- den FFmpeg-Pfad ändern
- die Programmsprache wechseln
- das App-Theme wechseln
- Logdatei-Einstellungen anpassen
- die automatische Update-Prüfung ein- oder ausschalten
- optional Vorabversionen einbeziehen

Die Update-Prüfung zeigt nur einen Hinweis und einen Link zur passenden GitHub-Veröffentlichung an. Updates werden niemals automatisch heruntergeladen oder installiert. Eine manuelle Prüfung findest Du unter Info -> Nach Updates suchen.


========================================
MASTERING-CHARAKTER-PRESETS
========================================

Transparent
Nur Lautheitsnormalisierung ohne zusätzliche Klangbearbeitung.

Kohäsiv
Sanfte Breitbandkompression mit subtiler Softclip-Kante für mehr Zusammenhalt.

Punchy
Mehr Präsenz und Druck durch stärkere Kompression.

Aggressiv
Die intensivste Variante für harte, dichte oder aggressive Produktionen.


========================================
WICHTIGE HINWEISE
========================================

FFmpeg-Pfad
Der Pfad zu ffmpeg.exe, ffplay.exe und ffprobe.exe muss korrekt gesetzt sein.

ffprobe.exe
Diese Datei wird für die Zeitanzeige im Audio-Player verwendet.
Fehlt sie, funktioniert die Wiedergabe trotzdem - jedoch ohne Zeitdarstellung.

LUFS-Presets
Die Presets helfen Dir bei der Auswahl geeigneter Lautheitswerte für verschiedene Plattformen.
Eigene Werte können selbstverständlich ebenfalls verwendet werden.

Ausgabeformat
Die Info-Box unter der Formatauswahl zeigt technische Details zum aktuell gewählten Ausgabeformat.


========================================
LIZENZ
========================================

Diese Software ist Open-Source und steht unter der MIT-Lizenz.
Weitere Informationen findest Du in der Datei:

LICENSE


Viel Spaß mit melcom's FFmpeg Audio Normalizer!

Mit freundlichen Grüßen
melcom
