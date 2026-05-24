melcom's FFmpeg Audio Normalizer v3.2.0 - Nachtschicht Edition

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
- Den "▶" Button drücken

Mit den "«" und "»" Buttons kannst Du wie in einer Playlist durch Deine Dateiliste springen.


5. Optionen und Einstellungen

Unter:
Datei -> Optionen

kannst Du:

- den FFmpeg-Pfad ändern
- die Programmsprache wechseln
- Logdatei-Einstellungen anpassen


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
Die intensivste Variante für dichtes und kantiges Material.


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

LICENSE.txt


Viel Spaß mit melcom's FFmpeg Audio Normalizer!

Mit freundlichen Grüßen
melcom