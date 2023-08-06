window.jarn.i18n.loadCatalog("bika");
window.jarn.i18n.loadCatalog("plone");

(function( $ ) {
"use strict";

window.bika = window.bika || {
    lims: {}
};


window.bika.lims.portalMessage = function (message) {
    window.jarn.i18n.loadCatalog("bika");
    var _ = window.jarn.i18n.MessageFactory("bika");
    var str = "<dl class='portalMessage error'>"+
        "<dt>"+_("Error")+"</dt>"+
        "<dd><ul>" + message +
        "</ul></dd></dl>";
    $(".portalMessage").remove();
    $(str).appendTo("#viewlet-above-content");
};

window.bika.lims.log = function(e) {
	var message = "(" + window.location.url + "): " + e;
    $.ajax({
        type: "POST",
        url: "js_log",
        data: {"message":message,
                "_authenticator": $("input[name='_authenticator']").val()}
    });
};

window.bika.lims.jsonapi_cache = {};
window.bika.lims.jsonapi_read = function(request_data, handler) {
    window.bika.lims.jsonapi_cache = window.bika.lims.jsonapi_cache || {};
	// if no page_size is specified, we need to explicitly add one here: 0=all.
	var page_size = request_data.page_size;
	if (page_size == undefined) {
		request_data.page_size = 0
	}
    var jsonapi_cacheKey = $.param(request_data);
    var jsonapi_read_handler = handler;
    if (window.bika.lims.jsonapi_cache[jsonapi_cacheKey] === undefined){
        $.ajax({
            type: "POST",
            dataType: "json",
            url: window.portal_url + "/@@API/read",
            data: request_data,
            success: function(data) {
                window.bika.lims.jsonapi_cache[jsonapi_cacheKey] = data;
                jsonapi_read_handler(data);
            }
        });
    } else {
        jsonapi_read_handler(window.bika.lims.jsonapi_cache[jsonapi_cacheKey]);
    }
};

$(document).ready(function(){

    window.jarn.i18n.loadCatalog("bika");
    var _ = window.jarn.i18n.MessageFactory("bika");

    var curDate = new Date();
    var y = curDate.getFullYear();
    var limitString = "1900:" + y;
    var dateFormat = _("date_format_short_datepicker");
    if (dateFormat == 'date_format_short_datepicker'){
        dateFormat = 'yy-mm-dd';
    }

    $("input.datepicker").live("click", function() {
        $(this).datepicker({
            showOn:"focus",
            showAnim:"",
            changeMonth:true,
            changeYear:true,
            dateFormat: dateFormat,
            yearRange: limitString
        })
        .click(function(){$(this).attr("value", "");})
        .focus();

    });

    $("input.datepicker_nofuture").live("click", function() {
        $(this).datepicker({
            showOn:"focus",
            showAnim:"",
            changeMonth:true,
            changeYear:true,
            maxDate: curDate,
            dateFormat: dateFormat,
            yearRange: limitString
        })
        .click(function(){$(this).attr("value", "");})
        .focus();
    });

    $("input.datepicker_2months").live("click", function() {
        $(this).datepicker({
            showOn:"focus",
            showAnim:"",
            changeMonth:true,
            changeYear:true,
            maxDate: "+0d",
            numberOfMonths: 2,
            dateFormat: dateFormat,
            yearRange: limitString
        })
        .click(function(){$(this).attr("value", "");})
        .focus();
    });

    // Analysis Service popup trigger
    $('.service_title span:not(.before)').live("click", function(){
        var dialog = $("<div></div>");
        dialog
            .load(window.portal_url + "/analysisservice_popup",
                {'service_title':$(this).closest('td').find("span[class^='state']").html(),
                "analysis_uid":$(this).parents("tr").attr("uid"),
                "_authenticator": $("input[name='_authenticator']").val()}
            )
            .dialog({
                width:450,
                height:450,
                closeText: _("Close"),
                resizable:true,
                title: $(this).text()
            });
    });

    $(".numeric").live("keypress", function(event) {
        var allowedKeys = [
			8,   // backspace
			9,   // tab
			13,  // enter
			35,  // end
			36,  // home
			37,  // left arrow
			39,  // right arrow
			46,  // delete - We don't support the del key in Opera because del == . == 46.
			60,  // <
			62,  // >
			45,  // -
			69,  // E
			101, // e,
			61   // =
		];
        var isAllowedKey = allowedKeys.join(",").match(new RegExp(event.which)); // IE doesn't support indexOf
        // Some browsers just don't raise events for control keys. Easy. e.g. Safari backspace.
        if (!event.which || // Control keys in most browsers. e.g. Firefox tab is 0
            (48 <= event.which && event.which <= 57) || // Always 0 through 9
            isAllowedKey) { // Opera assigns values for control keys.
            return;
        } else {
            event.preventDefault();
        }
    });

    // Archetypes :int and IntegerWidget inputs get filtered
    $("input[name*='\\:int'], .ArchetypesIntegerWidget input").keyup(function(e) {
        if (/\D/g.test(this.value)) {
            this.value = this.value.replace(/\D/g, "");
        }
    });

    // Archetypes :float and DecimalWidget inputs get filtered
    $("input[name*='\\:float'], .ArchetypesDecimalWidget input").keyup(function(e) {
        if (/[^.\d]/g.test(this.value)) {
            this.value = this.value.replace(/[^.\d]/g, "");
        }
    });

    // Check instrument validity and add an alert if needed
    $.ajax({
        url: window.portal_url + "/get_instruments_alerts",
        type: 'POST',
        data: {'_authenticator': $('input[name="_authenticator"]').val() },
        dataType: 'json'
    }).done(function(data) {
        if (data['out-of-date'].length > 0 || data['qc-fail'].length > 0) {
            $('#portal-alert').remove();
            var html = "<div id='portal-alert' style='display:none'>";
            var outofdate = data['out-of-date'];
            if (outofdate.length > 0) {
                // Out of date alert
                html += "<p class='title'>"+outofdate.length+_(" instruments are out-of-date")+":</p>";
                html += "<p>";
                $.each(outofdate, function(index, value){
                    var hrefinstr = value['url']+"/certifications";
                    var titleinstr = value['title'];
                    var anchor = "<a href='"+hrefinstr+"'>"+titleinstr+"</a>";
                    if (index == 0) {
                        html += anchor;
                    } else {
                        html += ", "+anchor;
                    }
                })
                html += "</p>";
            }
            var qcfail = data['qc-fail'];
            if (qcfail.length > 0) {
                // QC Fail alert
                html += "<p class='title'>"+qcfail.length+_(" instruments with QC Internal Calibration Tests failed")+":</p>";
                html += "<p>";
                $.each(qcfail, function(index, value){
                    var hrefinstr = value['url']+"/referenceanalyses";
                    var titleinstr = value['title'];
                    var anchor = "<a href='"+hrefinstr+"'>"+titleinstr+"</a>";
                    if (index == 0) {
                        html += anchor;
                    } else {
                        html += ", "+anchor;
                    }
                })
                html += "</p>";
            }
            html += "</div>"
            $('#portal-header').append(html);
            $('#portal-alert').fadeIn(2000);
        }
    });


	/* Replace kss-bbb spinner with a quieter one */
	var timer, spinner, counter = 0;
	$(document).unbind("ajaxStart");
	$(document).unbind("ajaxStop");
	$('#ajax-spinner').remove();
	spinner = $('<div id="bika-spinner"><img src="' + portal_url + '/spinner.gif" alt=""/></div>');
	spinner.appendTo('body').hide();
	$(document).ajaxStart(function () {
		counter++;
		setTimeout(function () {
			if (counter > 0) {
				spinner.show('fast');
			}
		}, 500);
	});
	function stop_spinner(){
		counter--;
		if (counter < 0){ counter = 0; }
		if (counter == 0) {
			clearTimeout(timer);
			spinner.stop();
			spinner.hide();
		}
	}
	$(document).ajaxStop(function () {
		stop_spinner();
	});
	$( document ).ajaxError(function( event, jqxhr, settings, thrownError ) {
		stop_spinner();
		window.bika.lims.log("Error at " + settings.url + ": " + thrownError);
	});
});
}(jQuery));
