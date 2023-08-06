/*global window, jQuery, document, alert*/

(function ($) {
    "use strict";

    if (window.calendarwidget === undefined) {
        window.calendarwidget = {};
    }
    var App = window.calendarwidget, methods;

    App.CalendarWidget = function (trigger, options) {
        var self = this;

        $.extend(self, options);
        if (self.sources === undefined) {
            self.sources = $("#calendar-legend div");
        }

        self.trigger = $(trigger);
        self.init();
    };

    // === CalendarWidget prototype ===
    //
    // extends CalendarWidget class with some methods
    App.CalendarWidget.prototype = {

        init: function () {
            var self = this,
                settings = $.extend({
                    header: {
                        left: 'prev,next today',
                        center: 'title',
                        right: 'month,agendaWeek,agendaDay'
                    },
                    editable: false,
                    eventClick: self.eventClick,
                    eventAfterRender: function (event, element, view) {
                        var link = $(element),
                            tooltip_str = self.tooltipFormat(event);

                        link.attr('title', tooltip_str);
                        link.tooltip({
                            position: "top center",
                            offset: [-5, 0]
                        });
                    }
                }, self.settings);

            self.trigger.fullCalendar(settings);
            self.data = self.getEventsData();
            self.initEvents();
            self.bindLegend();
        },

        tooltipFormat: function (event) {
            var self = this,
                tooltip_str = '<strong>' + event.title + '</strong>';

            if (event.description)
                tooltip_str += '<p>' + event.description + '</p>';

            tooltip_str += '<p>' + self.dateFormat(event.start, event.allDay);

            if (event.end)
                tooltip_str += ' - ' + self.dateFormat(event.end, event.allDay);
            tooltip_str += '</p>';

            return tooltip_str;
        },

        dateFormat: function (date, short_format) {
            var date_str = date.getDate() + '/' +
                    (date.getMonth() + 1) + '/' +
                    date.getFullYear();

                if (! short_format)
                    date_str += ' ' + date.getHours() + ':' + date.getMinutes();

            return date_str;
        },

        getEventsData: function() {
            var self = this,
                data = {},
                name,
                el;

            self.sources.each(function () {
                el = $(this);
                name = el.data("calendar-name");
                data[name] = {
                    url: el.data("calendar-url"),
                    className: name
                };
            });
            return data;
        },

        initEvents: function () {
            var self = this,
                el;
            self.sources.each(function () {
                el = $(this).find('input');
                if (el.is(":checked") === true) {
                    self.displayEvents(el.val());
                }
            });
        },

        showAllEvents: function () {
            var self = this,
                key;

            for (key in self.sources) {
                // see: http://goo.gl/cySQ2
                if (self.sources.hasOwnProperty(key)) {
                    self.displayEvents(key);
                }
            }
        },

        displayEvents: function (name) {
            var self = this;
            self.trigger.fullCalendar(
                'addEventSource',
                self.data[name]
            );
        },

        hideEvents: function (name) {
            var self = this;
            self.trigger.fullCalendar(
                'removeEventSource',
                self.data[name]
            );
        },

        toggleEvents: function (el) {
            var self = this,
                input = $(el),
                name = input.val();
            if (input.is(':checked') === true) {
                self.hideEvents(name);
                input.attr('checked', false);
            } else {
                self.displayEvents(name);
                input.attr('checked', true);
            }
        },

        bindLegend: function () {
            var self = this,
                el,
                input;
            self.sources.each(function () {
                $(this).bind('click', function (evt) {
                    el = $(this);
                    el.toggleClass('calendar-unchecked');
                    input = el.find('input');
                    self.toggleEvents(input);
                });
            });
        },

        eventClick: function (calEvent, jsEvent, view) {
            jsEvent.preventDefault();
        }

    };


    // == jQuery plugin's methods ==
    //
    // this object contains all jQuery's plugin methods.
    methods = {
        // === init ===
        // initialize the calendar
        init : function (options) {

            return this.each(function () {
                var $this = $(this),
                    data = $this.data('calendarwidget'),
                    calendarwidget;

                // If the plugin hasn't been initialized yet
                if (!data) {
                    calendarwidget = new App.CalendarWidget(this, options);
                    $(this).data('calendarwidget', {
                        target: $this,
                        calendarwidget: calendarwidget
                    });
                }
            });

        },

        destroy : function () {
            return this.each(function () {
                var $this = $(this),
                    data = $this.data('calendarwidget');
                if (data) {
                    data.calendarwidget.remove();
                    $this.removeData('calendarwidget');
                }
            });
        }

    };

    $.fn.extend({
        calendarwidget: function (method) {

            // Method calling logic
            if (methods[method]) {
                return methods[method].apply(
                    this,
                    Array.prototype.slice.call(arguments, 1)
                );
            }

            if (typeof method === 'object' || !method) {
                return methods.init.apply(this, arguments);
            }

            $.error('Method ' +  method + ' does not exist on jQuery.calendarwidget');

        }
    });

}(jQuery));
