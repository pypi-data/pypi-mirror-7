function createMap(info, ele) {
    var spl = info.split(', ')
    var lat = spl[0];
    var lng = spl[1];
    var zoom = parseInt(spl[2]);
    var mapOptions = {
        center: new google.maps.LatLng(lat, lng),
        zoom: zoom,
    }
    var map = new google.maps.Map(document.getElementById("map-canvas"),
        mapOptions);
    var bounds = new google.maps.LatLngBounds();
    google.maps.event.addListenerOnce(map, 'bounds_changed', function() {
        bounds = map.getBounds();
        document.getElementById("cityinfo").value = bounds;
    });
}

function initialize() {
    ele = document.getElementById("cityinfo")
    info = ele.value;
    ele.value = '';
    createMap(info, ele);
}
