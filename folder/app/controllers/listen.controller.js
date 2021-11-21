const axios = require('axios');
const apiUrl = require('../config/api.config.js');

// Send http request to the program to run

exports.record = (req, res) => {
    console.log("Call record micro-service with: " + JSON.stringify(req.body.params));

    axios.post(apiUrl.analyseSound + 'rec', req.body)
    .then(response => {
        console.log("Success: " + JSON.stringify(response.status))
        res.send(response.data)
    })
    .catch(error => {
        console.log("Error: " + JSON.stringify(error.response.status) + " " + JSON.stringify(error.response.data))
        res.status(error.response.status).send({error})
    });
};

exports.preprocess = (req, res) => {
    console.log("Call preprocessing micro-service with: " + JSON.stringify(req.body.params));

    axios.post(apiUrl.analyseSound + 'preproc', req.body)
    .then(response => {
        console.log("Success: " + JSON.stringify(response.status))
        res.send(response.data)
    })
    .catch(error => {
        console.log("Error: " + JSON.stringify(error.response.status) + " " + JSON.stringify(error.response.data))
        res.status(error.response.status).send({error})
    });
};