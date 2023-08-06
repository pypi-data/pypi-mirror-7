.. _buildout-env:

===========================
Installazione con buildout
===========================

Scopo del setup illustrato qui di seguito è:

* Creare un workflow in cui il setup di un sito sia fulmineo, almeno per
  quanto riguarda il lavoro umano...

* Creare una setup isolato e riproducibile. Le librerie utilizzate devono
  essere sotto stretto controllo del programmatore

* Deve essere possibile derogare se necessario (ad esempio non vogliamo
  ricompilare il modulo 'uno' necessario per collegarsi a Libreoffice)

Possibili alternative
======================

le alternative possibili sono 

1. virtualenv_

2. buildout_ (ricca documentazione su pypi_)

Mentre virtualenv risulta particolarmente efficace per l'isolamento,
buildout risulta più pratico per la configurabilità. Noi useremo
``buildout`` e costruiremo dentro un virtualenv in modo automatico. Entrambi
richiedono di compilare alcuni pacchetti quindi devono essere installati
anche alcuni pacchetti dev.


.. note::

  Buildout ha recentemente rilasciato un ramo >= 2.0 che NON possiamo usare
  in quanto la principale ricetta che usiamo (tl.buildout_virtual_python_)
  non è stata ancora portata. O usiamo la 1.7.1 o la 1.5.2-sd.

Buildout in pratica
===================

L'installazione di jumbo e dei siti che lo usano viene fatta usando
``buildout`` nel seguente modo::

   hg clone http://hg.thundersystems.it/siti/www.mysite.it
   cd www.mysite.it
   python bootstrap.py
   bin/buildout 
   dj    # equivalente a bin/django shell = ./manage.py shell


Configurazioni una tantum
==========================

Questo semplice sistema prevede che siano state prese alcune precauzioni una
volta nel sistema (non per ogni pacchetto/sito) e che sia stato
personalizzato il sistema opportunamente. Il modo facile è installando il
pacchetto ``thunder-buildout`` dai repositori argo ma raccomando di leggere
anche :ref:`l'installazione manuale <buildout-manual>` dove spiego i vari componenti.

installazione tramite pacchetto deb
-----------------------------------

Occorre installare il pacchetto ``thunder-buildout`` che è un pacchetto che
contien pochi file ma molte dipendenze, ad esempio libreoffice che viene
usato in molti progetti per produrre le stampe.

.. note::
    
   al momento fa partire in automatico libreoffice all'avvio del pc, questo
   non è opportuno per i nostri pc personali e quindi verrà modificato a
   breve. 

Aggiungere la sorgente argodef::

     echo deb http://apt.argolinux.org precise main >> /etc/apt/sources.list
     apt-get update
     apt-get install thunder-buildout

Attenzione che il pacchetto installa una situazione funzionante
comprensiva delle seguenti configurazioni:

   * configurazione in :file:`/root/.buildout` (leggi in seguito)
     
   * configurazione in :file:`/home/www` (leggi sotto)

   * fornisce i comandi 

     :dj_: interazione fondamental, equivalente a ``manage.py`` ma chiama 
	   Python nell'ambiente virtuale corretto e può essere chiamato da
	   qualunque sottocartella del progetto. Utile anche per generare
	   documentazione e fare upload della stessa

     :py_: chiama ip python dell ambiente virtuale

     :ipy_:  chiama ipython dell'ambiente virtuale

     :jmb-test-setup_: utile strumento per testate quali pacchetti sono
		       presenti nell'ambiente viutuale, generare i link ai
		       repositori (vedi sotto), manipolare i repo sotto ``.src``

     :jmb-start_: starter di ogni applicazione. Crea un
		  progetto/applicazione nuovi a partire da un template che
		  viene tenuto costantemente aggiornato a come vogliamo che
		  siano i progetti/applicazioni

     :jmb-prepare_: crea i pacchetti e cura l'upload nel nostro repository pipy_

     :jmb-go_: una script che permette un avvio rapido di progetti

Struttura cartelle
===================

Il comandi riportati sopra (file:`python boostrap.py` e file:`bin/buildout`)
creano una struttura come la seguente::

  .
  |-- bin
  |    `--python         << eseguibile "isolato"
  |-- .develop-eggs       << egg-link ai sorgenti
  |-- parts
  |   |-- buildout
  |   `-- vpython        << virtual evironment
  `-- .src
      |-- jmb.core    <<  codice sorgente (hg clone ...)
      |-- ...


mentre altre eggs saranno depositate nella cartella indicata nella
configurazionedi default ``~/.buildout/default.cfg``.

Sotto :file:`.src` troviamo tutti i sorgenti di cui è stato fatto il
checkout, ovvero quei sorgenti richiesti nella configurazione. È possibile
ed è lasciata libertà (dalla ricetta, non da me) di scegliere se sostituirlo
con un link simbolico. Spesso è la cosa più opportuna e per sostiture tutti
i link in un sol colpo potete usare il comando::

  jmb-test-setup -l


buildout.cfg
============

buildout usa "ricette" ed "estensioni" per implementare le cose che vogliamo
fare.  Le ricette che ho scelto puntano a:

.. _tl.buildout_virtual:

:creare un ambiente isolato:

  questo è compito di tl.buildout_virtual_python_, il compito è quello di
  fare in modo che il nostro ambiente non "veda" nessuna libreria di sistema
  in modo da essere sicuri che le librerie dichiarate in ``setup.py`` e in
  buildout.cfg siano le uniche necessarie.

.. _django-recipe:

:creare ambiente per django:

  questo è compito di djangorecipe_: crea un binario chiamato ``django``
  che è l'equivalente di ``manage.py`` ma che ha già impostato il path nel
  modo corretto: ogni volta che avremmo suato ``./manage.py`` suiamo questo
  in alternativa per avere un ``manage.py`` che opera sullo stesso ambiente
  virtuale. Ad esempio::
  
    bin/django test
    bin/django runserver
    bin/django shell

  djangorecipe crea anche una configurazione per wsgi che però è
  incompatibile con il virtualenv, vedi :ref:`wsgi` per leggere la soluzione.

:usare i nostri sorgenti:

  questo è compito di mr.developer_. Buildout può lavorare in modo ``eggs``
  o ``develop``. In sostanza per ogni libreria dichiarata in
  ``${vpython:eggs}`` verrà creata una voce di sys.path che punta ad una
  cartella egg.


Suggerisco di creare la configurazione iniziale con jmb-start_, ma riporto un
esempio di :file:`buildout.cfg` che non è completo::

  [buildout]
  extends = thunder-buildout.cfg
  develop = .                  # dichiariamo la cartella corrente 
                               # come cartella in sviluppo

  parts = req django ipython
  extensions = mr.developer
  auto-checkout = *
  sources-dir = .src

  [vpython]                     # creiamo un ambiente isolato analogo 
                                # a quello creato da virtualenv

  recipe = tl.buildout_virtual_python
  eggs = tl.buildout_virtual_python
	 cybergun
	 jumbo-core
	 jumbo-contacts 
	 jumbo-ecommerce

  extra-paths = ${thunder:extra-paths}
  site-packages = false          # come --no-site-packages di virtualenv
                                 

  [req]
  recipe = zc.recipe.egg
  python = vpython             # forza l'uso dell'ambiente virtuale
  eggs = babel
  interpreter = py

  [sources]
  # le sorgenti elencate qui sono automaticamnete messe 
  # nelle develop-egg quindi disponibili senza bisogno di aggiungerle nelle egg
  jmb.core = hg ${thunder:jmb2}/jmb.core
  jmb.openvpn = hg ${thunder:jmb2}/jmb.openvpn

  [django]
  recipe = djangorecipe
  settings = tsettings
  eggs = django
  python = vpython      
  absolute_path = True

  [ipython]
  recipe = zc.recipe.egg
  python = vpython      
  eggs =  ipython

.. _setup.py:

setup.py
=========

Tutto il sistema di packaging di Python si basa sulla configurazione
contenuta in ``setup.py`` in particolare nella direttive:

:name: nome del pacchetto (es.: jumbo-core)

:install_required:

   dipendenze esplicite del pacchetto::
   
      ['setuptools', 'xlwt', 'xlrd', 'django <= 1.2.7']


:packages:

   pacchetti messi a disposizione (es.: ['admin_tools',  'jumbo', ...])
   nella maggior parte dei casi va bene il default scritto nel template
   usato da jmb-start_::

       packages=find_packages(exclude=['tests', 'tests.*'])
   
:version:

   è la versione di un pacchetto, indispensabile per potere fissare le rel
   che veramente funzionano

:package_data: 

   sono i file che devono essere inclusi nel pacchetto anche se non sono
   moduli python: file css, js, html, png e txt. Oltre che qui vanno
   segnalati anche in MANIFEST.in. Il progetto di default mostra lesempio di
   come fare questo. Nel setup.py di default è inclusa la funzione
   ``get_data_files`` per facilitare l'inclusione degli stessi.


Una esauriente introduzione al setup può essere letta qui_

===============
Utilities
===============

.. _jmb-start:

jmb-start
=========

Per rendere più facile ed immediato partire con un nuovo progetto, ed in
attesa di creare un vero sistema di templating, ho creato
una semplice script che prende un mini-template per un progetto ed inserisce
già la configurazione per ``buildout.cfg``, ``setup.py``, ``MANIFEST.in`` ed
una intera struttura. Per un progetto sarà::

  jmb-start -t cms -vbm nome-progetto

o alternativamente per una app::

  jmb-start -t japp jmb.miapp

es::

   jmb-start -t japp jmb.timereport

Volendo aggiungere la struttura buildout ad un progetto esistente è
possibile usare l'opzione ``-e``, questa sovrascrive i file esistenti (che
sono sicuramente sotto controllo di versione), rendendo immediato capire
cosa va fatto per aggiornare il progetto/applicazione esistente all'ultma
versione del relativo template


È importante scrivere le dipendenze per ogni project/application direttamente
nel :file:`setup.py` come scritto sopra piuttosto che nel file
:file:`buildout.cfg` così che vengano correttamente ereditate da ogni altro
progetto che dichiari questo come dipendenza. Le dipendenze espresse in
:file:`buildout.cfg` devono servire o per integrare pacchetti di terze parti
non ben configurate (es.: manca dipendenza da PIL in ``sorl-thunmbnail``) o
per imporre una determinata versione, nel qual caso occorre usare la sezione
``[versions]`` (attenzione al case)::

  [versions]
  Django == 1.4.3-sd
  django == 1.4.3-sd   # mi pare siano letti solo in minuscolo

``jmb-start`` copia anche una versione di :file:`.hgignore`, ed un
tsettings.py che viene usato come default, sta a voi correggere a mano.


dj
==

il comando di gran lunga più utilizzato sarà ``bin/django`` che è
l'equivalente di ``manage.py``. Con lo script ``dj``
sarà possibile chiamarlo anche da sottocartelle del progetto nel modo
corretto. Senza argomenti è equivalente a ``bin/django shell``. 

La documentazione può essere prodotta da::

  dj docs

e può essere uploadata sul sito ufficiale_ con::

  dj -u docs   # nota l'opzione prima del pacchetto!!!

Leggere l'help prodotto da ``dj -h`` per ulteriori scorciatoie.

py
==

Lancia l'interprete Python dell'ambiente virtuale.
Analogamente a ``dj``, ``py`` chiama bin/py in ogni sotto cartella


ipy
===

Lancia l'interprete IPython dell'ambiente virtuale. Utile quando ``dj`` non
parte per problemi di configurazione di ``django``.
Analogamente a ``dj``, ``ipy`` chiama bin/py in ogni sotto cartella

jmb-test-setup
===============

Questa script permette di mostrare quali versione dei pacchetti sono incluse
nell'ambiente virtuale.

jmb-prepare
===========

Questa script permette di testare una aspetto della configurazione che può
facilmente sfuggire:  che siano inclusi nella distribuzione i file di dati,
ovvero quelli che non sono moduli python: css, html, png, js, txt. Crea una
distribuzione binaria e controlla quali file vengono effettivamente
inclusi. I file inclusi sono controllati da MANIFEST.in e dalla apposita
funzione get_data_files in setup.py.

Le opzioni -m e -b permettono di creare la distro binaria e sorgente e di
metterla nella cache di buildout (vedi help)::

  jmb-prepare -m    # crea .tar.gz nella cache locale
  jmb-prepare -u    # carica in pypi.thundersystems.it (via ssh)
  jmb-prepare -b    # crea egg per locale

jmb-go
======

Questa banale script esegue una serie di piccole operazioni che portano il
repo appena clonato o generato a funzionare::

  dj syncdb --all --noinput
  dj migrate --all --fake
  dj createsuperuser --username $SUPERUSER --email $EMAIL
  dj collectstatic --noinput $LINK

In sviluppo usa l'opzione ``-l`` di collectstatic, così facendo

* usa meno disco

* non è necessario lanciarlo nuovamente in caso di *modifica* dei file
  statici (l'aggiunta invece lo richiede ugualmente, così come la modifica
  dei file di dajax/dajaxice) 


jmb-sync
========

Questa script permette di sincronizzare un db remoto in uno locale facendo
un dump del remoto, un eventuale dump del locale ed usando rsync fra i due,
in questo modo è estremamente efficace.

Si basa su un file di configurazione (``.sync``) nella cartella del progetto
e NON legge la configurazione dai settings di django ed opera solo via ssh
(quindi è necessario avere la chiave di root sulla macchina remota).

È in grado di instaurare un ponte ssh in modo da sincronizzare anche db
dietro firewall.

jmb-deps
========

Fa un report delle dipendenze di un pacchetto basandosi su

* l'analisi del log di ``buildout -Nv``
* il file setup.py del progetto e di tutte le sottocartele di .src
* il file buildout.cfg
* le informazioni delle eggs dichiarate nelle dipendenze sopra citate

Può essere utile in alcune circostanze, ma sicuramente fallisce in altre.

.. _wsgi:

wsgi
====

djangorecipe_ crea una configurazione di wsgi che è incompatibile con il
virtualenv. La versione modificata da me (sandro) mette la versione corretta.

La motivazione è che il modulo indicato nella configurazione di
apache, viene importato da una istanza di python che non è isolata, mentre
il meccanismo necessario per rendere disponibili i pacchetti del porgetto
(le eggs) e basato sull'uso dei file ``.pth`` che risiedono solo in alcune
cartelle definite in fase di compilazione. È possibile aggiungere altre
cartelle con il comando ``site.addsitedir()``. La mia versione aggiunge::

  import site
  site.addsitedir(${buildout:directory} + \
                  '/parts/vpython/lib/python2.x/site-packages')

  
.. _link-statici:

Creazione link simbolici
==========================

Questa sezione è obsoleta. Con ``jmb.*`` non è più necessaria.

La configurazione di default crea automaticamente una cartella site-packages
con i link simbolici agli egg che contengono il pacchetto. Viene creata
dalla ricetta links per cui vanno solo messi i nomi dei pacchetti per cui si
vuole creare il link, ad esempio::

  [links]
  targets = jumbo-core
            jumbo-timereport

Documentazione
===============
La documentazione sta in docs. Nella configurazione standard viene
automaticamente creata ``bin/docs`` una script che genera la documentazione
e rigenera docs/Makefile in modo che punti ai file corretti con l'ambiente
corretto. 

.. note::

  al momento viene creata con un nome errato per la variabile
  ``DJANGO_SETTINGS_MODULE``. Per le apps occorre lasciare solo ``tsettings``.
  
Può essere chiamato semplicemente con::

  dj docs

Per le application occorre dichiarare come settings: tsettings nella
sezione [django] ed aggiungere::

  absolute_path = True

È possibile fare l'upload in http://docs.thux.it semplicemete aggiungendo
l'opzione -u  ``dj -u docs``

Test
======

i test per le application stanno in nome_application/tests/__init__.py e
possono essere lanciati con::

   dj t

equivalente a ``python manage.py test``. 


Troubleshooting
================

Esistono alcuni problemi tipici quando si crea un ambiente con
buildout. Vediamo di capirli e di capire come risolverli:

python bootstrap.py
-------------------

Attualmente questo comando non dà problemi se si usa l'utima versione di
bootstrap.py_. Alcun progetti/application più vecchi hanno una versione
precedente che va aggiornata e che scarica buildout >= 2.0 che non è
compatibile con la ricetta :ref:`tl.buildout_virtual <tl.buildout_virtual>` 

bin/buildout -N
---------------

Questo può dare molti errori differenti, in generale imputabili ad errori
di configurazione dei pacchetti da cui dipende il singolo progetto.

jmb.organization-light
.......................

::

  Error: There is a version conflict.
  We already have: jmb.organization-light 0.2.1

Questo è causato dal fatto che abbiamo 2 pacchetti che forniscono il package
jmb.organization, uno con nome jmb.organization ed uno con nome
``jmb.organization-light``. Il secondo viene trovato per primo e installato e
questo confligge con la richiesta di installare ``jmb.organization``.

L'unica soluzione funzionante che ho trovato è stato di installare il
pacchetto ``jmb.organization`` come sorgente::

  jmb.organization = hg ${thunder:jmb2}/jmb.organization

Error: Bad constraint 0.6.1 django-sekizai>=0.7
................................................

Questo errore viene introdotto da django-cms. non essendo io un eperto di
django-cms e finchè non ci sarà una spiegazione chiara ho trovato che
imponendo ``django-cms>=2.3,<2.4`` si bypassa il problema

Source URL for existing package 'jmb.organization' differs. Expected
......................................................................

Errore che capita solo se si usa la versione che scarica i pacchetti
sorgente via http, non via ssh. Il motivo sta nel fatto che hg clone
nasconde la password nel file :file:`.hg/hgrc` e quando successivamente va a
vedere quale URL abbia il repository, non trova corrispondenza.

La soluzione (brutta), è di aggiungere a mano la password nel repository

Non installa un pacchetto 
..........................

Se siete sicuri che il pacchetto sia dichiarato nelle dipendenze, provate a
cancellare il file :file:`.installed.cfg` nella cartella del progetto e
rilanciate :command:`bin/buildout`.




.. _tl.buildout_virtual_python: https://bitbucket.org/tlotze/tl.buildout_virtual_python/
.. _djangorecipe: http://pypi.python.org/pypi/djangorecipe/1.3
.. _mr.developer: http://pypi.python.org/pypi/mr.developer
.. _virtualenv: http://www.virtualenv.org/en/latest/index.html
.. _buildout: http://www.buildout.org/
.. _buidldout_pypi: http://pypi.python.org/pypi/zc.buildout/1.5.2
.. _virtualenv: http://www.virtualenv.org/en/latest/index.html
.. _pypi: http://pypi.python.org/pypi/zc.buildout/1.5.2
.. _qui: http://docs.python.org/distutils/sourcedist.html
.. _pipy: http://pypi.thundersystems.it
.. _ufficiale: http://docs.thux.it
.. _bootstrap.py: http://downloads.buildout.org/1/bootstrap.py
