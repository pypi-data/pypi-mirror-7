.. _conf:

================
Configurazione
================

urls.py
=======

in urls.py devono essere avviati i vari autodiscover::

 dajaxice_autodiscover()
 autocomplete_light.autodiscover() 
 admin.autodiscover()
 admin_tools.dashboard.autodiscover()

in aggiunta devono essere aggiunti i pattern per la localizzazione. 
:ref:`jmb-start` dovrebbe fare questo in automatico.

.. _monkey:

=============
Monkey Patch
=============

.. automodule:: jmb.core.monkey
