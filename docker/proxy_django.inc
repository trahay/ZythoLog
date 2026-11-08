proxy_pass http://web:8000;
proxy_set_header Host $host;
proxy_set_header X-Forwarded-For $proxy_add_x_forwarded_for;
# Transmet le schéma (https) fourni par le nginx de YunoHost
proxy_set_header X-Forwarded-Proto $http_x_forwarded_proto;
proxy_read_timeout 60s;
