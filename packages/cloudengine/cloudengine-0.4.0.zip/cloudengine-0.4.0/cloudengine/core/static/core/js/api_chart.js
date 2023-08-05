$(function() {

	$.ajax({
        url: "/api/v2/apicalls/",
        type: "GET",
        success: function(data){
        	Morris.Line({
      		  element: 'api-chart',
      		  data: data,
      		  xkey: 'date',
      		  ykeys: ['count'],
      		  labels: ['API Calls']
      		});
        },
        error: function(xhr, status, err){
			  
        	console.log(status);
        	console.log(err);
			  alert("Unable to complete operation. Server Error!");
		  }
        
 });
	
	

});
