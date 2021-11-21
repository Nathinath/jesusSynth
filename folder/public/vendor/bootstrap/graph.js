$( document ).ready(function() {

    //-------------------------------------------------- Highcharts chart --------------------------------------------------
        $('#rawSignalGraph').highcharts({
            chart: {
              type: 'line',
              zoomType: 'x',
              panning: true,
              panKey: 'shift'
            },
            
            title: {
              text: 'Title'
            },
        
            subtitle: {
              text: 'Subtitle'
            },
    
            xAxis: {
              title: {
                text: "Time [s]"
              },
            },
        
            yAxis: {
              opposite:false,
              showEmpty: true,
              title: {
                text: 'Amplitude [/]'
              },
            },
    
            series: [{
                id: "label",
                name: "Label",
                data: 0,
                marker: {
                    enabled: false
                }
            }],
    
            plotOptions: {
                series: {
                    lineWidth: 0.8
                }
            }
    
            // rangeSelector: {
            //     selected: 4,    // Select the 4th input button to select the range. (They are hidden but it is the full range button)
            //     enabled: true, // Hide buttons to select the range
            //     inputEnabled: false,           
            //     buttonTheme: {
            //         visibility: 'hidden'
            //     },
            //     labelStyle: {
            //         visibility: 'hidden'
            //     }
            // },
        });
    
        $('#preprocGraph').highcharts({    
            chart: {
              type: 'line',
              zoomType: 'x',
              panning: true,
              panKey: 'shift'
            },
    
            title: {
              text: 'Title'
            },
        
            subtitle: {
              text: 'Subtitle'
            },
    
            xAxis: {
              title: {
                text: "Time [s]"
              },
            },
        
            yAxis: {
              opposite:false,
              showEmpty: true,
              title: {
                text: 'Amplitude [/]'
              },
            },
    
            series: [{
                id: "label",
                name: "Label",
                data: 0
            }],
    
            plotOptions: {
                series: {
                    lineWidth: 0.8
                }
            }
        });
    //-------------------------------------------------- END Highcharts chart --------------------------------------------------
    });
    
    
    
    