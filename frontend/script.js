
// 🌍 ================= MAP INITIALIZATION =================

let map = L.map('map').setView([13.0827, 80.2707], 10); // Default Chennai

L.tileLayer('https://{s}.tile.openstreetmap.org/{z}/{x}/{y}.png', {
    attribution: '© OpenStreetMap contributors'
}).addTo(map);

let marker = L.marker([13.0827, 80.2707]).addTo(map)
    .bindPopup("Chennai")
    .openPopup()
    .bindTooltip("Chennai", {
        permanent: true,
        direction: "top",
        offset: [0, -10]
    });


// ================= SCROLL =================

function scrollToPredict() {
    document.getElementById("predictSection").scrollIntoView({
        behavior: "smooth"
    });
}


// ================= CO2 PREDICTION =================

function predictCO2() {

    const temperature = document.getElementById("temperature").value;
    const humidity = document.getElementById("humidity").value;
    const light = document.getElementById("light").value;
    const occupancy = document.getElementById("occupancy").value;

    if (!temperature || !humidity || !light || !occupancy) {
        alert("Please fill all fields");
        return;
    }

    fetch("https://smartco2-backend.onrender.com/predict", {
        method: "POST",
        headers: {
            "Content-Type": "application/json"
        },
        body: JSON.stringify({
            temperature: temperature,
            humidity: humidity,
            light: light,
            occupancy: occupancy
        })
    })
    .then(response => response.json())
    .then(data => {

        // Result Box
        document.getElementById("result").innerHTML =
            `<h2 style="color:${data.color}">CO₂: ${data.predicted_co2} ppm</h2>
             <h3>Air Quality: ${data.air_quality}</h3>
             <p>Range: ${data.range}</p>`;

        // Top Card Update
        document.getElementById("previewCo2").innerText = data.predicted_co2;
        document.getElementById("previewTemp").innerText = temperature;
        document.getElementById("previewHumidity").innerText = humidity;
        document.getElementById("previewOcc").innerText =
            occupancy == 1 ? "Yes" : "No";
    })
    .catch(error => {
        document.getElementById("result").innerHTML =
            "Error connecting to backend.";
    });
}


// ================= LOCATION SEARCH + AQI =================

function searchLocation() {

    const location = document.getElementById("locationInput").value;

    if (!location) {
        alert("Enter location");
        return;
    }

    const API_KEY = "3d169a6234216251515d1eb8dd83bdc0";

    // STEP 1: Get lat, lon
    fetch(`https://api.openweathermap.org/geo/1.0/direct?q=${location}&limit=1&appid=${API_KEY}`)
    .then(res => res.json())
    .then(data => {

        if (data.length === 0) {
            alert("Location not found");
            return;
        }

        const lat = data[0].lat;
        const lon = data[0].lon;

        // Move map
        map.setView([lat, lon], 11);
        marker.setLatLng([lat, lon])
           .bindPopup(location)
           .openPopup()
           .bindTooltip(location, {
               permanent: true,
               direction: "top",
               offset: [0, -10]
         });

        // STEP 2: Get AQI data
        return fetch(`https://api.openweathermap.org/data/2.5/air_pollution?lat=${lat}&lon=${lon}&appid=${API_KEY}`);
    })
    .then(res => res.json())
    .then(data => {

        const aqi = data.list[0].main.aqi;
        const co = data.list[0].components.co;
        const pm = data.list[0].components.pm2_5;

        // Convert AQI to text
        let status = "";
        if (aqi == 1) status = "Good 😊";
        else if (aqi == 2) status = "Fair 🙂";
        else if (aqi == 3) status = "Moderate 😐";
        else if (aqi == 4) status = "Poor 😷";
        else status = "Very Poor ☠";

        // Update UI
        document.getElementById("mapAqi").innerText = aqi + " (" + status + ")";
        document.getElementById("mapCo").innerText = co;
        document.getElementById("mapPm").innerText = pm;

    })
    .catch(err => {
        alert("Error fetching data");
        console.log(err);
    });
}