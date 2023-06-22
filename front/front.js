// Importar la biblioteca Paho MQTT
var Paho = require("paho-mqtt");
SERVER = "a1ji7xd8yopagp-ats.iot.us-east-2.amazonaws.com";
CLIENT_ID = "cerraduras-Esp32";
TOPIC_PUB = "$aws/things/" + CLIENT_ID + "/shadow/update";
TOPIC_SUB = "$aws/things/" + CLIENT_ID + "/shadow/update/delta";

// Crear un nuevo cliente MQTT
var client = new Paho.Client(SERVER, Number(443), CLIENT_ID);

// Configurar las callbacks
client.onConnectionLost = onConnectionLost;
client.onMessageArrived = onMessageArrived;

// Conectar el cliente
client.connect({
  useSSL: true,
  timeout: 3,
  mqttVersion: 4,
  onSuccess: onConnect,
});

// Cuando la conexión es exitosa
function onConnect() {
  console.log("onConnect");
  client.subscribe(TOPIC_SUB);
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

// Funciones para abrir los lockers
function abrirLockerAdmin(hash) {
  var message = new Paho.Message(hash);
  message.destinationName = TOPIC_PUB;
  client.send(message);
}

function abrirLockerUsuario(hash) {
  var message = new Paho.Message(hash);
  message.destinationName = TOPIC_PUB;
  client.send(message);
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
  // Llamamos la función que está en front.js
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
    // Llamamos la función que está en front.js
    abrirLockerUsuario(rut);
  } else {
    document.getElementById("verifyResult").innerHTML = "ACCESO DENEGADO";
  }
}

// Deberías implementar estas funciones que interactúan con el backend
// Función para abrir el locker del administrador
function abrirLockerAdmin(hash) {
  // Crear un objeto con la información necesaria
  var data = {
    rut: hash,
    action: "open",
  };

  // Convertir el objeto en una cadena JSON
  var jsonData = JSON.stringify(data);

  // Enviar la solicitud AJAX a la API de AWS IoT Core
  var xhr = new XMLHttpRequest();
  xhr.open("POST", SERVER, true);
  xhr.setRequestHeader("Content-Type", "application/json");
  xhr.send(jsonData);

  xhr.onreadystatechange = function () {
    if (xhr.readyState === 4 && xhr.status === 200) {
      var json = JSON.parse(xhr.responseText);
      console.log(json);
    }
  };
}

function getDeviceShadow() {
  // Enviar una solicitud AJAX para obtener la sombra del dispositivo
  var xhr = new XMLHttpRequest();
  xhr.open("GET", SERVER + "/device-shadow", true);
  xhr.setRequestHeader("Content-Type", "application/json");
  xhr.send();

  xhr.onreadystatechange = function () {
    if (xhr.readyState === 4 && xhr.status === 200) {
      var json = JSON.parse(xhr.responseText);
      console.log(json);
    }
  };
}

// Función para abrir el locker del usuario
function abrirLockerUsuario(hash) {
  // Crear un objeto con la información necesaria
  var data = {
    rut: hash,
    action: "open",
  };

  // Convertir el objeto en una cadena JSON
  var jsonData = JSON.stringify(data);

  // Enviar la solicitud AJAX a la API de AWS IoT Core
  var xhr = new XMLHttpRequest();
  xhr.open("POST", SERVER, true);
  xhr.setRequestHeader("Content-Type", "application/json");
  xhr.send(jsonData);

  xhr.onreadystatechange = function () {
    if (xhr.readyState === 4 && xhr.status === 200) {
      var json = JSON.parse(xhr.responseText);
      console.log(json);
    }
  };
}
