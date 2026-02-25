Haupterkenntnise?
Zeitpunkte der Erstellung
ChatGPT Export
Was ist das Wichtige wenn man mit ChatGPT code haben will.
im Stil von Bestpractices.

**ChatGPT**: 

Allgemeines:

ChatGPTs Codeerstellung ist sehr an das Min-Max Pronzip angelehnt.
Es wird versucht, mit der niedrigst möglichen Anzahl an Zeilen den möglichst größten Teil des Prompts zu erfüllen.
Das Erwähnen von Fokuspunkten und bestimmten Fachbegriffen führt meistens dazu, dass der fokussierte Teil des Codes auch wirklich funktioniert.
Hierbei besteht allerdings das Problem das durch Fokusierungen, häufig ein anderer Teil des Codes vernachlässig wird.
Der nicht-fokussierte Codeteil wird zwar meistens noch geschrieben, es kann aber sein, dass dieser nicht oder nur teilweise korrekt integriert wird.
Weiterhin setzt ChatGPT auf Codeklarheit, aber nicht im Zeilen/Methoden Verständnis, sondern im allgemein Verständnis. 
Es setzt über Klassen große Kommentarblöcke, die nur den Klassennamen wiederholen. 
Wenn einzelne Funktionen speziell gefordert werden (Wie in meinem Prompt "Schatten, Reflexionen, Shading und Lichtquellen") werden diese im Code markiert.
Nachfragen über Codeteile funktionieren nur als "Erkläre mir wie" Fragen und nicht als "Diese Methode macht X, oder?", da ChatGPT ein "Ja-Mann" ist.
Weiterhin hat man bei meinem Codebeispiel als auch bei Alex gesehen, dass ChatGPT keinen großen Gesamtplan für den Code setzt, sondern diesen aus Einzelteilen zusammensetzt.
Hierbei wird nicht (oder nicht ausreichend) überprüft ob einzelne Teile untereinander sich Zanken.
Dies wird ersichtlich hauptsächlich an drei Punkten unserer Beispiele.
Zuerst bei mir das Hauptproblem ChatGPTs mit den Shadowrays, welche in allen bis auf zwei Versionen genau gleich implementiert wurden.
Die zwei nicht gleichen Implementierungen sind einmal das komplette Ignorieren des Promptteils (Durch den vorher genannten Fokus auf andere Teile des Codes) und die einzige "perfekte" ("funktionierende") Lösung.
Der zweite Punkt, auch in meinem Teil, ist das sofortige Erkennen des Fehlers bei Gabe des Codes (Ersichtlich in /"AI Tries Fixing").
Hier zeigt sich, dass selbst wenn, der Prompt nur aus Problembeschreibung und Code besteht, dass ChatGPT den Fehler findet und lösenden Code zur Verfügung stellt.
Dies deutet darauf hin, dass ChatGPT Code dieser Länge versteht und auch untersuchen kann, aber nicht beim erstellen erneut überprüft.
Somit sollte das erneute senden des Codes in einen neuem Chat zu einem besseren Grundergebnis führen.
Zusätzlich zeigt sich, dass ChatGPT häufig stark auf die exakte Formulierung des Prompts reagiert.
Kleine sprachliche Änderungen können dabei bereits zu deutlich anderen Codeergebnissen führen.
Dabei wird ersichtlich, dass Prioritäten implizit aus der Wortwahl abgeleitet werden.
Explizite Gewichtungen im Prompt beeinflussen daher die Struktur des generierten Codes erheblich.
Ohne klare Priorisierung behandelt ChatGPT viele Anforderungen als gleichrangig.
Dies kann dazu führen, dass komplexe Kernlogik und nebensächliche Details denselben Raum erhalten.
Ein weiterer Punkt ist die Tendenz zur Wiederverwendung ähnlicher Lösungsstrukturen.
Oft orientiert sich der generierte Code an zuvor erfolgreichen Mustern.
Dadurch entstehen konsistente, aber nicht immer optimal angepasste Implementierungen.
Besonders bei grafischen oder mathematischen Problemen zeigt sich diese Musterorientierung deutlich.
ChatGPT optimiert zudem selten iterativ innerhalb einer einzigen Antwort.
Stattdessen wird eine scheinbar abgeschlossene Lösung präsentiert.
Interne Abhängigkeiten zwischen Methoden werden nicht systematisch validiert.
Fehlende Rückkopplungsschleifen im Generierungsprozess verstärken dieses Problem.
Auch Randfälle werden nur berücksichtigt, wenn sie explizit genannt werden.
Nicht spezifizierte Edge-Cases bleiben daher häufig unbeachtet.
Die Struktur des Codes wirkt oft logisch, aber nicht vollständig durchdacht.
Dies lässt vermuten, dass lokale Kohärenz über globale Konsistenz priorisiert wird.
Komplexitätsmanagement erfolgt eher oberflächlich als architektonisch geplant.
Insgesamt entsteht Code, der funktional wirkt, jedoch nicht immer als ganzheitliches System entworfen wurde.

Best Practice Advice:

1. Fokuspunkte deutlich markieren 
2. Nach Modularität und Erweiterbarkeit fragen
3. Sofortige Ausführbarkeit erwarten
4. Code in neuen Chats korrigieren lassen


Haupterkenntnisse:

1. ChatGPT ist min-max Code Gen
2. ChatGPTs Fehler kommen (häufig) vom Frankenstein Weg wie Code generiert wird
3. ChatGPT kann den eigenen Code (in neuen Chat) gut reperieren

**DeepSeek**:

Allgemein:

DeepSeek Codegenerierung ist oberflächig und ausgiebig.
Bei der Generierung werden häufig fehlerhaft Operanten verwendet.
Diese sind dann meist undefiniert für die bestimmte Typ-Kombination oder falsch implementiert im Allgemeinen.
Das Reparieren des gelieferten Codes dauert häufig an, da das Programm (natürlich) abbricht sobald es einen Fehler findet (z.b. operant+ undefined for int - Vec3).
Dies führt dazu das weitere Fehler der gleichen Art nicht angezeigt werden.
Da das ausführen von DeepSeek Code lange dauert, wird die Reparaturzeit somit stark verlängert (nicht DeepSeeks Problem zu 100%).
DeepSeek optimiert, bzw. setzt Standardwerte häufig auch außerhalb der Norm (z.b. V11 mit max_depth = 20).
Code generiert von DeepSeek ist meist stark Bloated. 
Dabei handelt er sich nicht um Erweiterungsmöglichkeiten oder ähnliches.
Die Lesbarkeit wird durch Kommentare vor den meisten Zeilen stark erhöht.
Dabei sind in den einzelnen Zeilen praktisch nie die Probleme, sondern nur in der Kombination mehrerer Zeilen die sich zanken.Zeilen.
Zusätzlich fällt auf, dass DeepSeek häufig sehr viele Hilfsvariablen einführt.
Diese Variablen tragen nicht immer zur tatsächlichen Problemlösung bei.
Oft werden Berechnungen unnötig aufgesplittet, obwohl eine kompaktere Lösung möglich wäre.
Dadurch entsteht ein erhöhter Wartungsaufwand im weiteren Entwicklungsprozess.
Strukturell wirken viele Implementierungen übermäßig verschachtelt.
Kontrollstrukturen werden teilweise redundant eingesetzt.
Fehlende Typprüfungen führen regelmäßig zu vermeidbaren Laufzeitfehlern.
Generische Funktionen werden selten wirklich generisch umgesetzt.
Stattdessen entstehen stark spezialisierte Einzelimplementierungen.
Optimierungen wirken häufig kosmetisch statt algorithmisch fundiert.
Speicher- oder Laufzeitkomplexität wird nur selten bewusst berücksichtigt.
Zudem werden bestehende Abhängigkeiten zwischen Komponenten nicht konsequent analysiert.
Das Zusammenspiel einzelner Module bleibt daher anfällig für Seiteneffekte.
Testfälle oder Validierungsmechanismen werden kaum mitgedacht.
Insgesamt entsteht der Eindruck einer ausführlichen, aber nicht tiefgreifend abgestimmten Codebasis.