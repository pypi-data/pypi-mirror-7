/* global google*/
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
                $(this).find('[name=lon]').val()
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
        var map = new google.maps.Map($('[data-id=outletsGoogleMap]')[0], mapOptions);

        // is later filled with marker objects for the map
        var markers = [];

        // attach zoom event listener
        var zoomChangeBoundsListener = google.maps.event.addListener(
            map, 'bounds_changed', function() {
                if (this.getZoom() > 15 && this.initialZoom === true) {
                    // Change max/min zoom here
                    this.setZoom(15);
                    this.initialZoom = false;
                }
            });

        // stop right here if there isn't any data
        if (!latlongs.length) {
            return;
        }

        // create google LatLng objects from the latitudes and longitudes
        for (i = 0; i < latlongs.length; i++) {
            latlngbounds.extend(new google.maps.LatLng(latlongs[i][0], latlongs[i][1]));
        }

        // center the map around all the gathered positions
        map.setCenter(latlngbounds.getCenter());

        // zoom the map to match the positions, so all markers fit into the map
        google.maps.event.addListener(map, 'zoom_changed', function() {
            google.maps.event.removeListener(zoomChangeBoundsListener);
        });
        map.initialZoom = true;
        map.fitBounds(latlngbounds);

        /*
            function to create markers for a map
            :param latlong_list: is an array of tuples in the format:
                (latitude, longitude, hotel name, roomsxml_id
            :param targetMap: is the google map object
        */
        for (i = 0; i < latlongs.length; i++) {
            if (latlongs[i][2] !== 'default') {
                markers.push(
                    new google.maps.Marker({
                        position: new google.maps.LatLng(latlongs[i][0], latlongs[i][1]),
                        map: map,
                        title: latlongs[i][2],
                    })
                );
            }
        }

        //TODO is this still required?
        //$('.nav li').click(function() {
            //window.setTimeout(function() {
                //google.maps.event.trigger(map, 'resize');
                //map.setCenter(latlngbounds.getCenter());
            //}, 10)
        //})

    }

    google.maps.event.addDomListener(window, 'load', initialize);
});
