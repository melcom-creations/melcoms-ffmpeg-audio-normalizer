**melcom's FFmpeg Audio Normalizer v3.0.0 (Halloween Edition)**

Mit diesem Programm kannst Du die Lautstärke Deiner Audiodateien, einzeln oder stapelweise, einfach mit FFmpeg normalisieren.
Die normalisierten Dateien werden automatisch im gleichen Ordner wie die Originaldateien gespeichert.

**Kurzanleitung für Dich:**

1. **FFmpeg-Suite installieren:**
   - Für dieses Programm benötigst Du die kostenlosen Kommandozeilen-Tools `ffmpeg.exe`, `ffplay.exe` und `ffprobe.exe`.
   - Lade die Tools von einer vertrauenswürdigen Webseite herunter. Für Windows-Nutzer empfehlen wir die "essentials" oder "full" Builds von https://github.com/BtbN/FFmpeg-Builds/releases. Halte Ausschau nach einer Datei wie `ffmpeg-master-latest-win64-gpl.zip`.
   - Entpacke das Archiv und platziere den Ordner, der die `.exe`-Dateien enthält, auf Deinem Computer.

2. **Programm starten und FFmpeg-Pfad angeben:**
   - Starte `AudioNormalizer.exe`.
   - Gehe im Programm zu "Datei" -> "Optionen".
   - Gib unter "FFmpeg Pfad" den Ordner an, in dem sich `ffmpeg.exe`, `ffplay.exe` und `ffprobe.exe` befinden. Dies ist entscheidend, damit das Programm funktioniert.

3. **Audiodateien normalisieren:**
   - Nutze im Hauptfenster die "Dateien hinzufügen" oder "Ordner hinzufügen" Buttons, um eine Liste der zu verarbeitenden Audiodateien zu erstellen.
   - Passe rechts die "LUFS Preset"- und "Ausgabeformat"-Einstellungen an Deine Bedürfnisse an.
   - Klicke auf "Normalisierung starten".
   - Der Fortschritt der gesamten Stapelverarbeitung wird angezeigt, und die normalisierten Dateien werden automatisch erstellt.

4. **Audio-Vorschau:**
   - Um eine Datei vorzuhören, klicke sie in der Liste an und drücke den "▶" (Play) Button.
   - Mit den "«" und "»" Buttons kannst Du wie in einer Playlist durch Deine Dateiliste navigieren.

5. **Optionen (Einstellungen):**
   - Im Menü "Datei" -> "Optionen" kannst Du den Pfad zu FFmpeg ändern, die Programmsprache auswählen und Logdatei-Einstellungen anpassen.

**Wichtige Hinweise für Dich:**

* **FFmpeg-Suite Pfad:** Stelle sicher, dass der Pfad zum Ordner mit `ffmpeg.exe`, `ffplay.exe` und `ffprobe.exe` in den Optionen korrekt ist, sonst funktioniert das Programm nicht.
*   **`ffprobe.exe`:** Diese Datei wird für die Zeitanzeige im Audio-Player benötigt. Wenn sie fehlt, funktioniert die Wiedergabe trotzdem, aber ohne Zeitanzeige.
* **LUFS Presets:** Die Voreinstellungen helfen Dir, die richtige Lautstärke für verschiedene Plattformen zu wählen. Du kannst aber auch eigene Werte eingeben.
* **Ausgabeformat:** Die Info-Box unter der Formatauswahl gibt Dir Details zu den technischen Spezifikationen der Ausgabedatei.

Diese Software ist Open-Source (MIT Lizenz). Siehe `LICENSE.txt` für Details.

Viel Spaß mit dem Programm!

Mit freundlichen Grüßen,
melcom