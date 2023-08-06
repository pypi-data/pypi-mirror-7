/* global google */
/* global createMarker, createInfoWindowAJAX, centerOnMarkerPosition */

$(document).ready(function() {

    function initialize() {
        /*=====================================================================
         * Map initialization function
         *
         * prepares everything from gathering the latitudes and longitues, over
         * setting the markers to displaying the actual map.
         *=====================================================================
         */

        // don't mind me, I'm just a counter variable
        var i;

        // list of latitudes and longitudes for the hotels
        var latlongs = [];
        var latlngbounds = new google.maps.LatLngBounds();

        // outlet detail elements
        var $outlet_detail_elements = $('[data-class=outletDetails]');

        // gather all the latitudes and longitudes from the template
        $outlet_detail_elements.each(function(){
            latlongs.push([
                $(this).find('[name=lat]').val(),
                $(this).find('[name=lon]').val(),
                $(this).find('[name=title]').val(),
                $(this).find('[name=map_marker_url]').val(),
                $(this).find('[name=outlet]').val()
            ]);
        });

        // setting default google map options. Might be extended sometime to
        // allow setting the defaults within django app settings.
        var mapOptions = {
            center: new google.maps.LatLng(latlongs[0][0], latlongs[0][1]),
            minZoom: 16,
            disableDefaultUI: true,
            zoomControl: true,
            apTypeId: google.maps.MapTypeId.ROADMAP
        };

        // create the map instance
        window.GoogleMap = new google.maps.Map($('[data-id=GoogleMap]')[0], mapOptions);

        // is later filled with marker objects for the map
        window.GoogleMapMarkers = [];

        // holds all the info windows
        window.GoogleMapInfoWindows = [];

        // attach zoom event listener
        var zoomChangeBoundsListener = google.maps.event.addListener(
            window.GoogleMap, 'bounds_changed', function() {
                if (this.getZoom() > 15 && this.initialZoom === true) {
                    // Change max/min zoom here
                    this.setZoom(15);
                    this.initialZoom = false;
                }
            }
        );

        // stop right here if there isn't any data
        if (!latlongs.length) {
            return;
        }

        // create google LatLng objects from the latitudes and longitudes
        for (i = 0; i < latlongs.length; i++) {
            latlngbounds.extend(new google.maps.LatLng(latlongs[i][0], latlongs[i][1]));
        }

        // center the map around all the gathered positions
        window.GoogleMap.setCenter(latlngbounds.getCenter());

        // zoom the map to match the positions, so all markers fit into the map
        google.maps.event.addListener(window.GoogleMap, 'zoom_changed', function() {
            google.maps.event.removeListener(zoomChangeBoundsListener);
        });
        window.GoogleMap.initialZoom = true;
        window.GoogleMap.fitBounds(latlngbounds);

        // create the markers and the info windows
        for (i = 0; i < latlongs.length; i++) {
            if (latlongs[i][2] !== 'default') {
                // create marker
                var marker = createMarker(latlongs[i][0], latlongs[i][1], window.GoogleMap, latlongs[i][2]);
                window.GoogleMapMarkers.push(marker);
                // create info window for each marker
                createInfoWindowAJAX(latlongs[i][3], window.GoogleMap, marker);
                latlongs[i].push(marker);
            }
        }
        // when clicking on a map marker center link as defined by the
        // data-class=outletMapMarkerCenter attribute, center the map on the outlet's position
        $(document).on('click', '[data-class=outletMapMarkerCenter]', function(e) {
            var lat, lon,
                marker;
            var outlet_id = $(this).attr('data-id');

            e.preventDefault();

            for (i = 0; i < latlongs.length; i++) {
                if (latlongs[i][4] === outlet_id) {
                    lat = latlongs[i][0];
                    lon = latlongs[i][1];
                    marker = latlongs[i][5];
                }
            }

            centerOnMarkerPosition(window.GoogleMap, lat, lon, marker);
        });
    }

    google.maps.event.addDomListener(window, 'load', initialize);
});
