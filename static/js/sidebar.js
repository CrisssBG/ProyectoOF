// static/js/sidebar.js

function openNav() {
    //document.getElementById("mySidenav").style.width = "250px";
    //document.getElementById("main").style.marginLeft = "250px";
    var sidenav = document.getElementById("mySidenav");
    var main = document.getElementById("main");
    var menuIcon = document.getElementById("menuIcon");
    
    // Ajusta el ancho de la barra lateral y el margen izquierdo del contenido principal
    sidenav.style.width = "200px";
    main.style.marginLeft = "200px";
    
    // Cambia el icono a la X
    menuIcon.className = "fas fa-chevron-left";

    localStorage.setItem('sidebarOpen', 'true');
}

function closeNav() {
    document.getElementById("mySidenav").style.width = "50px"; // Tamaño más pequeño
    document.getElementById("main").style.marginLeft= "50px"; // Margen más pequeño
    //document.getElementById("openBtn").style.display = "block"; // Muestra el botón al cerrar la barra

    // Oculta el texto en la barra lateral
    var links = document.querySelectorAll(".sidenav a");
    for (var i = 0; i < links.length; i++) {
        links[i].classList.add("hide-text");
    }

    localStorage.setItem('sidebarOpen', 'false');
}

function toggleNav() {
    var sidenav = document.getElementById("mySidenav");
    var main = document.getElementById("main");
    var menuIcon = document.getElementById("menuIcon");
    
    if (sidenav.style.width === "50px") {
        // Si la barra lateral está minimizada, ábrela y cambia el icono a la X
        sidenav.style.width = "200px";
        main.style.marginLeft = "200px";
        menuIcon.className = "fas fa-chevron-left";
        localStorage.setItem('sidebarOpen', 'true');
    } else {
        // Si la barra lateral está abierta, ciérrala y cambia el icono a las tres rayas
        sidenav.style.width = "50px";
        main.style.marginLeft = "50px";
        menuIcon.className = "fas fa-chevron-right";
        localStorage.setItem('sidebarOpen', 'false');
    }
    console.log("toggleNav() called"); // Agrega este console.log para depuración
}
/*
window.onload = function() {
    // Abre la barra lateral por defecto
    closeNav();
};*/

window.onload = function() {
    var sidebarOpen = localStorage.getItem('sidebarOpen');
    if (sidebarOpen === 'true') {
        openNav();
    } else {
        closeNav();
    }
};