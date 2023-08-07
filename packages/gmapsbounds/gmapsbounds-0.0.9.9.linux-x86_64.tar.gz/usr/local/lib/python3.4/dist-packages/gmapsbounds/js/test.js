function createMap() {
    var spl = INFO.split(', ')
    var lat = spl[0];
    var lng = spl[1];
    var zoom = parseInt(spl[2]);
    var mapOptions = {
        center: new google.maps.LatLng(lat, lng),
        zoom: zoom,
    }
    var map = new google.maps.Map(document.getElementById("map-canvas"),
        mapOptions);
    for (var i = 0; i < COORDINATES.length; i++) {
        boundaries = new google.maps.Polygon({
            map: map,
            paths: COORDINATES[i],
            strokeColor: '#FF0000',
            strokeOpacity: 0.8,
            strokeWeight: 2,
            fillColor: '#66FF66',
            fillOpacity: 0.35
      });
    }
}
