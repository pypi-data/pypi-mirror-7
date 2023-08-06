===============================
Struttura e Workflow
===============================


La versione :ref:`Jumbo <jumbo>` che usiamo ora prevede che 

* sviluppo e deploy siano fatti in ambiente virtuale. Noi usimo
  :ref:`buildout <buildout-env>`

* Ogni pacchetto deve essere creato come pacchetto Python corredato di
  :ref:`setup.py` funzionante, soprattutto in merito alle dipendenze che
  devono essere opportunamente dichiarate

* I pacchetti possono essere usati come sorgente o come pacchetto, a seconda
  del livello di sviluppo. I pacchetti rilasciati vengono caricati sul sito
  pypi_

* progetti e pacchetti nuovi devono essere generati con :ref:`jmb-start` che
  genera un template di application/progetti che riflette le scelte fatte
  (ovvero quali pacchetti usare per i singoli problemi, es filtri ricerca,
  autocompletion, ajax, javascript...)

.. _pypi: http://pypi.thundersystems.it
