//busqueda_inteligente.js
const formBusqueda = document.getElementById('form-busqueda');
const resultadoBusqueda = document.getElementById('resultado-busqueda');

formBusqueda.addEventListener('submit', (event) => {
    event.preventDefault();
    const habilidad = document.getElementById('habilidad').value;
    const experiencia = document.getElementById('experiencia').value;

    // Consultar a la API para obtener los docentes que coincidan con la búsqueda
    //fetch('/api/busqueda_inteligente', {
    fetch('/api/ontologia_fuzzy', {
        method: 'POST',
        headers: { 'Content-Type': 'application/json' },
        body: JSON.stringify({ habilidad, experiencia })
    })
    .then(response => response.json())
    .then(data => {
        //console.log(data); // Agregar este console.log para verificar los datos
        resultadoBusqueda.innerHTML = '';
        data.docentes.forEach(docente => {
            const elemento = document.createElement('li');
            //elemento.textContent = `${docente.nombre} - ${docente.experiencia} años de experiencia`;
            //elemento.textContent = `${docente[0]} - ${docente[1]} años de experiencia - Habilidades: ${docente[2]}`;
            elemento.textContent = `│ Docente: ${docente.nombre} │ ${docente.experiencia} años de experiencia │ Habilidades: ${docente.habilidades} │`;
            //elemento.textContent = `Docente: ${docente.nombre} - ${docente.experiencia} años de experiencia`;
            resultadoBusqueda.appendChild(elemento);
        });
    })
    .catch(error => console.error('Error:', error));    
});