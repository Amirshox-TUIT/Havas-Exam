server {
    listen 80;
    server_name furniture.amirshox.uz www.furniture.amirshox.uz 159.89.19.244;

    location /static/ {
        alias /vol/web/static/;
    }

    location /media/ {
        alias /vol/web/media/;
    }

    location / {
        include uwsgi_params;
        uwsgi_pass app:9000;
    }
}