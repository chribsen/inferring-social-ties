var app = angular.module("dtuApp", ['leaflet-directive', 'ngVis']);
        app.controller("UserExplorerController", [ "$scope", "leafletData", "$interval", "$http", function($scope, leafletData, $interval, $http, VisDataSet) {

            /*
            $http.get("/api/users/clusters") .success(function(response) {
                 // no context issues since "vm" is in scope
                 $scope.clusters = response.data.data;
            });
            */

            var vm = this;


            angular.extend($scope, {
                san_fran: {
                    lat: 55.618534,
                    lng: 12.080729,
                    zoom: 15
                },
                events: {},

                defaults: {
            tileLayer: "http://{s}.tiles.mapbox.com/v3/github.map-xgq2svrz/{z}/{x}/{y}.png",
            tileLayerOptions: {
                opacity: 0.8,
                detectRetina: true,
                reuseTiles: true
            },
            scrollWheelZoom: false
        }
            });

            /* Plot areas on Roskilde */
            leafletData.getMap("map").then(function(map) {
                for(var i = 0 ; i < rf_areas.length ; i++) {
                    L.geoJson(rf_areas[i].data, {style:rf_areas[i].style}).addTo(map);
                }
            });

            $scope.options = {
              autoResize: true,
              height: '600',
              width: '100%',
              layout: {improvedLayout:false}
            };

            var layersToRemove = [];
            var userMarkerLookup = {};
            var userDataLookup = {};

            var offset = 1;
            var network = null;
            var nodes = null;
            var edges = null;
            var graph = null;


            $scope.goForward = function() {
                offset++;
                $scope.startTemporalAnimation(offset);

            };

            $scope.goBackward = function() {
                offset--;
                $scope.startTemporalAnimation(offset);
            };

            $scope.startTemporalAnimation = function(newOffset) {
                $http.get("/api/dyads?network_type=common&offset=" + newOffset).success(function(response) {
                     // no context issues since "vm" is in scope
                        console.log(response);

                    $scope.timestamp = response.start + ' - ' + response.end;

                    if(graph === null) {
                        console.log('Making graph...');
                        /*
                        nodes = new vis.DataSet(response.network.nodes);
                        edges = new vis.DataSet(response.network.edges);
                        var container = document.getElementById('mynetwork');
                        var data = {
                            nodes: nodes,
                            edges: edges
                        };
                        var options = {
                            autoResize: true,
                            height: '600',
                            width: '100%',
                            layout: {improvedLayout: false},
                              interaction:{ dragNodes:true},
                              physics:{
                                enabled: true,
                                damping: 0.2,

                                stabilization: {
                                  enabled: true,
                                  iterations: 1000,
                                  updateInterval: 100,
                                  onlyDynamicEdges: false,
                                  fit: true
                                }
                          },
                            nodes: {
                                  shape: 'dot',
                                  scaling: {
                                    customScalingFunction: function (min,max,total,value) {
                                      return value/total;
                                    },
                                    min:5,
                                    max:300
                                  }
                                },
                            edges: {
                                width: 0.15,
                                color: {inherit: 'from'},
                                smooth: {
                                  type: 'continuous'
                                }
                              },
                              physics: {
                                stabilization: true,
                                barnesHut: {
                                  gravitationalConstant: -8000,
                                  springConstant: 0.001,
                                  springLength: 20
                                }
                              },
                              interaction: {
                                tooltipDelay: 200,
                                hideEdgesOnDrag: true
                              }
                        };
                        network = new vis.Network(container, data, options);
                        network.fit();

                        network.on("click", function (params) {
                            var user_id = params.nodes[0];
                            var marker = userMarkerLookup[user_id];
                            console.log(marker);
                            leafletData.getMap("map").then(function(map) {
                                //map.removeLayer(marker);

                                marker.setStyle({
                                    color: 'black',
                                    fillColor: 'black',
                                    fillOpacity: 0
                                });

                                marker.bindPopup('<strong>Same concerts: </strong><br> Paul McCartney, Ukendt Kunstner <br><strong>Mutual: </strong> 4').openPopup();
                            });

                        });
                        */
                        graph = Viva.Graph.graph();
                        // Step 2. We add nodes and edges to the graph:
                        var layout = Viva.Graph.Layout.forceDirected(graph, {
                            springLength : 100,
                            springCoeff : 0.0008,
                            dragCoeff : 0.02,
                            gravity : -1.2
                        });


                        response.network.nodes.forEach(function(node) {
                           graph.addNode(node.id, node);
                        });
                        response.network.edges.forEach(function(edge) {
                            graph.addLink(edge.from, edge.to);
                        });

                        var graphics = Viva.Graph.View.svgGraphics();

                        graphics.node(function(node) {
                            // node.data holds custom object passed to graph.addNode():
                            var ui =  Viva.Graph.svg('circle')
                               .attr('r', "8")
                                .attr('fill', node.data.color);
                            $(ui).click(function() { // mouse click
                                var user_id = node.id;
                                var marker = userMarkerLookup[user_id];
                                console.log(marker);
                                leafletData.getMap("map").then(function(map) {
                                    //map.removeLayer(marker);

                                    marker.setStyle({
                                        color: 'black',
                                        fillColor: 'black',
                                        fillOpacity: 0
                                    });

                                    marker.bindPopup('<strong>Same concerts: </strong><br> Paul McCartney, Ukendt Kunstner (dummy data) <br><strong>Mutual: </strong> 4 (dummy data)').openPopup();
                                });
                            });
                            return ui;
                        });
                        graphics.placeNode(function(nodeUI, pos) {
                            // nodeUI - is exactly the same object that we returned from
                            //   node() callback above.
                            // pos - is calculated position for this node.
                            nodeUI.attr('cx', pos.x).attr('cy', pos.y);
                        });

                        var renderer = Viva.Graph.View.renderer(graph, {
                            container: document.getElementById('mynetwork'),
                            graphics: graphics,
                            layout: layout,
                            prerender  : true
                        });

                        renderer.run();
                    } else {
                        /*
                        nodeLookup = {};
                        edgeLookup = {};

                        response.network.nodes.forEach(function(node) {
                           nodeLookup[node.id] = node;

                           if(nodes.get(node.id) == null){
                               nodes.add(node);
                           }
                        });

                        response.network.edges.forEach(function(edge){
                           edgeLookup[edge.id] = edge;
                           if(edges.get(edge.id) == null) {
                               edges.add(edge);
                           }
                        });



                        nodes.forEach(function(node){
                            if(nodeLookup[node.id] === undefined){
                                nodes.remove(node);
                            }
                        });
                        edges.forEach(function(edge){
                            if(edgeLookup[edge.id] === undefined) {
                                edges.remove(edge);
                            }
                        });
                        */

                        /*
                        nodes.forEach(function(node){
                            nodes.remove(node);
                        });
                        edges.forEach(function(edge){
                            edges.remove(edge);
                        });
                        nodes.update(response.network.nodes);
                        edges.update(response.network.edges);
                        */

                        for(_id in userMarkerLookup){
                            if(userDataLookup[_id] != undefined){
                                console.log(_id);
                                graph.removeNode(_id);
                            }

                        }
                        response.network.nodes.forEach(function(node) {
                            graph.addNode(node.id, node);
                        });
                        response.network.edges.forEach(function(edge) {
                            graph.addLink(edge.from, edge.to);
                        });

                    }

                        leafletData.getMap("map").then(function(map) {
                            layersToRemove.forEach(function(m) {
                                map.removeLayer(m);
                            });

                        response.points.forEach(function(point){
                            var marker = L.circle([point.lat, point.lon], 3, {
                                color: 'red',
                                fillColor: '#f03',
                                fillOpacity: 0.5
                            });
                            map.addLayer(marker);
                            layersToRemove.push(marker);
                            userMarkerLookup[point.user_a] = marker;
                            userMarkerLookup[point.user_b] = marker;

                            userDataLookup[point.user_a] = point;
                            userDataLookup[point.user_b] = point;
                        });
                    });


                });
            };

/*
            var dummyMarkers = [[55.62387352200005, 12.068865842000037], [55.62319385500007, 12.068641263000075], [55.62322936100003, 12.065757671000028], [55.62427928800008, 12.066027166000026], [55.62387352200005, 12.068865842000037],[55.62374672000004, 12.069746191000036], [55.622468526000034, 12.069988736000028]];

            layersToRemove = [];
            $interval(function(){
                newNodes = [];
                newEdges = [];

                for(var i = 0 ; i < 10 ; i++){
                    newNodes.push(org_nodes[Math.floor(Math.random() * org_nodes.length)])
                }
                for(var i = 0 ; i < 10 ; i++){
                    newEdges.push(edges[Math.floor(Math.random() * edges.length)])
                }
                $scope.data = {
                    nodes: newNodes,
                    edges: newEdges
                };

                leafletData.getMap("map").then(function(map) {

                    layersToRemove.forEach(function(m) {
                        map.removeLayer(m);
                    });
                    var marker = L.circle(dummyMarkers[Math.floor(Math.random() * dummyMarkers.length)], 20, {
                        color: 'red',
                        fillColor: '#f03',
                        fillOpacity: 0.5
                    });
                    layersToRemove.push(marker);
                    map.addLayer(marker);
                });
                $scope.timestamp = 'adsad';


            }, 4000);


*/


/*
            console.log(rf_areas);
            var t = [rf_areas[0],rf_areas[1]];
            for(var v = 0 ; v < t.length ; v++){
               angular.extend($scope, {
                    geojson: t[v]
                });
            }
*/

        }]);