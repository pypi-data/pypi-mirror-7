.. _buildout-manual:

===================================
Buildout: installazione manuale
===================================

1. Occorre disabilitare -se esiste- il sistema buildout perché confligge con
   quello che verrà scaricato in automatico::

     apt-get remove python-zc.buildout

   per potere compilare suggeriscodi installare::

     python-dev, libpq-dev,  postgresql-server-dev-8.4 | postgresql-dev , 
     libxslt1-dev, libsasl2-dev, libjpeg62 | libjpeg8,    
     libjpeg8-dev | libjpeg62-dev, libfreetype6, 
     libfreetype6-dev, zlib1g-dev, python-uno, mercurial, libldap2-dev


   in particolare:

   :libsasl2-dev: serve per compilare ldap, richiesto da django-ldap-groups
       e fornisce :file:`sasl.h`
   
   :libxslt1-dev: è necessario per compilare lxml
   
   :libpq-dev: è necessario per compilare psycopg2

   :libjpeg62 | libjpeg8: per PIL con render jpg

2. Occorre configurare una cache locale ed il puntatore ai repository::

      ~ $ cat ~/.buildout/default.cfg

      [buildout]
      eggs-directory = /home/tuonome/.buildout/eggs
      download-cache = /home/tuonome/.buildout/download-cache

      [thunder]
      jmb = /usr/local/src/jumbo-new
      jmb2 = /usr/local/src/hg/thunder/jmb2
      dj = /usr/local/src/hg/thunder/django
      # jmb = http://read:letmeread@hg.thundersystems.it/jumbo-new/
      # jmb2 = http://read:letmeread@hg.thundersystems.it/jumbo2/
      # dj = http://read:letmeread@hg.thundersystems.it/django/
      extra-paths = /home/local/.buildout/extra-path
      
3. Crea una cartella con dei link a librerie che vuoi vengano viste dal
   sistema isolato ma che non vuoi dovere compilare in buildout. Useremo
   questa princialmente per evitare di ricompilare la libreria ``uno`` di
   OpenOffice::

      mkdir ~/.buildout/extra-path
      cd  ~/.buildout/extra-path
      ln -s /usr/lib/python2.6/dist-packages/uno.py
      ln -s /usr/lib/python2.6/dist-packages/unohelper.py

Nota che buildout NON espande correttamente ``~`` che va quindi scritta
in esplicito. La cartella della cache e quella delle egg non sono
indispensabili ma accelerano immensamente il deploy.

La sezione ``[thunder]`` imposta invece la posizione dei
repository. Conviene farli puntare alla copia locale invece che a quella
remota per ovvii vantaggi di velocità.
