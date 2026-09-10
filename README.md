# RandomCleverGame
Eine Python-Implementierung eines digitalen Wertungsblocks für ein bekanntes Würfelspiel mit zufällig generierten Oberflächen.

## Beschreibung & Features
**RandomCleverGame** erzeugt ein zufällig generiertes Spielfeld. Dabei werden Farbfelder, Boni, Punktelogiken und Bedingungen dynamisch kombiniert.
Die Spieler nutzen physische Würfel, deren Ergebnisse über eine interaktive Maussteuerung auf dem Wertungsblock eingetragen werden.

### Features
* **Seed-System:**
  * Über eine Reroll-Funktion wird das Spielfeld basierend auf einem Seed zufällig generiert. Seeds können auch manuell eingegeben werden, um verschiedenen Mitspielern das gleiche Spielfeld zu ermöglichen.
* **Dynamisches Spielfeld:**
  * Verschiedene Varianten für unterschiedliche Farbbereiche (z. B. Gelb, Blau, Orange, Grün, Lila) werden zufällig kombiniert. Jeder Farbbereich hat unterschiedliche Regeln, die sich an den Clever-Spielen von Wolfgang Warsch / Schmidt Spiele orientieren (z. B. aufsteigende/absteigende Zahlenreihen, Multiplikatoren, Boni).
  * Die zufällige Farbplatzierung vermeidet Kollisionen, sodass jedes Farbfeld genau einmal vorkommt.
  * Die Boni innerhalb der Farbbereiche werden zufällig verteilt.
* **Interaktive Bedienung & Maussteuerung:**
  * **Linksklick:** Feld abkreuzen / Kreuz entfernen.
  * **Rechtsklick:** Feld einkreisen / Kreis entfernen.
  * **Mittelklick:** Zahlendialog öffnen, um Zahlenwerte in die Felder einzutragen.
* **Echtzeit-Auswertung & Punkteberechnung:**
  * Gesamtpunkte, Einzelfeld-Punkte und Punkte durch Füchse werden basierend auf den spezifischen Regeln der generierten Felder berechnet und übersichtlich angezeigt.
  * Die Anzahl der getätigten Aktionen und die Anzahl der aktivierten Boni werden ebenfalls erfasst.
* **Dynamische UI:**
  * Das Spielfeld wird passend zur ausgelesenen Monitor-Auflösung (`screeninfo`) skaliert.
  * Für optimale Lesbarkeit werden Farbanpassungen durch die Berechnung von Komplementärfarben vorgenommen.
* **Verlaufshistorie:**
  * Die Spielfeld-Interaktionen werden in einem Verlauf (`ScrolledText`) protokolliert und angezeigt.

## Technologie & Bibliotheken
* **Sprache:** Python 3.14.6
* **Benutzeroberfläche:** 
  * `tkinter` – Grafische Benutzeroberfläche (mit Dialogen, Schriften & ScrolledText)
  * `screeninfo` – Dynamische Skalierung der Benutzeroberfläche durch Monitor-Auflösung
* **Bildverarbeitung:**
  * `Pillow (PIL)` – Laden und Skalieren von Icons
* **Datenverarbeitung & Zufallslogik:**
  * `NumPy` – Mathematische Datenstrukturen
  * `random` – Zufällige Generierung der Spielfelder

## Inspiration & Disclaimer
RandomCleverGame ist ein privates, nicht-kommerzielles Programm zu Lern- und Portfoliozwecken.
Die Spielmechaniken sind inspiriert von der Clever-Reihe von Wolfgang Warsch / Schmidt Spiele.
Alle Markenrechte liegen bei den jeweiligen Rechteinhabern.
