Um einen Apache2-Server auf Debian 12 auf HTTPS umzustellen und ein eigenes Zertifikat zu verwenden, können Sie die folgenden Schritte befolgen:

1. Apache2 installieren:
 apt update
apt install apache2

2. SSL-Modul aktivieren:
a2enmod ssl
systemctl restart apache2

3. Verzeichnis für das Zertifikat erstellen:
mkdir /etc/apache2/ssl

4. Eigenes SSL-Zertifikat erstellen:
openssl req -x509 -nodes -days 365 -newkey rsa:2048 -keyout /etc/apache2/ssl/apache.key -out /etc/apache2/ssl/apache.crt

Folgen Sie den Anweisungen, um die Zertifikatsinformationen einzugeben.

Alternativ die vorhandene REG.CONF verwenden: normalerweise im /root/


5. Apache-Konfiguration anpassen: Öffnen Sie die Datei /etc/apache2/sites-available/default-ssl.conf mit einem Texteditor:
nano /etc/apache2/sites-available/default-ssl.conf

Ändern Sie die folgenden Zeilen, um auf Ihr Zertifikat und Ihren Schlüssel zu verweisen:
SSLCertificateFile /etc/apache2/ssl/apache.crt
SSLCertificateKeyFile /etc/apache2/ssl/apache.key

6. SSL-Site aktivieren:
a2ensite default-ssl
systemctl reload apache2

7. Firewall konfigurieren: Stellen Sie sicher, dass die Firewall HTTPS-Verbindungen zulässt:
ufw allow 'Apache Full'
ufw delete allow 'Apache'

Nach diesen Schritten sollte Ihr Apache2-Server auf Debian 12 HTTPS-Verbindungen mit Ihrem eigenen Zertifikat unterstützen


Updates der Zertifikate erfolgt dann über Ansible

