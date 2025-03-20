
// document.addEventListener("DOMContentLoaded", function () {
//     const element = document.querySelector("#miBoton"); // Cambia #miElemento por tu selector
//     if (element) {
//         element.addEventListener("click", function () {
//             console.log("¡Elemento clickeado!");
//         });
//     } else {
//         console.error("El elemento no se encontró en el DOM.");
//     }
// });

// const element = document.querySelector("#miboton"); // Cambia el selector según tu caso
// if (element) {
//     element.addEventListener("click", () => {
//         console.log("Evento registrado.");
//     });
// } else {
//     console.error("El elemento no fue encontrado.");
// }
// document.getElementById("registroForm").addEventListener("submit", function(event) {
//     event.preventDefault();

//     const nombre = document.getElementById("nombre").value;
//     const apellido = document.getElementById("apellido").value;
//     const documento_identidad = document.getElementById("documento_identidad").value;
//     const celular = document.getElementById("celular").value;
//     const correo = document.getElementById("correo").value;
//     const contrasena = document.getElementById("contrasena").value;

//     fetch("http://127.0.0.1:5000/auth/register", {  
//         method: "POST",
//         headers: { "Content-Type": "application/json" },
//         body: JSON.stringify({ nombre, apellido, documento_identidad, celular, correo, contrasena })
//     })
//     .then(response => response.json())
//     .then(data => alert(data.message))
//     .catch(error => console.error("Error:", error));
// });


// document.getElementById("loginForm").addEventListener("submit", function(event) {
//     event.preventDefault();

//     const correo = document.getElementById("correo").value;
//     const contrasena = document.getElementById("contrasena").value;

//     fetch("/auth/login", {
//         method: "POST",
//         headers: { "Content-Type": "application/json" },
//         body: JSON.stringify({ correo, contrasena })
//     })
//     .then(response => response.json())
//     .then(data => alert(data.message))
//     .catch(error => console.error("Error:", error));
// });

<script src="scripts.js"></script>
