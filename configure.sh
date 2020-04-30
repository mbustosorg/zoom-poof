#git clone https://github.com/elanlb/water-heater

#sudo apt install apache2
#sudo a2enconf serve-cgi-bin
#sudo a2enmod cgid
cd /etc/apache2
sudo sed -i "s|/var/www|${HOME}/git/zoom-poof/web|" apache2.conf
sudo sed -i "s|/var/www/html|${HOME}/git/zoom-poof/web|" sites-available/000-default.conf
sudo sed -i "s|/usr/lib/cgi-bin|${HOME}/git/zoom-poof/cgi-bin|g" conf-available/serve-cgi-bin.conf
sudo systemctl reload apache2

sudo usermod -a -G gpio www-data
