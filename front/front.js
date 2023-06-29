const CLIENT_ID = "cerraduras-Esp32";
const TOPIC_PUB = "$aws/things/" + CLIENT_ID + "/shadow/update";
const SERVER = "a1otg0g21ui78m-ats.iot.us-east-2.amazonaws.com";
const region = "us-east-2";
const clientId = "cerraduras-Esp32";
const accessKeyId = "AKIAW3UEPPIEHX6OK27B";
const secretAccessKey = "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";
const endpoint = `wss://${SERVER}`;

//const AWS = require("aws-sdk");
// Configura el SDK de AWS
AWS.config.region = "us-east-2"; // Reemplaza con tu región
AWS.config.credentials = new AWS.Credentials({
  accessKeyId: "AKIAW3UEPPIEHX6OK27B",
  secretAccessKey: "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",
});
console.log(AWS);

const mqttClient = new WebSocket(endpoint);

mqttClient.onopen = () => {
  console.log("Conexión MQTT establecida");

  const connectMsg = {
    action: "connect",
    client_id: clientId,
    access_key_id: accessKeyId,
    secret_access_key: secretAccessKey,
  };
  mqttClient.send(JSON.stringify(connectMsg));

  const subscribeMsg = {
    action: "subscribe",
    TOPIC_PUB,
  };
  mqttClient.send(JSON.stringify(subscribeMsg));
};

mqttClient.onmessage = (event) => {
  const message = JSON.parse(event.data);
  console.log("Mensaje recibido:", message);
};
mqttClient.onerror = (error) => {
  console.error("Error de conexión:", error);
};

mqttClient.onclose = (event) => {
  console.log("Conexión MQTT cerrada");
  console.log("Código de cierre:", event.code);
  console.log("Motivo del cierre:", event.reason);
};

// Para publicar un mensaje en el tema
//client.publish(TOPIC_PUB, 'Mensaje de prueba');

// Definir las constantes del servidor MQTT

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
  client.subscribe(TOPIC_PUB);
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
  console.log("Mensaje recibido: " + message.payloadString);
  let receivedMessage = JSON.parse(message.payloadString);

  if (receivedMessage.action === "rutVerification") {
    if (receivedMessage.result === "found") {
      console.log(
        `El RUT existe y está asociado a los lockers: ${receivedMessage.lockers.join(
          ", "
        )}`
      );
      // Aquí podrías actualizar la UI para mostrar que el RUT fue encontrado y mostrar los nombres de los lockers.
    } else {
      console.log(`El RUT no fue encontrado`);
      // Aquí podrías actualizar la UI para mostrar que el RUT no fue encontrado.
    }
  } else {
    // manejo de otros tipos de mensajes...
  }
}

function connectMqttClient() {
  console.log("holappp connectMqttClient 1");
  client.connect({
    useSSL: true,
    timeout: 3,
    mqttVersion: 4,
    onSuccess: onConnect,
  });
}

document.addEventListener("DOMContentLoaded", function () {
  connectMqttClient();
  console.log("holappp");
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
  rut = quitarPuntosYGuiones(rut);
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
  console.log(query);
  console.log(urlQueryParams);
  const rutValue = urlQueryParams.get("RUN");
  console.log(rutValue);

  document.getElementById("rutCheck").value = rutValue;

  html5QrcodeScanner.clear();
}

function startScan() {
  html5QrcodeScanner = new Html5QrcodeScanner("reader", {
    fps: 10,
    qrbox: 250,
  });
  html5QrcodeScanner.render(onScanSuccess);
}

function quitarPuntosYGuiones(cadena) {
  var nuevaCadena = cadena.replace(/[-.]/g, "");
  return nuevaCadena;
}

function verifyHashAndOpenLocker() {
  var rut = document.getElementById("rutCheck").value;
  rut = quitarPuntosYGuiones(rut);
  var hash = CryptoJS.SHA256(rut);
  var providedHash = document.getElementById("hashCheck").value;

  if (hash == providedHash) {
    document.getElementById("verifyResult").innerHTML = "ACCESO CONCEDIDO";
    abrirLockerUsuario(rut);
  } else {
    document.getElementById("verifyResult").innerHTML = "ACCESO DENEGADO";
  }
}

function abrirLockerAdmin(rut, lockervar) {
  if (!isConnected) {
    print(" aun no se ha conectado");
    return;
  }

  // Creamos un objeto con el estado deseado para el locker
  let desiredState = {
    action: "open",
    rut: rut,
    locker: lockervar,
    retiro: "false",
  };

  // Convertimos el objeto a una cadena JSON
  let message = new Paho.MQTT.Message(JSON.stringify(desiredState));
  message.destinationName = TOPIC_SUB;
  client.send(message);
}

function abrirLockerUsuario(rut) {
  if (!isConnected) {
    console.log("Aún no conectado, intentando conectar...");
    connectMqttClient();
    return;
  }

  // Creamos un objeto con el estado deseado para el locker
  let desiredState = {
    action: "open",
    rut: rut,
    retiro: "true",
  };

  // Convertimos el objeto a una cadena JSON
  let message = new Paho.MQTT.Message(JSON.stringify(desiredState));
  message.destinationName = TOPIC_SUB;
  client.send(message);
}

// function verifyRut(rut) {
//   if (!isConnected) {
//     console.log("Aún no conectado, intentando conectar...");
//     connectMqttClient();
//     return;
//   }

//   // Creamos un objeto con la acción y el RUT para verificar
//   let request = {
//     action: "verify",
//     rut: rut,
//   };

//   // Convertimos el objeto a una cadena JSON
//   let message = new Paho.MQTT.Message(JSON.stringify(request));
//   message.destinationName = TOPIC_SUB;
//   client.send(message);
// }
