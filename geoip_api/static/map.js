var map = L.map('map').setView([0, 0], 1);

L.tileLayer('https://api.mapbox.com/styles/v1/{id}/tiles/{z}/{x}/{y}?access_token={accessToken}', {
    attribution: 'Map data &copy; <a href="https://www.openstreetmap.org/copyright">OpenStreetMap</a> contributors, Imagery © <a href="https://www.mapbox.com/">Mapbox</a>',
    minZoom: 1,
    maxZoom: 18,
    id: 'mapbox/streets-v11',
    tileSize: 512,
    zoomOffset: -1,
    accessToken: 'pk.eyJ1IjoiY29kZWJ1Y2tldCIsImEiOiJjajF0cGVkcmswMDMwMzJyemIxYmxncnpiIn0.Y6Cnw8QVXgLXAPdsc2E0Nw'
}).addTo(map);

function geoip(response) {
    document.getElementById('ip_address').innerText = response.ip_address;
    document.getElementById('hostname').innerText = response.hostname || response.ip_address;
    document.getElementById('country').innerHTML = response.country.name + ' <span class="flag-icon flag-icon-' + response.country.iso_code.toLowerCase() + '"></span>';
    document.getElementById('city').innerText = response.city.name || 'Not available';
    document.getElementById('asn').innerText = 'AS' + response.asn.id + ' - ' + response.asn.name;

    // Add location and accuracy radius
    let marker = L.marker([response.location.latitude, response.location.longitude]);
    let accuracy_circle = L.circle([response.location.latitude, response.location.longitude], response.location.accuracy_radius * 1000);

    // Center view to marker group
    let group = L.featureGroup([marker, accuracy_circle]).addTo(map);

    map.fitBounds(group.getBounds(), {
        padding: [50, 50]
    });
};
