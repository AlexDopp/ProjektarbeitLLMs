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

Im Überblick:

| Versuch | Anzahl Iterationen | Zeilen Code | Ergebniss |
|:-------:|:------------------:|:-----------:|:---------:|
| Chat-GPT leicht | 6 | 442 | ✔ OK |
| Chat-GPT schwer | 4 | 261 | ✘ Abbruch |
| Cursor leicht | 3 | 1128 | ✔ OK |
| Cursor schwer | 3 | 1029 | ✔ OK |
