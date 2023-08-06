Postgresql
===========

Nella copia di un db, ed in generale quando si manipolano i dati imponendo
l'ID è possibile che le 'sequence' collegate all'incremento automatico di un
dato non siano più impostate correttamente.

È possibile lanciare una funzione che resetta al valore massimo utilizzato.

Suggerisco questo metodo, rubato da stackoverflow_

 1. aggiungere una funzione nel db chiamata reset_sequence
 2. eseguire una select che richiama questa funzione

reset_sequence
---------------

:: 

  CREATE OR REPLACE FUNCTION "reset_sequence" (tablename text, columnname text)
  RETURNS "pg_catalog"."void" AS
  $body$
  DECLARE
  BEGIN
      EXECUTE 'SELECT setval( pg_get_serial_sequence(''' || tablename || ''', ''' || columnname || '''),
      (SELECT COALESCE(MAX(id)+1,1) FROM ' || tablename || '), false)';
  END;
  $body$  LANGUAGE 'plpgsql';

Eseguirla
----------

::

  SELECT table_name || '_' || column_name , reset_sequence(table_name,   column_name) 
  FROM information_schema.columns where column_default like 'nextval%';


Dovendo fixare una singola tabella, la riga è::

  SELECT setval('your_table_id_seq', (SELECT MAX(id) FROM your_table_name))

.. _stackoverflow: http://stackoverflow.com/a/14633145/555236
