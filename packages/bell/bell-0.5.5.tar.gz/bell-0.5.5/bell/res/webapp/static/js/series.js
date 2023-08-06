// divs & spans
var xlineDiv;
var ylineDiv;
var linesDiv;
var metricsCountSpan;
var anomaliesCountSpan;
var rateSpan;
var timeRangeSpan;
var currentDatapointSpan;
var statusSpan;
var favicon;


function initElements() {
  xlineDiv = $('div#xline');
  ylineDiv = $('div#yline');
  linesDiv = $('div#xline, div#yline');
  metricsCountSpan = $('span#metrics-count');
  anomaliesCountSpan = $('span#anomalies-count');
  rateSpan = $('span#rate');
  timeRangeSpan = $('span#time-range');
  currentDatapointSpan = $('span#current-datapoint')
  statusSpan = $('span#status');
  favicon = $('#favicon');
}



var seriesName = 'value', anomaliesName = 'anomaly',
  aroundAnomaliesName = 'around';

var xLabelName = 'time';

var seriesColor = '#222', anomaliesColor = '#c03',
  aroundAnomaliesColor = '#c03';

var dygraphOptions = {
  labels: [xLabelName, seriesName, anomaliesName],
  colors: [seriesColor, anomaliesColor],
  axisLabelColor: '#444',
  drawXGrid: true,
  drawYGrid: true,
  drawPoints: true,
  gridLineColor: '#ddd',  // light gray
  strokeWidth: 1,
  legend: 'always',
  pointSize: 1.5,
  labelsDivStyles: {'background': 'transparent'},
  axes: {
    x: {
      valueFormatter: Dygraph.dateString_,
      ticker: Dygraph.dateTicker,
      axisLabelFormatter: Dygraph.dateAxisFormatter
    },
    y: {
      labelsKMB: true
    }
  },
  highlightCallback: function(event, x, points) {
    linesDiv.css('visibility', 'visible');
    xlineDiv.css('left', points[0].canvasx + 'px');
    xlineDiv.css('top', '0px');
    ylineDiv.css('top', points[0].canvasy + 'px');
    ylineDiv.css('left', '0px');
  },
  unhighlightCallback: function(event, x, points) {
    linesDiv.css('visibility', 'hidden');
  }
};


// special anomalies scatter
dygraphOptions[anomaliesName] = {
  strokeWidth: 0.0,  // scatter
  pointSize: 3,
  highlightCircleSize: 6
};


function updateGraphData(graph, data) {
  graph.updateOptions({file: data.data});
}


function updateGraphDataForAround(graph, data, timestamp) {
  // new array for series `around`
  $.each(data.data,  function(key, val) {
    if (val[0] == timestamp * 1000) {  // around datapoint
      val.push(val[1]);
    } else {
      val.push(null);
    }
  });

  // update graph to add series `around`
  var options = {
    file: data.data,
    labels: [xLabelName, seriesName, anomaliesName, aroundAnomaliesName],
    colors: [seriesColor, anomaliesColor, aroundAnomaliesColor]
  };
  options[aroundAnomaliesName] = {
    strokeWidth: 0.0,  // scatter
    pointSize: 8,
    highlightCircleSize: 8
  };
  graph.updateOptions(options);
}


function setPointClickCallback(graph, data) {
  var pointClickCallback = function(event, point) {
    var currentDatapointTemplate = '{0}, {1}, {2}';
    var xval = point.xval;
    var yval = point.yval;
    var isAbnormal = data.breaks.indexOf(xval) == -1 ? 0 : 1;
    var html = currentDatapointTemplate.format(xval / 1000, yval, isAbnormal);
    currentDatapointSpan.html(html);
  };
  var options = {pointClickCallback: pointClickCallback};
  graph.updateOptions(options);
}


function updateStaticsTable(data) {
  var pointsCount = data.data.length;
  var breaksCount = data.breaks.length;

  // metrics count
  var metricsCount = pointsCount;
  // anomalies count
  var anomaliesCount = breaksCount;
  // rate
  if (pointsCount > 0) {
    var rate = (breaksCount / pointsCount * 100.0)
    .toFixed(2) + '%';
  }
  // time range
  var datetimeFormatter = 'yyyy/MM/dd hh:mm';
  var timeRange = new Date(data.data[0][0]) .format(datetimeFormatter) + // the earlies datetime
    ' ~ ' +
    new Date(data.data[pointsCount - 1][0]).format(datetimeFormatter);  //  the latest datetime

  // refresh statics
  metricsCountSpan.html(metricsCount);
  anomaliesCountSpan.html(anomaliesCount);
  rateSpan.html(rate);
  timeRangeSpan.html(timeRange);
}


function updateFaviconHref(data) {
  return favicon.attr('href', data.icon);
}


function updateSeriesStatusColor(data) {
  var color = data.stat == 1 ? '#c03' : 'green';
  return statusSpan.css('background-color', color);
}


function fire(graphDiv, apiUri, timestamp){

  var graph = new Dygraph(graphDiv, [], dygraphOptions);

  var render = function() {
    $.getJSON(apiUri, function(data) {
      $('img.spinner, div.spinner-box').hide();
      if (timestamp === null) {
        updateGraphData(graph, data);  // refresh graph
      } else {
        updateGraphDataForAround(graph, data, timestamp);
      }
      setPointClickCallback(graph, data);
      updateStaticsTable(data);
      updateSeriesStatusColor(data);
      updateFaviconHref(data);
    });
  };

  if (timestamp === null) {
    setIntervalAndExecuteRightNow(render, 5000);
  } else {
    render();
  }
}
