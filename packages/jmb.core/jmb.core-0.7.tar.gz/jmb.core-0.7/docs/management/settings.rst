==========
Settings
==========

I settings di default vengono presi dal modulo 'settings' all'interno. È
compito di una funzione apposita chiamata dall'``__init__`` di ogni modulo
di aggiungere questi default ai settings di django se non è stato già
definito. Questo viene gestito direttamente dallo starter :ref:`jmb-start`

.. automodule:: jmb.core.conf

jmb.core settings
=================

In aggiunta ci sono alcuni settings specifici di ``jmb.core``:

:RUNNING_DEVSERVER: usato nella patch :ref:`monkey-errors`. 
