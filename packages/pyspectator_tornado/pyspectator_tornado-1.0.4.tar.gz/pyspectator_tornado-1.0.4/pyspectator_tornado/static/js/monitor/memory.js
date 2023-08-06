$(function() {

    var memory_info_updater = new MemoryInfoUpdater({
        label_memory_available: '#available',
        label_memory_used_percent: '#used_percent',
        chart_container: '#memory-used_percent-chart',
        interval: 500
    });
    memory_info_updater.start_updating();

});


function MemoryInfoUpdater(params) {

    var self = this;

    this.__label_memory_available = $(params.label_memory_available);

    this.__label_memory_used_percent = $(params.label_memory_used_percent);

    this.__chart_container = $(params.chart_container);

    this.__chart_series = [{
        data: [],
        lines: {
            fill: true
        },
        shadowSize: 0
    }];

    this.__chart_data_size = 100;

    this.__chart_plot = null;

    this.actual_memory_available = null;

    this.actual_memory_used_percent = null;

    this.interval = params.interval;

    this.__updating_chart_interval = params.interval * 2;

    this.start_updating = function() {
        self.__get_chart_data(function() {
            self.__init_chart();
            self.__draw_chart();
            self.__start_updating_chart();
        });
        setTimeout(
            function() { setInterval(self.__update, self.interval); },
            self.interval
        );
    }

    this.__start_updating_chart = function() {
        self.__add_chart_value(self.actual_memory_used_percent);
        self.__draw_chart();
        setTimeout(self.__start_updating_chart, self.__updating_chart_interval);
    }

    this.__update = function() {
        $.get(
            '/api/computer_info/virtual_memory.available&virtual_memory.used_percent',
            function(data) {
                var memory_available = data['virtual_memory.available'];
                if((memory_available !== null) && (self.actual_memory_available !== memory_available)) {
                    self.actual_memory_available = memory_available;
                    self.__label_memory_available.text(memory_available);
                }
                var memory_used_percent = data['virtual_memory.used_percent'];
                if((memory_used_percent !== null) && (self.actual_memory_used_percent !== memory_used_percent)) {
                    self.actual_memory_used_percent = memory_used_percent;
                    self.__label_memory_used_percent.text(memory_used_percent);
                }
            },
            'json'
        );
    }

    this.__get_chart_data = function(callback) {
        $.get(
            '/api/computer_info/virtual_memory.used_percent_stats[]',
            function(data) {
                var chart_data = data['virtual_memory.used_percent_stats[]'];
                if(chart_data.length < self.__chart_data_size) {
                    var filled_data = [];
                    for(var i=0; i<self.__chart_data_size-chart_data.length; i++) {
                        filled_data.push([i, -1]);
                    }
                    for(var i=0, key=filled_data.length; i<chart_data.length; i++, key++) {
                        var val = chart_data[i][1];
                        filled_data.push([key, val]);
                    }
                    chart_data = filled_data;
                }
                self.__chart_series[0].data = chart_data;
                if(callback) {
                    callback();
                }
            },
            'json'
        );
    }

    this.__init_chart = function() {
        self.__chart_plot = $.plot(self.__chart_container, self.__chart_series, {
            grid: {
                borderWidth: 1,
                minBorderMargin: 20,
                labelMargin: 10,
                backgroundColor: {
                    colors: ["#fff", "#e4f4f4"]
                },
                margin: {
                    top: 8,
                    bottom: 20,
                    left: 20
                }
            },
            xaxis: {
                show: false
            },
            yaxis: {
                min: 0,
                max: 110
            },
            legend: {
                show: false
            }
        });
    }

    this.__add_chart_value = function(new_value) {
        if(new_value === null) {
            return null;
        }
        var new_data = [];
        for(var i=1; i<self.__chart_data_size; i++) {
            new_data.push([
                i - 1, self.__chart_series[0].data[i][1]
            ]);
        }
        new_data.push([self.__chart_data_size - 1, new_value]);
        self.__chart_series[0].data = new_data;
    }

    this.__draw_chart = function() {
        self.__chart_plot.setData(self.__chart_series);
        self.__chart_plot.draw();
    }

}