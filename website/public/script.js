// Map initialization 
var map = L.map('map').setView([41.425058, -87.33366], 5);

//osm layer
var osm = L.tileLayer('https://{s}.tile.openstreetmap.org/{z}/{x}/{y}.png', {
    attribution: '&copy; <a href="https://www.openstreetmap.org/copyright">OpenStreetMap</a> contributors'
});
osm.addTo(map);


// document.getElementById('slide-button').addEventListener('click', fadeOutInfo);
// document.getElementById('slide-button-2').addEventListener('click', fadeInInfo);


// function fadeInInfo() {
//     var leftContainer = document.getElementById('left-container');
//     var rightContainer = document.getElementById('right-container');

//     // Slide out left container
//     leftContainer.style.left = '0';

//     // Move right container to the middle
//     rightContainer.style.right = '0';

//     map.invalidateSize();

// }
// function fadeOutInfo() {
//     var leftContainer = document.getElementById('left-container');
//     var rightContainer = document.getElementById('right-container');

//     // Slide out left container
//     leftContainer.style.left = '-100%';

//     // Move right container to the middle
//     rightContainer.style.right = '25%';
//     map.invalidateSize();
// }

/*
<div class="accordion-item">
    <h2 class="accordion-header" id="headingOne">
        <button class="accordion-button" type="button" data-bs-toggle="collapse" data-bs-target="#collapseOne" aria-expanded="true" aria-controls="collapseOne">
            Notification for load id 123
        </button>
    </h2>
    <div id="collapseOne" class="accordion-collapse collapse show" aria-labelledby="headingOne" data-bs-parent="#accordionExample">
    <div class="accordion-body">
        <strong>This is the first item's accordion body.</strong> It is shown by default, until the collapse plugin adds the appropriate classes that we use to style each element. These classes control the overall appearance, as well as the showing and hiding via CSS transitions. You can modify any of this with custom CSS or overriding our default variables. It's also worth noting that just about any HTML can go within the <code>.accordion-body</code>, though the transition does limit overflow.
    </div>
    </div>
</div>
*/
var truckList = {}
var truckMarkerList = {}
var loadList = {}
var loadMarkerList = {}
var notificationForTruck = {}
var notificationForLoad = {}

function addNotification(notification, accordionParent) {
    let load = loadList[notification.loadId]
    if(load == undefined) return
    let accordion = 
    `<div class="accordion-item">
        <h2 class="accordion-header" id="headingOne">
            <button class="accordion-button" type="button" data-bs-toggle="collapse" data-bs-target="#collapseOne" aria-expanded="true" aria-controls="collapseOne">
                ${notification.timestamp} Load ID: ${notification.loadId}
            </button>
        </h2>
        <div id="${notification.loadId}m${notification.truckId}" class="accordion-collapse collapse show" aria-labelledby="headingOne" data-bs-parent="#accordionParent">
        <div class="accordion-body">
            ${loadList[notification.loadId].price}
        </div>
        </div>
    </div>`
    accordionParent.innerHTML += accordion;
}



var marker, circle;

fetch('/config').then(response => response.json()).then(config => {
    const port = config.clientPort;
    let socket = new WebSocket("ws://127.0.0.1:" + port);

    socket.addEventListener('open', function (event) {
        console.log("Connected to WebSocket server");
    });

    socket.addEventListener('message', function (event) {
        let regex = /(?<=\})\{(?=\")/g;
        let jsonStrings = event.data.split(regex).map((str, index, array) => {
            if (str[0] !== '{') {
                return '{' + str;
            }
            return str;
        });
    
        // Process each JSON string separately
        jsonStrings.forEach(jsonString => {
            try {
                if (jsonString) { // Check if the string is not empty
                    let jsonData = JSON.parse(jsonString);
                    markPosition(jsonData);
                }
            } catch (e) {
                console.error("Error parsing JSON: ", e, "Data: ", jsonString);
            }
        });
    });
});

function truckClick(truckId){
    if(document.getElementById("load_info").style.display == "block"){
        document.getElementById("load_info").style.display = "none";
    }
    document.getElementById("truck_info").style.display = "block";
    var truck = truckList[truckId];
    document.getElementById("truck_id").innerHTML = truckId;
    document.getElementById("truck_type").innerHTML = truck.equipType; 
    
    // update notification list
    // var notificationList = document.getElementById("truck_notification_list");
    // notificationList.innerHTML = "";
    const notificationListDOM = document.getElementById("truck_notification_list")
    const notification_list = notificationForTruck[truckId]
    if(notification_list != undefined && notification_list.length == 0){
        // console.log("no notifications for truck " + truckId);
        const noNotifHeader = document.createElement("h3");
        noNotifHeader.textContent = "No notifications for this truck";
        notificationListDOM.appendChild(noNotifHeader);
        return;
    }else{
        for (const notification of notification_list){
            addNotification(notification, notificationListDOM)
        }
    }
    // temporarily using trucks instead of notifications
    
}
function loadClick(loadId){
    if(document.getElementById("truck_info").style.display == "block"){
        document.getElementById("truck_info").style.display = "none";
    }
    document.getElementById("load_info").style.display = "block";
    var load = loadList[loadId];
    document.getElementById("load_id").innerHTML = loadId;
    document.getElementById("load_type").innerHTML = load.equipmentType; 
    
    // update notification list
    var notificationList = document.getElementById("load_notification_list");
    notificationList.innerHTML = "";
    
    if(notificationForLoad.length == 0){
        console.log("no notifications for load " + loadId);
        listItem.textContent = "No notifications for this truck";
        notificationList.appendChild(listItem);
        return;
    }
    // temporarily using trucks instead of notifications
    for (const notification of notificationForLoad[loadId]){
        var listItem = document.createElement("li");
        listItem.textContent =  notification.timestamp+ ": Truck ID " + notification.truckId; 
        notificationList.appendChild(listItem);
    }
}

var blinkTruckIcon = L.icon({
    iconUrl: "/icon_truck_blink.png",
    iconSize: [38, 38]
});
var truckIcon = L.icon({
    iconUrl: "/icon_truck.png",
    iconSize: [38, 38]
});

function blinkTruckMarker(truckId){
    var originalIcon = truckIcon;
    truckMarkerList[truckId].setIcon(blinkTruckIcon);
    setTimeout(truckMarkerList[truckId].setIcon.bind(truckMarkerList[truckId], originalIcon), 500)
}
var loadIcon = L.icon({
    iconUrl: "/icon_load.png",
    iconSize: [38, 38]
});
var blinkLoadIcon = L.icon({
    iconUrl: "/icon_load_blink.png",
    iconSize: [38, 38]
})
function blinkLoadMarker(loadId){
    var originalIcon = loadIcon;
    loadMarkerList[loadId].setIcon(blinkLoadIcon);
    setTimeout(loadMarkerList[loadId].setIcon.bind(loadMarkerList[loadId], originalIcon), 500)
}

function clearMarkers(markerList) {
    for(marker in markerList) {
        map.removeLayer(marker)
    }
}

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

        marker = L.marker([lat, long], {
            icon: loadIcon
        })
        marker.on('click', loadClick.bind(this, loadId));
        loadMarkerList[loadId] = marker
        
        
        // var accuracy = 200000
        // circle = L.circle([lat, long], {radius: accuracy})
        // var featureGroup = L.featureGroup([marker, circle]).addTo(map)

    }else if(message["type"]=="Notification"){
        var notification = new Notification(message)
        var truckId = notification.truckId
        var loadId = notification.loadId

        if(notificationForTruck[truckId]){
            notificationForTruck[truckId].push(notification);
            blinkTruckMarker(truckId);
        }else{
            //console.error(`TruckId ${truckId} does not exist.`);
            return;
        }
        if(notificationForLoad[loadId]){
            notificationForLoad[loadId].push(notification)
            blinkLoadMarker(loadId);
        }else{
            //console.error(`LoadId ${loadId} does not exist.`);
            return;
        }  
    }else if(message["type"]=="Start"){
        clearMarkers(truckMarkerList)
        clearMarkers(loadMarkerList)
        truckList = {}
        truckMarkerList = {}
        loadList = {}
        loadMarkerList = {}
        notificationForTruck = {}
        notificationForLoad = {}
    }else{
        return;
    }
    // console.log("Your coordinate is: Lat: "+ lat +" Long: "+ long)
}//markPosition

function clearMarkers(markerList){
    for (const [key, marker] of Object.entries(markerList)){
        marker.remove();
    }
}

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
      this.id = message['id'];
      this.estimated_hourly_profit = message['estimated_wage']
      this.estimated_distance = message['estimated_distance']
    }
  }//notification