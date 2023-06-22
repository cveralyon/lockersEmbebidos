// Definir las constantes del servidor MQTT
const SERVER = "a1ji7xd8yopagp-ats.iot.us-east-2.amazonaws.com";
const CLIENT_ID = "cerraduras-Esp32";
const TOPIC_PUB = "$aws/things/" + CLIENT_ID + "/shadow/update";
const TOPIC_SUB = "$aws/things/" + CLIENT_ID + "/shadow/update/delta";

// Crear un nuevo cliente MQTT
const client = new Paho.MQTT.Client(SERVER, Number(443), CLIENT_ID);

// Configurar las callbacks
client.onConnectionLost = onConnectionLost;
client.onMessageArrived = onMessageArrived;

let isConnected = false;

// Cuando la conexión es exitosa
function onConnect() {
  console.log("onConnect");
  client.subscribe(TOPIC_SUB);
  isConnected = true; // Marcamos que la conexión fue exitosa.
}

// Cuando se pierde la conexión
function onConnectionLost(responseObject) {
  if (responseObject.errorCode !== 0) {
    console.log("onConnectionLost:" + responseObject.errorMessage);
  }
}

// Cuando llega un mensaje
function onMessageArrived(message) {
  console.log("onMessageArrived:" + message.payloadString);
}

function connectMqttClient() {
  client.connect({
    useSSL: true,
    timeout: 3,
    mqttVersion: 4,
    onSuccess: onConnect,
  });
}

document.addEventListener("DOMContentLoaded", function () {
  // Admin
  if (document.getElementById("generateBtn")) {
    document
      .getElementById("generateBtn")
      .addEventListener("click", openLocker);
  }

  // User
  if (document.getElementById("startScanBtn")) {
    document
      .getElementById("startScanBtn")
      .addEventListener("click", startScan);
  }

  if (document.getElementById("verifyBtn")) {
    document
      .getElementById("verifyBtn")
      .addEventListener("click", verifyHashAndOpenLocker);
  }
});

// Funciones para el admin
function generateHash(rut) {
  var hash = CryptoJS.SHA256(rut);
  document.getElementById("hashResult").innerHTML = "Hash de tu RUT: " + hash;
  return hash;
}

function openLocker() {
  var rut = document.getElementById("rut").value;
  var hash = generateHash(rut);
  abrirLockerAdmin(rut);
}

// Funciones para el usuario
let html5QrcodeScanner;

function onScanSuccess(decodedText, decodedResult) {
  if (html5QrcodeScanner === undefined) {
    alert("Scanner not initialized");
    return;
  }

  if (!decodedText.includes("?")) {
    alert("Are you reading a valid document?");
    return;
  }

  const [url, query] = decodedText.split("?");

  const urlQueryParams = new URLSearchParams(query);

  const rutValue = urlQueryParams.get("RUN");

  html5QrcodeScanner.clear();

  const element = document.getElementById("document-result");

  element.innerHTML = `We have found a document: ${rutValue}`;

  document.getElementById("rutCheck").value = rutValue;
}

function startScan() {
  html5QrcodeScanner = new Html5QrcodeScanner("reader", {
    fps: 10,
    qrbox: 250,
  });
  html5QrcodeScanner.render(onScanSuccess);
}

function verifyHashAndOpenLocker() {
  var rut = document.getElementById("rutCheck").value;
  var hash = CryptoJS.SHA256(rut);
  var providedHash = document.getElementById("hashCheck").value;

  if (hash == providedHash) {
    document.getElementById("verifyResult").innerHTML = "ACCESO CONCEDIDO";
    abrirLockerUsuario(rut);
  } else {
    document.getElementById("verifyResult").innerHTML = "ACCESO DENEGADO";
  }
}

function abrirLockerAdmin(lockerName) {
  if (!isConnected) {
    console.log("Aún no conectado, intentando conectar...");
    connectMqttClient();
    return;
  }

  // Creamos un objeto con el estado deseado para el locker
  let desiredState = {
    action: "open",
    locker: lockerName,
  };

  // Convertimos el objeto a una cadena JSON
  let message = new Paho.MQTT.Message(JSON.stringify(desiredState));
  message.destinationName = TOPIC_PUB;
  client.send(message);
}

function abrirLockerUsuario(lockerName) {
  if (!isConnected) {
    console.log("Aún no conectado, intentando conectar...");
    connectMqttClient();
    return;
  }

  // Creamos un objeto con el estado deseado para el locker
  let desiredState = {
    action: "open",
    locker: lockerName,
  };

  // Convertimos el objeto a una cadena JSON
  let message = new Paho.MQTT.Message(JSON.stringify(desiredState));
  message.destinationName = TOPIC_PUB;
  client.send(message);
}
