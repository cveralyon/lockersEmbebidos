const express = require("express");
const path = require("path");
const app = express();

app.use(express.static(path.join(__dirname, "public"))); // Aquí "public" debería ser el nombre de la carpeta que contiene tus archivos HTML, CSS y JavaScript.

const PORT = process.env.PORT || 5000;

app.listen(PORT, () => {
  console.log(`Server is running on port ${PORT}`);
});
