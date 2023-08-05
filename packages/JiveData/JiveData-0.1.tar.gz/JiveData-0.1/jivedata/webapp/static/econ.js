var current;
var next;

$(document).ready(function(){
  $("#options_row").show();
  $('#collapseOne').collapse('show');
  current = $("#current").text();
  next = $("#next").text();
  $(window).bind('scroll', loadOnScroll);
});

$("#most_viewed").change(function(){
	update_settings({'most_viewed': $('#most_viewed').is(':checked') }, base_path);
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
   
function pager(){
	$("#datagrid").find('tbody').append($('<tr id="loading" style="border-bottom:0px;">').append($('<td colspan="4" style="text-align:center">').append($('<i class="fa fa-spinner fa-spin fa-lg"></i>'))));
  	var html = [];
    $.ajax({
    type: 'GET',
    url: '/econ/',
 		headers:{'cache-control':'no-cache'},
 		cache: false,
    data: {page: next},
    dataType:'json'
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

//autocomplete
$(function(){
	 current_location = window.location.pathname.toString();
	 $("#series").autocomplete({
     minLength: 1,
     source: function(request, callback){
	    $.getJSON('/econ/search/',request,function(data){
	       callback(data.results);
	    });
	  },
     select: function(event, ui){
	   update_settings({'series': ''}, '/econ/' + ui.item.id);
	   return false;
     }
    }).data('ui-autocomplete')._renderItem = function(ul,item){
		var re = new RegExp(this.term,"i");
	    var name = item.name.replace(re,"<span style='font-weight:bold;color:#000;'>" + "$&" + "</span>");
	    var details = "<small><span style='color:#666;'>" + item.start+" to " + item.end + ", " + item.frequency + ", " + item.units + ", " + item.saar + "</span></small>";
	    return $("<li></li>").data("item.autocomplete",item).append("<a>" + name + "<br>" + details + "</a>").appendTo(ul);
	};
  });

$('#series').click(function(){ // clear the fund
  var abc = document.getElementById('series');
  if(abc.value != ''){  
    $(this).val('');
  }
});

$('.clear_all').click(function(){ // clear the series
	$('#series').val('');
    update_settings({'series':''}, '/econ/');
});



