:Title:    Installare una applicazione Django usando Nginx e Gunicorn
:Created:  2018-07-22 10:01:01
:Summary:  Non è facile installare una applicazione Django 
    in un web server di produzione. 
    In questo articolo vedremo i passi necessari per farlo 
    in un server CentOs 7, con web server Nginx e middleware 
    Gunicorn. 
:Language: it
:Slug:     installare-una-applicazione-django-usando-nginx-e-gunicorn
:Author:   Luciano De Falco Alfano


.. _django_deployment:

**Django deployment**
######################

Sono un sostenitore di Python e Django. Per questo motivo sto per affermare 
un concetto che non mi piace: *"non è facile installare in produzione una
applicazione sviluppata con Django"*.

D'altro canto, non è neanche una *"mission impossible"*, se si sa
dove e perché mettere le mani.

In questo articolo illustro la procedura che seguo quando installo
in produzione una applicazione Django. Come vedremo, non è banale,
ma, con un po' di pazienza, funziona.

Cosa serve? 

Prerequisito è la disponibilità di un server con sistema operativo
`CentOS 7 <https://www.centos.org/>`_, con *openssh*, e
servizio web server `NGINX <https://www.nginx.com/>`_.

Il DB utilizzato è *sqlite3*, incluso in Python.

L'installazione dell'applicazione avviene via *remote copy*, copiando i file
applicativi e di configurazione. Quindi modificando manualmente i file di
configurazione. Ed infine inizializzando l'ambiente (DB e file statici).

In coda all'articolo indicheremo anche qualche altra operazione,
che solitamente è utile.
  
E' necessaria un minimo di conoscenza dei comandi `Linux <https://www.linux.org/>`_ da console.
Così come saper utilizzare un editor di testo da console. Un classico è
``vi``, ma qualunque editor presente nel server va bene.

**Passi da effettuare**
*************************

* `installare nginx`_;
* `installare python 3.6`_;
* `preparare l'ambiente virtuale per l'applicazione`_;
* `configurare l'applicazione per la produzione`_;
* `configurare e demonizzare Gunicorn`_;
* `configurare il server http Nginx`_.

Ipotizziamo di avere un progetto che si chiama *base* e che ha la seguente
struttura sui computer di sviluppo (struttura familiare per chi
lavora con *Django*)::

  base/
   |-- .git/                    # non in produzione
   |-- deployment/              # non in produzione
   |-- docs/                    # non in produzione
   |-- venv/                    # non in produzione
   |                            
   |-- sito/                    # in produzione
   |    |                       
   |    |-- app1/               # in produzione
   |    |    |-- templates/
   |    |    |      +-- app1/
   |    |    +-- urls.py, views.py, models.py, ...
   |    |  
   |    |-- sito/
   |    |    |-- settings.py,    # in produzione MA MODIFICATO
   |    |    +-- urls.py, views.py, wsgi.py
   |    |
   |    |-- templates/
   |    |    +-- base.html, home.html, login.html
   |    |
   |    +-- static/
   |         |-- css/
   |         |-- images/
   |         +-- js/
   |
   +-- .gitignore, requirements.txt # in produzione solo requirements.txt
   
Il nostro progetto risponderà al dominio ``www.sito.org``. 
  

Lato web server utilizzeremo *Nginx* che passa la richiesta
tramite socket a `Gunicorn <http://gunicorn.org/>`_. Questo a sua volta incamera l'applicazione
*Django* ``base/sito``, e la esegue passando la richiesta proveniente da *Nginx*.

*Gunicorn*, *Django*, ``base/sito``, sono applicazioni *Python 3.6* 
ospitate in un ambiente virtuale leggero configurato tramite *virtualenv*.

Da Python versione 3.3 e successive, *virtualenv* è incluso nell'ambiente
di base dell'interprete, nel modulo ``venv``.

L'applicazione ``base`` verrà installata nella directory
``/usr/share/nginx/html/base``.


**Istruzioni**
*****************

Vediamo le diverse fasi dell'installazione.


**Installare Nginx**
======================

Per installare Nginx possiamo usare la seguente [1]_:

.. code:: console

  # > utenza root su server
  yum install epel-release     # aggiungere il repository epel
  yum install nginx            # installare nginx
  systemctl start nginx        # avviare nginx
  # aprire le porte http(s) su firewall
  firewall-cmd --permanent --zone=public --add-service=http 
  firewall-cmd --permanent --zone=public --add-service=https
  firewall-cmd --reload
  systemctl enable nginx       # nginx starts on system boot
  curl localhost.localdomain   # to check
  mkdir /etc/nginx/sites-available
  mkdir /etc/nginx/sites-enabled
  yum -y install vim           # un minimo di comfort rispetto vi
  # disk usage: 1.2G


**Installare python 3.6**
===========================

Questa procedura [2]_ installa *Python 3.6* di fianco a *Python 2.7*,
che è la normale dotazione di CentOS 7, e che **NON** può essere sostituito.

.. code-block:: console

  # utenza root su server
  # installare utilities varie
  yum install deltarpm
  #yum update                  ## ATTENZIONE: può dare problemi alla
                               #    configurazione di php, se presente nel sistema
                               #    e utilizzato dal server http
  yum install yum-utils
  yum groupinstall development
  
  # IUS (Inline with Upstream Stable) repository e installazione python 3.6 (di fianco al 2.7)
  yum install https://centos7.iuscommunity.org/ius-release.rpm
  yum install python36u
  yum install python36u-pip
  yum install python36u-devel


**Preparare l'ambiente virtuale per l'applicazione**
======================================================

.. code:: console

  cd /usr/share/nginx/html
  mkdir base
  cd base
  python3.6 -m venv venv
  mkdir run
  mkdir log
  # copiare dal sistema di sviluppo, via remote copy, l'applicazione in /usr/share/nginx/html
  #    la dir.da cui iniziare la copia è .../base/sito, inoltre copiare il file
  #    .../base/requirements.txt. NON copiare sul server il venv del pc di sviluppo
  # ad esempio, da client di sviluppo con windows, utilizzando il programma pscp.exe:
  #    pscp -r C:\...\Sviluppi\base\sito  root@server_address:/usr/share/nginx/html/base/sito
  #    pscp    C:\...\Sviluppi\base\requirements.txt  root@server_address:/usr/share/nginx/html/base
  source venv/bin/activate
  pip install -r requirements.txt
  pip install --upgrade pip
  pip install gunicorn  


**Configurare l'applicazione per la produzione**
==================================================

La configurazione dell'applicazione consiste in:

* inibire il ``DEBUG``,
* settare l'indirizzo del dominio accettato da *Django*
* settare la ``SECRET_KEY`` con una apposita chiave, sconosciuta a chi sviluppa

In pratica i seguenti passi.

**Inibire il DEBUG e settare il dominio accettato da Django**
----------------------------------------------------------------

.. code:: console

  cd sito/sito
  # modificare /usr/share/nginx/html/base/sito/sito/settings.py
  #    in questo file porre:
  #        ...
  #        DEBUG = False
  #        ALLOWED_HOSTS = ['www.sito.org', ]
  #        ...
  
**Settare la SECRET_KEY**
------------------------------

Per settare la ``SECRET_KEY`` ad un valore non conosciuto a chi sviluppa,
è possibile generare un file *secretkey.txt* utilizzato
poi da *settings.py*. 

Questa operazione non è del tutto immediata. Perché dobbiamo generare
una chiave segreta in modo randomico. Per farlo è bene utilizzare
*Django*. Ma per utilizzare *Django* abbiamo bisogno di un file di configurazione
funzionante, ovvero con la SECRET_KEY già impostata.

Un bell'esempio di cane che si morde la coda.

Per aggirare il problema: utilizziamo una chiave conosciuta, generiamo
quella segreta, e poi mettiamo al lavoro quest'ultima. Questo si traduce in:

* modificare il *settings.py*,
* generare *secretkey.txt*,
* riportare il *settings.py* alla configurazione originaria.

Quindi riconfigurare la seguente sezione di ``settings.py``:

.. code:: python

  #        ...
          # SECURITY WARNING: keep the secret key used in production secret!
          # SECRET_KEY = '71t4+5nfq^#$i*ltas_%ssc$#!t^^rap2%i#3i2&ye)e)c=d@0'
          with open(BASE_DIR + '/secretkey.txt') as f:
              SECRET_KEY = f.read().strip()
  #        ...
  
in questo modo:

.. code:: python

  #        ...
          # SECURITY WARNING: keep the secret key used in production secret!
          SECRET_KEY = '71t4+5nfq^#$i*ltas_%ssc$#!t^^rap2%i#3i2&ye)e)c=d@0'
          #with open(BASE_DIR + '/secretkey.txt') as f:
          #    SECRET_KEY = f.read().strip()
  #        ...

Quindi eseguire:

.. code:: console

  python mksecret.py >secretkey.txt
  
Infine riportare il ``settings.py`` nella configurazione iniziale.  
  
Il file ``mksecret.py`` [3]_ è come segue:

.. code-block:: python
  :number-lines:

  # filename: mksecret.py
  import os, sys
  
  # CHANGE THIS -  this the project's manage.py directory
  proj_path = "/usr/share/nginx/html/base_fs_rst/rstsite"
  # CHANGE THIS - This is so Django knows where to find stuff.
  os.environ.setdefault("DJANGO_SETTINGS_MODULE", "rstsite.settings")
  sys.path.append(proj_path)
  
  # This is so my local_settings.py gets loaded.
  os.chdir(proj_path)
  
  # This is so models get loaded.
  from django.core.wsgi import get_wsgi_application
  application = get_wsgi_application()
  
  ################## FROM HERE - your script
  
  from django.core.management import utils
  print(utils.get_random_secret_key())
  
  
**Generare la base dati e il superuser**
-----------------------------------------

.. code:: console

  cd ..                                 # cd .../base/sito
  # rm db.sqlite3                       # se esiste il file db.sqlite3 dal pc di sviluppo
  # crea il DB e il suo amministratore
  python3.6 manage.py makemigrations
  python3.6 manage.py migrate
  python3.6 manage.py createsuperuser
  
  
**Generare i contenuti statici**
-----------------------------------

.. code:: console

  python manage.py collectstatic --noinput   # contenuti statici per il server http
  
**Compilare i file per le traduzioni**
----------------------------------------

Questa attività va fatta se
l'applicazione da installare può gestire più di un linguaggio (non è
banale: il multilingua é una problematica molto vasta).

.. code:: console

  python manage.py compilemessages -l it    # compila il dizionario dei messaggi soggetti a traduzione


**Configurare e demonizzare Gunicorn**
=======================================

Gunicorn è il passa-dati tra il server web e l'applicazione *Django* [4]_.

Dopo averlo installato (ricordate *pip install gunicorn*?), per metterlo
al lavoro dobbiamo fare due cose.

Primo. Dobbiamo fare in modo che Gunicorn sappia come avviare la nostra
applicazione. Per questo creiamo o copiamo il file ``gunicorn_start``
nella directory ``/usr/share/nginx/html/base/venv/bin/``

Il contenuto del file può essere il seguente (o simile):

.. code:: bash

  #!/bin/bash
  
  NAME="sito"                                  # Name of the application
  DJANGODIR=/usr/share/nginx/html/base/sito             # Django project directory
  SOCKFILE=/usr/share/nginx/html/base/run/gunicorn.sock  # we will communicte using this unix socket
  #USER=nginx                                        # the user to run as
  #GROUP=webdata                                     # the group to run as
  USER=root                                        # the user to run as
  GROUP=root                                     # the group to run as
  NUM_WORKERS=1                                     # how many worker processes should Gunicorn spawn
  DJANGO_SETTINGS_MODULE=sito.settings             # which settings file should Django use
  DJANGO_WSGI_MODULE=sito.wsgi                     # WSGI module name
  
  echo "Starting $NAME as `whoami`"
  
  # Activate the virtual environment
  cd $DJANGODIR
  source /usr/share/nginx/html/base/venv/bin/activate
  export DJANGO_SETTINGS_MODULE=$DJANGO_SETTINGS_MODULE
  export PYTHONPATH=$DJANGODIR:$PYTHONPATH
  
  # Create the run directory if it doesn't exist
  RUNDIR=$(dirname $SOCKFILE)
  test -d $RUNDIR || mkdir -p $RUNDIR
  
  # Start your Django Unicorn
  # Programs meant to be run under supervisor should not daemonize themselves (do not use --daemon)
  exec /usr/share/nginx/html/base/venv/bin/gunicorn ${DJANGO_WSGI_MODULE}:application \
    --name $NAME \
    --workers $NUM_WORKERS \
    --user=$USER --group=$GROUP \
    --bind=unix:$SOCKFILE \
    --log-level=debug \
    --log-file=-:

**Attenzione**. Prendetevi il tempo necessario per capire che cosa fa lo 
script precedente, perché deve essere personalizzato per l'installazione
in corso.

I parametri da variare sono parecchi, ed è inutile dire che basta sbagliare
un nonnulla per impedire la comunicazione tra Nginx e l'applicazione.

Un'altra osservazione. Notate le variabili ``USER`` e ``GROUP``, originariamente
[5]_ poste a *nginx* e *webdata*. Noi le abbiamo poste a *root*. In generale 
questo modo di fare *non è raccomandabile*: può generare criticità
di sicurezza nel sistema. Quindi, se avete tempo, provate a mantenere
e far funzionare il tutto con i valori originali. Personalmente vado sempre
di corsa, e finora ho continuato a lavorare con *root* [6]_.

Proseguiamo. La seconda cosa da fare è fare partire Gunicorn come servizio.
Per questo dobbiamo creare o copiare il seguente script ``gunicorn_sito.service``
nella directory ``/etc/systemd/system/``.

Lo script, più semplice del precedente, è:

.. code:: bash

  [Unit]
  Description=sito gunicorn daemon
  
  [Service]
  Type=simple
  User=root
  ExecStart=/usr/share/nginx/html/base/venv/bin/gunicorn_start
  
  [Install]
  WantedBy=multi-user.target

Quasi ci siamo. Dobbiamo abilitare il servizio e avviarlo. Come segue:

.. code:: console

  systemctl enable gunicorn_sito
  systemctl start gunicorn_sito
  systemctl status -l gunicorn_sito   # per controllare se il servizio è partito; credeteci: ne vale la pena!

**Troubleshooting**. Aspettatevi segnalazioni di errore al lancio di
*Gunicorn*. Un errore frequente è il **203**. Nella mia esperienza vi sono
almeno due possibili cause, entrambe relative allo script
``/usr/share/nginx/htm/base/venv/bin/gunicorn_start``:

* uso dell'utente *nginx* invece di *root*;
* oppure mancanza del bit di esecuzione [7]_.

Per approfondire si può consultare:
`Setting up Gunicorn for Django Project - 203/EXEC <https://www.digitalocean.com/community/questions/setting-up-gunicorn-for-django-project-203-exec>`_.



**Configurare il server http Nginx**
=======================================

La configurazione di Nginx è un altro punto chiave.

Un esempio di configurazione di base si ottiene creando o copiando nel file 
``/etc/nginx/nginx.conf`` il seguente:

.. code:: nginx
  :number-lines:

  # sito@centos7: this file @ /etc/nginx/nginx.conf
  # For more information on configuration, see:
  #   * Official English Documentation: http://nginx.org/en/docs/
  #   * Official Russian Documentation: http://nginx.org/ru/docs/
  
  user nginx;
  worker_processes auto;
  error_log /var/log/nginx/error.log;
  pid /run/nginx.pid;
  
  # Load dynamic modules. See /usr/share/nginx/README.dynamic.
  include /usr/share/nginx/modules/*.conf;
  
  events {
      worker_connections 1024;
  }
  
  http {
      log_format  main  '$remote_addr - $remote_user [$time_local] "$request" '
                        '$status $body_bytes_sent "$http_referer" '
                        '"$http_user_agent" "$http_x_forwarded_for"';
  
      access_log  /var/log/nginx/access.log  main;
  
      sendfile            on;
      tcp_nopush          on;
      tcp_nodelay         on;
      keepalive_timeout   65;
      types_hash_max_size 2048;
  
      include             /etc/nginx/mime.types;
      default_type        application/octet-stream;
  
      # Load modular configuration files from the /etc/nginx/conf.d directory.
      # See http://nginx.org/en/docs/ngx_core_module.html#include
      # for more information.
      include /etc/nginx/conf.d/*.conf;
  
      server {
          listen       80 default_server;
          listen       [::]:80 default_server;
  
          #server_name  localhost;
          server_name  sito.org;
  
          root         /usr/share/nginx/html;
          index index.html index.htm;
  
          # Add headers to serve security related headers
          # Before enabling Strict-Transport-Security headers please read into this
          # topic first.
          #add_header Strict-Transport-Security "max-age=15768000; includeSubDomains; preload;";
          add_header X-Content-Type-Options nosniff;
          add_header X-XSS-Protection "1; mode=block";
          add_header X-Robots-Tag none;
          add_header X-Download-Options noopen;
          add_header X-Permitted-Cross-Domain-Policies none;
  
          # Load configuration files for the default server block.
          include /etc/nginx/default.d/*.conf;
          include /etc/nginx/sites-enabled/*.conf;
  
          location / {
              try_files $uri $uri/ =404;
          }
  
          error_page 404 /404.html;
              location = /40x.html {
          }
  
          error_page 500 502 503 504 /50x.html;
              location = /50x.html {
          }
          
          location ~ (\.php$) {
              return 403;
          }
          
      listen [::]:443 ssl ipv6only=on; # managed by Certbot
      listen 443 ssl;                  # managed by Certbot
      ssl_certificate /etc/letsencrypt/live/defalcoalfano.org/fullchain.pem; # managed by Certbot
      ssl_certificate_key /etc/letsencrypt/live/defalcoalfano.org/privkey.pem; # managed by Certbot
      include /etc/letsencrypt/options-ssl-nginx.conf; # managed by Certbot
      ssl_dhparam /etc/letsencrypt/ssl-dhparams.pem; # managed by Certbot
      }
  
      # add other enabled servers
      include /etc/nginx/sites-enabled/*;
  }

Alcune osservazioni.

Alcune linee hanno il commento ``# managed by Certbot``, queste sono state
introdotte dal software per il rilascio del certificato ssl del sito.
Ne riparliamo tra poco. In questa fase **NON** saranno presenti.

Vi sono riferimenti alla directory ``/etc/nginx/sites-enabled``. Questa è un
tecnica che facilita la gestione dei siti da mettere in (o togliere dalla) 
linea. In pratica:

* si mette un file di configurazione del sito in ``/etc/nginx/sites-available``,
* e si abilita il sito creando un link da ``/etc/nginx/sites-enabled``
  alla configurazione predetta.
  
Ad esempio creiamo o copiamo nel file
``/etc/nginx/sites-available/www.sito.org.conf`` il seguente:

.. code:: nginx
  :number-lines:

  upstream gunicorn_handler {
    server unix:/usr/share/nginx/html/base/run/gunicorn.sock fail_timeout=10s;
  }
  
  server {
      listen   80;
      server_name www.sito.org;
  
      root         /usr/share/nginx/html/base;
      index index.html index.htm;
  
      client_max_body_size 4G;
  
      access_log /usr/share/nginx/html/base/logs/access.log;
      error_log  /usr/share/nginx/html/base/logs/error.log warn;
  
      location /static/ {
          autoindex on;
          alias   /usr/share/nginx/html/base/sito/static_root/;
      }
  
      location /media/ {
          autoindex on;
          alias   /usr/share/nginx/html/base/sito/media/;
      }
  
      location / {
          proxy_set_header X-Forwarded-For $proxy_add_x_forwarded_for;
          proxy_set_header Host $http_host;
          proxy_redirect off;
          
          if (!-f $request_filename) {
              proxy_pass http://gunicorn_handler;
              break;
          }
      }
  
      location ~ (\.php$) {
          return 403;
      }
  
   # managed by Certbot
  
      listen 443 ssl; # managed by Certbot
      ssl_certificate /etc/letsencrypt/live/luciano.defalcoalfano.it/fullchain.pem; # managed by Certbot
      ssl_certificate_key /etc/letsencrypt/live/luciano.defalcoalfano.it/privkey.pem; # managed by Certbot
      include /etc/letsencrypt/options-ssl-nginx.conf; # managed by Certbot
      #ssl_dhparam /etc/letsencrypt/ssl-dhparams.pem; # managed by Certbot
      ssl_dhparam /etc/ssl/certs/dhparam.pem;  # better Diffie-Hellman params
  }
  
  server {
      if ($host = luciano.defalcoalfano.it) {
          return 301 https://$host$request_uri;
      } # managed by Certbot
  
  
      server_name www.sito.org;
      listen 80;
      return 404; # managed by Certbot
  }


Di nuovo, ipotizziamo che le linee commentate come ``# managed by Certbot``
in questa fase non esistano.

Le linee da 1 a 3 della configurazione, istruiscono Nginx ad usare 
il socket ``gunicorn.sock`` per comunicare con l'applicazione *Django*
quando si richiede il dominio ``www.sito.org``.

Le linee da 17 a 25 istruiscono Nginx a servire direttamente 
i contenuti statici dell'applicazione, senza impegnare *Django*.

Quindi, per abilitare il sito dobbiamo linkarlo da enabled
e riavviare Nginx:

.. code:: console

  ln -s /etc/nginx/sites-available/www.sito.org.conf /etc/nginx/sites-enabled/
  nginx -t                        # controlla la sintassi dei file di config.di Nginx
  systemctl restart nginx         # riavvia il web server


**Altre operazioni**
======================

Passiamo ad alcune operazioni finali, di solito molto utili.

**Disabilitare selinux**
--------------------------

Questo sarebbe meglio non farlo, e spendere il tempo necessario per
configurare opportunamente i profili delle aree dati impattate da Nginx
e dall'applicazione *Django*. Ma, andando di fretta:

.. code:: console

  sestatus                       # per controllare
  setenforce Permissive
  vim /etc/sysconfig/selinux     # modificare a: SELINUX=disabled
  
**Modificare i permessi di scrittura**
----------------------------------------

Questo è fondamentale, altrimenti Nginx non sarà in grado di gestire 
i flussi di dati:

.. code:: console

  cd /usr/share/nginx/http
  chown nginx:nginx base        # qui NON -R perché coinvolgerebbe venv
  cd base
  chown -R nginx:nginx sito
  chown -R nginx:nginx log
  chown -R nginx:nginx run
  
Per sicurezza, verificare che in ``.../base/venv/bin/gunicorn_start``
valgano le seguenti:

.. code:: bash

  ...
  USER=root        # the user to run as
  GROUP=root       # the group to run as
  ...
  
A questo punto, se da WEB browser richiediamo il dominio
http://www.sito.org dovrebbe rispondere la nostra applicazione.

Il condizionale è d'obbligo :-) debug, debug, 
troubleshoot, troubleshoot, ... [8]_
  
**Installare un certificato SSL tramite Let's Encrypt**
--------------------------------------------------------

Quando avremo verificato che l'applicazione risponde all'indirizzo
Web previsto utilizzando il protocollo http, usualmente avremo 
necessità di abilitare anche, o esclusivamente, il protocollo
https.

A questo fine dovremo ottenere ed installare un certificato ssl
relativo al sito in configurazione.

Qui entra in campo `Let's Encrypt <https://letsencrypt.org/>`_, un
servizio che rilascia certificati ssl/tls senza necessità di acquisto,
*ed agisce come certification authority (CA)*. Quindi i certificati rilasciati
da *Let's Encrypt* sono validi a tutti gli effetti.

Come ottenere e installare questi certificati in un server *CentOS 7*
è documentato in:
`How To Secure Nginx with Let's Encrypt on CentOS 7 <https://www.digitalocean.com/community/tutorials/how-to-secure-nginx-with-let-s-encrypt-on-centos-7>`_

Qui si seguito sintetizziamo utilizzando la strada più semplice, che nel nostro caso
consiste nell'usare l'applicazione ``certbot`` per nginx:

.. code:: console

  # yum install epel-release          # già installato
  yum install certbot-nginx           # installa certbot x nginx
  # genera il certificato e modifica la configurazione di nginx
  certbot --nginx -d sito.org -d www.sito.org           # rispondere alle domande
  # genera un certificato con parametri Diffie-Hellman migliori
  openssl dhparam -out /etc/ssl/certs/dhparam.pem 2048
  
Attenzione a modificare la configurazione di ``www.sito.org.conf`` aggiungendo
la linea 49.

Vi sono **rari** casi in cui si ha la necessità di generare certificati autofirmati.
Ad esempio se si lavora in TLD di tipo ``.local``.

In questi casi si può usare questa procedura:

.. code:: console

  # directory per le chiavi private (cert x i certificati pubblici deve già esistere)
  mkdir /etc/ssl/private
  chmod 700 /etc/ssl/private
  # generare una chiave e relativo certificato pubblico
  openssl req -x509 -nodes -days 365 -newkey rsa:2048 -keyout /etc/ssl/private/nginx-selfsigned.key -out /etc/ssl/certs/nginx-selfsigned.crt
  # generare un Diffie-Hellmann group
  openssl dhparam -out /etc/ssl/certs/dhparam.pem 2048
  # controllare la configurazione di /etc/nginx/sites-available/www.sito.org.conf

**Regolare l'orario**
----------------------

Quando si effettua debugging, è comune la necessità di controllare gli
orari riportati nei file di log per capire quando è successo qualcosa.

E qui sorge il problema del confronto con il *proprio* orario. Già, perché
solitamente un server utilizza il fuso orario UTC, che spesso non 
é quello utilizzato dal client. Ad esempio lavorando su Roma, è normale 
essere un'ora in anticipo rispetto UTC.

Quindi può essere comodo regolare l'orario del server su quello del client,
come segue:

.. code:: console

  timedatectl set-timezone "Europe/Rome"
  timedatectl set-time 15:58:30
  timedatectl set-local-rtc 1
  
Al termine delle attività di debugging, ricordarsi di riportare
il sever su UTC:

.. code:: console

  timedatectl set-timezone UTC   # prima del rilascio mettersi in UTC


**Riferimenti**
================

La procedura è stata costruita consultando (creativamente :-) le indicazioni dei riferimenti
riportati qui di seguito. Cui si rimanda per i dovuti approfondimenti.

* Il riferimento principale è stato:
  `Deploying nginx + django + python 3 <https://tutos.readthedocs.io/en/latest/source/ndg.html>`_
* `How-to install Python 3.6.1 on CentOS 7 <https://janikarhunen.fi/how-to-install-python-3-6-1-on-centos-7.html>`_
* `How To Set Up Django with Postgres, Nginx, and Gunicorn on Ubuntu 16.04 <https://www.digitalocean.com/community/tutorials/how-to-set-up-django-with-postgres-nginx-and-gunicorn-on-ubuntu-16-04#install-the-packages-from-the-ubuntu-repositories>`_
* `django documentation: how to deploy with WSGI <https://docs.djangoproject.com/en/2.0/howto/deployment/wsgi/#how-to-deploy-with-wsgi>`_
* `How to use Django with Gunicorn <https://docs.djangoproject.com/en/2.0/howto/deployment/wsgi/gunicorn/>`_
* `Which WSGI server should I use? <https://djangodeployment.com/2017/01/02/which-wsgi-server-should-i-use/>`_
  per decidere di utilizzare Unicorn come server Wsgi;
* `How to Deploy a Django Application on RHEL 7 <https://simpleisbetterthancomplex.com/tutorial/2017/05/23/how-to-deploy-a-django-application-on-rhel.html>`_ 
  come procedura generale per l'installazione.
  
  
**Note**
==========

.. [1] Ripresa da 
   `installare nginx su centos 7 <https://www.digitalocean.com/community/tutorials/how-to-install-nginx-on-centos-7>`_

.. [2] Ripresa da 
   `How-to install Python 3.6.1 on CentOS 7`_

.. [3] Grazie a 
   `Standalone Django scripts: The definitive guide <https://www.stavros.io/posts/standalone-django-scripts-definitive-guide/>`_
   
.. [4] Più in generale, Gunicorn mette a disposizione di una qualunque applicazione Python
   un modo di comunicare dati detto wsgi (alias: Web Server Gateway Interface),
   inventato dai *pythonisti* per comunicare tra applicazione Pyhton e un ipotetico 
   WEB server.
   
.. [5] Ovvero da `Deploying nginx + django + python 3`_

.. [6] Questo è *outing* accompagnato da cenere cosparsa sul capo, e la intima
   convinzione che capiterà di nuovo :-)
   
.. [7] In questo caso:
   ``chmod +x /usr/share/nginx/htm/base/venv/bin/gunicorn_start``
   
.. [8] Riflettendo, probabilmente il troubleshooting di una
   configurazione di produzione vale un articolo a parte. Ci
   penseremo e, se avremo tempo e capacità, vedremo di scrivere qualcosa.