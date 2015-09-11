$(function() {
    var randomScalingFactor = function(){ return Math.round(Math.random()*100)};

    function StatsViewModel(parameters) {
        var self = this;
        self.loginState = parameters[0];
        self.settings = parameters[1];

        self.pollingEnabled = false;
        self.pollingTimeoutId = undefined;

        window.statFull = undefined;

        self.onAfterTabChange = function(current, previous) {
            if (current != "#tab_plugin_stats") {
                return;
            }

            self.requestData();
        };

        self.fromResponse = function (response) {
            // Full Stats
            self.setFullChart(response.fullDataset);

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
            self.setFullChart(self.fullDataset);
        };

        self.setFullChart = function(ds) {
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

            var ctx = document.getElementById("canvas_fullstat").getContext("2d");
            if (window.statFull != undefined)
                window.statFull.clear();

            window.statFull = new Chart(ctx).Bar(self.statfull, {
              responsive : true,
              legendTemplate : "<ul class=\"<%=name.toLowerCase()%>-legend\"><% for (var i=0; i<datasets.length; i++){%><li><span style=\"background-color:<%=datasets[i].fillColor%>\"></span><%if(datasets[i].label){%><%=datasets[i].label%><%}%></li><%}%></ul>"
            });

            document.getElementById("legend_full").innerHTML = window.statFull.generateLegend();
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
