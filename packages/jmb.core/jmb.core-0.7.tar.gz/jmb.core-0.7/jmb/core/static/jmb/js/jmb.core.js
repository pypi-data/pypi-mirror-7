//NAME space di jmb 
if (window.jmb == undefined) window.jmb = {};

// fissa a 10px la larghezza delle colonne edit/delete nella change-list
jmb.fix_width_edit_delete = function () {
    $(function(){
        $("[field=v], [field=e], [field=d]").parent("th").width("10px").css("textAlign","center")
    });
}
//nasconde i campi nascosti nella change-form, che hanno name initial
jmb.hide_input = function () {
    $(function(){
        $(".form-row div input[type=hidden]:not([name*='initial'])").parent("div").hide()
    });
}

//funzione per le admin tab, colora di rosso se sono presenti errori e apre la tab giusta
jmb.error_tab = function () {
     $(function(){
        $(".admintab-content .tab-pane").each(function(){
            var errors = $(this).find(".errors").length
            var errorslist = $(this).find(".errorlist li").length
            if(errors || errorslist){ 
                $("a[href='#"+  $(this).attr("id")+"']").addClass("taberror")
                $("a[href='#"+  $(this).attr("id")+"']").append('<span class="badge badge-important">'+ (errors + errorslist) +'</span>')
            }
        })
     });
    
}

//funzione per le admintab per averle sempre fisse in alto anche se si scorre
jmb.stickytab = function () {
    $(function(){
        //https://github.com/garand/sticky
        $(".stickytab").sticky({topSpacing:1, bottomSpacing:1});
    });
}


//i link con classe iframe vengo aperti nel popup, e possibile avere una funzione di callback
jmb.iframe_hjson_link = function (callback) {
	if(typeof(callback) == "undefined") callback  = function(){}
    $(document).on("click", ".iframe", function () {
    	jmb.last_link = this
        link = $(this).attr("href")
	if (link.indexOf('?') < 0) {
           link += '?'
        } else {
           link += '&'
        }
    	origin = ($("body").hasClass("change-form")) ? "&_origin=change-form" : ""
    	origin = ($("body").hasClass("change-list")) ? "&_origin=change-list" : ""
        if ($(this).hasClass("hjson")) link += "_hjson=1&_popup=1" + origin;
        var title = $(this).attr("title")
        var width = $(this).attr("width")
        var height = $(this).attr("height")
        jmb.show_in_popup(link, title, width, height,callback)
        return false;
    });

}
//funzionalità per il multi autocomplete, ora anche per tabularinline
jmb.autocomplete_filterby_patch = function () {

    yourlabs.Autocomplete.prototype.makeXhr = function () {
    	auto = this
        if (this.filterBy) {
            filters = this.filterBy.split("||")
            autocomplete = this
            $(filters).each(function (k, v) {
                filter_key = v.split("|")[0]
                dom_element = v.split("|")[1]
                if ($(dom_element).length == 0){
                	index = auto.input.attr("id").match(/([0-9])+/g)[0]
                	dom_element = dom_element.replace("-x-","-" + index +"-")
                }
                filter_value = $(dom_element).val()
                if (filter_value && typeof (filter_value) == "object") filter_value = filter_value[0]
                if (filter_value) {
                    autocomplete.data[filter_key] = filter_value
                }
            })
        }
        this.xhr = $.ajax(this.url, {
            type: "GET",
            data: this.data,
            complete: $.proxy(this.fetchComplete, this)
        });
    }

}

jmb.auto_popup = function (classe,callback) {
	if (!(classe)) classe = 'a.iframe';
    jQuery(document).ready(function($) {
	    $(classe)
		    .click(
			    function() {
			        var src = $(this).attr("href")
			        suffix = (src.indexOf("?") !=-1) ?"&_popup=1" : "?_popup=1"
				    src+=  suffix
				    var title = $(this).attr("title")
				    var width = $(this).attr("width")
				    var height = $(this).attr("height")
				    jmb.show_in_popup(src, title, width, height,callback)
				    return false;
			    })
    })
}

//apre il popup
jmb.show_in_popup = function (src, title, width, height, callback) {
	if(typeof(callback) == "undefined") callback  = function(){}
    if (!(src)) return false;
    var title = title || " "
    var width = width || 1000
    var height = height || 500
    var iframe = $('<iframe id="popiframe" frameborder="0" marginwidth="0" marginheight="0" allowfullscreen></iframe>');

    dialog = $("<div></div>").append(iframe).appendTo("body")
    $(dialog).dialog({
        autoOpen: false,
        modal: true,
        resizable: true,
        width: "auto",
        height: "auto",
        close: function () {
            iframe.attr("src", "");
            callback()
        },
        open: function (event, ui) {
            iframe.attr({
                width: '100%',
                height: '90%'
            });
            iframe.parents(".ui-dialog").css(
                'width', width);
            $(".ui-dialog-content").css('overflow', 'hidden');
                
                
            $(".ui-dialog-titlebar-close").html("X")
            dialog.parent().height(parseInt(height) + 10)
            dialog.height(height)
        }
    });
    iframe.attr({
        width: +width,
        height: +height,
        src: src
    });
    $(dialog).dialog("option", "title", title)
    $(dialog).dialog("open");

    return true;
}

//funzione chiamata dal return delle pagine con hjson
jmb.iframe_callback = function(action, model, pk, content, message, method) {
    if (action == "change") {
        tr = $("<div></div>").append(content).find("tr")
        //aggiunge la checkbox e sostiutisce il tr con quello nuovo
        $(tr).prepend('<td class="action-checkbox"><input class="action-select" name="_selected_action" type="checkbox" value="'+pk+'"></td>')
        row = $(jmb.last_link).parents("tr")
        row.html(tr.html())
    }
    
    if (action == "add") {
       // da implementare in futuro
    }

    if (action == "delete") {
    	row = $(jmb.last_link).parents("tr")
        $(row).hide("slow", function() {
        	// ricolora blu e bianco le righe alternate
        	$(row).parents("tbody").find("tr:visible:even").addClass("row1").removeClass("row2")
        	$(row).parents("tbody").find("tr:visible:odd").addClass("row2").removeClass("row1")
        });
        
    }
    if(message){
    	//aggiunge il messaggio se presente
        if( $("ul.messagelist").length==0){
		    $(".breadcrumbs").after("<ul class='messagelist'></ul>")
	    }
	    $("ul.messagelist").html($("<li class='info'></li>").html(message))
	}
	dialog.dialog("close")
	
	if (method == "_json_continue"){
		//caso del salva e continua
		$(jmb.last_link).click()
    }
    if (method == "_addanother"){
    	row = $(jmb.last_link).parents("tr")
    	tr = $("<div></div>").append(content).find("tr")
        $(tr).prepend('<td class="action-checkbox"><input class="action-select" name="_selected_action" type="checkbox" value="'+pk+'"></td>')
    	$(row).after(tr);
    	$(row).parents("tbody").find("tr:visible:even").addClass("row1").removeClass("row2")
    	$(row).parents("tbody").find("tr:visible:odd").addClass("row2").removeClass("row1")
    }
    
}

iframe_callback = jmb.iframe_callback