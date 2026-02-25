**Fragestellung und Vorgehen:**

Kann eine LLM einen Junior-Developer ersetzen und eine strickt vorgegebene Programmanforderung 
in zwei verschieden komplexen Programmiersprachen umsetzen?
Welche Probleme treten dabei auf und für welche Teile benötigt sie externe Hilfe? 
Gibt es Dinge, die gar nicht funktionieren?

Mit diesen Fragen habe ich mich im Zuge dieser Projektarbeit beschäftigt und verwende dabei
stellvertretend für kostenlose LLMs ChatGPT 5.2 und stellvertretend für Business Lösungen
Cursor AI Agents auf Basis von Claude 4.6, Gemini 3.0, GPT-5.2 / GPT-5.3 Codex und Grok Code,
wobei Cursor intern je nach Aufgabe entscheided, welches Model am besten dafür geeignet ist.
Die Verwendung dieser Modelle fand im Februar 2026 statt.

Grundlegend sollen in diesem Versuch beide Anbieter mit denselben Anforderungen eine .html erstellen, 
die lokal im Browser eine ausführbare App implementiert. Die App selbst soll mittels eines festgelegten 
Import-Formats Anki-Karten darstellen und dem Nutzer ermöglichen, seinen Fortschritt beim Lernen dieser
zu tracken und grafisch dargestellt bekommen. 
Dabei wird in zwei unterschiedlichen Versuchen die Sprache festgelegt.
Bei der leichten Version nur auf HTML, CSS und Javascript und 
bei der schweren Version auf HTML, CSS und Javascript im Frontend mit WebAssembly in Rust geschrieben im Backend. 
Damit soll ein Vergleich geschaffen werden zwischen weitverbreiteten Sprachen mit vielen Informationen
und eher unbekannteren Sprachen mit weniger Bezugsquellen dazu.
Außerdem werde ich durch gezielte Iterationen versuchen, die LLMs zum Reparieren ihrer Fehler zu bewegen.

 
**Ergebnisse:**

Im Überblick
| Versuch | Anzahl Iterationen | Zeilen Code | Ergebniss |
|:-------:|:------------------:|:-----------:|:---------:|
| Chat-GPT leicht | 6 | 442 | ✔ OK |
| Chat-GPT schwer | 4 | 261 | ✘ Abbruch |
| Cursor leicht | 3 | 1128 | ✔ OK |
| Cursor schwer | 3 | 1029 | ✔ OK |

Quality Assurance und Absicherung der Imports

*EC = Edge-Case-Tests, maximal 6*

*Bestehend aus: DoubleID, InvalidDate(Abgelaufen), LongText, Minimal(0 Karten), MissingParts, WrongTime(Zukunft)*
| Versuch | Erfüllte EC zu Beginn | Erfüllte EC nach "Selbstreflektierung" | Erfüllte EC nach spezifischer Hilfestellung |
|:-------:|:------------------:|:-----------:|:---------:|
| Chat-GPT leicht | 1 | 3 | 6 |
| Chat-GPT schwer | 0 | - | - |
| Cursor leicht | 1 | 3 | 6 |
| Cursor schwer | 0 | 3 | 6 |

**Chat-GPT leicht:**

![Bild](Bilder/GPT_JS.png)

Anfangs keine ordentlichen Importkontrollen und Fehler in Boxplotdarstellung.
Außerdem Implementierung für "Lernziele" nur oberflächlich und nicht eingebunden in den Rest.
Auch kritische Fehler in der Umsetzung von Lernsessions vorhanden, 
wodurch mehrere gleichzeitig startbar waren und damit das Programm zerlegt haben.
Über mehrere Iterationsschritte konnten alle Fehler dann Schritt für Schritt ausgebessert werden. 

**Chat-GPT schwer:**

![Bild](Bilder/GPT_Rust.png)

Erste Version wirft bei Verwendung direkt Fehler und hat gar kein funktionierendes Backend.
Auch nach mehreren Versionen können zwar Imports oberflächlich stattfinden und Fehlermeldungen beseitigt werden, 
aber die Daten gehen direkt wieder verloren und Lernsessions können nicht gestartet werden.
Ein Boxplot ist auch nicht vorhanden. Beim aufwändigen Denkprozess zum Rust-Teil wurde zeitgleich ein Großteil 
der eigentlichen Anforderungen des Programms wieder verworfen und auch mit zusätzlichen Prompts
dreht sich die Entwicklung im Kreis. 
Deshalb habe ich den Versuch abgebrochen.

**Cursor leicht:**

![Bild](Bilder/Cursor_JS.png)

Anfangs keine ordentlichen Importkontrollen, aber sehr viele Details zur besseren Verwendung aus Usersicht.
Kontrollen lassen sich leicht ergänzen und auch kleinere Alignment-Fehler sind schnell behoben.
Nur Unschönheiten in Boxplots sind nicht ganz optimal lösbar.

**Cursor schwer:**

![Bild](Bilder/Cursor_Rust.png)

Anfangs garkeine Importkontrollen!
Im Thinkingprozess wurde außerdem der Sinn hinter Rust-Implementierung hinterfragt.
Umsetzung aber solide, allerdings fehlen durch Mehraufwand mit Rust jetzt 
viele der "optionalen" Zusätze, die in der 1. Version noch vorhanden waren.
Kontrollen lassen sich leicht fixen und Boxplots sind diesmal von vorne herein durchdachter.


**Interpretation:**
Bereits während der Ausführung der Tests und auch jetzt mit den fertigen Ergebnissen im Vergleich
wird für mich deutlich, dass ChatGPT deutlich kürzere und vereinfachte Lösungen bevorzugt.
Dabei scheinen die Anforderungen im Prompt das Maximum zu sein, das GPT erreichen kann, aber oftmals
nicht erreicht und im Denkprozess Teile davon wieder vergisst.
Meine Vermutung hierbei ist, dass Chat-GPT die Grenzen seines Context Cache sehr schnell erreicht bei so großen Aufgaben.
Beim Verwenden einer schwereren Programmiersprache wurde dies besonders deutlich,
wenn ganze Abschnitte der ersten drei Anforderungen wegfallen und das Ergebniss trotzdem nicht einmal den
technischen Kern erfolgreich implementieren kann. 

Diese Ergebnisse stehen im starken Kontrast zu Leons Erfahrungen mit Chat-GPT 
bei einer einfacheren Aufgabe mit weniger Kontext.


Cursor hingegen hat ab der allerersten Verwendung ein deutlich professionelleres Bild abgegeben.
Jede Iteration bei beiden Varianten war immer voll ausführbar und deutlich ansprechender für mich als User.
Dabei viel schnell auf, dass Cursor die Anforderungen als zu erfüllendes Minimum sah 
und immer deutlich mehr geliefert hat. Allerdings ging dadurch auch die Komplexität und reine Länge
des Codes durch die Decke, was auch zu deutlich höherem Rechenaufwand führt.
Beim Vergleich beider Tests mit Cursor vielen auch einige Ähnlichkeiten vorallem in der UI-Gestaltung auf, 
was mich vermuten lässt, dass Teile davon hardcoded sind und nicht direkt von der LLM entschieden wurden.


**Fazit:**

Im Bezug auf meine ursprünglichen drei Fragen kann ich nun sagen:

Chat-GPT kann einfache Aufgaben nach dem Minimalprinzip einigermaßen erfolgreich erfüllen,
benötigt dabei aber dringend Unterstützung beim Testen und Absichern gegen Fehlerquellen 
und bei der Darstellung des UI und möglicher Boxplots.
Des Weiteren begrenzen sich die Möglichkeiten auf leichtere Programmiersprachen und nicht zu viel Kontext.

Cursor kann sowohl einfache als auch schwere Aufgaben erfolgreich erfüllen und die Ergebnisse
sehr gut darstellen und präsentieren, auch bei großem Kontextumfang.
Dabei nimmt Cursor die gegebenen Anforderungen als Minimum und fügt viele optionale Erweiterungen automatisch hinzu.
Allerdings benötigt auch Cursor dringend Hilfe beim Testen und Absichern gegen Fehlerquellen
und am Ende muss der User selbst entscheiden, wieviele der optionalen Erweiterungen er für sinnvoll hält.

Auf Basis dieser Erkenntnisse blicke ich gespannt auf die Entwicklung von LLMs in der Zukunft! :)
