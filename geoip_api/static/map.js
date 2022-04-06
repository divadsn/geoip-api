'use strict';

var map = L.map('map').setView([0, 0], 1);
var markerGroup = new L.FeatureGroup().addTo(map);

L.tileLayer('https://api.mapbox.com/styles/v1/{id}/tiles/{z}/{x}/{y}?access_token={accessToken}', {
    attribution: 'Map data &copy; <a href="https://www.openstreetmap.org/copyright">OpenStreetMap</a> contributors, Imagery © <a href="https://www.mapbox.com/">Mapbox</a>',
    minZoom: 1,
    maxZoom: 18,
    id: 'mapbox/streets-v11',
    tileSize: 512,
    zoomOffset: -1,
    accessToken: 'pk.eyJ1IjoiY29kZWJ1Y2tldCIsImEiOiJjajF0cGVkcmswMDMwMzJyemIxYmxncnpiIn0.Y6Cnw8QVXgLXAPdsc2E0Nw'
}).addTo(map);

document.getElementById('lookup').onsubmit = function(e) {
    e.preventDefault();

    let ipAddress = document.getElementById('ip').value;
    let xhr = new XMLHttpRequest();

    xhr.open('GET', '/api/' + ipAddress, true);
    xhr.responseType = 'json';
    xhr.onload = function() {
        // Check if we have a valid response
        if (xhr.status >= 200 && xhr.status < 400) {
            geoip(xhr.response);
        } else {
            alert('Invalid public IPv4 or IPv6 Address');
        }
    };
    xhr.send();

    // Reset form after submit
    e.target.reset();
};

function geoip(response) {
    document.getElementById('ip_address').innerText = response.ip_address;
    document.getElementById('hostname').innerText = response.hostname || response.ip_address;
    document.getElementById('country').innerHTML = response.country.name + '&ensp;<span class="flag-icon flag-icon-' + response.country.iso_code.toLowerCase() + '"></span>';
    document.getElementById('city').innerText = response.city.name || 'Not available';
    document.getElementById('asn').innerText = 'AS' + response.asn.id + ' - ' + response.asn.name;

    // Remove marker before creating new
    markerGroup.clearLayers();

    // Add location and accuracy radius
    L.marker([response.location.latitude, response.location.longitude]).addTo(markerGroup);
    L.circle([response.location.latitude, response.location.longitude], response.location.accuracy_radius * 1000).addTo(markerGroup);

    // Center view to marker group
    map.fitBounds(markerGroup.getBounds(), {
        padding: [50, 50]
    });
}
