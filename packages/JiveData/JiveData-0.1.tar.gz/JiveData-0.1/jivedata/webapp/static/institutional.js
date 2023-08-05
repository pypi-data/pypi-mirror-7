var current;
var next;

$(document).ready(function () { 
	$("#options_row").show();
	$('#collapseOne').collapse('show');
	current = $("#current").text();
	next = $("#next").text();
	$(window).bind('scroll', loadOnScroll);
	$("#my_funds_view").change(function(){
		update_settings({'my_funds_view': $('#my_funds_view').is(':checked') }, base_path);
	});
});

var loadOnScroll = function(){	
    if ($(window).scrollTop() > $(document).height() - ($(window).height()*1.50)){
       $(window).unbind();
       if(next === 'None'){ // the end. stop getting new data
   	  	 return false; 
       }
       pager();
    }
   };

function pager(){
  $("#datagrid").find('tbody').append($('<tr id="loading" style="border-bottom:0px;">').append($('<td colspan="4" style="text-align:center">').append($('<i class="fa fa-spinner fa-spin fa-lg"></i>'))));
  var html = [];

  $.ajax({
	  type: 'GET',
	  url: '/13F/',
	  headers: {"cache-control":"no-cache"},
	  cache: false,
	  data: {page: next},
	  dataType: 'json'
  })
  .done(function(data){
	current = data.pagination.current;
	next = data.pagination.next;
    $('#datagrid > tbody:last').append(data.html);
   
    $(window).bind('scroll', loadOnScroll);
    if(next === null){ // no more records
    	next='None';
 		var htmlString='<tr style="height:50px;border-bottom:0px;"><td colspan="4" style="text-align:center">No More Records</td></tr>';
 		$("#datagrid > tbody:last").append(htmlString);
 		return false; 
	}
  })
  .always(function(){
  	$("#loading").remove();
  });
 }

// autocomplete
$("#fund").autocomplete({
	selectFirst: true,
    minLength: 1,
    source: function(request, callback){
    $.getJSON('/13F/search/', request, function(data){
       callback(data.results);
    });
  },
  select: function(event,ui){
	update_settings({'fund':''}, base_path + ui.item.cik);
    return false;
  },
  open: function(){
    $('.ui-menu .ui-menu-item a').css('word-wrap','break-word');
	 }
}).data("uiAutocomplete")._renderItem = function(ul,item){
    var re = new RegExp(this.term,"i");
    var v = item.name.replace(re,"<span style='font-weight:bold;color:#000;'>" + "$&" + "</span>");
    var aum = '';
    if(item.aum != ''){
      var aum = '<br><small><span style="color:#666;">'+ item.latest_filing +' Reported AUM: ' + item.aum + '</span></small>';
    }
    return $("<li></li>").data("item.autocomplete",item).append('<a>' + v + aum + '</a>').appendTo(ul);
};

$('#fund').click(function(){ // clear the fund
  var abc = document.getElementById('fund');
  if(abc.value != ''){  
    $(this).val('');
  }
});

$('#clear_all').click(function(){ // clear the fund
  var abc = document.getElementById('fund');
    $('#fund').val('');
    update_settings({'fund':''}, base_path);
});

$('#institution_add').click(function(){ 
	d = JSON.stringify({'item': 'funds', 'action': 'add'}); // we'll get the cik from the session variable
	update_user({'params':d});
});

