$(function(){
	init();
	
	
	$("#doTranslate").click(function() {
		//lowlevelAPICall();
		$("#result").html("");
		$("#resultcontainer").slideUp();
		mainAPICall();
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
	
	// example selection
	$(".translate-examples").click(function() {
		var ex = $(this).text();
		
		$("#result").html("");
		$("#resultcontainer").slideUp();
		if(ex == "CSV to JSON"){
			$("#from").val("csv");
			$("#to").val("json");
			$("#docURL").val("http://omnidator.appspot.com/examples/solar-system.csv");
		}
		if(ex == "Microdata to RDF/Turtle"){
			$("#from").val("microdata");
			$("#to").val("rdf-turtle");
			$("#docURL").val("http://omnidator.appspot.com/examples/md-test-1.html");
		}
	});
});

function mainAPICall() {
	var from = $("#from").val();
	var to = $("#to").val();
	
	$.ajax({
		url : "/" + from + "/" + to + "/",
		type: "GET",
		dataType: 'text',
		data: "url=" + escape($("#docURL").val()),
		success : function(data, textStatus, errorThrown) {
			if(data != 'None'){
				$("#result").html(htmlEntities(data));
			}
			else {
				$("#result").html("Either you selected the wrong translation parameters (from/to) or the input is crap.");
			}
			$("#resultcontainer").slideDown();
		
		},
		error: function(data, textStatus, errorThrown){
			$("#result").html("Some error prevented me to show you the result. I got a " +  data.status + " - sorry, not much we can do about it ;)");
			$("#resultcontainer").slideDown();
		}
	});
}

function lowlevelAPICall() {
	$.ajax({
		url : "/translate",
		type: "GET",
		dataType: 'text',
		data: "url=" + escape($("#docURL").val()),
		success : function(data) {
			if(data != 'None'){
				$("#result").html(htmlEntities(data));
			}
			else {
				$("#result").html("Some error prevented me to show you the result. Blame <a href='http://sw-app.org/mic.xhtml'>Michael</a> ...")
			}
			$("#resultcontainer").slideDown();
		
		},
		error: function(xhr, textStatus, errorThrown){
			alert("Sorry, there was an error: " + textStatus);
		}
	});
}

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