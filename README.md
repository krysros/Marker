# Marker

## O aplikacji

Aplikacja dla Generalnych Wykonawców usprawniającą proces ofertowania oraz kontraktowania realizacji przedsięwzięć budowlanych, analizy rynku materiałów i usług oraz projektów i inwestycji. Stanowi bazę wiedzy (ang. knowledge base) i narzędzie do raportowania w analityce biznesowej (ang. Business Intelligence).

### Przeznaczenie

- Obsługa informacji o firmach i projektach oraz relacjach pomiędzy nimi
- Zwiększenie wydajności i skuteczności ofertowania
- Zmniejszenie progu wejścia dla nowych pracowników
- Automatyzacja procesu generowania dokumentów (m.in. wzorów umów w formacie docx) na podstawie szablonów
- Analiza rynku

### Co wyróżnia aplikację?

- Dostęp do danych mają tylko zalogowani użytkownicy zgodnie z uprawnieniami nadanymi przez administratora
- Dane nie są wyłącznie zbiorem rekordów, lecz odzwierciedlają dotychczasową działalność
- Eksportowanie danych do Excela w formie umożliwiającej skorzystanie z korespondencji seryjnej i tabel przestawnych
- Wizytówki vCard (błyskawiczny kontakt z poziomu smartfona, ustandaryzowany format wymiany danych kontaktowych)
- Podpowiadanie firm o podobnym profilu działalności do aktualnie wyświetlanej firmy
- Dostęp do interesujących danych bez znajomości SQL i VBA

### Dlaczego Marker?

Nazwa Marker pochodzi od angielskiego czasownika *mark*. Jedną z podstawowych funkcjonalności aplikacji jest możliwość zaznaczania, rekomendowania lub obserwowania przez użytkowników wybranych pozycji. Dzięki temu z gąszczu danych można w szybki sposób wybrać te najbardziej interesujące, np. firmy z wybranej branży posortowane wg liczby rekomendacji. Dodatkowo firmy można przypisywać do kategorii oznaczonych kolorami, np. kategoria czerwona możne oznaczać firmy znajdujące się na *czarnej liście*, a  pomarańczowa firmy konkurencyjne.

### Dlaczego nie Excel?

Do przedstawienia wyżej wymienionych relacji najlepszym rozwiązaniem jest relacyjna baza danych. Swoboda umieszczania danych w skoroszycie Excela oraz ich formatowania w dowolny sposób często skutkuje tym, że w krótkim czasie zasoby stają się nieczytelne i trudno wydobyć z nich interesujące informacje. Szczególnie jeśli arkusze uzupełniane są przez różne osoby.
Marker dba o to, aby wprowadzane dane były kompletne i poprawne, a dostęp do nich łatwy i szybki. Aplikacja przeprowadza walidację danych (m.in. adresów email, numerów NIP i REGON). Sprawdza czy wymagane pola zostały wypełnione oraz czy format danych jest prawidłowy. W razie potrzeby dokonuje korekty przed zapisem.

## Wybrane możliwości i interfejs użytkownika

Aktualnie dostępne moduły:
- Firmy
- Projekty
- Tagi
- Użytkownicy
- Komentarze
- Raporty

Głównym założeniem jest intuicyjność obsługi i szybkość dostępu do interesujących danych. Aplikację i interfejs zrealizowano przy zastosowaniu reguł KISS i DRY.

## Pod maską

Aplikacja została napisana od zera w języku programowania Python 3. Interfejs graficzny aplikacji korzysta z biblioteki Bootstrap, wszystkie formularze generowane są przez bibliotekę WTForms, a szablony przez bibliotekę mako, zgodnie z filozofią: *Python is a great scripting language. Don't reinvent the wheel...your templates can handle it!* Interaktywność zapewnia htmx. Zapytania do bazy danych realizowane są przez SQLAlchemy ORM.

W rezultacie w kodzie źródłowym aplikacji wykorzystywany jest wyłącznie język Python i HTML (nie występuje np. JavaScript i SQL). Umożliwia to prostą budowę aplikacji, łatwe jej utrzymanie i testowanie, zmianę silnika bazodanowego bez modyfikacji kodu oraz szybkie dodawanie nowych możliwości.

### Back-end

- Framework Pyramid
- Baza danych współpracująca z SQLAlchemy

### Front-end

- Bootstrap
- htmx