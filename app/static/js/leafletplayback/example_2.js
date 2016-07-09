var plotTrajectoryTimeline = (function(user_ids_str) {
    console.log(user_ids_str);
    // Setup leaflet map
    var map = new L.Map('map');

    var basemapLayer = new L.TileLayer('http://{s}.tiles.mapbox.com/v3/github.map-xgq2svrz/{z}/{x}/{y}.png');

    // Center map and default zoom level
    map.setView([55.622534,12.080729], 15);

    // Adds the background layer to the map
    map.addLayer(basemapLayer);

    // Colors for AwesomeMarkers
    var _colorIdx = 0,
        _colors = [
          'orange',
          'green',
          'blue',
          'purple',
          'darkred',
          'cadetblue',
          'red',
          'darkgreen',
          'darkblue',
          'darkpurple'
        ];
        
    function _assignColor() {
        return _colors[_colorIdx++%10];
    }
    
    // =====================================================
    // =============== Playback ============================
    // =====================================================

    // Playback options
    var playbackOptions = {        
        // layer and marker options
        layer: {
            pointToLayer : function(featureData, latlng){
                var result = {};
                
                if (featureData && featureData.properties && featureData.properties.path_options){
                    result = featureData.properties.path_options;
                }
                
                if (!result.radius){
                    result.radius = 5;
                }
                
                return new L.CircleMarker(latlng, result);
            }
        },
        
        marker: function(){
            return {
                icon: L.AwesomeMarkers.icon({
                    prefix: 'fa',
                    icon: 'bullseye', 
                    markerColor: _assignColor()
                }) 
            };
        }        
    };
    
    // Initialize playback

    var url = 'http://127.0.0.1:5000/api/trajectory-timeline?user_ids=' + user_ids_str;
    d3.json(url,function(data){
        var playback = new L.Playback(map, data.data, null, playbackOptions);
        // Initialize custom control
        var control = new L.Playback.Control(playback);
        control.addTo(map);
        
        // Add data

        //playback.addData(data.data[0]);

        data.data.forEach(function(entry) {
           playback.addData(entry)
        });
    });
       
});

var plotTimeline = (function(data, div_id) {
    var map = new L.Map(div_id);

    var basemapLayer = new L.TileLayer('http://{s}.tiles.mapbox.com/v3/github.map-xgq2svrz/{z}/{x}/{y}.png');

    // Center map and default zoom level
    map.setView([55.622534,12.080729], 15);

    // Adds the background layer to the map
    map.addLayer(basemapLayer);

    // Colors for AwesomeMarkers
    var _colorIdx = 0,
        _colors = [
          'orange',
          'green',
          'blue',
          'purple',
          'darkred',
          'cadetblue',
          'red',
          'darkgreen',
          'darkblue',
          'darkpurple'
        ];

    function _assignColor() {
        return _colors[_colorIdx++%10];
    }

    // =====================================================
    // =============== Playback ============================
    // =====================================================

    // Playback options
    var playbackOptions = {
        // layer and marker options
        layer: {
            pointToLayer : function(featureData, latlng){
                var result = {};

                if (featureData && featureData.properties && featureData.properties.path_options){
                    result = featureData.properties.path_options;
                }

                if (!result.radius){
                    result.radius = 5;
                }

                return new L.CircleMarker(latlng, result);
            }
        },

        marker: function(){
            return {
                icon: L.AwesomeMarkers.icon({
                    prefix: 'fa',
                    icon: 'bullseye',
                    markerColor: _assignColor()
                })
            };
        }
    };

    // Initialize playback

    var url = 'http://127.0.0.1:5000/api/routes_to_rf';
    d3.json(url,function(data){
        var playback = new L.Playback(map, data.data, null, playbackOptions);
        // Initialize custom control
        var control = new L.Playback.Control(playback);
        control.addTo(map);

        // Add data

        //playback.addData(data.data[0]);

        data.data.forEach(function(entry) {
           playback.addData(entry)
        });
    });

});


