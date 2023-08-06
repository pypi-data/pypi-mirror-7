.. _show_in_popup:

================
Popup via iframe
================

Lo scopo è far aprire un popup, in jquery ui chiamata dialog o modale
al click di un link. Con un iframe con sorgente il link stesso.
si può attivare su qualsiasi link della change_list
aggiungendo la classe iframe.
il sistema aggiunge automaticamente il parametro _popup=1
la dimenensione della finestra per default è 1000x500.
questi parametri sono configurabili mettendoli come attributo del link

vedi libreria jmb completa :ref:`jmb.javascript` 

chiamata singola
================
Nel caso si voglia utilizzare la funzione singolarmente
si può utilizzare 

jmb.show_in_popup(src, title, width=1000, height=500, callback = function(){})

* src -> sorgente dell iframe
* title -> titolo della modale
* width e height -> altezza e larghezza della modale
* callback -> funzione triggerata alla chiusura della modale
* ritorna l'apertura dell iframe nella modale (true)

esempio
=======

in admin.py::

  def get_add_assistance(self, obj):
	  return """
		 <a class='iframe' href='%(reverse_url)s?_popup=1&ticket=%(ticket_id)s'
		 </a>""" % {
			  'reverse_url': reverse('admin:ticket_ticketassistance_add'),
			  'ticket_id': obj.id
		 }

  get_add_assistance_.allow_tags = True

aggiungere nella change_list.html::

    <script>
        // classe predefinita a.iframe
        jmb.auto_popup(classe, callback)
    </script>

dipendenze
==========

* jQuery e jQuery ui
* popup.js e jmb.core.js
