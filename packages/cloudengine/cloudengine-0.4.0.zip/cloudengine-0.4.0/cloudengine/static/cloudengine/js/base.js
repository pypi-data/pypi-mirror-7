var apps = [];
var myspinner = new Spinner({
	  lines: 13, // The number of lines to draw
	  length: 7, // The length of each line
	  width: 4, // The line thickness
	  radius: 10, // The radius of the inner circle
	  corners: 1, // Corner roundness (0..1)
	  rotate: 0, // The rotation offset
	  color: '#000', // #rgb or #rrggbb
	  speed: 1, // Rounds per second
	  trail: 60, // Afterglow percentage
	  shadow: false, // Whether to render a shadow
	  hwaccel: false, // Whether to use hardware acceleration
	  className: 'spinner', // The CSS class to assign to the spinner
	  zIndex: 2e9, // The z-index (defaults to 2000000000)
	  top: 'auto', // Top position relative to parent in px
	  left: 'auto' // Left position relative to parent in px
});

$(function () {
	
	$.ajaxSetup({
	    beforeSend: function(xhr, settings) {
	        if (!csrfSafeMethod(settings.type) && sameOrigin(settings.url)) {
	        	var csrftoken = $.cookie('csrftoken');
	            xhr.setRequestHeader("X-CSRFToken", csrftoken);
	        }
	    }
	});
	
	
	$('#newAppModal').on('hidden', function () {
	    $("#create-app-error-msg").html();
	    $("#input-app-name").val("");
	});
	
	$('#newAppModal').on('shown', function () {
	    $("#input-app-name").val("");
	    $("#input-app-name").focus();
	});
	
	
	
	$("#btn-create-app").click(function(){
		
		var appname = $("#input-app-name").val();
	/*	if (false === $('#new_app_form').parsley().validate())
	        return;
		*/
		$.ajax({
			
			type:"POST",
			url: "/api/v2/apps/" + appname + "/",
			context: document.body
			
		}).success(function(data){
			
			$("#newAppModal").modal("hide");
			$("#new-app-id").append(data.id);
			$("#appCreatedModal").modal("show");
			
		}).error(function(xhr, status, error){
			
			$("#newAppModal").modal("hide");
			try{
				result = JSON.parse(xhr.responseText)
				var $err_msg = result.detail;
			}	
			catch(err){
				var $err_msg = "Server Error";
			}
			$("#create-app-error-msg").html("");
			$("#create-app-error-msg").append($err_msg);
			$("#appCreateErrorModal").modal("show");
			
		});
		
	});
	
});



function csrfSafeMethod(method) {
    // these HTTP methods do not require CSRF protection
    return (/^(GET|HEAD|OPTIONS|TRACE)$/.test(method));
}

function sameOrigin(url) {
    // test that a given url is a same-origin URL
    // url could be relative or scheme relative or absolute
    var host = document.location.host; // host + port
    var protocol = document.location.protocol;
    var sr_origin = '//' + host;
    var origin = protocol + sr_origin;
    // Allow absolute or scheme relative URLs to same origin
    return (url == origin || url.slice(0, origin.length + 1) == origin + '/') ||
        (url == sr_origin || url.slice(0, sr_origin.length + 1) == sr_origin + '/') ||
        // or any other URL that isn't scheme relative or absolute i.e relative.
        !(/^(\/\/|http:|https:).*/.test(url));
}




function update_apps_list($scope, $store){

	//  $my_session_apps = $store.get("session_apps");
	  
	  // todo: update the localStorage applist when an app is created or deleted 
	  
	/*  if(($my_session_apps != undefined) ||($my_session_apps != null)){
		  
		  $scope.apps = $my_session_apps;
		  
		}
		
	  else{*/
		  
		  ///// Get apps list from the server
		  myspinner.spin($("#spinner")[0]);
		  
		  $.get("/api/v2/apps/", function(data){
			  applist = data["results"];
			  myspinner.stop();
			 $scope.$apply(function(){
				 $scope.apps = applist; 
			 });
			  
			 
			  //$store.set("session_apps", applist);
			  
			});  
	//  }
}








