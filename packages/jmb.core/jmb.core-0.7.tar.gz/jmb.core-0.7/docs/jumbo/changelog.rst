Changelog
==========

rel 0.7
--------
* Admin tabs: now tabular/stacked inlines can be used rather then their models
* checkbox: label on left side
* change_list: modified to pass over _popup (used in nested iframe)
* added MboxEmailBackend
* requires django-filters-sd_0.7a1-sd6 that adds "search in selection"

rel 0.6.2
----------

* fix date-time picker
* porting to 1.6
* detail icon: now fixed width (partial)

rel 0.6.1
------------

* fix: ajax_inlines/monkey patch/porting
* export: works also for functions


rel 0.6
-------

* aggiunte le :ref:`admin_tabs` 

* aggiunte le  :ref:`ajax_inline`

* aggiunta monkey-patch per runserver :ref:`monkey-errors` per trovare
  facilmente quali campi creano errori

* riordinata la libreria :ref:`jmb.core.js <jmb.javascript>` e
  standardizzato il modo di aprire finestre in iframe

* aggiunt plugin jQuery ``dataTable`` per riordinare tabelle. Questa
  versione ha una piccol modifica perchÃ© l'originaria non si comportava bene
  con molte tabelle nella pagina.

* aggiunta classe :ref:`EmailMessageCalendar <ics>` per invio semplicifato
  di appuntamenti ``vcalendar``

* aggiunta :ref:`autocompletion dinamica <dynamic-autocompletion>`

* ora dipende da admin_tools_0.5.1-sd2 che corregge i css ed aggiunge un
  ritardo via javascript nella scomparsa dei menu

In concomitanza con questa release jmb-start:

* impone admin_tools-sd2 che fixa il menu che usa funzioni coerenti con
  jQuery 1.9.1 

* aggiunge il plugin ``jquery-migrate`` richiesto all'interno di 
  ``bootstrap_generic.html`` per compatibilità dei plugin fatti per 
  jQuery < 1.9. riguarda principalmente alcune funzioni del cms.

rel 0.5
-------

* non richiede più una versione specifica di django in quanto fa
  :ref:`monkey patching <monkey>` 

* aggiunge il layout a :ref:`tabs <admin_tabs>`  nell'admin

* supporta Django 1.5 e Django 1.6 ma:

  + stiamo ancora usando cms 2.3 che supporta solo Django 1.4
   
  + django-toolbar support Django-1.6 solo dalla rel 1.0.1 che però
    confligge con dajaxie (quando si lancia ``dj collectstatic``).

  Il modo più semplice di provare Django 1.5 ed 1.6 è di usare 
  l'ultima versione di jmb-start rispettivamente così::

    jmb-start -t p15 -a prj.django.test

    jmb-start -t p16 -a prj.django.test

  Nuove dipendenze: django-dajax => django-dajax-ng, djangoice-dajax => django-dajaxice-ng
