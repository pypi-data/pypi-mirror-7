function iframe_callback(action, model, pk, content, message, method) {

    if (action == "change") {
        tr = $("<div></div>").append(content).find("tr")
        arraydata = []
        $(tr).children().each(function(){
            data = $(this).html();  
            arraydata.push(data)
        })
        idx =  datatables[inlinetable.index('.dataTable')].fnGetPosition(rowtable[0]);
        datatables[inlinetable.index('.dataTable')].fnUpdate(arraydata,
        idx, undefined, true, undefined,
        datatablesettings[inlinetable.index('.dataTable')]);
    }

    if (action == "add") {
        tr = $("<div></div>").append(content).find("tr")
        if (!(datatables[inlinetable.index('.dataTable')])){
            inlinetable.append(content)
            element = $("[pk=" + pk + "]")
        }
        arraydata = []
        $(tr).children().each(function(){
            data = $(this).html();  
            arraydata.push(data)
        })
        datatables[inlinetable.index('.dataTable')].parents(".results").show()
        datatables[inlinetable.index('.dataTable')].fnAddData(arraydata, true,
        datatablesettings[inlinetable.index('.dataTable')])
    }

    if (action == "delete") {
    
         $( tr).animate({height:0}, 1000,function(){
        	idx =  datatables[inlinetable.index('.dataTable')].fnGetPosition(tr[0]);
            datatables[inlinetable.index('.dataTable')].fnDeleteRow( idx,
            function(){}, true, datatablesettings[inlinetable.index('.dataTable')]);
         });
        
    }
    if(message){
        if( $("ul.messagelist").length==0){
		    $(".breadcrumbs").after("<ul class='messagelist'></ul>")
	    }
	    $("ul.messagelist").html($("<li class='info'></li>").html(message))
	}
	dialog.dialog("close")
	if (method == "_json_continue"){
        rowtable.find(".edit").click()
    }
    if (method == "_addanother"){
        inlinetable.parents(".module").find(".linkadd").click()
    }
    
}

var inlinetable = false
var rowtable = false
var tr = false
var datatables =[];
var datatablesettings =[];

$(document).ready(function ($) {

	$(".ajaxinline-group").each(function(){
		var cols = $(this).find("thead tr th").length
		var aoColumns = []
		for (var i=0;i<cols-2;i++)
            { 
            aoColumns.push(null)
            }
            
		aoColumns.push({ "bSortable": false })
		aoColumns.push({ "bSortable": false })
           
		var dat = $(this).find('table').dataTable( {
	        "bPaginate": false,
	        "bInfo": false,
	        "oLanguage": {
	            "sSearch": gettext("Search"),
	            "sZeroRecords": gettext("No records to display"),
	            "sInfoEmpty": gettext("No entries to show")
	          },
	          "aoColumns": aoColumns,
	          "fnRowCallback": function( nRow, aData, iDisplayIndex, iDisplayIndexFull ) {
                if (typeof table_callback == 'function') { 
                    table_callback(); 
                }
              }
	    } );
	    
	    datatables.push(dat)
		datatablesettings.push($.fn.DataTable.settings[0])
	})
	
        
    $(".linkadd").on("click", function () {
        inlinetable = $(this).parents(".module").find("table")
    })
    

    $("body").on("click", ".edit", function () {
        rowtable = $(this).parents("tr")
        inlinetable = $(this).parents(".module").find("table")
    })

    $("body").on("click", ".delete", function () {
        inlinetable = $(this).parents(".module").find("table")
        href = $(this).attr('href')
        tr = $(this).parents('tr')
    })
    
    
    
})

function RefreshTable(tableId, urlData)
    {
       $(nRowObject).find("TD").each( function(i) {
          var iColIndex = oSettings.oApi._fnVisibleToColumnIndex( oSettings, i );
          oSettings.oApi._fnSetCellData( oSettings, iRowIndex, iColIndex, $(this).html() );
    } );
  }
    
