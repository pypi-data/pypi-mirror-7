var rotheraLat = '-67.57';
var rotheraLong = '-68.13';
var stations = {
    'r': {'lat': '-67.57', 'lon': '-68.13'},
    'kg': {'lat': '-71.33', 'lon': '-68.26'},
    'sbr': {'lat': '-74.85', 'lon': '-71.58'},
    'z': {'lat': '-75.60', 'lon': '-26.20'},
    'kep': {'lat': '-54.28', 'lon': '-36.50'},
    'bi': {'lat': '-54.00', 'lon': '-38.05'},
    'si': {'lat': '-60.72', 'lon': '-45.60'},
    'sv': {'lat': '78.92', 'lon': '11.93'},
    'sp': {'lat': '-90', 'lon': '0'},
    'cam': {'lat': '52.21', 'lon': '0.17'}
};

function getTimesForDay(latitude, longitude, start_day, end_day, callback) {
    var apiDayUrl = $SCRIPT_ROOT + '/api/sun/';
    start_day = typeof start_day !== 'undefined' ? start_day : new Date();
    end_day = typeof end_day !== 'undefined' ? end_day : new Date();

    $.getJSON( apiDayUrl, {
        //a: $('input[name="a"]').val(),
        lat: latitude,
        lon: longitude,
        start: start_day.toJSON(),
        end: end_day.toJSON(),
        output_type: 'iso'
    }, callback);
}

function updateTimes(lat, lon, date) {
    getTimesForDay(lat, lon, date, date, function( data ) {
        //var timeLeft = dusk.fromNow();
        var events = {};
        $.each( data.days[0].events, function( key, val ) {
            if(val != null) {
                $("#" + key).text(moment(val).format('HH:mm'));
            } else {
                $("#" + key).text('–');
            }
        });
    });
}

function makeTimeTable(lat, lon, start, end, output_target) {
    getTimesForDay(lat, lon, start, end, function( data ) {
        var days = [];
        $.each( data.days, function( day ) {
            var row = [];
            var row_date = $('<td/>')
                .text(moment(data.days[day].date).format('YYYY-MM-DD'));
            row.push(row_date);
            eventTypes = ['civil_dawn', 'sunrise', 'sunset', 'civil_dusk'];
            $.each( eventTypes, function( val ) {
                if (data.days[day].events[eventTypes[val]] != null) {
                    var cell = $('<td/>').text(moment(data.days[day].events[eventTypes[val]]).format('HH:mm'));
                } else {
                    var cell = $('<td/>').text('–');
                }
                row.push(cell);
            });
            var row_output = $('<tr/>').append(row);
            days.push(row_output);
        });
        var titles = ['Date', 'Dawn', 'Sunrise', 'Sunset', 'Dusk'];
        var header = $('<tr/>');
        $.each( titles, function ( i ) {
            $('<th/>').text(titles[i]).appendTo(header);
        })
        var tbl = $('<table/>').attr({ class: 'table' })
            .append(header).append(days);
        $(output_target).html(tbl);
    });
}

function makeStationTableIfReady() {
    var start = moment($( '#daterange-start' ).datepicker('getDate'));
    var end = moment($( '#daterange-end' ).datepicker('getDate'));
    var station = $( '#station' ).val();
    if (start.isValid() && end.isValid()) {
        makeTimeTable(stations[station].lat, stations[station].lon, start, end, '#timetable');
    }
}

function isValidCoord(coord) {
    // Remove any commas, and split at space
    var coords = coord.replace(',', '').split(' ');
    var tempLat = coords[0];
    var tempLon = coords[1];
    if ($.isNumeric(tempLat) && $.isNumeric(tempLon)) {
        var lat = parseFloat(tempLat);
        var lon = parseFloat(tempLon);
    } else {
        return false;
    }
    if (lat >= -90  && lat <= 90 && lon >= -180 && lon <= 180) {
        var result = {'lat': lat, 'lon': lon};
        return result;
    } else {
        return false;
    }
}

function makeCoordTableIfReady() {
    var start = moment($( '#daterange-start-ew' ).datepicker('getDate'));
    var end = moment($( '#daterange-end-ew' ).datepicker('getDate'));
    var coord = isValidCoord($( '#coord' ).val());
    console.log(coord);
    if (start.isValid() && end.isValid() && coord !== false) {
        $('#coord-parent').removeAttr('class', 'has-error');
        $('#bad-coord').remove();
        makeTimeTable(coord.lat, coord.lon, start, end, '#timetable-ew');
    } else if (coord == false) {
        $('#coord-parent').attr('class', 'has-error');
        $('<p/>', {
            'class': 'text-center muted small',
            'id': 'bad-coord',
            text: 'Latitude & longitude should be decimals, separated by a space.'
        }).appendTo('#coord-parent');
    }
}

$(document).ready(function() {
    var today = moment(0, 'HH');
    updateTimes(rotheraLat, rotheraLong, today);

    $('#datepicker-container .input-group.date').datepicker({
        format: "dd/mm/yyyy",
        orientation: "top left",
        autoclose: true,
        todayHighlight: true
    })
        .on('changeDate', function(e){
            updateTimes(stations.r.lat, stations.r.lon, moment(e.date));
        });


    $('#station').change( function(){
        makeStationTableIfReady();
    });

    $('#daterange-container .input-daterange').datepicker({
        format: "dd/mm/yyyy",
        autoclose: true,
        todayHighlight: true
    });

    // Populate with today's date as initial value
    $('#daterange-start').datepicker('update', moment(0, 'HH').toDate());

    $('#daterange-start').datepicker().on('changeDate', function(e){
        var end = moment($( '#daterange-end' ).datepicker('getDate'));
        var start = moment(e.date);
        if (end.isAfter(start) || end.isSame(start)) {
            $('#daterange-start-parent').removeAttr('class', 'has-error');
            $('#daterange-end-parent').removeAttr('class', 'has-error');
            makeStationTableIfReady();
        } else {
            $('#daterange-start-parent').attr('class', 'has-error');
            $('#timetable').html('');
        }
    });

    $('#daterange-end').datepicker().on('changeDate', function(e){
        var start = moment($( '#daterange-start' ).datepicker('getDate'));
        var end = moment(e.date);
        if (end.isAfter(start) || end.isSame(start)) {
            $('#daterange-start-parent').removeAttr('class', 'has-error');
            $('#daterange-end-parent').removeAttr('class', 'has-error');
            makeStationTableIfReady();
        } else {
            $('#daterange-end-parent').attr('class', 'has-error');
            $('#timetable').html('');
        }
    });


// Stuff for Elsewhere tab

    $('#datepicker-container-ew .input-daterange').datepicker({
        format: "dd/mm/yyyy",
        autoclose: true,
        todayHighlight: true
    });

    // Populate with today's date as initial value
    $('#daterange-start-ew').datepicker('update', moment(0, 'HH').toDate());

    $('#daterange-start-ew').datepicker().on('changeDate', function(e){
        var end = moment($( '#daterange-end-ew' ).datepicker('getDate'));
        var start = moment(e.date);
        if (end.isAfter(start) || end.isSame(start)) {
            $('#daterange-start-parent-ew').removeAttr('class', 'has-error');
            $('#daterange-end-parent-ew').removeAttr('class', 'has-error');
            makeCoordTableIfReady();
        } else {
            $('#daterange-start-parent-ew').attr('class', 'has-error');
            $('#timetable-ew').html('');
        }
    });

    $('#daterange-end-ew').datepicker().on('changeDate', function(e){
        var start = moment($( '#daterange-start-ew' ).datepicker('getDate'));
        var end = moment(e.date);
        if (end.isAfter(start) || end.isSame(start)) {
            $('#daterange-start-parent-ew').removeAttr('class', 'has-error');
            $('#daterange-end-parent-ew').removeAttr('class', 'has-error');
            makeCoordTableIfReady();
        } else {
            $('#daterange-end-parent-ew').attr('class', 'has-error');
            $('#timetable-ew').html('');
        }
    });

    $('#coord').blur( function(){
        makeCoordTableIfReady();
    });


    $('#browser-timezone').tooltip({title: 'Your browser thinks your timezone is UTC'+moment().format('ZZ')}
    );


    $('#about-link a').click(function (e) {
        $('#tabs').preventDefault();
        $('#about').tab('show');
    });
});
