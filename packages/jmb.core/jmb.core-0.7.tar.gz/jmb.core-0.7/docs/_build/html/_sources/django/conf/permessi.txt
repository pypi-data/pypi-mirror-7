==========
Permessi
==========

L'attenzione a garantire i giusti permessi  non troppo stretti e neanche
troppo laschi è molto importante per il tipo di applicazioni per cui usiamo
Jumbo.

Gestione permessi
==================

.. automodule:: jmb.core.management.commands.add_permissions

Managers
=========

In alcuni moduli dove è  necessario gestire la visibilità di ogni singolo
record, si è scelta la via di usare dei manager per implementare i permessi.

Questo ha reso necessario propagare l'informazione dello user (normalmente
aggiunta alla request) fino all'interno del manager. Questo compito è svolto
dal middleware :ref:`thread-local` che memorizza lo user nel thread.
