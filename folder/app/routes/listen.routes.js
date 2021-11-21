
module.exports = (app) => {
    const services = require('../controllers/listen.controller.js');
    
    // Post request to /record => launches services.record function
    app.post('/record', services.record);

    app.post('/preprocess', services.preprocess); 
}