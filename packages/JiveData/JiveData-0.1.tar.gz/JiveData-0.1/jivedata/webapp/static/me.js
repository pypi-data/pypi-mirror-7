$(document).ready(function () { 
	count_rows();
});

var count_rows = function(){
	var rows = $('#watchlist > tbody > tr').length;
	if(rows==0){
		$('#watchlist').toggle();
		$('#empty_watchlist').toggle();
	}
	rows = $('#funds_list > tbody > tr').length;
	if(rows==0){
		$('#funds_list').toggle();
		$('#empty_funds').toggle();
	}
}

$('#watchlist .delete').on('click',function(){
	var cik = $(this).siblings('.cik').text();
	d = JSON.stringify({'item':'watchlist', 'action': 'delete', 'cik': cik});
	update_user({'params':d});
});

$('#funds_list .delete').on('click',function(){
	var cik = $(this).siblings('.cik').text();
	d = JSON.stringify({'item':'funds', 'action': 'delete', 'cik': cik});
	update_user({'params':d});
});
