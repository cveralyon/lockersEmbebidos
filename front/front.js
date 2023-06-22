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
  abrirLockerAdmin(hash);
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
    abrirLockerUsuario(hash);
  } else {
    document.getElementById("verifyResult").innerHTML = "ACCESO DENEGADO";
  }
}

// Deberías implementar estas funciones que interactúan con el backend
function abrirLockerAdmin(hash) {
  // TODO: Implementar esta función
}

function abrirLockerUsuario(hash) {
  // TODO: Implementar esta función
}
