
    // Map initialization 
    var map = L.map('map').setView([41.425058, -87.33366], 5);

    //osm layer
    var osm = L.tileLayer('https://{s}.tile.openstreetmap.org/{z}/{x}/{y}.png', {
        attribution: '&copy; <a href="https://www.openstreetmap.org/copyright">OpenStreetMap</a> contributors'
    });
    osm.addTo(map);

    var marker, circle;

    let socket = new WebSocket("ws://127.0.0.1:8081/");

    socket.addEventListener('open', function (event) {
        console.log("Connected to WebSocket server");
    });

    socket.addEventListener('message', function (event) {
        console.log('Message from server ', event.data);
        let jsonData = JSON.parse(event.data);
        markPosition(jsonData)
    });

    function markPosition(message){
        // console.log(position)
        var lat = message["positionLatitude"]

        if(lat == null) return;
        var long = message["positionLongitude"]
        var accuracy = 5000
        marker = L.marker([lat, long])
        circle = L.circle([lat, long], {radius: accuracy})

        var featureGroup = L.featureGroup([marker, circle]).addTo(map)

        console.log("Your coordinate is: Lat: "+ lat +" Long: "+ long+ " Accuracy: "+ accuracy)
    }
