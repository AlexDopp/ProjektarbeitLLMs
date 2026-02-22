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

