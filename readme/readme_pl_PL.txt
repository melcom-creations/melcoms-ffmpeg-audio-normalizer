melcom's FFmpeg Audio Normalizer v4.1.2 - Herbstklang Edition

Wyniki analizy
--------------

Użyj Tylko analizuj, aby zmierzyć pliki z kolejki bez zmiany ani kodowania dźwięku. Raport otwiera się automatycznie po zakończeniu i można go otworzyć ponownie przyciskiem "Wyniki analizy...". Lista pokazuje głośność, True Peak, zakres głośności (LRA) i PLR oraz dodatkowe pomiary dla każdego pliku. Cele wybrane przy rozpoczęciu analizy służą wyłącznie do porównania; różnice nie przewidują wyniku normalizacji. Można skopiować jeden wynik lub wszystkie wyniki oraz wyeksportować cały raport jako CSV. Raporty analizy i normalizacji są przechowywane oddzielnie w tej sesji. Nowe uruchomienie zastępuje tylko raport tego samego rodzaju. Brak pomiaru, błędy i anulowanie są oznaczone osobno. Po błędzie pliku analiza jest kontynuowana dla pozostałych plików. Anulowanie zachowuje zebrane wyniki.

Sprawdzanie plików wyjściowych i wyniki
---------------------------------------

Wyniki normalizacji również umożliwiają kopiowanie jednego lub wszystkich wyników i eksport CSV z oryginałem, celem, zmierzonym wynikiem, stanem, trybem przetwarzania i szczegółami kodowania.

Po zakończeniu analizy lub normalizacji odpowiednie okno wyników otwiera się automatycznie. Najedź myszą na przycisk wyników, aby zobaczyć wyjaśnienie, także gdy przycisk jest nieaktywny. Po anulowaniu zebrane wyniki pozostają dostępne przez odpowiedni przycisk.

Zakres głośności (LRA) opisuje zmienność głośności w czasie. Sample Peak to najwyższy poziom próbki cyfrowej; True Peak uwzględnia także szacowane szczyty między próbkami. Offset DC to składowa stała sygnału.

Głośność w tabelach wyników oznacza głośność zintegrowaną całego pliku, mierzoną w LUFS. Względny próg bramkowania to względny próg pomiaru głośności podawany przez FFmpeg, a nie próg kompresora ani bramka szumów w torze audio. Min. / maks. wartość próbki oznacza wartości próbek ze znakiem, a nie poziomy w dBFS. Współczynnik szczytu porównuje Sample Peak z RMS, a PLR porównuje True Peak z głośnością zintegrowaną. LRA opisuje zmienność głośności i nie jest zamiennikiem żadnego z tych współczynników. Zmierzona głębia bitowa opisuje zdekodowane próbki, a nie głębię bitową formatu pliku.

PLR (Peak-to-Loudness Ratio)
PLR to różnica między maksymalnym poziomem True Peak a głośnością zintegrowaną tego samego pliku. Wartość w LU uzupełnia LRA i współczynnik szczytu. Jest obliczana z istniejącej analizy bez dodatkowego pomiaru. Brakujące lub nieskończone wartości są wyświetlane jako N/A; sam PLR nie ocenia jakości dźwięku.

Układ okna
Przeciągnij poziomy separator nad dziennikiem, aby zmienić jego wysokość. Pionowy separator między plikami a ustawieniami zmienia ich szerokość. Przy mniejszej ilości miejsca ustawienia można przewijać. Przyciski przetwarzania pozostają widoczne pod obszarami roboczymi.

Rozmiar okna, położenie separatorów i stan maksymalizacji są automatycznie zapisywane w sekcji Layout pliku options.ini i przywracane przy następnym uruchomieniu. Plik - Przywróć domyślny układ okna przywraca układ wbudowany. Układ jest niezależny od profili audio i zachowywany przy zmianie formatu wyjściowego, języka lub motywu.

MP3 i M4A domyślnie używają teraz jawnie 320 kbps CBR, niezależnie od przepływności źródła. MP3 używa jakości algorytmu LAME 0. VBR włącza się tylko przez wybór poziomu jakości VBR; M4A oferuje q2 i q1. OGG/Vorbis domyślnie używa 320 kbps ABR, czyli średniej przepływności docelowej, a nie ścisłego CBR. Poziomy jakości VBR pozostają osobnymi opcjami. Starsze profile stratne z Oryginalny / Domyślny wczytują nową wartość domyślną formatu; dawna opcja Vorbis 320 kbps (CBR) jest wczytywana jako 320 kbps (ABR). Profile zapisują jawny wybór jakości. Pomoc pod specyfikacją wyjaśnia headroom kodera i dopasowuje zawijanie tekstu do szerokości panelu. Wyniki i schowek zawierają wybrane ustawienie kodowania.

"Headroom kodera (dB)" rezerwuje od 0 do 3 dB przed kodowaniem MP3, M4A lub OGG na szczyty, które mogą powstać przy kodowaniu stratnym. Wewnętrzny limit True Peak jest obniżany o ustawioną wartość, nie niżej niż do minimalnego poziomu -9 dBTP obsługiwanego przez FFmpeg. Cel głośności i końcowy docelowy limit True Peak pozostają bez zmian. Wartość 0 wyłącza dodatkowy zapas. Ustawienie jest dostępne w sekcji Format wyjściowy i zapisywane w profilach. Starsze profile używają wartości domyślnej 0. WAV i FLAC ignorują to ustawienie. Wyniki i schowek pokazują żądany i zastosowany zapas. Weryfikacja porównuje gotowy zakodowany plik z wybranymi celami bez zmieniania pliku.

Włącz "Sprawdzaj pliki wyjściowe" przed normalizacją, aby zmierzyć gotowe, zakodowane pliki. Opcja jest domyślnie wyłączona i wymaga dodatkowego czasu analizy. Plik - Opcje zapisuje ustawienie domyślne; profile mogą zapisać wybór. Starsze profile są wczytywane ze sprawdzaniem wyłączonym.

Po przetwarzaniu otwórz "Wyniki...", aby porównać oryginał, cel i zmierzony wynik. Wyniki dotyczą ostatniej partii normalizacji i pozostają w pamięci do rozpoczęcia kolejnej partii lub zamknięcia programu. Wybrany wynik można skopiować.

Utworzenie pliku i jego sprawdzenie mają osobne stany. Błąd lub anulowanie sprawdzania nie usuwa poprawnie utworzonego pliku. Tolerancja głośności wynosi +/- 0,2 LU; True Peak może przekroczyć wybrany limit najwyżej o 0,1 dB, aby kontrola zakończyła się pomyślnie. LRA jest wyświetlane bez oceny względem celu. Są to tolerancje aplikacji, a nie certyfikacja.

Najpierw mierzy sygnał, a potem żąda stałej zmiany poziomu. FFmpeg może przejść do trybu dynamicznego, jeśli limity True Peak lub zakresu głośności (LRA) uniemożliwiają przetwarzanie liniowe. Preset masteringowy przetwarza dźwięk przed normalizacją i może zmienić dynamikę nawet wtedy, gdy FFmpeg zgłasza tryb liniowy. Gdy nie można zmierzyć głośności, w trybie dwuprzebiegowym regulacja głośności jest pomijana i nie można potwierdzić zgodności z celem. Dotyczy to na przykład ciszy i bardzo krótkich plików.

Liczba przebiegów dotyczy normalizacji. Weryfikacja dodaje pomiar zakodowanego pliku; mastering może też wymagać osobnego pomiaru oryginału.

Poprawne cele to od -70 do -5 LUFS oraz od -9 do 0 dBTP. Oryginalny / Domyślny zachowuje obsługiwane głębie bitowe WAV, w tym 64-bitowy float. Gdy bitrate źródła nie pasuje do kodeka wyjściowego, używane są jego ustawienia domyślne. Konflikty ścieżek wyjściowych są odrzucane przed przetwarzaniem.

Normalizacja audio open source z użyciem FFmpeg oraz obsługą LUFS i True Peak.

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
- Kliknij przycisk "Odtwórz"

Przyciski "Poprzedni" oraz "Następny" pozwalają poruszać się po liście plików jak po playliście.


5. Opcje i ustawienia

W menu:
Plik -> Opcje

możesz:

- zmienić ścieżkę FFmpeg
- wybrać język programu
- zmienić motyw aplikacji
- skonfigurować ustawienia plików logów
- włączyć lub wyłączyć automatyczne sprawdzanie aktualizacji
- opcjonalnie uwzględnić wersje przedpremierowe

Mechanizm aktualizacji wyświetla tylko powiadomienie i link do odpowiedniej wersji w serwisie GitHub. Nigdy nie pobiera ani nie instaluje aktualizacji automatycznie. Ręczne sprawdzanie jest dostępne w menu Info -> Sprawdź aktualizacje.


========================================
PRESETY CHARAKTERU MASTERINGU
========================================

Nazwy te opisują zamierzony charakter brzmienia, a nie znormalizowane wielkości pomiarowe. Efekt zależy od materiału źródłowego. Kompresja i miękkie obcinanie szczytów działają przed normalizacją głośności i mogą zmieniać zarówno atak i gęstość brzmienia, jak i poziom szczytów.

Transparentny
Normalizacja głośności bez dodatkowych filtrów masteringowych. Normalizacja dynamiczna nadal może zmienić dynamikę.

Spójny
Delikatna kompresja i miękkie obcinanie szczytów dla większej spójności miksu. Może ograniczyć dynamikę także w trybie liniowym.

Punchy
Kompresja i miękkie obcinanie szczytów dla mocniejszego uderzenia i większej wyrazistości. Może zmienić transjenty i dynamikę także w trybie liniowym.

Agresywny
Silniejsza kompresja i miękkie obcinanie szczytów dla gęstszego brzmienia. Może ograniczyć dynamikę także w trybie liniowym.


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

LICENSE


Miłego korzystania z melcom's FFmpeg Audio Normalizer!

Pozdrawiam
melcom
