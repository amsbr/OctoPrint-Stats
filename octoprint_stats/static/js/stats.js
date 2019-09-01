$(function () {
    var randomScalingFactor = function () {
        return Math.round(Math.random() * 100);
    };

    var fillColor = [];
    var label = [];
    var stack = [];
    var statsidebar = false;
    var stattabdata = false;
    var statsidedata = false;

    function StatsViewModel(parameters) {
        var self = this;
        self.loginState = parameters[0];
        self.settings = parameters[1];

        self.tabVisible = false;

        self.pollingEnabled = false;
        self.pollingTimeoutId = undefined;

        window.statFull = undefined;
        window.statHourly = undefined;
        window.statDaily = undefined;
        window.statPrint = undefined;
        window.statTime = undefined;
        window.statdkWh = undefined;
        window.statmkWh = undefined;

        window.sideStatPrint = undefined;
        window.sideStatDay = undefined;
        window.sideStatkWh = undefined;

        fillColor['CONNECTED'] = 'rgba(159,247,160,0.5)';
        label['CONNECTED'] = 'Connection';
        stack['CONNECTED'] = 'Conn';

        fillColor['DISCONNECTED'] = 'rgba(179,171,161,0.5)';
        label['DISCONNECTED'] = 'Disconnection';
        stack['DISCONNECTED'] = 'Conn';

        fillColor['UPLOAD'] = 'rgba(52,152,219,0.5)';
        label['UPLOAD'] = 'Upload';

        fillColor['PRINT_STARTED'] = 'rgba(0,20,166,0.5)';
        label['PRINT_STARTED'] = 'Started';

        fillColor['PRINT_DONE'] = 'rgba(49,154,37,0.5)';
        label['PRINT_DONE'] = 'Complete';
        stack['PRINT_DONE'] = 'Print';

        fillColor['PRINT_FAILED'] = 'rgba(231,76,60,0.5)';
        label['PRINT_FAILED'] = 'Failed';
        stack['PRINT_FAILED'] = 'Print';

        fillColor['PRINT_CANCELLED'] = 'rgba(217,180,95,0.5)';
        label['PRINT_CANCELLED'] = 'Cancelled';
        stack['PRINT_CANCELLED'] = 'Print';

        fillColor['PRINT_PAUSED'] = 'rgba(93,105,179,0.5)';
        label['PRINT_PAUSED'] = 'Paused';
        stack['PRINT_PAUSED'] = 'Pause';

        fillColor['PRINT_RESUMED'] = 'rgba(90,179,160,0.5)';
        label['PRINT_RESUMED'] = 'Resumed';
        stack['PRINT_RESUMED'] = 'Pause';

        fillColor['ERROR'] = 'rgba(241,196,15,0.5)';
        label['ERROR'] = 'Error';
        stack['ERROR'] = 'Print';

        fillColor['kwh'] = 'rgba(241,196,15,0.5)';
        label['kwh'] = 'kWh';
        stack['kwh'] = 'kWh';

        fillColor['ptime'] = 'rgba(52,152,219,0.5)';
        label['ptime'] = 'Hours';
        stack['ptime'] = 'Hours';

        self.onBeforeBinding = function() {
            daystats = self.settings.settings.plugins.stats.daystats();
            dayprint = self.settings.settings.plugins.stats.dayprint();
            daykwh = self.settings.settings.plugins.stats.daykwh();

            if ((daystats == false) && 
                (dayprint == false) && 
                (daykwh == false)) {
                $("#sidebar_plugin_stats").parent("div").hide();
                statsidebar = false;
            } else {
                $("#sidebar_plugin_stats").parent("div").show();
                statsidebar = true;
                if (daystats == true) {
                    $("#daystats_sidebar").show();
                } else {
                    $("#daystats_sidebar").hide();
                }

                if (dayprint == true) {
                    $("#printstats_sidebar").show();
                } else {
                    $("#printstats_sidebar").hide();
                }

                if (daykwh == true) {
                    $("#kwhstats_sidebar").show();
                } else {
                    $("#kwhstats_sidebar").hide();
                }

                self.requestSideData();
            }
        }

        self.onAfterTabChange = function (current, previous) {
            if (current != '#tab_plugin_stats') {
                self.tabVisible = false;
                return
            }
            self.tabVisible = true;

            self.requestData();
        }

        self.renderCharts = function () {}

        self.fromResponse = function (response) {
            // Full Stats
            self.setFullChart(response.fullDataset);
            // Hour Stats
            self.setHourChart(response.hourDataset);
            // Day Stats
            self.setDayChart(response.dayDataset);
            // Print Stats
            self.setPrintChart(response.printDataset);
            // Time Stats
            self.setTimeChart(response.timeDataset);
            // Day kWh
            self.setDaykWhChart(response.dkwhDataset);
            // Month kWh
            self.setMonthkWhChart(response.mkwhDataset);

            // Sidebar
            self.setTodayPrintChart(response.todayPrintDataset);
            self.setTodayStatChart(response.todayStatDataset);
            self.setTodaykWhChart(response.todaykWhDataset);

            if (self.pollingEnabled) {
                self.pollingTimeoutId = setTimeout(function () {
                    self.requestData();
                }, 30000)
            }

            if (statsidedata) {
                $("#stats_side_data").show();
                $("#stats_side_nodata").hide();
            } else {
                $("#stats_side_data").hide();
                $("#stats_side_nodata").show();
            }

            if (stattabdata) {
                $("#stats_tab_data").show();
                $("#stats_tab_nodata").hide();
            } else {
                $("#stats_tab_data").hide();
                $("#stats_tab_nodata").show();
            }

            $("#stats_loading").hide();
            $("#sidestats_loading").hide();
        }

        self.fromSideResponse = function (response) {
            // Sidebar
            self.setTodayPrintChart(response.todayPrintDataset);
            self.setTodayStatChart(response.todayStatDataset);
            self.setTodaykWhChart(response.todaykWhDataset);

            if (self.pollingEnabled) {
                self.pollingTimeoutId = setTimeout(function () {
                    self.requestData();
                }, 30000)
            }
            $("#sidestats_loading").hide();
        }

        self.requestData = function () {
            $("#stats_loading").show();
            $("#sidestats_loading").show();

            if (self.pollingTimeoutId != undefined) {
                clearTimeout(self.pollingTimeoutId);
                self.pollingTimeoutId = undefined;
            }

            $.ajax({
                url: API_BASEURL + 'plugin/stats?filter=' + document.getElementById('stats_filter').value,
                type: 'GET',
                dataType: 'json',
                success: self.fromResponse
            });
        }

        self.requestSideData = function () {
            $("#sidestats_loading").show();

            if (self.pollingTimeoutId != undefined) {
                clearTimeout(self.pollingTimeoutId);
                self.pollingTimeoutId = undefined;
            }

            $.ajax({
                url: API_BASEURL + 'plugin/stats?type=side',
                type: 'GET',
                dataType: 'json',
                success: self.fromSideResponse
            });
        }

        self.onDataUpdaterPluginMessage = function (plugin, message) {
            if (plugin != 'stats')
                return

            if ((self.fullDataset != message.fullDataset) && (message.fullDataset != undefined)) {
                self.fullDataset = message.fullDataset;
                self.setFullChart(self.fullDataset);
            }

            if ((self.hourDataset != message.hourDataset) && (message.hourDataset != undefined)) {
                self.hourDataset = message.hourDataset;
                self.setHourChart(self.hourDataset);
            }

            if ((self.dayDataset != message.dayDataset) && (message.dayDataset != undefined)) {
                self.dayDataset = message.dayDataset;
                self.setDayChart(self.dayDataset);
            }

            if ((self.printDataset != message.printDataset) && (message.printDataset != undefined)) {
                self.printDataset = message.printDataset;
                self.setPrintChart(self.printDataset);
            }

            if ((self.timeDataset != message.timeDataset) && (message.timeDataset != undefined)) {
                self.timeDataset = message.timeDataset;
                self.setTimeChart(self.timeDataset);
            }

            if ((self.dkwhDataset != message.dkwhDataset) && (message.dkwhDataset != undefined)) {
                self.dkwhDataset = message.dkwhDataset;
                self.setDaykWhChart(self.dkwhDataset);
            }

            if ((self.mkwhDataset != message.mkwhDataset) && (message.mkwhDataset != undefined)) {
                self.mkwhDataset = message.mkwhDataset;
                self.setMonthkWhChart(self.mkwhDataset);
            }

            // Sidebar
            if ((self.todayPrintDataset != message.todayPrintDataset) && (message.todayPrintDataset != undefined)) {
                self.todayPrintDataset = message.todayPrintDataset;
                self.setTodayPrintChart(self.todayPrintDataset);
            }
            if ((self.todayStatDataset != message.todayStatDataset) && (message.todayStatDataset != undefined)) {
                self.todayStatDataset = message.todayStatDataset;
                self.setTodayStatChart(self.todayStatDataset);
            }
            if ((self.todaykWhDataset != message.todaykWhDataset) && (message.todaykWhDataset != undefined)) {
                self.todaykWhDataset = message.todaykWhDataset;
                self.setTodaykWhChart(self.todaykWhDataset);
            }
        }

        self.setFullChart = function (ds) {
            if ((ds == undefined) || (ds.length == 0))
                return

            stattabdata = true;

            ds = JSON.parse(ds);
            last_data = "";

            self.statfull_data = {
                labels: [],
                datasets: []
            };

            for (var k in ds) {
                self.statfull_data.labels.push(k);
                last_data = k;
            }

            if (last_data != "") {
                for (var s in ds[last_data]) {
                    data_series = [];
                    for (var k in ds) {
                        for (var d in ds[k]) {
                            if (d == s) {
                                data_series.push(ds[k][d]);
                            }
                        }
                    }

                    dataset = {
                        backgroundColor: fillColor[s],
                        stack: stack[s],
                        data: data_series,
                        label: label[s]
                    };
                    self.statfull_data.datasets.push(dataset);
                }
            }

            self.statfull = {
                type: 'bar',
                data: self.statfull_data,
                options: {
                    responsive: true,
                    legend: {
                        position: 'top'
                    },
                    title: {
                        display: true,
                        text: 'Printer Statistics'
                    }
                }
            };

            if (self.tabVisible == true) {
                var ctx = document.getElementById('canvas_fullstat').getContext('2d');
                if (window.statFull != undefined)
                    window.statFull.clear();

                window.statFull = new Chart(ctx, self.statfull);
            }
        }

        self.setHourChart = function (ds) {
            if ((ds == undefined) || (ds.length == 0))
                return

            stattabdata = true;

            ds = JSON.parse(ds);
            last_data = "";

            self.stathour_data = {
                labels: [],
                datasets: []
            };

            for (var k in ds) {
                self.stathour_data.labels.push(k);
                last_data = k;
            }

            if (last_data != "") {
                for (var s in ds[last_data]) {
                    data_series = [];
                    for (var k in ds) {
                        for (var d in ds[k]) {
                            if (d == s) {
                                data_series.push(ds[k][d]);
                            }
                        }
                    }

                    dataset = {
                        backgroundColor: fillColor[s],
                        stack: stack[s],
                        data: data_series,
                        label: label[s]
                    };
                    self.stathour_data.datasets.push(dataset);
                }
            }

            self.stathour = {
                type: 'radar',
                data: self.stathour_data,
                options: {
                    responsive: true,
                    legend: {
                        position: 'bottom'
                    },
                    title: {
                        display: true,
                        text: 'by Hour'
                    }
                }
            };

            if (self.tabVisible == true) {
                var ctx = document.getElementById('canvas_hourlystat').getContext('2d');
                if (window.statHourly != undefined)
                    window.statHourly.clear();

                window.statHourly = new Chart(ctx, self.stathour);
            }
        }

        self.setDayChart = function (ds) {
            if ((ds == undefined) || (ds.length == 0))
                return

            stattabdata = true;

            ds = JSON.parse(ds);
            last_data = "";

            self.statday_data = {
                labels: [],
                datasets: []
            };

            for (var k in ds) {
                self.statday_data.labels.push(k);
                last_data = k;
            }

            if (last_data != "") {
                for (var s in ds[last_data]) {
                    data_series = [];
                    for (var k in ds) {
                        for (var d in ds[k]) {
                            if (d == s) {
                                data_series.push(ds[k][d]);
                            }
                        }
                    }

                    dataset = {
                        backgroundColor: fillColor[s],
                        stack: stack[s],
                        data: data_series,
                        label: label[s]
                    };
                    self.statday_data.datasets.push(dataset);
                }
            }

            self.statday = {
                type: 'radar',
                data: self.statday_data,
                options: {
                    responsive: true,
                    legend: {
                        position: 'bottom'
                    },
                    title: {
                        display: true,
                        text: 'by Day'
                    }
                }
            };

            if (self.tabVisible == true) {
                var ctx = document.getElementById('canvas_dailystat').getContext('2d');
                if (window.statDaily != undefined)
                    window.statDaily.clear();

                window.statDaily = new Chart(ctx, self.statday);
            }
        }

        self.setPrintChart = function (ds) {
            if ((ds == undefined) || (ds.length == 0))
                return

            stattabdata = true;

            ds = JSON.parse(ds);

            self.statprint_data = {
                labels: [],
                datasets: []
            };

            dataset = {
                data: [],
                backgroundColor: [],
                label: 'Prints'
            };
            for (var k in ds) {
                dataset.data.push(ds[k]);
                dataset.backgroundColor.push(fillColor[k]);
                self.statprint_data.labels.push(label[k]);
            }
            self.statprint_data.datasets.push(dataset);

            self.statprint = {
                data: self.statprint_data,
                options: {
                    responsive: true,
                    legend: {
                        position: 'bottom'
                    },
                    title: {
                        display: true,
                        text: 'Prints'
                    },
                    scale: {
                        ticks: {
                            beginAtZero: true
                        },
                        reverse: false
                    },
                    animation: {
                        animateRotate: false,
                        animateScale: true
                    }
                }
            };

            if (self.tabVisible == true) {
                var ctx = document.getElementById('canvas_printstat').getContext('2d');
                if (window.statPrint != undefined)
                    window.statPrint.clear();

                window.statPrint = new Chart.PolarArea(ctx, self.statprint);
            }
        }

        self.setTimeChart = function (ds) {
            if ((ds == undefined) || (ds.length == 0))
                return

            stattabdata = true;

            ds = JSON.parse(ds);

            self.stattime_data = {
                labels: [],
                datasets: []
            };

            dataset = {
                data: [],
                backgroundColor: [],
                label: 'Time (hr)'
            };
            for (var k in ds) {
                dataset.data.push((ds[k] / 60 / 60).toFixed(2))
                dataset.backgroundColor.push(fillColor[k])
                self.stattime_data.labels.push(label[k])
            };
            self.stattime_data.datasets.push(dataset);

            self.stattime = {
                type: 'doughnut',
                data: self.stattime_data,
                options: {
                    responsive: true,
                    legend: {
                        position: 'bottom'
                    },
                    title: {
                        display: true,
                        text: 'Time (hr)'
                    },
                    animation: {
                        animateRotate: true,
                        animateScale: true
                    }
                }
            };

            if (self.tabVisible == true) {
                var ctx = document.getElementById('canvas_timestat').getContext('2d');
                if (window.statTime != undefined)
                    window.statTime.clear();

                window.statTime = new Chart(ctx, self.stattime);
            }
        }

        self.setDaykWhChart = function (ds) {
            if ((ds == undefined) || (ds.length == 0))
                return

            stattabdata = true;

            ds = JSON.parse(ds);
            last_data = "";

            self.statdkWh_data = {
                labels: [],
                datasets: []
            };

            for (var k in ds) {
                self.statdkWh_data.labels.push(k);
                last_data = k;
            }

            if (last_data != "") {
                for (var s in ds[last_data]) {
                    data_series = [];
                    point_radius = [];
                    for (var k in ds) {
                        for (var d in ds[k]) {
                            if (d == s) {
                                if (d != 'ptime') {
                                    data_series.push(ds[k][d]);
                                    point_radius.push((ds[k][d] / 60 / 60).toFixed(2));
                                }
                            }
                        }
                    }

                    dataset = {
                        backgroundColor: fillColor[s],
                        data: data_series,
                        pointRadius: point_radius,
                        label: label[s]
                    };
                    if (s != 'ptime') {
                        self.statdkWh_data.datasets.push(dataset);
                    }
                }
            }

            self.statdkWh = {
                type: 'line',
                data: self.statdkWh_data,
                options: {
                    responsive: true,
                    legend: {
                        position: 'top'
                    },
                    title: {
                        display: true,
                        text: 'kWH per Day'
                    }
                }
            };

            if (self.tabVisible == true) {
                var ctx = document.getElementById('canvas_dkwhstat').getContext('2d');
                if (window.statdkWh != undefined)
                    window.statdkWh.clear();

                window.statdkWh = new Chart(ctx, self.statdkWh);
            }
        }

        self.setMonthkWhChart = function (ds) {
            if ((ds == undefined) || (ds.length == 0))
                return

            stattabdata = true;

            ds = JSON.parse(ds);
            last_data = "";

            self.statmkWh_data = {
                labels: [],
                datasets: []
            };

            for (var k in ds) {
                self.statmkWh_data.labels.push(k);
                last_data = k;
            }

            if (last_data != "") {
                for (var s in ds[last_data]) {
                    data_series = [];
                    point_radius = [];
                    for (var k in ds) {
                        for (var d in ds[k]) {
                            if (d == s) {
                                if (d != 'ptime') {
                                    data_series.push(ds[k][d]);
                                    point_radius.push((ds[k][d] / 60 / 60).toFixed(2));
                                }
                            }
                        }
                    }

                    dataset = {
                        backgroundColor: fillColor[s],
                        data: data_series,
                        pointRadius: point_radius,
                        label: label[s]
                    };
                    if (s != 'ptime') {
                        self.statmkWh_data.datasets.push(dataset);
                    }
                }
            }

            self.statmkWh = {
                type: 'line',
                data: self.statmkWh_data,
                options: {
                    responsive: true,
                    legend: {
                        position: 'top'
                    },
                    title: {
                        display: true,
                        text: 'kWH per Month'
                    }
                }
            };

            if (self.tabVisible == true) {
                var ctx = document.getElementById('canvas_mkwhstat').getContext('2d');
                if (window.statmkWh != undefined)
                    window.statmkWh.clear();

                window.statmkWh = new Chart(ctx, self.statmkWh);
            }
        }

        self.setTodayPrintChart = function (ds) {
            if ((ds == undefined) || (ds.length == 0))
                return

            statsidedata = true;

            ds = JSON.parse(ds)

            self.todaystatprint_data = {
                labels: [],
                datasets: []
            };

            dataset = {
                data: [],
                backgroundColor: [],
                label: 'Prints'
            };
            for (var k in ds) {
                dataset.data.push(ds[k]);
                dataset.backgroundColor.push(fillColor[k]);
                self.todaystatprint_data.labels.push(label[k]);
            }
            self.todaystatprint_data.datasets.push(dataset);

            self.todaystatprint = {
                data: self.todaystatprint_data,
                options: {
                    responsive: true,
                    legend: {
                        display: false
                    },
                    title: {
                        display: true,
                        text: 'Prints'
                    },
                    scale: {
                        ticks: {
                            beginAtZero: true
                        },
                        reverse: false
                    },
                    animation: {
                        animateRotate: false,
                        animateScale: true
                    }
                }
            };

            if (statsidebar == true) {
                document.getElementById('sidecanvas_printstat').remove();
                var canvSidePrint = document.createElement('canvas');
                canvSidePrint.id = 'sidecanvas_printstat';
                canvSidePrint.class = 'chart';
                canvSidePrint.width = '300';
                canvSidePrint.height = '300';
                document.getElementById('printstats_sidebar').appendChild(canvSidePrint);

                var ctx = document.getElementById('sidecanvas_printstat').getContext('2d');
                if (window.sideStatPrint != undefined)
                    window.sideStatPrint.clear();
        
                window.sideStatPrint = new Chart.PolarArea(ctx, self.todaystatprint);
            }
        }

        self.setTodayStatChart = function (ds) {
            if ((ds == undefined) || (ds.length == 0))
                return

            statsidedata = true;

            ds = JSON.parse(ds);

            self.todaystat_data = {
                labels: [],
                datasets: []
            };

            dataset = {
                data: [],
                backgroundColor: [],
                label: 'Day'
            };
            for (var k in ds) {
                dataset.data.push(ds[k]);
                dataset.backgroundColor.push(fillColor[k]);
                self.todaystat_data.labels.push(label[k]);
            }
            self.todaystat_data.datasets.push(dataset);

            self.todaystat = {
                type: 'pie',
                data: self.todaystat_data,
                options: {
                    responsive: true,
                    legend: {
                        display: false
                    },
                    title: {
                        display: true,
                        text: 'Today'
                    },
                }
            };

            if (statsidebar == true) {
                document.getElementById('sidecanvas_daystat').remove();
                var canvSideDay = document.createElement('canvas');
                canvSideDay.id = 'sidecanvas_daystat';
                canvSideDay.class = 'chart';
                canvSideDay.width = '300';
                canvSideDay.height = '300';
                document.getElementById('daystats_sidebar').appendChild(canvSideDay);

                var ctx = document.getElementById('sidecanvas_daystat').getContext('2d');
                if (window.sideStatDay != undefined)
                    window.sideStatDay.clear();
        
                window.sideStatDay = new Chart(ctx, self.todaystat);
            }
        }

        self.setTodaykWhChart = function (ds) {
            if ((ds == undefined) || (ds.length == 0))
                return

            statsidedata = true;

            ds = JSON.parse(ds);
            last_data = "";

            self.todaykwhstat_data = {
                labels: [],
                datasets: []
            };

            self.todaykwhstat_data = {
                labels: [],
                datasets: []
            };

            for (var k in ds) {
                self.todaykwhstat_data.labels.push(k);
                last_data = k;
            }

            if (last_data != "") {
                for (var s in ds[last_data]) {
                    data_series_ptime = [];
                    data_series_kwh = [];
                    point_radius = [];
                    for (var k in ds) {
                        for (var d in ds[k]) {
                            if (d == s) {
                                if (d == 'ptime') {
                                    data_series_ptime.push((ds[k][d] / 60 / 60).toFixed(2));
                                }
                                else {
                                    data_series_kwh.push(ds[k][d]);
                                    point_radius.push((ds[k][d] / 60 / 60).toFixed(2));
                                }
                            }
                        }
                    }

                    if (s == 'ptime') {
                        dataset = {
                            type: 'bar',
                            backgroundColor: fillColor[s],
                            data: data_series_ptime,
                            label: label[s]
                        };
                        self.todaykwhstat_data.datasets.push(dataset);
                    } else {
                        dataset = {
                            type: 'line',
                            fill: false,
                            backgroundColor: fillColor[s],
                            data: data_series_kwh,
                            label: label[s]
                        };
                        self.todaykwhstat_data.datasets.push(dataset);
                    }
                }
            }

            self.todaykwhstat = {
                type: 'bar',
                data: self.todaykwhstat_data,
                options: {
                    responsive: true,
                    legend: {
                        display: false
                    },
                    title: {
                        display: true,
                        text: 'kWH per Hour'
                    }
                }
            };

            if (statsidebar == true) {
                document.getElementById('sidecanvas_kwhstat').remove();
                var canvSidekWh = document.createElement('canvas');
                canvSidekWh.id = 'sidecanvas_kwhstat';
                canvSidekWh.class = 'chart';
                canvSidekWh.width = '300';
                canvSidekWh.height = '300';
                document.getElementById('kwhstats_sidebar').appendChild(canvSidekWh);

                var ctx = document.getElementById('sidecanvas_kwhstat').getContext('2d');
                if (window.sideStatkWh != undefined)
                    window.sideStatkWh.clear();
        
                window.sideStatkWh = new Chart(ctx, self.todaykwhstat);
            }
        }

        self.statsSendFilter = function () {
            window.statFull.clear();
            document.getElementById('canvas_fullstat').remove();
            var canvFull = document.createElement('canvas');
            canvFull.id = 'canvas_fullstat';
            canvFull.class = 'chart';
            canvFull.width = '600';
            canvFull.height = '300';
            document.getElementById('td_fullstat').appendChild(canvFull);

            window.statHourly.clear();
            document.getElementById('canvas_hourlystat').remove();
            var canvHourly = document.createElement('canvas');
            canvHourly.id = 'canvas_hourlystat';
            canvHourly.class = 'chart';
            canvHourly.width = '300';
            canvHourly.height = '300';
            document.getElementById('td_hourlystat').appendChild(canvHourly);

            window.statDaily.clear();
            document.getElementById('canvas_dailystat').remove();
            var canvDaily = document.createElement('canvas');
            canvDaily.id = 'canvas_dailystat';
            canvDaily.class = 'chart';
            canvDaily.width = '300';
            canvDaily.height = '300';
            document.getElementById('td_dailystat').appendChild(canvDaily);

            window.statPrint.clear();
            document.getElementById('canvas_printstat').remove();
            var canvPrint = document.createElement('canvas');
            canvPrint.id = 'canvas_printstat';
            canvPrint.class = 'chart';
            canvPrint.width = '300';
            canvPrint.height = '300';
            document.getElementById('td_printstat').appendChild(canvPrint);

            window.statTime.clear();
            document.getElementById('canvas_timestat').remove();
            var canvTime = document.createElement('canvas');
            canvTime.id = 'canvas_timestat';
            canvTime.class = 'chart';
            canvTime.width = '300';
            canvTime.height = '300';
            document.getElementById('td_timestat').appendChild(canvTime);

            window.statdkWh.clear();
            document.getElementById('canvas_dkwhstat').remove();
            var canvdkWh = document.createElement('canvas');
            canvdkWh.id = 'canvas_dkwhstat';
            canvdkWh.class = 'chart';
            canvdkWh.width = '600';
            canvdkWh.height = '300';
            document.getElementById('td_dkwhstat').appendChild(canvdkWh);

            window.statmkWh.clear();
            document.getElementById('canvas_mkwhstat').remove();
            var canvmkWh = document.createElement('canvas');
            canvmkWh.id = 'canvas_mkwhstat';
            canvmkWh.class = 'chart';
            canvmkWh.width = '600';
            canvmkWh.height = '300';
            document.getElementById('td_dkwhstat').appendChild(canvmkWh);
    
            self.requestData();
        }
    }

    $("#resetStats").click(function () {
        showConfirmationDialog({
            message: 'Do you really want to reset stats history?',
            onproceed: function() {
                $.ajax({
                    url: API_BASEURL + 'plugin/stats?type=reset',
                    type: 'GET',
                    dataType: 'json',
                    success: function() {
                        new PNotify({
                            title: 'Stats',
                            text: 'Database of stats is now empty.',
                            type: 'success',
                            hide: true
                        });        
                    }
                });
            },
        });
    });

    OCTOPRINT_VIEWMODELS.push([
        StatsViewModel,
        ['loginStateViewModel', 'settingsViewModel'],
        [document.getElementById('tab_plugin_stats')],
        [document.getElementById('sidebar_plugin_stats')],
        [document.getElementById('settings_plugin_stats_form')]
    ]);
})