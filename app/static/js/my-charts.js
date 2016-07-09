
var DiscreteBarChart = (function(div_id) {

    var plotFromData = function(data) {
        nv.addGraph(function() {
            var chart = nv.models.discreteBarChart()
                .x(function(d) { return d.label })
                .y(function(d) { return d.value })
                .staggerLabels(true)
                .tooltips(false)
                .showValues(true);

            d3.select(div_id)
                .datum(data)
                .call(chart);

            nv.utils.windowResize(chart.update);
            return chart;
        });
    };

    var plotFromUrl = function(url) {
        d3.json(url, plotFromData);
    };

    return {
        plotFromData: plotFromData,
        plotFromUrl: plotFromUrl
    }
});

var StackedAreaChart = (function(div_id){

    var plotFromData = function(data) {

        nv.addGraph(function() {
            var chart = nv.models.stackedAreaChart()
                .margin({right: 40})
                .x(function(d) { return d[0] })
                .y(function(d) { return d[1] })
                .useInteractiveGuideline(true)
                .rightAlignYAxis(false)
                .showControls(true)
                .clipEdge(true);

            chart.xAxis.tickFormat(function(d) { 
                return d3.time.format('%x')(new Date(d)) 
            });

            chart.yAxis.tickFormat(d3.format(',.2f'));

            d3.select(div_id)
                .datum(data)
                .call(chart);

            nv.utils.windowResize(chart.update);

            return chart;
        });
    };

    var plotFromUrl = function(url) {
        d3.json(url, plotFromData);
    };

    return {
        plotFromData: plotFromData,
        plotFromUrl: plotFromUrl
    }
});


var PieChart = (function(div_id) {

    var plotFromData = function(data) {
        nv.addGraph(function() {
            var chart = nv.models.pieChart()
                .x(function(d) { return d.label })
                .y(function(d) { return d.value })
                .showLabels(true);

            d3.select(div_id)
                .datum(data)
                .transition().duration(350)
                .call(chart);

            return chart;
        });
    }

    var plotFromUrl = function(url) {
        d3.json(url, plotFromData);
    };

    return {
        plotFromData: plotFromData,
        plotFromUrl: plotFromUrl
    }
});


var BulletChart = (function(div_id){

    var plotFromData = function(data) {
        nv.addGraph(function() {  
            var chart = nv.models.bulletChart();

            d3.select(div_id)
              .datum(exampleData2())
              .transition().duration(1000)
              .call(chart);

            return chart;
        });
    }

    var plotFromUrl = function(url) {
        d3.json(url, plotFromData);
    }

    return {
        plotFromData: plotFromData,
        plotFromUrl: plotFromUrl
    }
});


var BubbleChart = (function(div_id){

    var plotFromData = function(data) {
        nv.addGraph(function() {
          var chart = nv.models.scatterChart()
                        .showDistX(true)    //showDist, when true, will display those little distribution lines on the axis.
                        .showDistY(true)
                        .color(d3.scale.category10().range());

          //Configure how the tooltip looks.
          chart.tooltipContent(function(key) {
              return '<h3>' + key + '</h3>';
          });

          //Axis settings
          chart.xAxis.tickFormat(d3.format('.02f'));
          chart.yAxis.tickFormat(d3.format('.02f'));

          //We want to show shapes other than circles.
          //chart.scatter.onlyCircles(false);

          d3.select(div_id)
              .datum(data)
              .call(chart);

          nv.utils.windowResize(chart.update);

          return chart;
        });
    }

    var plotFromUrl = function(url) {
        d3.json(url, plotFromData);
    }

    return {
        plotFromData: plotFromData,
        plotFromUrl: plotFromUrl
    }

})

var HorizontalBarChart = (function(div_id){

    var plotFromData = function(data){
      nv.addGraph(function() {
        var chart = nv.models.multiBarHorizontalChart()
            .x(function(d) { return d.label })
            .y(function(d) { return d.value })
            .margin({top: 30, right: 20, bottom: 50, left: 175})
            .showValues(true)           //Show bar value next to each bar.
            .tooltips(true)
            .showControls(true);        //Allow user to switch between "Grouped" and "Stacked" mode.

        chart.yAxis
            .tickFormat(d3.format(',.2f'));

        d3.select(div_id)
            .datum(data)
            .call(chart);

        nv.utils.windowResize(chart.update);

        return chart;
      });
    };

    var plotFromUrl = function(url) {
        d3.json(url, plotFromData);
    };

    return {
        plotFromData: plotFromData,
        plotFromUrl: plotFromUrl
    }
});


var LineChart = (function(div_id, x_label, y_label){

    var plotFromData = function(data){
          nv.addGraph(function() {
            var chart = nv.models.lineChart()
                          .x(function(d) { return d[0] * 1000 })
                          .y(function(d) { return d[1] }) //adjusting, 100% is 1.00, not 100 as it is in the data
                          .color(d3.scale.category10().range())
                          .useInteractiveGuideline(true)
                          .showYAxis(true)
                          .showXAxis(true)
                          ;

             chart.xAxis
                //.tickValues([1078030800000,1122782400000,1167541200000,1251691200000])
                 .axisLabel(x_label)
                .tickFormat(function(d) {
                    return d3.time.format('%m-%d %H:%M')(new Date(d))
                  });

            chart.yAxis
                .axisLabel(y_label)
                .tickFormat(d3.format(',.2f'));

            d3.select(div_id)
                .datum(data)
                .transition().duration(500)
                .call(chart);

            //TODO: Figure out a good way to do this automatically
            nv.utils.windowResize(chart.update);

            return chart;
          });
    };

    var plotFromUrl = function(url) {
        d3.json(url, plotFromData);
    };

    return {
        plotFromData: plotFromData,
        plotFromUrl: plotFromUrl
    }

});

var MultiBarChart = (function(div_id, x_label, y_label){

    var plotFromData = function(data){

        nv.addGraph(function() {
            var chart = nv.models.multiBarChart()
              .reduceXTicks(true)   //If 'false', every single x-axis tick label will be rendered.
              .rotateLabels(0)      //Angle to rotate x-axis labels.
              .showControls(true)   //Allow user to switch between 'Grouped' and 'Stacked' mode.
              .groupSpacing(0.1)    //Distance between each group of bars.
            ;

            chart.xAxis
                .axisLabel(x_label)
                .tickFormat(d3.format(',f'));

            chart.yAxis
                .axisLabel(y_label)
                .tickFormat(d3.format(',.1f'));

            d3.select(div_id)
                .datum(data)
                .call(chart);

            nv.utils.windowResize(chart.update);

            return chart;
        });
    };

    var plotFromUrl = function(url) {
        d3.json(url, plotFromData);
    };

    return {
        plotFromData: plotFromData,
        plotFromUrl: plotFromUrl
    }
});