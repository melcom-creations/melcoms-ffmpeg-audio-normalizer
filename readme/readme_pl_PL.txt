**melcom's FFmpeg Audio Normalizer v3.1.0 (Feierabend Edition)**

Za pomocą tego programu możesz profesjonalnie normalizować głośność swoich plików audio, pojedynczo lub wsadowo, używając FFmpeg. Znormalizowane pliki są automatycznie zapisywane w tym samym folderze, co pliki źródłowe.

**Szybki przewodnik dla Ciebie:**

1. **Zainstaluj pakiet FFmpeg:**
   - Ten program wymaga darmowych narzędzi wiersza poleceń: `ffmpeg.exe`, `ffplay.exe` i `ffprobe.exe`.
   - Pobierz narzędzia z zaufanej strony internetowej. Polecamy kompilacje ze strony https://github.com/BtbN/FFmpeg-Builds/releases (np. `ffmpeg-master-latest-win64-gpl.zip`).
   - Rozpakuj archiwum i upewnij się, że ścieżka do folderu `bin` jest poprawnie ustawiona w opcjach programu.

2. **Uruchom program i skonfiguruj:**
   - Uruchom `AudioNormalizer.exe`.
   - Przejdź do "Plik" -> "Opcje" i wskaż folder zawierający pliki wykonywalne FFmpeg.

3. **Znormalizuj swoje pliki audio (Nowość w v3.1):**
   - Dodaj pliki lub całe foldery do listy przetwarzania.
   - Po prawej stronie wybierz presety LUFS i True Peak.
   - **Wybierz tryb:** 
     - *Liniowy (2 przebiegi):* Zalecany dla muzyki. Zachowuje pełny zakres dynamiki.
     - *Dynamiczny (1 przebieg):* Zalecany dla mowy/radia. Dostosowuje głośność na bieżąco.
   - Wybierz format wyjściowy i kliknij "Start Normalizacji".

4. **Podgląd audio:**
   - Użyj zintegrowanego odtwarzacza pod listą, aby odsłuchać utwory i nawigować po swojej playliście.

**Ważne Highlights i Wskazówki dla Ciebie:**

*   **Najwyższa jakość:** Przy eksporcie do WAV lub FLAC program automatycznie zachowuje oryginalną częstotliwość próbkowania (np. 96 kHz) i głębię bitową (np. 24-bit) pliku źródłowego. Brak niepotrzebnego downsamplingu.
*   **Metadane:** Twoje tagi (Artysta, Tytuł, Album itp.) są zachowywane i przenoszone do nowego pliku. Pliki MP3 korzystają ze standardu ID3v2.3 dla najlepszej kompatybilności z systemem Windows i odtwarzaczami zewnętrznymi.
*   **Tryb Liniowy:** Nowy tryb 2-przebiegowy zapewnia precyzję na poziomie masteringu, najpierw analizując plik, a następnie idealnie go peglując bez niszczenia dynamiki.
*   **Automatyczne czyszczenie:** Program automatycznie usuwa tymczasowe pliki robocze (`.temp`), nawet jeśli proces zostanie przerwany lub wystąpi błąd.
*   **Ścieżka FFmpeg:** Program nie może funkcjonować bez poprawnej ścieżki do plików `ffmpeg.exe`, `ffplay.exe` i `ffprobe.exe` w Opcjach.

To oprogramowanie jest Open-Source (Licencja MIT). Zobacz `LICENSE.txt` po szczegóły.

Miłego korzystania z Feierabend Edition!

Z poważaniem,
melcom