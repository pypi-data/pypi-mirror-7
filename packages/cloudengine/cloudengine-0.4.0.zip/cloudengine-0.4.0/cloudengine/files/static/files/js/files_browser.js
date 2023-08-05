
$app_object = null;

var filesBrowserApp = angular.module('filesBrowserApp', []);

filesBrowserApp.controller('fileListCtrl', function fileListCtrl($scope) {
	 
	if($curr_app == null){
		$scope.selectedApp = "Select an App";
	}
	else{
		$scope.selectedApp = $curr_app;
	}
  
  $scope.fileList = [];
  $scope.apps = [];
  
  
  update_apps_list($scope);
  
  $scope.selectApp = function(app){
	  
	  
	  myspinner.spin($("#spinner")[0]);
	  $scope.selectedApp = app;
	  var apps = $scope.apps;
	  for(index in apps){
		var cur_app = apps[index];
		if( cur_app.name == app){
			$app_object = cur_app;
			break;
			
		}
	  }

	  $.ajax({
	      url: "/api/v2/files/",
	      type: "GET",
	      beforeSend: function(xhr){xhr.setRequestHeader('AppId', $app_object.key);},
	      success: function(data) {
	    	  myspinner.stop();
	     	filelist = data["results"];
			  	$scope.$apply(function(){
				  	$scope.fileList = filelist;
			    });
			  }
	   });
	  
  }
  
  
  $scope.deleteFile = function(file){
	  
	  confirm_delete = confirm("Are you sure you want to delete this file?");
	  if(confirm_delete == false){
		  return;
	  }
	  myspinner.spin($("#spinner")[0]);
		$.ajax({
	         url: "/api/v2/files/" + file + "/",
	         type: "DELETE",
	         beforeSend: function(xhr, settings){
	        	 if (!csrfSafeMethod(settings.type) && sameOrigin(settings.url)) {
	 	            // Send the token to same-origin, relative URLs only.
	 	            // Send the token only if the method warrants CSRF protection
	 	            // Using the CSRFToken value acquired earlier
	 	        	var csrftoken = $.cookie('csrftoken');
	 	            xhr.setRequestHeader("X-CSRFToken", csrftoken);
	 	        }
	        	 xhr.setRequestHeader('AppId', $app_object.key);
	        	 
	         },
	         success: function(data) {
	        	myspinner.stop();
	        	$scope.selectApp($app_object.name)
			  },
			  error: function(xhr, status, err){
				  myspinner.stop();
				  alert("Unable to complete operation. Server Error!");
			  }
	      });
  }
  
  
});



