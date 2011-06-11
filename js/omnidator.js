$(function(){
	init();
	
	
	$("#doTranslate").click(function() {
		$.ajax({
			url : "/translate",
			type: "GET",
			dataType: 'text',
			data: "url=" + escape($("#docURL").val()),
			success : function(data) {
				$("#result").html(htmlEntities(data));
			},
			error: function(xhr, textStatus, errorThrown){
				alert("Sorry, there was an error: " + textStatus);
			}
		});
	});
	
	
	// menu selection
	$("#menu span").click(function() {
		$("#menu span").each(function(index) {
			$('#' + $(this).attr('id') + '-content').hide();
			$(this).removeClass('active');
		});
		$(this).addClass('active');
		$('#' + $(this).attr('id') + '-content').show();
		window.location =  '#' + $(this).attr('id');
	});
});

function init(){
	var hashPos = document.URL.indexOf("#");
	
	if(hashPos >= 0){ // one of the menu items is selected
		$("#menu span").each(function(index) {
			$('#' + $(this).attr('id') + '-content').hide();
			$(this).removeClass('active');
		});
		menuSelection = '#' + document.URL.substring(hashPos + 1);
		$(menuSelection).addClass('active');
		$(menuSelection + '-content').show();
	}
}

// from http://css-tricks.com/snippets/javascript/htmlentities-for-javascript/
function htmlEntities(str) {
    return String(str).replace(/&/g, '&amp;').replace(/</g, '&lt;').replace(/>/g, '&gt;').replace(/"/g, '&quot;');
}