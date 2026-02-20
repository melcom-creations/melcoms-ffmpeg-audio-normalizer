**melcom's FFmpeg Audio Normalizer v3.1.0 (Feierabend Edition)**

Mit diesem Programm kannst Du die Lautstärke Deiner Audiodateien, einzeln oder stapelweise, professionell mit FFmpeg normalisieren. Die normalisierten Dateien werden automatisch im gleichen Ordner wie die Originaldateien gespeichert.

**Kurzanleitung für Dich:**

1. **FFmpeg-Suite installieren:**
   - Für dieses Programm benötigst Du die kostenlosen Kommandozeilen-Tools `ffmpeg.exe`, `ffplay.exe` und `ffprobe.exe`.
   - Lade die Tools von einer vertrauenswürdigen Webseite herunter. Wir empfehlen die Builds von https://github.com/BtbN/FFmpeg-Builds/releases (z.B. `ffmpeg-master-latest-win64-gpl.zip`).
   - Entpacke das Archiv und stelle sicher, dass der Pfad zum `bin`-Ordner in den Programm-Optionen hinterlegt ist.

2. **Programm starten und einrichten:**
   - Starte `AudioNormalizer.exe`.
   - Gehe zu "Datei" -> "Optionen" und gib den Pfad zu Deinem FFmpeg-Ordner an.

3. **Audiodateien normalisieren (Neu in v3.1):**
   - Füge Dateien oder ganze Ordner zur Liste hinzu.
   - Wähle rechts Dein LUFS- und True-Peak-Preset.
   - **Wähle den Modus:** 
     - *Linear (2 Durchgänge):* Empfohlen für Musik. Erhält die volle Dynamik.
     - *Dynamisch (1 Durchgang):* Empfohlen für Sprache/Radio. Passt die Lautstärke live an.
   - Wähle das Ausgabeformat und klicke auf "Normalisierung starten".

4. **Audio-Vorschau:**
   - Nutze den integrierten Player unter der Liste, um Titel vorzuhören und durch Deine Playlist zu navigieren.

**Wichtige Highlights & Hinweise für Dich:**

*   **Höchste Qualität:** Bei der Ausgabe als WAV oder FLAC behält das Programm automatisch die originale Samplerate (z.B. 96 kHz) und Bit-Tiefe (z.B. 24-Bit) der Quelldatei bei.
*   **Metadaten:** Deine Tags (Interpret, Titel, Album etc.) bleiben erhalten und werden in die neue Datei übernommen. MP3s nutzen den ID3v2.3 Standard für beste Kompatibilität.
*   **Linearer Modus:** Der neue 2-Pass-Modus (Linear) sorgt für echtes Mastering-Niveau, indem er die Datei erst analysiert und dann perfekt pegelt, ohne die Dynamik zu verändern.
*   **Automatisches Cleanup:** Das Programm löscht temporäre Arbeitsdateien (`.temp`) automatisch, auch wenn ein Vorgang abgebrochen wird.
*   **FFmpeg-Pfad:** Ohne den korrekten Pfad zu `ffmpeg.exe`, `ffplay.exe` und `ffprobe.exe` in den Optionen kann das Programm nicht arbeiten.

Diese Software ist Open-Source (MIT Lizenz). Siehe `LICENSE.txt` für Details.

Viel Spaß mit der Feierabend Edition!

Mit freundlichen Grüßen,
melcom