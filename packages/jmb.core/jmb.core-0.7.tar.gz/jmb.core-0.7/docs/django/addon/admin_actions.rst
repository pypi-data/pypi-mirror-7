.. _admin-actions:

================
Admin actions
================


in questa sezione vengono elencate le admin actions personalizzate presenti in jmb.core_:


clone_action
============

permette di duplicare gli item selezionati nella ``changelist_view`` con una nuova pk.
Questa action va abilitata esplicitamente nell'ExtendibleModelAdmin.

Utilizzo
--------

effettuare l'import dell'action::
	
  from jmb.core.admin.options import clone_action
	
ridefinire o aggiungere la action tra le actions presenti::

  actions = (clone_action,)


.. _jmb.core: http://docs.thux.it/jmb.core
