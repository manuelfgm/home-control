// Called after form input is processed
function startConnect() {
    // Generate a random client ID
    clientID = "clientID-" + parseInt(Math.random() * 100);

    // Fetch the hostname/IP address and port number from the form
    host = "192.168.1.100";//document.getElementById("host").value;
    port = "8080";//document.getElementById("port").value;

    // Print output for the user in the messages div
    document.getElementById("messages").innerHTML += '<span>Connecting to: ' + host + ' on port: ' + port + '</span><br/>';
    document.getElementById("messages").innerHTML += '<span>Using the following client value: ' + clientID + '</span><br/>';

    // Initialize new Paho client connection
    client = new Paho.MQTT.Client(host, Number(port), clientID);

    // Set callback handlers
    client.onConnectionLost = onConnectionLost;
    client.onMessageArrived = onMessageArrived;

    // Connect the client, if successful, call onConnect function
    client.connect({ 
        onSuccess: onConnect,
    });
}

// Called when the client connects
function onConnect() {

    // Print output for the user in the messages div
    document.getElementById("messages").innerHTML += '<span>Subscribing to: home/#</span><br/>';

    // Subscribe to the requested topic
    client.subscribe("home/#");
	
	// Send update commands
	message1 = new Paho.MQTT.Message("1");
	message1.destinationName = "home/relay/get";
	client.send(message1);
	message2 = new Paho.MQTT.Message("1");
	message2.destinationName = "home/params/get";
	client.send(message2);
}

// Called when the client loses its connection
function onConnectionLost(responseObject) {
    document.getElementById("messages").innerHTML += '<span>ERROR: Connection lost</span><br/>';
    if (responseObject.errorCode !== 0) {
        document.getElementById("messages").innerHTML += '<span>ERROR: ' + + responseObject.errorMessage + '</span><br/>';
    }
}

// Called when a message arrives
function onMessageArrived(message) {
    console.log("onMessageArrived: " + message.payloadString);
	topic = message.destinationName;
	value = message.payloadString;
    document.getElementById("messages").innerHTML += '<span>Topic: ' + topic + '  | ' + value + '</span><br/>';
    updateScroll();
	if(topic == "home/params/status/time_start"){
		document.getElementById("startTime").innerHTML = value;
	}else if(topic == "home/params/status/time_stop"){
		document.getElementById("stopTime").innerHTML = value;
	}else if(topic == "home/params/status/user_temp"){
		document.getElementById("userTemp").innerHTML = value + ' ºC';
	}else if(topic == "home/params/status/back_temp"){
		document.getElementById("backTemp").innerHTML = value + ' ºC';
	}else if(topic == "home/params/status/curr_temp"){
		document.getElementById("currentTemp").innerHTML = value + ' ºC';
	}else if(topic == "home/realy/status"){
		document.getElementById("boilerStatus").innerHTML = value;
	}
}


function setUserTemp(){
	var sel = Number(document.getElementById("userTempSelect").value) + 16;
	message = new Paho.MQTT.Message(sel.toString());
	message.destinationName = "home/params/set/user_temp";
	client.send(message);
}

function setBackTemp(){
	var sel = Number(document.getElementById("backTempSelect").value) + 16;
	message = new Paho.MQTT.Message(sel.toString());
	message.destinationName = "home/params/set/back_temp";
	client.send(message);
}

function setStartTime(){
	var sel = document.getElementById("startTimeSelect").value;
	message = new Paho.MQTT.Message(sel);
	message.destinationName = "home/params/set/time_start";
	client.send(message);
}

function setStopTime(){
	var sel = document.getElementById("stopTimeSelect").value;
	message = new Paho.MQTT.Message(sel);
	message.destinationName = "home/params/set/time_stop";
	client.send(message);
}

// Called when the disconnection button is pressed
function startDisconnect() {
    client.disconnect();
    document.getElementById("messages").innerHTML += '<span>Disconnected</span><br/>';
}

// Updates #messages div to auto-scroll
function updateScroll() {
    var element = document.getElementById("messages");
    element.scrollTop = element.scrollHeight;
}
