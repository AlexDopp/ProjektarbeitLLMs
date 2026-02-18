ChatGPT hat sich 6/13 (46.2%) der Zeit für C++ und 7/13 (53.8%) für Python entschieden. Versuche auf Java zu lenken (ohne Zwang) liefen leer aus.
Bei 1/13 (7.7%) Versionen ist zur Initialerstellung ein "perfektes" oder gewolltes Ergebnis erstellt worden. 
Dieses gelang bei Version 4 in C++ (siehe Endergebnis "/Pictures/V4Box.ppm").
Das Am meisten Verbreiteteste Problem bereitete der Promptteil der Schattenerstellung. 
8/13 (61.5%) der Versionen (V: 2, 3, 5, 6, 8, 9, 10, 13) haben den gleichen Fehler. 
2/13 (15.4%) haben das Problem auch, haben aber Ambient Light (unaufgefordert) im Code hinzugefügt und damit das komplett schwarze Output File vermieden.
Somit haben 10/13 (76.9%) das selbe Problem. Dieses ist, dass bei der Schattenberechnung Wände ("Plane"s in den meisten Versionen) als Intersectobjekte gezählt werden. Dies führt dazu, dass die Wand hinter, sowie jede andere, als Schattenkriterium gewertet werden. Damit wird der komplette Output Schwarz (außer Ambient Light erhellt nachträglich).
In Version 11 (1/13 7.7%) ist das Compilieren fehlgeschlagen, da eine define Zeile für M_PI vergessen wurde. Nach Lösen dieses Problems ist es eines der besten Ergebnisse (zu finden in Einfach/Edits/GPT/Dark/V11/cornellbox.ppm).
2/13 (15.4%) haben als Output Filetype .png gewählt. Der Rest 11/13 (84.6%) haben .ppm gewählt. Dies liegt wahrscheinlich daran, dass im Prompt dieser (V10-V13) ein "(z.B. Cornellbox)" benutzt wurde.

Bei der Fehlerbehebung mit ChatGPT des eigenen Fehlers im Code von Version 2, konnte ChatGPT den Hauptfehler (Schatten-Ray) immer erkennen.
Hierbei war es egal wie genau die Fehlerquelle eingegrenzt wurde. Alleine das Endergebnis des Fehlers (Schwarze Output File) hat gereicht um ChatGPT auf die korrekte Fehlerbehebung zu bringen. Sobald auch nur die konkrete Klasse des Fehlers genannt wurde hat ChatGPT auch den Fehler gefunden, der speziell bei der 2. Version zum Kompilierabbruch führt (Die Negation eines Vec3 ist undefiniert). Weitere Präzision führt zu keiner Verbesserung des Codes oder der Antwort.

Länge von ChatGPT Code (Zeilen)

    | Version | Lines |
    |---------|-------|
    |   V1    |  199  |
    |   V2    |  261  |
    |   V3    |  272  |
    |   V4    |  239  |
    |   V5    |  163  |
    |   V6    |  127  |
    |   V7    |  209  |
    |   V8    |  196  |
    |   V9    |  213  |
    |   V10   |  215  |
    |   V11   |  267  |
    |   V12   |  226  |
    |   V13   |  213  |
| **Total**   | **2800**  |
| **Average** | **215.4** |