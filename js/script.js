	

	var CartoDB_Positron = L.tileLayer('http://{s}.basemaps.cartocdn.com/light_all/{z}/{x}/{y}.png', {
		attribution: '&copy; <a href="http://www.openstreetmap.org/copyright">OpenStreetMap</a> &copy; <a href="http://cartodb.com/attributions">CartoDB</a>',
		subdomains: 'abcd',
		maxZoom: 19
	});

    var map = L.map('map', {layers: [CartoDB_Positron], center: new L.LatLng(43.9, -72), zoom: 8});
	  	
	function buildPopup(feature, layer) {

		var divNode = document.createElement('DIV');

		var popup = "<div class='popup_box_header'><strong>" + feature.properties.town + ": " + titleCase(feature.properties.result)+ "</strong></div>";
		popup += "<hr />";

		var wc = feature.properties.word_count

		for (i = 0; i < wc.length; i++) { 
			popup += titleCase(wc[i].word) + ": " + wc[i].count + "<br>";
		}

		divNode.innerHTML = popup
		layer.bindPopup(divNode, {maxWidth:450, autoPan:true})

	}

	var results = ['HILL', 'FARM', 'BROOK', 'POND', 'Tie', 'other']

	var styles = {
			'HILL': '#4daf4a',
			'FARM': '#e41a1c',
			'BROOK': '#377eb8',
			'POND': '#984ea3',
			'Tie': '#999999',
			'other': '#ff7f00'

		}

	function style_poly(layer) {



		var style_color = (styles[layer.feature.properties.result] || styles['other']);

		layer.setStyle({color:style_color,
                		fill:style_color,
                		weight: 1,
						})
	}

	function titleCase(str)
		{
		    return str.replace(/\w\S*/g, function(txt){return txt.charAt(0).toUpperCase() + txt.substr(1).toLowerCase();});
		}

	function getMarkerColor(feature)  {
 
	var markerImg = 'js/images/marker-icon.png'

 	if (feature.properties.Status == 'Closed') {
 		markerImg = 'js/images/marker-icon-grey.png'

 	} else {
 		markerImg = 'js/images/marker-icon-red.png'
 	}

 	var myIcon = new L.Icon.Default({iconUrl: markerImg})
 	
 	return myIcon
};

    var townLayer = omnivore.topojson('../output.json')

      .on('ready', function() {

      	//Source: https://www.mapbox.com/mapbox.js/example/v1.0.0/omnivore-kml-tooltip/
      	//Also: https://bl.ocks.org/mpmckenna8/60910c22b47777967704

        // After the 'ready' event fires, the GeoJSON contents are accessible
        // and you can iterate through layers to bind custom popups.
        townLayer.eachLayer(function(layer) {

        	style_poly(layer);

        	buildPopup(layer.feature, layer);

        });
    })

    .addTo(map);


	var legend = L.control({position: 'bottomleft'});

		legend.onAdd = function (map) {

			var div = L.DomUtil.create('div', 'info legend'),
				labels = [];

			labels.push('<strong>Most Common Road Name</strong>')

			for (var i = 0; i < results.length; i++) {

				labels.push('<i style="background:' + styles[results[i]] + '"></i>' + ' ' + titleCase(results[i]) );
			}

			div.innerHTML = labels.join('<br>');
			return div;
		};

		legend.addTo(map);
	

// Toggle for 'About this map' and X buttons
// Only visible on mobile
isVisibleDescription = false;
// Grab header, then content of sidebar
sidebarHeader = $('.sidebar_header').html();
sidebarContent = $('.sidebar_content').html();
// Then grab credit information
creditsContent = $('.leaflet-control-attribution').html();
$('.toggle_description').click(function() {
	if (isVisibleDescription === false) {
		$('.description_box_cover').show();
		// Add Sidebar header into our description box
		// And 'Scroll to read more...' text on wide mobile screen
		$('.description_box_header').html(sidebarHeader + '<div id="scroll_more"><strong>Scroll to read more...</strong></div>');
		// Add the rest of our sidebar content, credit information
		$('.description_box_text').html(sidebarContent + '<br />');
		$('#caption_box').html('Credits: ' + creditsContent);
		$('.description_box').show();
		isVisibleDescription = true;
	} else {
		$('.description_box').hide();
		$('.description_box_cover').hide();
		isVisibleDescription = false;
	}
});
