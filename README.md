# flaskapp
web dev



Flask server for Berliner-Zeitung in 2 branches. 


1. To update the server use: git pull --rebase. (from the main branch). 
2. The second branch contains information about the LetsEncrypt certificates procedures. If you wish to start it on a new server, you should use the second branch and then adapt to LetsEncrypt Certbot.
for the changes. The certificates renewal should work automatically. 

3. Better for the future: Build the server inside the K8s cluster. (with shared volumes instead of http updates, although both will work fine). 

4. docker-compose up to start the server. 

