$(document).ready(function(){
	var baseUrl = 'http://localhost:8000/lista/';
	var filter = $('#filter');
	var filter2 = $('#selectcode');


$(filter).change(function(){
	 	var filter = $(this).val();
	 	console.log(filter);
	 	window.location.href = baseUrl + '?filter=' +filter;
	 });

})

