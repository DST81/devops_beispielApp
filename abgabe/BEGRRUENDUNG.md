# Teilaufgabe 6 – Optimierungen begründen

Beim Vergleich der beiden Docker-Images ist mir aufgefallen, dass das optimierte Image viel kleiner ist als das naive Image. Das optimierte Image ist **217 MB** gross, während das naive Image **1.67 GB** benötigt.

Ein Grund dafür ist das schlanke Basis-Image `python:3.12-slim`. Es enthält weniger zusätzliche Programme als das normale `python:3.12`-Image und benötigt deshalb weniger Speicherplatz. Ausserdem wird beim optimierten Dockerfile ein Multi-Stage-Build verwendet. Dabei werden die Abhängigkeiten zuerst in einer eigenen Build-Stufe installiert. In das fertige Image kommen nur die benötigten Dateien. Dadurch bleibt es kleiner.

Auch die Reihenfolge der Layer ist wichtig. Die `requirements.txt` wird zuerst kopiert und die Pakete werden installiert, bevor der eigentliche Programmcode kopiert wird. Wenn ich später den Code ändere, müssen die Pakete dadurch nicht jedes Mal neu installiert werden. Das spart Zeit beim erneuten Bauen.

Die `.dockerignore`-Datei verhindert, dass unnötige Dateien wie `.git`, lokale Testdateien oder virtuelle Umgebungen in das Image kopiert werden. So bleibt es übersichtlich und es gelangen weniger unnötige Daten hinein.

Zusätzlich läuft die Anwendung mit einem unprivilegierten Benutzer statt als `root`. Dadurch können mögliche Schäden bei einem Sicherheitsproblem begrenzt werden. Insgesamt habe ich gelernt, dass diese Entscheidungen das Image kleiner, sicherer und wartbarer machen.
