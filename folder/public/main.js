var localDB = {};

//-------------------------------------------------- Forms & Graphs --------------------------------------------------
$('form').submit(function(event) {
    var sendData = {}, paramsSer = [], params = {}, formName, url, method, graphID;
    
    // --------------------------------------------- Get the inputs
    paramsSer = $(this).serializeArray();
    for (index = 0; index < paramsSer.length; ++index) {
        params[paramsSer[index].name] = paramsSer[index].value;
    }
    sendData['params'] = params;

    // --------------------------------------------- Get the additional needed data
    formName = $(this).attr('name');
    console.log(formName)
    switch (formName) {
        case 'rawSignal':
            break;
        case 'preprocSignal':
            sendData['rawSignal'] = localDB['rawSignal'];
            break;
    }

    // Get url and method
    url = $(this).attr('action');
    method = $(this).attr('method');
    console.log(method + ' ' + url + '. Request in data : ');
    console.log(sendData);

    // Get graph ID
    graphID = '#'+$(this).next().attr('id');

    // --------------------------------------------- Send the form
    axios({
        method: method,
        url: url,
        data: sendData
    })// --------------------------------------------- Receive the response
    .then(function (response) {
        console.log("Success: " + JSON.stringify(response.status));
        console.log(response.data)
        // If micro-service action is succesful, dispay received data on a graph
        if (response.data.statusOp.success) {
            // Store response in local DB
            localDB[formName] = response.data;
            console.log('localDB: ');
            console.log(localDB);

            // --------------------------------------------- Highcharts graph
            // Format graph data for highchart
            const graphDataJSON = response.data.data 
            const keyGraph = Object.keys(graphDataJSON)
            const graphData = [graphDataJSON[keyGraph[0]],graphDataJSON[keyGraph[1]]]
            transpose = array => array[0].map((x,i) => array.map(x => x[i]))
            const graphDataT = transpose(graphData)

            // Update the graph
            var myChart = $(graphID).highcharts();
            while (myChart.series.length) {
                myChart.series[0].remove();
            }
            myChart.addSeries({
                id: response.data.name,
                name: response.data.name,
                data: graphDataT,
                marker: {
                    enabled: false
                  },
                // type: 'area',
            }, false);
            myChart.redraw();
        }   // End of: if request successed
    })
    .catch(function (error) {
        console.log(error);
    })

    // Do not send the form by built-in html form action
    event.preventDefault(); 
    return false;
});

//-------------------------------------------------- Buttons --------------------------------------------------

$( "#thresdVisu" ).click(function() {
    const thres = parseFloat($("#preprocThres").val())
    const dur = parseFloat($('input[name="recDuration"]').val())   
    var myChart = $("#rawSignalGraph").highcharts();
    if (myChart.series.length > 1) {
        myChart.get('Threshold').remove();
    }
    myChart.addSeries({
        id: "Threshold",
        name: "Threshold",
        data: [[0, thres], [localDB.rawSignal.data.time[localDB.rawSignal.data.time.length-1], thres]],
        marker: {
            enabled: false
            },
    });
});