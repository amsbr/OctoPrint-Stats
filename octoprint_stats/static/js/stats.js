$(function() {
    var randomScalingFactor = function(){ return Math.round(Math.random()*100)};

    function StatsViewModel(parameters) {
        var self = this;
        self.loginState = parameters[0];
        self.settings = parameters[1];

        self.tabVisible = false;

        self.pollingEnabled = false;
        self.pollingTimeoutId = undefined;

        window.statFull = undefined;
        window.statHourly = undefined;
        window.statPrint = undefined;
        window.statdkWh = undefined;
        window.statmkWh = undefined;

        self.onAfterTabChange = function(current, previous) {
            if (current != "#tab_plugin_stats") {
                self.tabVisible = false;
                return;
            }
            self.tabVisible = true;

            self.requestData();
        };

        self.renderCharts = function () {

        }

        self.fromResponse = function (response) {
            // Full Stats
            self.setFullChart(response.fullDataset);
            // Hour Stats
            self.setHourChart(response.hourDataset);
            // Day Stats
            self.setPrintChart(response.printDataset);
            // Day kWh
            self.setDaykWhChart(response.dkwhDataset);
            // Month kWh
            self.setMonthkWhChart(response.mkwhDataset);

            if (self.pollingEnabled) {
                self.pollingTimeoutId = setTimeout(function() {
                    self.requestData();
                }, 30000)
            }
        };

        self.requestData = function () {
            if (self.pollingTimeoutId != undefined) {
                clearTimeout(self.pollingTimeoutId);
                self.pollingTimeoutId = undefined;
            }

            $.ajax({
                url: API_BASEURL + "plugin/stats",
                type: "GET",
                dataType: "json",
                success: self.fromResponse
            });
        };

        self.onDataUpdaterPluginMessage = function(plugin, message) {
            if (plugin != 'stats')
                return;

            self.fullDataset = message.fullDataset;
            self.hourDataset = message.hourDataset;
            self.printDataset = message.printDataset;
            self.dkwhDataset = message.dkwhDataset;
            self.mkwhDataset = message.mkwhDataset;
            self.setFullChart(self.fullDataset);
            self.setHourChart(self.hourDataset);
            self.setPrintChart(self.printDataset);
            self.setDaykWhChart(self.dkwhDataset);
            self.setMonthkWhChart(self.mkwhDataset);
        };

        self.setFullChart = function(ds) {
            if (ds == undefined)
                return;

            self.statfull = {
              labels : ds.month,
              datasets : [//Connections
                {
                  fillColor : "rgba(46,204,113,0.5)",
                  strokeColor : "rgba(46,204,113,0.8)",
                  highlightFill: "rgba(46,204,113,0.75)",
                  highlightStroke: "rgba(46,204,113,1)",
                  data : ds.connected,
                  label : "Connection"
                },// Uploads
                {
                  fillColor : "rgba(52,152,219,0.5)",
                  strokeColor : "rgba(52,152,219,0.8)",
                  highlightFill: "rgba(52,152,219,0.75)",
                  highlightStroke: "rgba(52,152,219,1)",
                  data : ds.upload,
                  label : "Upload"
                },// Prints
                {
                  fillColor : "rgba(41,128,185,0.5)",
                  strokeColor : "rgba(41,128,185,0.8)",
                  highlightFill: "rgba(41,128,185,0.75)",
                  highlightStroke: "rgba(41,128,185,1)",
                  data : ds.print_started,
                  label : "Print"
                },// Dones
                {
                  fillColor : "rgba(26,188,156,0.5)",
                  strokeColor : "rgba(26,188,156,0.8)",
                  highlightFill: "rgba(26,188,156,0.75)",
                  highlightStroke: "rgba(26,188,156,1)",
                  data : ds.print_done,
                  label : "Print complete"
                },// Failed
                {
                  fillColor : "rgba(231,76,60,0.5)",
                  strokeColor : "rgba(231,76,60,0.8)",
                  highlightFill: "rgba(231,76,60,0.75)",
                  highlightStroke: "rgba(231,76,60,1)",
                  data : ds.print_failed,
                  label : "Print failed"
                },// Cancelled
                {
                  fillColor : "rgba(189,195,199,0.5)",
                  strokeColor : "rgba(189,195,199,0.8)",
                  highlightFill: "rgba(189,195,199,0.75)",
                  highlightStroke: "rgba(189,195,199,1)",
                  data : ds.print_cancelled,
                  label : "Print cancelled"
                },// Error
                {
                  fillColor : "rgba(241,196,15,0.5)",
                  strokeColor : "rgba(241,196,15,0.8)",
                  highlightFill: "rgba(241,196,15,0.75)",
                  highlightStroke: "rgba(241,196,15,1)",
                  data : ds.error,
                  label : "Error"
                }
              ]
            }

            if (self.tabVisible == true) {
                var ctx = document.getElementById("canvas_fullstat").getContext("2d");
                if (window.statFull != undefined)
                    window.statFull.clear();

                window.statFull = new Chart(ctx).Bar(self.statfull, {
                  responsive : true,
                  legendTemplate : "<ul class=\"<%=name.toLowerCase()%>-legend\"><% for (var i=0; i<datasets.length; i++){%><li><span style=\"background-color:<%=datasets[i].fillColor%>\"></span><%if(datasets[i].label){%><%=datasets[i].label%><%}%></li><%}%></ul>"
                });

                document.getElementById("legend_full").innerHTML = window.statFull.generateLegend();
            }
        };

        self.setHourChart = function(ds) {
            if (ds == undefined)
                return;

            self.stathour = {
              labels : ds.hour,
              datasets : [//Connections
                {
                  fillColor : "rgba(46,204,113,0.5)",
                  strokeColor : "rgba(46,204,113,0.8)",
                  pointColor: "rgba(46,204,113,1)",
                  pointStrokeColor: "#fff",
                  pointHighlightFill: "#fff",
                  pointHighlightStroke: "rgba(46,204,113,1)",
                  data : ds.connected,
                  label : "Connection"
                },// Uploads
                {
                  fillColor : "rgba(52,152,219,0.5)",
                  strokeColor : "rgba(52,152,219,0.8)",
                  pointColor: "rgba(52,152,219,1)",
                  pointStrokeColor: "#fff",
                  pointHighlightFill: "#fff",
                  pointHighlightStroke: "rgba(52,152,219,1)",
                  data : ds.upload,
                  label : "Upload"
                },// Prints
                {
                  fillColor : "rgba(41,128,185,0.5)",
                  strokeColor : "rgba(41,128,185,0.8)",
                  pointColor: "rgba(41,128,185,1)",
                  pointStrokeColor: "#fff",
                  pointHighlightFill: "#fff",
                  pointHighlightStroke: "rgba(41,128,185,1)",
                  data : ds.print_started,
                  label : "Print"
                },// Dones
                {
                  fillColor : "rgba(26,188,156,0.5)",
                  strokeColor : "rgba(26,188,156,0.8)",
                  pointColor: "rgba(26,188,156,1)",
                  pointStrokeColor: "#fff",
                  pointHighlightFill: "#fff",
                  pointHighlightStroke: "rgba(26,188,156,1)",
                  data : ds.print_done,
                  label : "Print complete"
                },// Failed
                {
                  fillColor : "rgba(231,76,60,0.5)",
                  strokeColor : "rgba(231,76,60,0.8)",
                  pointColor: "rgba(231,76,60,1)",
                  pointStrokeColor: "#fff",
                  pointHighlightFill: "#fff",
                  pointHighlightStroke: "rgba(231,76,60,1)",
                  data : ds.print_failed,
                  label : "Print failed"
                },// Cancelled
                {
                  fillColor : "rgba(189,195,199,0.5)",
                  strokeColor : "rgba(189,195,199,0.8)",
                  pointColor: "rgba(189,195,199,1)",
                  pointStrokeColor: "#fff",
                  pointHighlightFill: "#fff",
                  pointHighlightStroke: "rgba(189,195,199,1)",
                  data : ds.print_cancelled,
                  label : "Print cancelled"
                },// Error
                {
                  fillColor : "rgba(241,196,15,0.5)",
                  strokeColor : "rgba(241,196,15,0.8)",
                  pointColor: "rgba(241,196,15,1)",
                  pointStrokeColor: "#fff",
                  pointHighlightFill: "#fff",
                  pointHighlightStroke: "rgba(241,196,15,1)",
                  data : ds.error,
                  label : "Error"
                }
              ]
            }

            if (self.tabVisible == true) {
                var ctx = document.getElementById("canvas_hourlystat").getContext("2d");
                if (window.statHourly != undefined)
                    window.statHourly.clear();

                window.statHourly = new Chart(ctx).Radar(self.stathour, {
                  responsive : true,
                  legendTemplate : "<ul class=\"<%=name.toLowerCase()%>-legend\"><% for (var i=0; i<datasets.length; i++){%><li><span style=\"background-color:<%=datasets[i].fillColor%>\"></span><%if(datasets[i].label){%><%=datasets[i].label%><%}%></li><%}%></ul>"
                });

                document.getElementById("legend_hour").innerHTML = window.statHourly.generateLegend();
            }
        };

        self.setPrintChart = function(ds) {
            if (ds == undefined)
                return;

            self.statprint = [
                {// Uploads
                  color : "rgba(52,152,219,0.5)",
                  highlight: "rgba(52,152,219,1)",
                  value : ds.upload,
                  label : "Upload"
                },// Prints
                {
                  color : "rgba(41,128,185,0.5)",
                  highlight: "rgba(41,128,185,1)",
                  value : ds.print_started,
                  label : "Print"
                },// Dones
                {
                  color : "rgba(26,188,156,0.5)",
                  highlight: "rgba(26,188,156,1)",
                  value : ds.print_done,
                  label : "Print complete"
                },// Failed
                {
                  color : "rgba(231,76,60,0.5)",
                  highlight: "rgba(231,76,60,1)",
                  value : ds.print_failed,
                  label : "Print failed"
                },// Cancelled
                {
                  color : "rgba(189,195,199,0.5)",
                  highlight: "rgba(189,195,199,1)",
                  value : ds.print_cancelled,
                  label : "Print cancelled"
                },
            ];

            if (self.tabVisible == true) {
                var ctx = document.getElementById("canvas_printstat").getContext("2d");
                if (window.statPrint != undefined)
                    window.statPrint.clear();

                window.statPrint = new Chart(ctx).PolarArea(self.statprint, {
                  segmentStrokeColor: "#000000",
                  responsive : true,
                  legendTemplate : "<ul class=\"<%=name.toLowerCase()%>-legend\"><% for (var i=0; i<datasets.length; i++){%><li><span style=\"background-color:<%=datasets[i].fillColor%>\"></span><%if(datasets[i].label){%><%=datasets[i].label%><%}%></li><%}%></ul>"
                });

                //document.getElementById("legend_print").innerHTML = window.statPrint.generateLegend();
            }
        };

        self.setDaykWhChart = function(ds) {
            if (ds == undefined)
                return;

            self.statdkwh = {
              labels : ds.day,
              datasets : [
                {// kWh
                  fillColor : "rgba(241,196,15,0.5)",
                  strokeColor : "rgba(241,196,15,0.8)",
                  pointColor: "rgba(241,196,15,1)",
                  pointStrokeColor: "#fff",
                  pointHighlightFill: "#fff",
                  pointHighlightStroke: "rgba(241,196,15,1)",
                  data : ds.kwh,
                  label : "kWh"
                },// Print Time
                {
                  fillColor : "rgba(52,152,219,0.5)",
                  strokeColor : "rgba(52,152,219,0.8)",
                  pointColor: "rgba(52,152,219,1)",
                  pointStrokeColor: "#fff",
                  pointHighlightFill: "#fff",
                  pointHighlightStroke: "rgba(52,152,219,1)",
                  data : ds.phour,
                  label : "Hours"
                },
              ]
            };

            if (self.tabVisible == true) {
                var ctx = document.getElementById("canvas_dkwhstat").getContext("2d");
                if (window.statdkWh != undefined)
                    window.statdkWh.clear();

                window.statdkWh = new Chart(ctx).Line(self.statdkwh, {
                  responsive : true,
                  legendTemplate : "<ul class=\"<%=name.toLowerCase()%>-legend\"><% for (var i=0; i<datasets.length; i++){%><li><span style=\"background-color:<%=datasets[i].fillColor%>\"></span><%if(datasets[i].label){%><%=datasets[i].label%><%}%></li><%}%></ul>"
                });

                document.getElementById("legend_dkwh").innerHTML = window.statdkWh.generateLegend();
            }
        };

        self.setMonthkWhChart = function(ds) {
            if (ds == undefined)
                return;

            self.statmkwh = {
              labels : ds.month,
              datasets : [
                {// kWh
                  fillColor : "rgba(241,196,15,0.5)",
                  strokeColor : "rgba(241,196,15,0.8)",
                  pointColor: "rgba(241,196,15,1)",
                  pointStrokeColor: "#fff",
                  pointHighlightFill: "#fff",
                  pointHighlightStroke: "rgba(241,196,15,1)",
                  data : ds.kwh,
                  label : "kWh"
                },// Print Time
                {
                  fillColor : "rgba(52,152,219,0.5)",
                  strokeColor : "rgba(52,152,219,0.8)",
                  pointColor: "rgba(52,152,219,1)",
                  pointStrokeColor: "#fff",
                  pointHighlightFill: "#fff",
                  pointHighlightStroke: "rgba(52,152,219,1)",
                  data : ds.phour,
                  label : "Hours"
                },
              ]
            };

            if (self.tabVisible == true) {
                var ctx = document.getElementById("canvas_mkwhstat").getContext("2d");
                if (window.statmkWh != undefined)
                    window.statmkWh.clear();

                window.statmkWh = new Chart(ctx).Line(self.statmkwh, {
                  responsive : true,
                  legendTemplate : "<ul class=\"<%=name.toLowerCase()%>-legend\"><% for (var i=0; i<datasets.length; i++){%><li><span style=\"background-color:<%=datasets[i].fillColor%>\"></span><%if(datasets[i].label){%><%=datasets[i].label%><%}%></li><%}%></ul>"
                });

                document.getElementById("legend_mkwh").innerHTML = window.statmkWh.generateLegend();
            }
        };

    }


    ADDITIONAL_VIEWMODELS.push([
        StatsViewModel,
        ["loginStateViewModel", "settingsViewModel"],
        [document.getElementById("tab_plugin_stats")]
    ]);
});

function printObject(o) {
  var out = '';
  for (var p in o) {
    out += p + ': ' + o[p] + '\n';
  }
  alert(out);
}
