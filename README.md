# MusicManager
Manage and share your music interest with MusicManager!

## Requirements
You need there requirements to deploy MusicManager on your own server.

* PostgreSQL (DB)
* AWS S3

You need to install this package for using PostgreSQL like this:

* On Ubuntu
<pre>
sudo apt-get install postgresql libpq-dev
</pre>
* On CentOS / AWS EC2 AMI
<pre>
sudo yum install postgresql postgresql-devel
</pre>

If you don't want to use MusicManager without PostgreSQL or AWS S3, pull until [aaf17e](https://github.com/rubysoho07/MusicManager/commit/aaf17e689e0882a6d5162054c76882887f368b18) commit.

## Installing Development Environment.
I want to recommend using `virtualenv` for your development environment not to confuse your development or deployment.
You can install requisite packages with pip on the directory which `requirement.txt` file exists.
<pre>
pip install -r requirement.txt
</pre>

## Setting Configuration
I store password settings with `settings.json` file. Write this file and save it project root directory.
For example:
``` json
{
  "SECRET_KEY": "SECRET_KEY",
  "DB_PASSWORD": "PostgreSQL DB Password",
  "PORT": "5432"
}
```
You can generate your `SECRET_KEY` with http://www.miniwebtool.com/django-secret-key-generator/.

## Deploying and Running MusicManager 

### Using Django runserver
If you want to debug or test MusicManager, start runserver of Django. You should specify setting file with `--settings` option.

<pre>
python manage.py runserver 0.0.0.0:8000 --settings=MusicManager.settings.local
</pre>

### Using nginx + uWSGI
If you want to deploy MusicManager on server, try this with nginx and uWSGI.

#### nginx Setting
edit /etc/nginx/sites-enabled/MusicManager.conf (I used vim).
<pre>
# MusicManager.conf

# the upstream component nginx needs to connect to
upstream django {
        server unix:///home/ec2-user/musicmanager/MusicManager/MusicManager.socket; # for a file socket
        # server 127.0.0.1:8001; # for a web port socket (we'll use this first)
}

# configuration of the server
server {
# the port your site will be served on
        listen      80;
# the domain name it will serve for
        server_name musicmanager.gonigoni.kr; # substitute your machine's IP address or FQDN
        charset     utf-8;

# max upload size
        client_max_body_size 75M;   # adjust to taste

# Django media

        location /static {
                alias /home/ec2-user/musicmanager/MusicManager/static; # your Django project's static files - amend as required
        }

        location /media {
                alias /home/ec2-user/musicmanager/MusicManager/media; # your Django project's static files - amend as required
        }

# Finally, send all non-media requests to the Django server.
        location / {
                uwsgi_pass  django;
                include     /home/ec2-user/musicmanager/MusicManager/uwsgi_params; # the uwsgi_params file you installed
        }
}
</pre>

After that, edit `/etc/nginx/nginx.conf` file.
<pre>
http {

    (...)

    # Load modular configuration files from the /etc/nginx/conf.d directory.
    # See http://nginx.org/en/docs/ngx_core_module.html#include
    # for more information.
    include /etc/nginx/conf.d/*.conf;

    # Load configuration files for sites-enabled directory.
    # ADD THIS TO DEPLOY MUSICMANAGER!!
    include /etc/nginx/sites-enabled/*.conf;

    (...)
</pre>

#### uWSGI Setting
Run uWSGI on your project root directory.

<pre>
uwsgi --socket MusicManager.socket --module MusicManager.wsgi --env DJANGO_SETTINGS_MODULE=MusicManager.settings.production --chmod-socket=666 > MusicManager.log 2> MusicManager.err.log &
</pre>

If you experience "Permission denied" on ngnix, try to change permission of your source directory to 666 or 755.
