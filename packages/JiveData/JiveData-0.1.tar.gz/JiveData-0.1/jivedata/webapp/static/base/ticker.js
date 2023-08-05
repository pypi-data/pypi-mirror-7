$("#tickers").autocomplete({
    minLength: 1,
    source: function(request, callback){
        $.getJSON('/ticker/', request, function(data){
            callback(data.results);
        });
    },
    select: function(event,ui){
  	    d = JSON.stringify({'cik': ui.item.cik, 'ticker': ui.item.ticker, 'name': ui.item.name})
	    update_settings({'watchlist': false}, false);
	    update_settings({'ticker': d}, base_path + ui.item.cik);
        return false;
    }
}).data('ui-autocomplete')._renderItem = function(ul,item){
	var re = new RegExp(this.term, 'i');
    var ticker = item.ticker.replace(re, "<span style='font-weight:bold;color:#000;'>" + "$&" + "</span>");
    var name = item.name.replace(re, "<span style='font-weight:bold;color:#000;'>" + "$&" + "</span>");
    return $("<li></li>" ).data("item.autocomplete", item).append(ticker == '' ? "<a>" + name + "</a>" :  "<a>" + ticker + ":&nbsp;" + name + "</a>").appendTo(ul);
};

$('#tickers').click(function(){ // clear the ticker
    var abc = document.getElementById('tickers');
    if(abc.value != ''){
        $('#tickers').val('');
    }
});

$('#clear_all').click(function(){ // clear the ticker and re-set session variable
    $('#tickers').val('');
    update_settings({'ticker':'{}'}, base_path);
});

$('#wl_add').click(function(){ 
	d = JSON.stringify({'item': 'watchlist', 'action': 'add'}); // we'll get the cik from the session variable
	update_user({'params':d});
});



