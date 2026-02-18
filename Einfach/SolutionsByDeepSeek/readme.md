DeepSeek Antworten sind sind meistens (codeweise) deutlich länger als ChatGPT Antworten (ca. 374 Zeilen).
Der Code ist dafür meistens nicht beim initialen erstellen benutzbar in 7/13 (53.8%) ist kein compilieren möglich.
Weiterhin ist in keinem der 6/13 übrigen Testprompts ein verwendbarer Code initial herausgekommen.
Im Sonderfall V13DNS (Prompt V13 und Aktiviertes "Search" und "Deep Think") kam nach ~2 minütigem (118 Sekunden) Denken ein brauchbares Ergebnis geliefert. 
Jedoch wurde hier, sowie in 2/13 (Total: 3/14 21.4%) der Versionen externen extra zu installierende nicht-standard Imports (Dazu zählt: numpy und PIL) verwendet.
Weiterhin hat Deepseek trotz des Versuchs mit Promptänderungen die Sprachwahl zu beeinflussen, zu 11/13 (84.6%) der Zeit für Python und 2/13 (15.4%) für C++ entschieden.


Länge von DeepSeek Code (Zeilen)

    | Version | Lines |
    |---------|-------|
    |   V1    |  373  |
    |   V2    |  425  |
    |   V3    |  375  |
    |   V4    |  321  |
    |   V5    |  432  |
    |   V6    |  282  |
    |   V7    |  353  |
    |   V8    |  475  |
    |   V9    |  337  |
    |   V10   |  379  |
    |   V11   |  408  |
    |   V12   |  382  |
    |   V13   |  325  |
| **Total**   | **4867**  |
| **Average** | **374.4** |
