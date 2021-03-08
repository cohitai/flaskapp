# flaskapp
web dev



Flask server for Berliner- Zeitung in 2 branches. 


1. to update the server use: git pull --rebase. (from the main branch). 
2. The second branch contains information the Lets encrypt certificates. If you wish to start a new server you should use this branch and then adapt the Lets Encrypt Certbot
with the changes. The certificates renewal should work automatically. 

3. Better for the future: Build the server inside the K8s cluster. (with shared volumes instead of http updates, although both will work fine). 

