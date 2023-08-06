.. _jmb.javascript:

javascript
==========

Si utilizza jquery 1.9 e jquery.ui 1.10, da locale e non da remoto, per
le esigenze di alcuni clienti.  le librerie sono fornite da jmb.core e
sono richieste all'interno del template del :file:`base_site.html`.

``jmb.core`` fornisce una liberia :file:`jmb.core.js` che ha le seguente
funzionalità

jmb.hide_input()
----------------

Solo nella ``change_form`` al caricamento della pagina vengono nascosti i
fields con type hidden ovvero con widget HiddenInput, utile sia nell'EDIT
che nell'ADD passando l'attributo tra gli initial.

Un esempio in cogema.contratto admin.py::

    self.fields['contratto']  = forms.ModelChoiceField(
                queryset=Contratto.objects.all(), required=False,
                widget=forms.widgets.HiddenInput()
           )

jmb.show_in_popup(classe, callback)
-------------------

* show_in_popup(src, title, width, height, callback)

  funzione per mostrare un URL nell iframe sfrutta le modali di
  ``jquery.ui``, usa il resize, si adatta alla dimensione dell'iframe. 
  ``URL`` è l'url da aprire esempio::

       jmb.show_in_popup("http://google.it")
       
  la callback predefinta è vuota, viene chiamata alla chiusura della modale
  per esempio si può usare::
       show_in_popup(src, title, width, height, function(){ parent.chiusura() })
    
vedi documentazione completa :ref:`show_in_popup` 
        
jmb.stickytab()
---------------

Aggiunge il position fixed allo scroll della pagina.
per utilizzarlo aggiungere la classe stickytab all'elemento
.. https://github.com/garand/sticky

jmb.iframe_hjson_link(callback)
-----------------------

Ai link con classe iframe, hsjon e popup, aggiunge come suffisso
il parametro _hjson=1&_popup=1, e apre il link in un iframe
la modalità hjson, funziona solo nei casi di change e di add e delete
al save la pagina viene rediretta su un template iframe che chiama
la iframe_callback del parent ovvero della pagina che ha 
chiamato l'iframe, questa funzione va implementata sempre

* iframe_callback(action, model, pk, html, message)

la callback predefinta è vuota, viene chiamata alla chiusura della modale
esempio::
    jmb.iframe_hjson_link(function(){ parent.chiusura() })



