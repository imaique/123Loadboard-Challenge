
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

function truckClick(truckId){
    var truck = truckList[truckId];
    document.getElementById("truck_id").innerHTML = truckId;
    document.getElementById("truck_type").innerHTML = truck.equipType; 
    
    // update notification list
    var notificationList = document.getElementById("notification_list");
    notificationList.innerHTML = "";
    
    if(notificationForTruck.length == 0){
        console.log("no notifications for truck " + truckId);
        notificationList.appendChild(document.createElement("li").textContent = "No notifications for this truck");
        return;
    }
    // temporarily using trucks instead of notifications
    for (const [key, value] in notificationForTruck.entries()){
        var listItem = document.createElement("li");
        listItem.textContent =  value.timestamp+ ": " + value.load; 
        notificationList.appendChild(listItem);
    }
}

var truckList = {}
var truckMarkerList = {}
var loadList = {}
var notificationForTruck = {}
var notificationForLoad = {}

function markPosition(message){
    // console.log(position)
    if(message["type"]=="Truck"){
        var truckId = message["truckId"]
        
        var truck = truckList[truckId]
        var lat = message["positionLatitude"]
        if(lat == null) return;
        var long = message["positionLongitude"]
        
        if(truck === undefined){
            truckList[truckId] = new Truck(message)
            notificationForTruck[truckId] = []
            var truckIcon = L.icon({
                iconUrl: "/icon_truck.png",
                iconSize: [38, 38]
            });
            marker = L.marker([lat, long], {
                icon: truckIcon
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
        var loadId = message["loadId"]
        var lat = message["originLatitude"]
        if(lat == null) return;
        var long = message["originLongitude"]
        
        loadList[loadId] = new Load(message)
        notificationForLoad[loadId] = []
        // console.log("load added: "+loadList[loadId].id);
        var loadIcon = L.icon({
            iconUrl: "/icon_load.png",
            iconSize: [38, 38]
        });
        marker = L.marker([lat, long], {
            icon: loadIcon
        })
        // marker.on('click', function(){
        //     document.getElementById("load_id").innerHTML = loadId;
        //     document.getElementById("load_type").innerHTML = load.equipmentType; 
        // });
        marker.addTo(map)
        // var accuracy = 200000
        // circle = L.circle([lat, long], {radius: accuracy})
        // var featureGroup = L.featureGroup([marker, circle]).addTo(map)

    }else if(message["type"]=="Notification"){
        var notification = new Notification(message)
        var truckId = notification.truckId
        var loadId = notification.loadId

        if(notificationForTruck[truckId]){
            notificationForTruck[truckId].push(notification);
        }else{
            console.error(`TruckId ${truckId} does not exist.`);
            return;
        }
        if(notificationForLoad[loadId]){
            notificationForLoad[loadId].push(notification)
        }else{
            console.error(`LoadId ${loadId} does not exist.`);
            return;
        }  

    }else{
        return;
    }
    // console.log("Your coordinate is: Lat: "+ lat +" Long: "+ long)
}//markPosition

class Truck {
    constructor(message) {
        this.id = message["truckId"];
        this.timestamp = new Date(message["timestamp"]).toLocaleDateString('en-US');
        this.positionLatitude = message["positionLatitude"];
        this.positionLongitude = message["positionLongitude"];
        this.equipType = message["equipType"];
        this.nextTripLengthPreference = message["nextTripLengthPreference"];
    //   this.notifications = [];
    }//constructor
}//Truck
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
        // console.log("load added: "+this.id);
        // this.notifications = [];
    }//constructor
}//Load
class Notification {
    constructor(message) {
      this.truckId = message["truck_id"];
      this.loadId = message["load_id"];
      this.timestamp = message["timestamp"];
    }
  }//notification