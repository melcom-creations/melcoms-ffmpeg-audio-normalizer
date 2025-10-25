**melcom's FFmpeg Audio Normalizer v3.0.0 (Halloween Edition)**

Za pomocą tego programu możesz łatwo normalizować głośność swoich plików audio, pojedynczo lub w partiach, używając FFmpeg.
Znormalizowane pliki są automatycznie zapisywane w tym samym folderze, co pliki oryginalne.

**Szybki przewodnik dla Ciebie:**

1. **Zainstaluj pakiet FFmpeg:**
   - Ten program wymaga darmowych narzędzi wiersza poleceń: `ffmpeg.exe`, `ffplay.exe` i `ffprobe.exe`.
   - Pobierz narzędzia z zaufanej strony internetowej. Dla użytkowników systemu Windows polecamy kompilacje "essentials" lub "full" ze strony https://github.com/BtbN/FFmpeg-Builds/releases. Szukaj pliku o nazwie `ffmpeg-master-latest-win64-gpl.zip`.
   - Rozpakuj archiwum i umieść folder zawierający pliki `.exe` na swoim komputerze.

2. **Uruchom program i ustaw ścieżkę FFmpeg:**
   - Uruchom `AudioNormalizer.exe`.
   - W programie przejdź do "Plik" -> "Opcje".
   - W polu "Ścieżka FFmpeg" wskaż folder, w którym znajdują się `ffmpeg.exe`, `ffplay.exe` i `ffprobe.exe`. Jest to kluczowe do działania programu.

3. **Znormalizuj swoje pliki audio:**
   - W oknie głównym użyj przycisków "Dodaj pliki" lub "Dodaj folder", aby stworzyć listę plików audio do przetworzenia.
   - Dostosuj "Preset LUFS" i "Format wyjściowy" po prawej stronie do swoich potrzeb.
   - Kliknij "Start Normalizacji".
   - Postęp całego procesu wsadowego będzie wyświetlany, a znormalizowane pliki zostaną utworzone automatycznie.

4. **Podgląd audio:**
   - Aby odsłuchać plik, po prostu kliknij go na liście i naciśnij przycisk "▶" (Odtwarzaj).
   - Użyj przycisków "«" i "»", aby nawigować po liście plików jak po playliście.

5. **Opcje (Ustawienia):**
   - W menu "Plik" -> "Opcje" możesz zmienić ścieżkę do FFmpeg, wybrać język programu i dostosować ustawienia pliku logu.

**Ważne Wskazówki dla Ciebie:**

* **Ścieżka pakietu FFmpeg:** Upewnij się, że ścieżka do folderu zawierającego `ffmpeg.exe`, `ffplay.exe` i `ffprobe.exe` jest poprawnie ustawiona w opcjach, w przeciwnym razie program nie będzie działać.
*   **`ffprobe.exe`:** Ten plik jest wymagany do wyświetlania czasu w odtwarzaczu audio. Jeśli go brakuje, odtwarzanie nadal będzie działać, ale bez informacji o czasie.
* **Presety LUFS:** Presety pomagają wybrać odpowiednią głośność dla różnych platform (np. YouTube, Spotify). Możesz także wprowadzić własne wartości.
* **Format wyjściowy:** Pole informacyjne pod wyborem formatu dostarcza szczegółów na temat specyfikacji technicznych pliku wyjściowego.

To oprogramowanie jest Open-Source (Licencja MIT). Zobacz `LICENSE.txt` po szczegóły.

Miłej zabawy z programem!

Z poważaniem,
melcom