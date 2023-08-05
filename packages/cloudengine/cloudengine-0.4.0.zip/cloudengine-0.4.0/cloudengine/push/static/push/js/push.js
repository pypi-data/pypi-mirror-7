 $app_object = null;

(function() {

	 var $msg_form = $("#push-msg-form");
	 $msg_form.bind('submit', function(){

		 	var $input = $(this).find('textarea');
			$message = $input.val().trim();
			
			if(($message == '') || ($message == null)){
				alert('Please enter a notification message');
				return false;
			}
			
			if($app_object == null){
				alert('Please select an app first');
				return false;
			}
			
			$input.val('');
			
		 	myspinner.spin($("#spinner")[0]);
			$.ajax({
		         url: "/api/v2/push/",
		         type: "POST",
		         data: {"message": $message},
		         beforeSend: function(xhr, settings){
		        	 
		        	 	xhr.setRequestHeader('AppId', $app_object.key);
		        	 	if (!csrfSafeMethod(settings.type) && sameOrigin(settings.url)) {
		    	            // Send the token to same-origin, relative URLs only.
		    	            // Send the token only if the method warrants CSRF protection
		    	            // Using the CSRFToken value acquired earlier
		    	        	var csrftoken = $.cookie('csrftoken');
		    	            xhr.setRequestHeader("X-CSRFToken", csrftoken);
		    	        }
		        	 },
		         success: function(data) { 
		        	$("#pushModal").modal("show");
				  },
		         error: function(  jqXHR,  textStatus,  errorThrown){
		        	 console.log('Error in ajax request /api/v1/push/');
		        	 console.log('Error: ' + textStatus + ' exception: ' + errorThrown);
		         },
		         complete: function( jqXHR,  textStatus){
		        	 myspinner.stop();
		         }
		      });
			return false;
		});
	
	
	
})();



var pushMsgApp = angular.module('pushMsgApp', []);

pushMsgApp.controller('pushMsgCtrl', 
		function pushCtrl($scope) {
	
	$scope.currAppObject = null;
	$scope.selectedApp = "Select an App";
	$scope.numSubscribers = 0;
	$scope.selectedClass = "";
	$scope.apps = [];
	
	
	 update_apps_list($scope);
	
	  
	 $scope.selectApp = function(app){
		 
		
		 
		 $scope.selectedApp = app;
		 myspinner.spin($("#spinner")[0]);
		 
		
		  var apps = $scope.apps;
		  for(index in apps){
			var cur_app = apps[index];
			if( cur_app.name == app){
				$app_object = cur_app;
				break;				
			}
		  }
		  
		  $scope.currAppObject = $app_object;		  
		  $.ajax({
		         url: "/api/v2/push/subscribers/",
		         type: "GET",
		         beforeSend: function(xhr){xhr.setRequestHeader('AppId', $app_object.key);},
		         success: function(data) { 
		        	myspinner.stop();
		        	num_subscribers = data["result"];
				  	$scope.$apply(function(){
					  	$scope.numSubscribers = num_subscribers;
				    }); 
				  },
				 complete: function( jqXHR, textStatus){
			        	 myspinner.stop();
			         }
		      });
	 };
	
	 
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

	
	
	
	
	
	
	
	
	