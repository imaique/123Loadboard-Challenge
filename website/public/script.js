
    // Map initialization 
    var map = L.map('map').setView([41.425058, -87.33366], 5);

    //osm layer
    var osm = L.tileLayer('https://{s}.tile.openstreetmap.org/{z}/{x}/{y}.png', {
        attribution: '&copy; <a href="https://www.openstreetmap.org/copyright">OpenStreetMap</a> contributors'
    });
    osm.addTo(map);

    var marker, circle;

    fetch('/config').then(response => response.json()).then(config => {
        const port = config.clientPort;
        let socket = new WebSocket("ws://127.0.0.1:" + port);

        socket.addEventListener('open', function (event) {
            console.log("Connected to WebSocket server");
        });
    
        socket.addEventListener('message', function (event) {
            console.log('Message from server ', event.data);
            let jsonData = JSON.parse(event.data);
            markPosition(jsonData)
        });
    });

    var notificationList = []
    
    function truckClick(truckId){
        console.log(truckId);
        document.getElementById("truck_id").innerHTML = truckId;
        document.getElementById("truck_type").innerHTML = truckList[truckId].equipType; 
        
        // update notification list
        var notificationList = document.getElementById("notification_list");
        notificationList.innerHTML = "";
        
        if(truckList.length == 0) return;
        // temporarily using trucks instead of notifications
        truckList.forEach(function(truck){
            var listItem = document.createElement("li");
            listItem.textContent = truck.id;
            notificationList.appendChild(listItem);
        });
    }

    var truckList = []
    var truckMarkerList = []
    function markPosition(message){
        // console.log(position)
        if(message["type"]=="Truck"){

            var truckId = message["truckId"]
            
            var truck = truckList[truckId]
            var lat = message["positionLatitude"]
            if(lat == null) return;
            var long = message["positionLongitude"]
            
            if(truck == null){
                truckList[truckId] = new Truck(message)
                var truckIcon = L.icon({
                    iconUrl: "/icon_truck.png",
                    iconSize: [38, 38]
                });
                marker = L.marker([lat, long], {
                    icon: truckIcon,
                    title: 'Truck '+truckId
                    })
                marker.on('click', truckClick.bind(this, truckId));
                truckMarkerList[truckId] = marker
                marker.addTo(map)
            }else{
                marker = truckMarkerList[truckId]
                truck = truckList[truckId]
                marker.setLatLng([lat, long])
                truck.positionLatitude = lat
                truck.positionLongitude = long 
                truck.timestamp = new Date(message["timestamp"]).toLocaleDateString('en-US');
                truck.nextTripLengthPreference = message["nextTripLengthPreference"];
            }
        }else if(message["type"]=="Load"){
            // console.log("Load")
            var lat = message["originLatitude"]

            if(lat == null) return;
            var long = message["originLongitude"]
            
            var loadIcon = L.icon({
                iconUrl: "/icon_load.png",
                iconSize: [38, 38]
            });

            var accuracy = 200000
            marker = L.marker([lat, long], {icon: loadIcon}) 
            marker.addTo(map)
            // circle = L.circle([lat, long], {radius: accuracy})
            // var featureGroup = L.featureGroup([marker, circle]).addTo(map)

        }else{
            return;
        }


        console.log("Your coordinate is: Lat: "+ lat +" Long: "+ long+ " Accuracy: "+ accuracy)
    }

    class Truck {
        constructor(message) {
          this.id = message["truckId"];
          this.timestamp = new Date(message["timestamp"]).toLocaleDateString('en-US');
          this.positionLatitude = message["positionLatitude"];
          this.positionLongitude = message["positionLongitude"];
          this.equipType = message["equipType"];
          this.nextTripLengthPreference = message["nextTripLengthPreference"];
        }
      }
    class Load {
        constructor(message) {
            this.id = message["loadId"];
            this.timestamp = new Date(message["timestamp"]).toLocaleDateString('en-US');
            this.originLatitude = message["originLatitude"];
            this.originLongitude = message["originLongitude"];
            this.destinationLatitude = message["destinationLatitude"];
            this.destinationLongitude = message["destinationLongitude"]
            this.equipmentType = message["equipmentType"];
            this.price = message["price"];
            this.mileage = message["mileage"];
          }
      }
      class Notification {
        constructor(truckId, loadId, timestamp) {
          this.truck = truckId;
          this.load = loadId;
          this.timestamp = timestamp;
        }
      }