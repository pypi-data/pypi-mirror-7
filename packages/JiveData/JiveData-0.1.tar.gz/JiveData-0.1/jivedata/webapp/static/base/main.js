var path_array = window.location.pathname.split('/');
var base_path = '/' + path_array[1] + '/';

(function(doc) { //Keeps the iphone scale in tact after we focus on a form or combobox, etc 
    var scales = [1, 1],
	    meta = 'querySelectorAll' in doc ? doc['querySelectorAll']('meta[name=viewport]') : [];

	function fix() {
		meta.content = 'width=device-width,minimum-scale=' + scales[0] + ',maximum-scale=' + scales[1];
		doc.removeEventListener('gesturestart', fix, true);
	}
	if ((meta = meta[meta.length - 1]) && 'addEventListener' in doc) {
		fix();
		scales = [.25, 1.6];
		doc['addEventListener']('gesturestart', fix, true);
	}
}(document));


$(document).ready(function(){
	if(/iPhone|iPad|iPod/i.test(navigator.userAgent)){ /* change keyboard on mobile...only apple stuff for now as I don't know how android/blackberry reacts */
  	    if($("#email").length > 0) { /* make sure it is the DOM first, otherwise this will block any other functions you may have */
  	        document.getElementById('email').type = 'email';
  	    }
	}
});

function update_settings(updated_data, url){ // update our session variables
	var now = new Date();
    var n = now.getTime();
    $.ajax({  
        url: "/update_settings/?time=" + n,
        type: "GET",
        headers: {"cache-control":"no-cache"},
        cache: false,
        data: updated_data,
        dataType: 'json'
	})
    .done(function(data){ 
        if(url != false){
    	    if(data.result){
    		    location.href = url;
    		}
    	}
	});		  
}

function update_user(updated_data){ // update a user's watchlist and/or funds list
	var now = new Date();
    var n = now.getTime();
    $.ajax({  
        url: '/update/?time=' + n,
        type: 'GET',
        headers: {'cache-control':'no-cache'},
        cache: false,
        data: updated_data,
        dataType: 'json'
	})
	.done(function(data){ 
	    location.reload();
	});		  
}
