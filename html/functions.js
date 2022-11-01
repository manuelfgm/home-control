// Called after form input is processed
function startConnect() {
	document.getElementById("boilerStatus").style.color="#3d434c";
	
    // Generate a random client ID
    clientID = "clientID-" + parseInt(Math.random() * 1000);

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
	document.getElementById("boilerStatus").style.color="#3d434c";
	document.getElementById("aircondStatus").style.color="#3d434c";

    // Print output for the user in the messages div
    document.getElementById("messages").innerHTML += '<span>Subscribing to: home/#</span><br/>';

    // Subscribe to the requested topic
    client.subscribe("home/#");
	
	// Send update commands
	message1 = new Paho.MQTT.Message("1");
	message1.destinationName = "home/boiler/get";
	client.send(message1);
	message2 = new Paho.MQTT.Message("2");
	message2.destinationName = "home/aircond/get";
	client.send(message2);
	message3 = new Paho.MQTT.Message("3");
	message3.destinationName = "home/params/get";
	client.send(message3);
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
	var date = new Date();
    document.getElementById("messages").innerHTML +=
		'<span>'+ date.getFullYear() + "/" + (date.getMonth() + 1) + "/" + date.getDate() +
		"-" + date.getHours() + ":" + date.getMinutes() + ":" + date.getSeconds() + ": " +
		topic + '  | ' + value + '</span><br/>';
    updateScroll();
	if(topic == "home/params/status/curr_temp"){
		document.getElementById("currentTemp").innerHTML = value + ' ºC';
	}else if(topic == "home/boiler/status/start_time"){
		document.getElementById("startTime").innerHTML = value;
	}else if(topic == "home/boiler/status/stop_time"){
		document.getElementById("stopTime").innerHTML = value;
	}else if(topic == "home/boiler/status/user_temp"){
		document.getElementById("userTemp").innerHTML = value + ' ºC';
	}else if(topic == "home/boiler/status/back_temp"){
		document.getElementById("backTemp").innerHTML = value + ' ºC';
	}else if(topic == "home/boiler/status"){
		document.getElementById("boilerStatus").innerHTML = value;
		if(value=="OFF"){
			document.getElementById("boilerStatus").style.color="#dd0000";
		}else if(value=="ON"){
			document.getElementById("boilerStatus").style.color="#00dd00"
		}else{
			document.getElementById("boilerStatus").style.color="#3d434c";
		}
	}else if(topic == "home/aircond/status/on_temp"){
		document.getElementById("aircondTempOn").innerHTML = value + ' ºC';
	}else if(topic == "home/aircond/status/off_temp"){
		document.getElementById("aircondTempOff").innerHTML = value + ' ºC';
	}else if(topic == "home/aircond/status/auto"){
		if(value == "OFF"){
			document.getElementById("aircondAutoOn").
		}
		document.getElementById("userTemp").innerHTML = value;
	}else if(topic == "home/aircond/status"){
		document.getElementById("aircondStatus").innerHTML = value;
		if(value=="OFF"){
			document.getElementById("aircondStatus").style.color="#dd0000";
		}else if(value=="ON"){
			document.getElementById("aircondStatus").style.color="#00dd00"
		}else{
			document.getElementById("aircondStatus").style.color="#3d434c";
		}
	}
}

function selectControl(){
	var sel = document.getElementById("controlSelect").value;

	if (sel == 1){
		document.getElementById("boilerSect").style.display = 'block';
		document.getElementById("boilerOpt").style.display = 'block';
		document.getElementById("aircondSect").style.display = 'none';
		document.getElementById("aircondOpt").style.display = 'none';
	} else if (sel == 2){
		document.getElementById("boilerSect").style.display = 'none';
		document.getElementById("boilerOpt").style.display = 'none';
		document.getElementById("aircondSect").style.display = 'block';
		document.getElementById("aircondOpt").style.display = 'block';
	}else{
		document.getElementById("boilerSect").style.display = 'none';
		document.getElementById("boilerOpt").style.display = 'none';
	}
}

// Boiler
function setUserTemp(){
	document.getElementById("boilerStatus").style.color="#3d434c";
	
	var sel = Number(document.getElementById("userTempSelect").value) + 16;
	message = new Paho.MQTT.Message(sel.toString());
	message.destinationName = "home/boiler/set/user_temp";
	client.send(message);
}

function setBackTemp(){
	document.getElementById("boilerStatus").style.color="#3d434c";
	
	var sel = Number(document.getElementById("backTempSelect").value) + 16;
	message = new Paho.MQTT.Message(sel.toString());
	message.destinationName = "home/boiler/set/back_temp";
	client.send(message);
}

function setStartTime(){
	document.getElementById("boilerStatus").style.color="#3d434c";
	
	var sel = document.getElementById("startTimeSelect").value;
	message = new Paho.MQTT.Message(sel);
	message.destinationName = "home/boiler/set/start_time";
	client.send(message);
}

function setStopTime(){
	document.getElementById("boilerStatus").style.color="#3d434c";
	
	var sel = document.getElementById("stopTimeSelect").value;
	message = new Paho.MQTT.Message(sel);
	message.destinationName = "home/boiler/set/stop_time";
	client.send(message);
}

// Air cond
function setAircondTempOn(){
	document.getElementById("aircondStatus").style.color="#3d434c";
	
	var sel = Number(document.getElementById("aircondOnSelect").value) + 25;
	message = new Paho.MQTT.Message(sel.toString());
	message.destinationName = "home/aircond/set/on_temp";
	client.send(message);
}

function setAircondTempOff(){
	document.getElementById("aircondStatus").style.color="#3d434c";
	
	var sel = Number(document.getElementById("aircondOffSelect").value) + 24;
	message = new Paho.MQTT.Message(sel.toString());
	message.destinationName = "home/aircond/set/off_temp";
	client.send(message);
}

function setAircondAuto(on){
	document.getElementById("aircondStatus").style.color="#3d434c";
	
	if (on == true){
		message = new Paho.MQTT.Message("1");
		message.destinationName = "home/aircond/set/auto";
		client.send(message);
	}else{
		message = new Paho.MQTT.Message("0");
		message.destinationName = "home/aircond/set/auto";
		client.send(message);
	}
}

// Called when the disconnection button is pressed
function startDisconnect() {
	document.getElementById("boilerStatus").style.color="#3d434c";
	document.getElementById("aircondStatus").style.color="#3d434c";
	
    client.disconnect();
    document.getElementById("messages").innerHTML += '<span>Disconnected</span><br/>';
}

// Updates #messages div to auto-scroll
function updateScroll() {
    var element = document.getElementById("messages");
    element.scrollTop = element.scrollHeight;
}
