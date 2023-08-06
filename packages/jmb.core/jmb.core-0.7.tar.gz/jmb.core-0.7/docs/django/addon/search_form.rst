.. _advanced-search:

============
Search_form
============

Scopo
======
Rimpiazzare la ricerca semplice dell'admin di Django con una ricerca
selettiva per campi. 

Scenario
=========

una patch di sicurezza_ del 23/12/2010 ha aggiunto un metodo di ModelAdmin
``lookup_allowed()`` che prende un lookup (eg.: ``user__username``) e
ritorna un booleano per sapere se può essere utilizzato o meno.

Questa patch influenza sicuramente django 1.4+ che aggiunge molte modifiche
al sistema di filtri di admin.

Qui_ c'è un blog sul modo di bypassarlo e tanti riferimenti al problema. 
Djangosnippets, riporta uno snippet_ che affronta la questione in modo analogo.
 
In sintesi i filtri ammessi per default sono solo quelli inseriti nella lista
``list_filters``, in altenativa si può modificare lookup_allowed().

Componenti
==========
* Un oggetto ChangeList e la sua derivata
  :class:`jmb.core.admin.main.JmbChangeList`

  Questa classe ha 2 metodi rilevanti per noi:

  :get_filters: che prepara tutti i filtri. Noi prima di questa chiamata
    modifichiamo la copia dei parametri in GET in modo che siano già stati
    puliti dai metodi clean_* della form

  :get_query_set: ritorna il queryset applicando i filtri

* La form necessaria per creare il link che verrà usato in GET. Questa form
  viene creata automaticamente a partire dal campo
  ``ModelAdmin.advanced_search_fields`` 

* Un inclusion templatetag (``advanced_search_form``) che renderizza la form
  e che a sua volta utilizza il template ``advanced_search_form.html`` e viene
  chiamato così::

   {% block advanced_search %}{% advanced_search_form cl %}{% endblock %}

  Il tag riceve quindi l'oggetto ``ChangeList`` in argomento ed utilizza il
  suo metodo ``.cl.model_admin.get_search_form`` per trovare la
  ``search_form`` idonea. 

* :attr:``jmb.core.admin.options.ExtendedModelAdmin.lookup_allowed``

Utilizzo
========

Nella implementazione più semplice basta creare l'attributo
``ModelAdmin.advanced_search_fields`` come tupla di tuple con field_names::

   class CertificateAdmin(ExtendedModelAdmin):
       model = Certificates
       advanced_search_fields = (
	       ('start_date__gte','user'),
	       ('user__username__icontains', 'user__last_name__icontains', ),
	       ('status', 'description__icontains',),
	       )

Nel caso serva una personalizzazione più ricca è possibile utilizzare il
metodo ``ModelAdmin.get_filterset`` e fare ritornare una classe che eredita
da :class:``django_filters.Filterset``.

django-filters
===============

Rispetto al pacchetto originario di ``django-filters`` le nostre aggiunte
permettono di:

* dichiarare il lookup_type nel nome del campo. È quindi possibile
  srivere ``start__date__gte`` per impostare come lookup_type ``gte``. In
  questo modo non è necessario dichiarare il filter in modo dichiarativo solo
  per l'impostazione del ``lookup_type``

* riempire i campi con *choices* secondo il field dichiarato nel modello

* aggiunge ai booleani l'opzione nulla (``-----``)

* quando il ``lookup_type`` è ``in`` viene usato il widget di scelta
  multipla

* quando una data ha il ``lookup_type`` ``range`` viene usato un widget che
  permette di scegliere fra oggi, ieri, ultimi 7 giorni, ultimo mese, mese
  precedente, anno in corso, anno precedente.


Altri filtri
==============

Nella change list compaiono i bottoni per ricerca semplice, ricerca avanzata
e filtri secondo questa logica:

:ricerca semplice: se definito l'attributo ``search_fields``

:ricerca avanzata: se definito ``advanced_search_fields`` in
		   modeladmin o l'attributo ``filterset_class``

:filtri: se definito l'attributo list_filter_

Personalizzazioni
==================

Jumbo (per Django 1.2.7) utilizzava una JChangeList preparata per manipolare
le date utilizzando :func:`django.utils.translation.get_format_date`` che
ora è soppiantato da ``django.utils.format_date``.

Con l'attuale sistema le date vengono interpretate come localizzate.


Implementazione
================

L'attuale implementazione di basa su questi elementi:

:django-filters: modificata da noi, vedi sopra
:change_list.html: il template usato è quello contenuto in ``jmb.core``
		   È importante che ``admin/change_list.html`` di ``jmb.core``
		   venga usato al posto di quello di ``django.contrib.admin``,
		   questo è ottenuto impostando nelle ``installed_apps``
		   ``jmb.core`` al primo posto (il
		   template.loader.app_directories usa INSTALLED_APPS ): qui
		   vengono messi 2 nuovi templatetags

          :advanced_search_form: un templatetag che implementa la ricerca avanzata
          :jsearch_form: un template tag che implementa la toolbar della
			 ricerca

:ExtendibleModelAdmin.setup_advanced_search: crea il filterset a partire da
					     ``advanced_search_fields`` o
					     ``search_filterset_class`` o ``get_filterset__class``
:ExtendibleModelAdmin.lookup_allowed: permette ogni ``search_field``
:ExtendibleModelAdminget.changelist: return JmbChangeList
:ExtendibleModelAdminget.queryset: Se c'è un filtro, qui viene restituito il
				   qs generato da search_filterset.qs
:JmbChangeList.get_filters: All'interno di questo metodo pulisco self.params
:advanced_search.js: 
     * gestione di visibilità advanced_search_form
     * serialize dei soli campi non vuoti

.. _sicurezza: https://github.com/django/django/commit/732198ed5c
.. _Qui: http://www.hoboes.com/Mimsy/hacks/fixing-django-124s-suspiciousoperation-filtering/lookup_allowed-gets-new-parameter-value/
.. _snippet: http://djangosnippets.org/snippets/2322
.. _list_filter: https://docs.djangoproject.com/en/dev/ref/contrib/admin/#django.contrib.admin.ModelAdmin.list_filter
.. _seacrch_fields: https://docs.djangoproject.com/en/dev/ref/contrib/admin/#django.contrib.admin.ModelAdmin.search_fields
