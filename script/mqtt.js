var mqttClient;
var lastRetainedMessage = "empty";
var statusid
var currentDeviceId = "";
var currentOutputedCoins = "";
var sensorData = "";

/**
 * @summary Creates a new instance of the MQTTClient class from Paho if the
 *          mqttClient is null
 */
if(mqttClient == null) {
    connect_to_broker("broker.hivemq.com", 8000, generate_unique_id());
}

/**
 * @summary Callback that handles the connection on success
 */
function onConnect() {
    console.log("Master Client Connected");
}

/**
 * @summary callback that handles a lost connection.
 * @param {*} responseObject 
 */
function onConnectionLost(responseObject) {
    if (responseObject.errorCode !== 0) {
        console.log("onConnectionLost:" + responseObject.errorMessage);
    }
}

/**
 * @summary Callback that handles the messages that arrive
 * @param {*} message 
 */
function onMessageArrived(message) {
    lastRetainedMessage = message.payloadString;
    console.log("onMessageArrived:" + message.payloadString);
}

/** 
* @summary Connects to the brocker over websockets
* @param {String} broker  : Command id that will be published to the topic
* @param {int}    port    : Topic that will be used to send the message
* @param {String} clientID: ID of the clien (name, number, etc.)
* @return {none}
*/
function connect_to_broker(broker, port, clientID) {
    mqttClient = new Paho.MQTT.Client(broker, port, "/mqtt", clientID);

    mqttClient.onConnectionLost = onConnectionLost;
    mqttClient.onMessageArrived = onMessageArrived;

    mqttClient.connect({
        keepAliveInterval: 30,
        onSuccess: onConnect
    });
}

/** 
* @summary Subscribes to a specific topic and publishes an MQTT message to it.
* @param {String} command: Command id that will be published to the topic
* @param {String} topic: Topic that will be used to send the message
* @return {none}
*/
function publish_message(command, topic) {
    mqttClient.subscribe(topic);
    message = new Paho.MQTT.Message(command);
    message.destinationName = topic;
    message.qos = 1;
    mqttClient.send(message);
}

/**
 * @summary Checks the received message and compares it with the expected respons.
 *          Triggers a callback after.
 * @param {*} expectedResponse It will be used to compare it with the received message
 * @param {*} callback         Callback that will implement the logic based on the received message
 */
function check_device_response(expectedResponse, callback) {
    var timeoutCounter = 0;

    var timer = setInterval(function () {
        if (lastRetainedMessage.length != expectedResponse.length) { 
            sensorData= lastRetainedMessage;            
            callback(true);                
            lastRetainedMessage = "empty";
            clearInterval(timer);
        }
        else {
            if ((timeoutCounter++) == 10) {
                 
                lastRetainedMessage = "empty";
                callback(false);  
                clearInterval(timer);
            }
        }
    }, 1000);
}

/**
 * 
 * @param {*} topic 
 */
function get_data_from_device(topic) {
    $("#read-data").html('<i class="fa fa-spinner fa-spin"></i>&nbsp;Citire in curs');
    publish_message('BURSTREAD', topic);
    check_device_response("BURSTREAD", check_received_response);
}

/**
 * 
 * @param {*} res 
 */
function check_received_response(res) {
    if(res == true) {
        $("#read-data").html('<i class="fa fa-upload"></i>&nbsp;Citeste Date');
        data = JSON.parse(sensorData);
        $.ajax({
            type: 'POST',
            url: `log_received_data.php`,
            data: data,
            success: function(response) {
                if (response == "ok") {
                    document.getElementById("info-msg").innerHTML = "Citirea a fost facuta cu succes. Datele au fost inregistrate in baza de date";

                } else {
                    document.getElementById("info-msg").innerHTML = "Eroare la citirea datelor";
                }
            }
        });        
    } else {
        $("#read-data").html('<i class="fa fa-times"></i>&nbsp;Reincearca');
    }
}


// generate a unique GUID for mqtt user uniqueness and allow same multiple devices
// toconnect in the same time
function generate_unique_id() {
    return 'xxxxxxxx-xxxx-4xxx-yxxx-xxxxxxxxxxxx'.replace(/[xy]/g, function (c) {
        var r = Math.random() * 16 | 0, v = c == 'x' ? r : (r & 0x3 | 0x8);
        return v.toString(16);
    });
}
