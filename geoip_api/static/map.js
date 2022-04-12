'use strict';

var map = L.map('map').setView([0, 0], 1);
var markerGroup = new L.FeatureGroup().addTo(map);

// Load map tiles from Mapbox
L.tileLayer('https://api.mapbox.com/styles/v1/{id}/tiles/{z}/{x}/{y}?access_token={accessToken}', {
    attribution: 'Map data &copy; <a href="https://www.openstreetmap.org/copyright">OpenStreetMap</a> contributors, Imagery © <a href="https://www.mapbox.com/">Mapbox</a>',
    minZoom: 1,
    maxZoom: 18,
    id: 'mapbox/streets-v11',
    tileSize: 512,
    zoomOffset: -1,
    accessToken: 'pk.eyJ1IjoiY29kZWJ1Y2tldCIsImEiOiJjbDF3bWYycTMwNzVzM2lwOGQzOXAwcXpjIn0.f1KUQhfW60Y-ShBIG95GSQ'
}).addTo(map);

// Add a scale bar to the map
L.control.scale().addTo(map);

function lookup(ip) {
    let ipAddress = ip || '';
    let xhr = new XMLHttpRequest();

    // Set IP address in URL
    window.location.hash = '#/' + ipAddress;

    xhr.open('GET', '/api/' + encodeURIComponent(ipAddress), true);
    xhr.responseType = 'json';
    xhr.onload = function() {
        // Check if we have a valid response
        if (xhr.status >= 200 && xhr.status < 400) {
            showResult(xhr.response);
        } else {
            alert('Invalid public IPv4 or IPv6 Address');
        }
    };
    xhr.send();
}

function getCountryFlag(country) {
    if (country.name && country.iso_code) {
        return country.name + '&ensp;<span class="flag-icon flag-icon-' + country.iso_code.toLowerCase() + '"></span>';
    } else if (country.name) {
        return country.name;
    }
}

function showResult(response) {
    // Load the response details into the table
    document.getElementById('ip_address').innerText = response.ip_address;
    document.getElementById('hostname').innerText = response.hostname || response.ip_address;
    document.getElementById('country').innerHTML = getCountryFlag(response.country) || 'Not available';
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

document.forms.lookup.onsubmit = function(e) {
    // Stop form from submitting
    e.preventDefault();

    // Send a request to API with IP address and wait
    lookup(document.getElementById('ip').value);

    // Reset form after submit
    e.target.reset();
};

window.onload = function(e) {
    // Use the IP address from the URL if specified
    lookup(decodeURIComponent(window.location.hash.slice(2)));
};
