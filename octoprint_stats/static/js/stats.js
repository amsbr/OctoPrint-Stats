$(function() {
    var randomScalingFactor = function(){ return Math.round(Math.random()*100)};

    function StatsViewModel(parameters) {
        var self = this;

        //self.testV = ko.observable();
        //self.testV('teste Model');

        //self.loginState = parameters[0];
        //self.settings = parameters[1];

        // this will hold the URL currently displayed by the iframe
        //self.currentUrl = ko.observable();

        // this will hold the URL entered in the text field
        //self.newUrl = ko.observable();

        // this will be called when the user clicks the "Go" button and set the iframe's URL to the entered URL
        self.goToUrl = function() {
            //self.currentUrl(self.newUrl());
        };

        // This will get called before the HelloWorldViewModel gets bound to the DOM, but after its depedencies have
        // already been initialized. It is especially guaranteed that this method gets called _after_ the settings
        // have been retrieved from the OctoPrint backend and thus the SettingsViewModel been properly populated.
        self.onAfterTabChange = function() {
            // Full Stats
            //var ctx = document.getElementById("canvas_fullstat").getContext("2d");
          	//window.statFull = new Chart(ctx).Bar(self.fullDataset, {
          	//    responsive : true
          	//});

        }

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
                  data : ds.connected
                },// Uploads
                {
                  fillColor : "rgba(52,152,219,0.5)",
                  strokeColor : "rgba(52,152,219,0.8)",
                  highlightFill: "rgba(52,152,219,0.75)",
                  highlightStroke: "rgba(52,152,219,1)",
                  data : ds.upload
                },// Prints
                {
                  fillColor : "rgba(41,128,185,0.5)",
                  strokeColor : "rgba(41,128,185,0.8)",
                  highlightFill: "rgba(41,128,185,0.75)",
                  highlightStroke: "rgba(41,128,185,1)",
                  data : ds.print_started
                },// Dones
                {
                  fillColor : "rgba(26,188,156,0.5)",
                  strokeColor : "rgba(26,188,156,0.8)",
                  highlightFill: "rgba(26,188,156,0.75)",
                  highlightStroke: "rgba(26,188,156,1)",
                  data : ds.print_done
                },// Failed
                {
                  fillColor : "rgba(231,76,60,0.5)",
                  strokeColor : "rgba(231,76,60,0.8)",
                  highlightFill: "rgba(231,76,60,0.75)",
                  highlightStroke: "rgba(231,76,60,1)",
                  data : ds.print_failed
                },// Cancelled
                {
                  fillColor : "rgba(189,195,199,0.5)",
                  strokeColor : "rgba(189,195,199,0.8)",
                  highlightFill: "rgba(189,195,199,0.75)",
                  highlightStroke: "rgba(189,195,199,1)",
                  data : ds.print_cancelled
                },// Error
                {
                  fillColor : "rgba(241,196,15,0.5)",
                  strokeColor : "rgba(241,196,15,0.8)",
                  highlightFill: "rgba(241,196,15,0.75)",
                  highlightStroke: "rgba(241,196,15,1)",
                  data : ds.print_cancelled
                }
              ]
            }

            printObject(self.statfull);
            printObject(ds);
            var ctx = document.getElementById("canvas_fullstat").getContext("2d");
            window.statFull = new Chart(ctx).Bar(self.statfull, {
              responsive : true
            });

        }

    }

    // This is how our plugin registers itself with the application, by adding some configuration information to
    // the global variable ADDITIONAL_VIEWMODELS
    ADDITIONAL_VIEWMODELS.push([
        // This is the constructor to call for instantiating the plugin
        StatsViewModel,

        // This is a list of dependencies to inject into the plugin, the order which you request here is the order
        // in which the dependencies will be injected into your view model upon instantiation via the parameters
        // argument
        ["loginStateViewModel", "settingsViewModel"],

        // Finally, this is the list of all elements we want this view model to be bound to.
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
