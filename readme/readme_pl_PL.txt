melcom's FFmpeg Audio Normalizer v4.0.2 - Läderlappen Edition 🦇

Open-source'owa normalizacja audio z użyciem FFmpeg oraz obsługą LUFS i True Peak.

Za pomocą tego programu możesz łatwo normalizować głośność swoich plików audio - pojedynczo lub wsadowo - przy użyciu FFmpeg. Przetworzone pliki są automatycznie zapisywane w tym samym folderze co oryginały.


========================================
SZYBKI START
========================================

1. Zainstaluj pakiet FFmpeg

Program wymaga następujących darmowych narzędzi wiersza poleceń:

- ffmpeg.exe
- ffplay.exe
- ffprobe.exe

Polecane źródło pobrania:
https://github.com/BtbN/FFmpeg-Builds/releases

Dla użytkowników Windows zalecane są wersje "essentials" lub "full".
Szukaj pliku podobnego do:

ffmpeg-master-latest-win64-gpl.zip

Rozpakuj archiwum w dowolnym miejscu na komputerze.


2. Uruchom program i ustaw ścieżkę FFmpeg

- Uruchom AudioNormalizer.exe
- Otwórz: Plik -> Opcje
- Wskaż folder zawierający ffmpeg.exe, ffplay.exe oraz ffprobe.exe

Ważne:
Bez poprawnie ustawionej ścieżki FFmpeg program nie będzie działał prawidłowo.


3. Normalizacja plików audio

- Użyj przycisków "Dodaj pliki" lub "Dodaj folder"
- Wybierz odpowiedni preset LUFS
- Wybierz format wyjściowy
- Kliknij "Rozpocznij normalizację"

Postęp przetwarzania wsadowego jest wyświetlany na bieżąco.
Znormalizowane pliki zostaną utworzone automatycznie.


4. Podgląd audio

- Wybierz plik z listy
- Kliknij przycisk "▶"

Przyciski "«" oraz "»" pozwalają poruszać się po liście plików jak po playliście.


5. Opcje i ustawienia

W menu:
Plik -> Opcje

możesz:

- zmienić ścieżkę FFmpeg
- wybrać język programu
- zmienić motyw aplikacji
- skonfigurować ustawienia plików logów


========================================
PRESETY CHARAKTERU MASTERINGU
========================================

Transparent
Wykonuje wyłącznie normalizację głośności bez dodatkowego kształtowania brzmienia.

Cohesive
Dodaje delikatną kompresję szerokopasmową oraz subtelny softclip dla bardziej spójnego miksu.

Punchy
Zwiększa obecność i energię dzięki mocniejszej kompresji.

Aggressive
Najmocniejszy preset przeznaczony dla gęstego i agresywnego materiału.


========================================
WAŻNE INFORMACJE
========================================

Ścieżka FFmpeg
Upewnij się, że ścieżka do ffmpeg.exe, ffplay.exe oraz ffprobe.exe została ustawiona poprawnie.

ffprobe.exe
Ten plik odpowiada za wyświetlanie czasu odtwarzania w odtwarzaczu audio.
Bez niego odtwarzanie nadal będzie działać, ale bez informacji o długości utworu.

Presety LUFS
Presety pomagają dobrać odpowiedni poziom głośności dla różnych platform.
Możesz również ręcznie wpisać własne wartości.

Format wyjściowy
Pole informacyjne pod wyborem formatu pokazuje techniczne szczegóły aktualnie wybranego formatu wyjściowego.


========================================
LICENCJA
========================================

To oprogramowanie jest Open-Source i korzysta z licencji MIT.
Więcej informacji znajdziesz w pliku:

LICENSE.txt


Miłego korzystania z melcom's FFmpeg Audio Normalizer!

Pozdrawiam
melcom