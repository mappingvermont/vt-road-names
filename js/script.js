	

	var Esri_WorldTopoMap = L.tileLayer('http://server.arcgisonline.com/ArcGIS/rest/services/World_Topo_Map/MapServer/tile/{z}/{y}/{x}', {
		attribution: 'Tiles &copy; Esri'
	});
    var map = L.map('map', {layers: [Esri_WorldTopoMap], center: new L.LatLng(43.9, -72), zoom: 8});
	  	
	function buildPopup(feature, layer) {

		var divNode = document.createElement('DIV');

		var popup = "<div class='popup_box_header'><strong>Company: " + feature.properties.Companies + "</strong></div>";
		popup += "<hr />";
		popup += "Address: " + feature.properties.town + "<br />";
		popup += "Opened: " + feature.properties.result + "<br />";

/*
		if (feature.properties.Status == 'Closed') {
			popup += "Closed: " + feature.properties.Closed + "<br />";
		} else {
			popup += "Status: " + feature.properties.Status + "<br />";
		}

		if (feature.properties.Notes) {
			popup += "Notes: " + feature.properties.Notes + "<br />";
		}

		popup += "<hr />";
		popup += "<img style='height:auto; width:auto; max-width:300px; max-height:300px;' src=" + "." + feature.properties.image + ">";
		popup += "<hr />" + "Photo Credit: " + feature.properties.Photo + "<br />";
		popup += "</div>";

		// Important to include this so the HTML is built first, then given to the popup
		// Allows the images to be resized properly, and Leaflet to know exactly how big the popup is
*/
		divNode.innerHTML = popup
		layer.bindPopup(divNode, {maxWidth:450, autoPan:true})


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
		
	var addJSON = new L.GeoJSON.AJAX(["./stations.geojson"],{

		 onEachFeature: function (feature, layer) {
			buildPopup(feature, layer);

        },

        pointToLayer: function (feature, latlng) {
        	return L.marker(latlng, {icon: getMarkerColor(feature)});
        }
		
		}).addTo(map);


    var townLayer = omnivore.topojson('../output.json')

      .on('ready', function() {

      	//Source: https://www.mapbox.com/mapbox.js/example/v1.0.0/omnivore-kml-tooltip/

        // After the 'ready' event fires, the GeoJSON contents are accessible
        // and you can iterate through layers to bind custom popups.
        townLayer.eachLayer(function(layer) {

        	buildPopup(layer.feature, layer);
            // See the `.bindPopup` documentation for full details. This
            // dataset has a property called `name`: your dataset might not,
            // so inspect it and customize to taste.
            //layer.bindPopup(layer.feature.result);
        });
    })

    .addTo(map);
	

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
