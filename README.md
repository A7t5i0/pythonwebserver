# Python webserver
Webserver written in Python

Features:

-Supports file uploads

-Auto detect files (html, js, png, jpeg, jpg, mp4, php etc)

-Filenames are turned into urls (after upoading eg filename you can use protocol://ip:port/filename to view them in browser)

-uses SSL

-Multithreading

-SSL cert and key generated with:
openssl req -newkey rsa:4096 -nodes -keyout key.pem -x509 -days 365 -out cert.pem
