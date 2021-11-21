const express = require('express');
var bodyParser = require('body-parser'); // Charge le middleware de gestion des paramètres
var favicon = require('serve-favicon'); // Charge le middleware de favicon

// Config
const PORT = 3000;

// Create express app
const app = express();

//Add the middlewares. Warning, the order is important!!
app.use(express.static('public')); // Indique que le dossier /public contient des fichiers statiques (middleware chargé de base)
app.use(favicon(__dirname + '/public/favico.ico'));
app.use(express.urlencoded({extended: true, limit: '50mb'}))   // Valable pour toutes les routes. On peut le changer pour 1 route en le mettant en param de la route
app.use(express.json({extended: true, limit: '50mb'}))
app.use((req, res, next) => {               // Permettre notre front-end de faire des requêtes http
    res.header('Access-Control-Allow-Origin', '*');
    next(); 
});

// Define the main route
app.get('/', (req, res) => {
    res.sendFile(__dirname + '/index.html');
});

// Define other routes
require('./app/routes/listen.routes.js')(app);

// Routes error management. If the request match with no routes, it is this one.
app.use((req, res, next) => {
    res.setHeader('Content-Type', 'text/plain');
    res.status(404).send('Error 404 : Unknown route');
});

// Listen for requests
server = app.listen(PORT, () => {
    console.log("Server is listening on port " + PORT);
    console.log("http://localhost:" + PORT)
});
