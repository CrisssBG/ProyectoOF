// api.js

const express = require('express');
const app = express();
const db = require('./db');
const axios = require('axios');  // Importa Axios para realizar solicitudes HTTP
//const ontologiaFuzzy = require('./ontologia_fuzzy');

app.use(express.json());

app.post('/api/busqueda_inteligente', (req, res) => {
    //const habilidad = req.body.habilidad;
    //const experiencia = req.body.experiencia;
    const { habilidad, experiencia } = req.body;

    // Realiza una solicitud HTTP a la ruta en Flask que utiliza la ontología difusa
    axios.post('http://localhost:5000/api/ontologia_fuzzy', { habilidad, experiencia })
        .then(response => {
            res.json(response.data);  // Devuelve los datos obtenidos de la ontología difusa
        })
        .catch(error => {
            console.error(error);
            res.status(500).json({ error: 'Error al realizar la búsqueda inteligente' });
        });

    ontologiaFuzzy.obtener_docentes_similares(habilidad, experiencia)
    .then(docentes => res.json(docentes))
    .catch(error => res.status(500).json({ error: 'Error al consultar base de datos' }));
});

// Inicia el servidor de Express
app.listen(5000, () => {
    console.log('Servidor de búsqueda inteligente en ejecución en el puerto 3000');
});