var current;
var next;

$(document).ready(function(){ 
	$("#options_row").show();
	$('#collapseOne').collapse('show');
	    
	current = $("#current").text();
	next = $("#next").text();
	$(window).bind('scroll',loadOnScroll);
});

var loadOnScroll = function(){	
	if($(window).scrollTop() > $(document).height() - $(window).height() - 100){
	   $(window).unbind();
	   if(next === 'None'){ // the end. stop getting new data
	       return false; 
	   }
	   pager();
	   }
    };
	
    $('#watchlist_view').click(function () {
		update_settings({'watchlist_view': $('#watchlist_view').is(':checked')}, base_path);
	});
	$(document).on('change','#planned',function(){
		update_settings({'planned':$('#planned').is(':checked')}, base_path);
	});
	$(document).on('change','#insiders',function(){
		update_settings({'insider':$('#insiders').prop('selectedIndex')}, base_path);
	});
	
function pager(){
	$("#datagrid").find('tbody').append($('<tr id="loading" style="border-bottom:0px;">').append($('<td colspan="3" style="text-align:center">').append($('<i class="fa fa-spinner fa-spin fa-lg"></i>'))));
    $.ajax({
	    type: 'GET',
	    url: '/insiders/',
	    headers: {"cache-control":"no-cache"},
	    cache: false,
	    data: {page: next},
	    dataType: 'json'
	})
   .done(function(data){  
	    current = data.pagination.current;
	    next = data.pagination.next;
	    $("#datagrid > tbody:last").append(data.html);
	    $(window).bind('scroll', loadOnScroll);
	    if(next === null){ // no more records
	    	next='None';
	   		var htmlString='<tr style="height:50px;border-bottom:0px;"><td colspan="3" style="text-align:center">No More Records</td></tr>';
	   		$("#datagrid > tbody:last").append(htmlString);
	   		return false; 
	   	}
  })
  .always(function(){
  	$("#loading").remove();
  });
 }