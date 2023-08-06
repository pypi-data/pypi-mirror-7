(function( $ ) {
    "use strict";

function destroy(arr, val) {
    for (var i = 0; i < arr.length; i++) if (arr[i] === val) arr.splice(i, 1);
    return arr;
}
function getRelTag() {
    //Return the tag that identifies the position of the 
    var layout = $("input[id='layout']").val();
    var rel_tag = 'tr';
    if (layout == 'columns') {
        rel_tag = 'td'; 
    };
    return rel_tag;
}
    
function clearHiddenPopupFields(analyses) {
    $(analyses).find(".overlay_field").remove();
}

function getResultRange(service_uid, spec_uid, keyword) {
        //console.log('getResultRange:'+service_uid+':'+spec_uid+':'+keyword);
        //var to know if analysis need specification
        var return_val = ["", "", ""];
        $.ajaxSetup({async:false});
        //Search if current analysis's service allows specification
        var request_allowspec = {
            catalog_name: "uid_catalog",
            UID: service_uid
        };
        window.bika.lims.jsonapi_read(request_allowspec, function (result) {
            if (result.objects && result.objects.length > 0 &&
                ( result.objects[0].ResultOptions == null ||
                  result.objects[0].ResultOptions.length == 0)) {
                //console.log('getResultRange:service:'+service_uid+':'+result.objects[0].ResultOptions.length);
                var request_data = {
                    catalog_name: "uid_catalog",
                    UID: spec_uid
                };
                window.bika.lims.jsonapi_read(request_data, function (data) {
                    if (data.objects && data.objects.length > 0 &&
                        data.objects[0].ResultsRange && 
                        data.objects[0].ResultsRange.length > 0) {
                        //console.log('getResultRange:spec:'+spec_uid+':'+data.objects[0].ResultsRange.length);
                        var rr = data.objects[0].ResultsRange;
                        for (var i in rr) {
                            if (!(rr.hasOwnProperty(i))) {
                                continue;
                            }
                            //console.log(rr[i].keyword +'=='+ keyword);
                            if (rr[i].keyword == keyword) {
                                return_val = [rr[i].min, rr[i].max, rr[i].error];
                                break;
                            }
                        }
                    }
                })
            };
       });
       $.ajaxSetup({async:true});
       //console.log('getResultRange:'+return_val);
       return return_val;
    } 

function toggle_spec_fields(element) {
    // When a service checkbox is clicked, this is used to display
    // or remove the specification inputs.
    if (!$("#bika_setup").attr("EnableARSpecs")) {
        return;
    }
    var arnum = $(element).attr("arnum");
    var spec_uid = $("#ar_" + arnum + "_Specification_uid").val();
    var service_uid = $(element).attr("value");
    var min_name = "ar." + arnum + ".min." + service_uid;
    var max_name = "ar." + arnum + ".max." + service_uid;
    var error_name = "ar." + arnum + ".error." + service_uid;
    if ($(element).prop("checked") && $(element).siblings().filter("[name='" + min_name + "']").length === 0) {
        //var to know if analysis need specification
        var allowspec = true;
        //Search if current analysis's service allows specification
        var request_allowspec = {
            catalog_name: "uid_catalog",
            UID: service_uid
        };
        window.bika.lims.jsonapi_read(request_allowspec, function (result) {
            if (result.objects && result.objects.length > 0) {
                var allowspec = result.objects[0].ResultOptions == null || result.objects[0].ResultOptions.length == 0;
                // To force the next if statments part to be syncron
                if ((spec_uid !== "") && allowspec) {
                    var request_data = {
                        catalog_name: "uid_catalog",
                        UID: spec_uid
                    };
                    window.bika.lims.jsonapi_read(request_data, function (data) {
                        var min_val = "";
                        var max_val = "";
                        var error_val = "";
                        if (data.objects && data.objects.length > 0) {
                            var rr = data.objects[0].ResultsRange;
                            for (var i in rr) {
                                if (!(rr.hasOwnProperty(i))) {
                                    continue;
                                }
                                if (rr[i].keyword == $(element).attr("keyword")) {
                                    min_val = rr[i].min;
                                    max_val = rr[i].max;
                                    error_val = rr[i].error;
                                    break;
                                }
                            }
                        }
                        var min = $("<input class='spec_bit min' type='text' size='3' uid='" + service_uid + "' value='" + min_val + "' name='" + min_name + "' keyword='" + $(element).attr("keyword") + "' autocomplete='off' placeholder='&gt;'/>");
                        var max = $("<input class='spec_bit max' type='text' size='3' uid='" + service_uid + "' value='" + max_val + "' name='" + max_name + "' keyword='" + $(element).attr("keyword") + "' autocomplete='off' placeholder='&lt;'/>");
                        var error = $("<input class='spec_bit error' type='text' size='3' uid='" + service_uid + "' value='" + error_val + "' name='" + error_name + "' keyword='" + $(element).attr("keyword") + "' autocomplete='off' placeholder='%'/>");
                        $(element).after(error).after(max).after(min);
                    });
                }
                else if (allowspec) {
                    var min = $("<input class='spec_bit min' type='text' size='3' uid='" + service_uid + "' value='' name='" + min_name + "' keyword='" + $(element).attr("keyword") + "' autocomplete='off' placeholder='&gt;'/>");
                    var max = $("<input class='spec_bit max' type='text' size='3' uid='" + service_uid + "' value='' name='" + max_name + "' keyword='" + $(element).attr("keyword") + "' autocomplete='off' placeholder='&lt;'/>");
                    var error = $("<input class='spec_bit error' type='text' size='3' uid='" + service_uid + "' value='' name='" + error_name + "' keyword='" + $(element).attr("keyword") + "' autocomplete='off' placeholder='%'/>");
                    $(element).after(error).after(max).after(min);
                }
            }
        });
    } else {
        $("input[name='" + min_name + "']").remove();
        $("input[name='" + max_name + "']").remove();
        $("input[name='" + error_name + "']").remove();
    }
}

function reset_spec_field_values(arnum) {
    // When a spec is selected, all existing spec fields are cleared and reset
    if (!$("#bika_setup").attr("EnableARSpecs")) {
        return;
    }
    var spec_uid = $("#ar_" + arnum + "_Specification_uid").val();
    if (spec_uid !== "") {
        var request_data = {
            catalog_name: "uid_catalog",
            UID: spec_uid
        };
        window.bika.lims.jsonapi_read(request_data, function (data) {
            // empty all specification inputs.
            var min_name = "[name^='ar." + arnum + ".min']";
            var max_name = "[name^='ar." + arnum + ".max']";
            var error_name = "[name^='ar." + arnum + ".error']";
            $(min_name).val("");
            $(max_name).val("");
            $(error_name).val("");
            // set specification values in all supported services.
            if (data.objects && data.objects.length > 0) {
                var rr = data.objects[0].ResultsRange;
                for (var i in rr) {
                    var this_min = "[name='ar." + arnum + ".min\\." + rr[i].uid + "']";
                    var this_max = "[name='ar." + arnum + ".max\\." + rr[i].uid + "']";
                    var this_error = "[name='ar." + arnum + ".error\\." + rr[i].uid + "']";
                    if ($(this_min)) {
                        $(this_min).val(rr[i].min);
                        $(this_max).val(rr[i].max);
                        $(this_error).val(rr[i].error);
                    }
                }
            }
        });
    }
}

function validate_spec_field_entry(element) {
    var arnum = $(element).attr("name").split(".")[1];
    var uid = $(element).attr("uid");
    $("[name^='ar\\."+arnum+"\\.Specification']").val("");
    $("[name^='ar\\."+arnum+"\\.Specification_uid']").val("");
    var min_element = $("[name='ar."+arnum+".min."+uid+"']");
    var max_element = $("[name='ar."+arnum+".max."+uid+"']");
    var error_element = $("[name='ar."+arnum+".error."+uid+"']");
    var min = parseFloat($(min_element).val(), 10);
    var max = parseFloat($(max_element).val(), 10);
    var error = parseFloat($(error_element).val(), 10);
    if($(element).hasClass("min")){
        if(isNaN(min)) {
            $(min_element).val("");
        } else if ((!isNaN(max)) && min > max) {
            $(max_element).val("");
        }
    } else if($(element).hasClass("max")){
        if(isNaN(max)) {
            $(max_element).val("");
        } else if ((!isNaN(min)) && max < min) {
            $(min_element).val("");
        }
    } else if($(element).hasClass("error")){
        if(isNaN(error) || error < 0 || error > 100){
            $(error_element).val("");
        }
    }
}

function set_default_spec(arnum) {
    if(!$("#bika_setup").attr("EnableARSpecs")) { return; }
    // I use only the sampletype for looking up defaults.
    var sampletype_title = $("#ar_"+arnum+"_SampleType").val();
    var client_uid = $("#ar_"+arnum+"_Client_uid").val();
    if(sampletype_title !== ""){
        var bika_analysisspecs_uid = $("#bika_setup").attr("bika_analysisspecs_uid");
        var request_data = {
            catalog_name: "bika_setup_catalog",
            portal_type: "AnalysisSpec",
            getSampleTypeTitle: encodeURIComponent(sampletype_title),
            getClientUID: [client_uid, bika_analysisspecs_uid]
        };

        window.bika.lims.jsonapi_read(request_data, function(data) {
            var ob, obj;
            if (data.objects && data.objects.length > 0) {
                for(ob in data.objects){
                    if ((!data.objects.hasOwnProperty(ob))) { continue; }
                    obj = data.objects[ob];
                    if ((!obj.hasOwnProperty("getClientUID"))) { continue; }
                    if(client_uid == obj.getClientUID){
                        $("#ar_"+arnum+"_Specification").val(obj.title);
                        $("#ar_"+arnum+"_Specification_uid").val(obj.UID);
                        reset_spec_field_values(arnum);
                        return;
                    }
                }
                for(ob in data.objects){
                    if ((!data.objects.hasOwnProperty(ob))) { continue; }
                    obj = data.objects[ob];
                    if ((!obj.hasOwnProperty("getClientUID"))) { continue; }
                    if (obj.getClientUID != client_uid) {
                        $("#ar_"+arnum+"_Specification").val(obj.title);
                        $("#ar_"+arnum+"_Specification_uid").val(obj.UID);
                        reset_spec_field_values(arnum);
                        return;
                    }
                }
            }
        });

    }
}

function set_cc_contacts(arnum) {
    var contact_uid = $("#ar_"+arnum+"_Contact_uid").val();
    var fieldName = "ar."+arnum+".CCContact";
    // clear the CC widget
    $("input[name='"+fieldName+":record']").val("");
    $("input[name='"+fieldName+":record']").attr("uid", "");
    $("input[name='"+fieldName+"_uid']").val("");
    $("#ar_"+arnum+"_CCContact-listing").empty();
    if(contact_uid !== ""){
        var request_data = {
            portal_type: "Contact",
            UID: contact_uid
        };
        window.bika.lims.jsonapi_read(request_data, function(data) {
            if(data.objects && data.objects.length < 1) {
                return;
            }
            var ob = data.objects[0];
            var cc_titles = ob.CCContact;
            var cc_uids = ob.CCContact_uid;
            if(!cc_uids) {
                return;
            }
            $("input[name='"+fieldName+"_uid']").val(cc_uids.join(","));
            for (var i = 0; i < cc_uids.length; i++) {
                var title = cc_titles[i];
                var uid = cc_uids[i];
                var del_btn_src = window.portal_url+"/++resource++bika.lims.images/delete.png";
                var del_btn = "<img class='ar_deletebtn' src='"+del_btn_src+"' fieldName='"+fieldName+"' uid='"+uid+"'/>";
                var new_item = "<div class='reference_multi_item' uid='"+uid+"'>"+del_btn+title+"</div>";
                $("#ar_"+arnum+"_CCContact-listing").append($(new_item));
            }
        });
    }
}
function modify_Specification_field_filter(arnum) {
    // when a SampleType is selected I will allow only specs to be selected
    // which 1- (have the same Sample Types)
    // 2- (have no sample type at all)
    var sampletype_title = $("#ar_"+arnum+"_SampleType").val();
    var e = $("#ar_"+arnum+"_Specification");
    var query_str = $(e).attr("search_query");
    var query_obj = $.parseJSON(query_str);
    if (    query_obj.hasOwnProperty("getSampleTypeTitle") ){
        delete query_obj.getSampleTypeTitle;
    }
    query_obj.getSampleTypeTitle = [sampletype_title, ""];
    query_str = $.toJSON(query_obj);
    $(e).attr("search_query", query_str);
}


function ar_set_tabindexes() {
    // Sets the tab index to the elements. Tab flow top to bottom instead of left
    // to right.
    // Keyboard tab flow top to bottom instead of left to right
    var index = 10;
    var count = $("input[id='ar_count']").val();
    for (var i=0; i<count; i++) {
         var elements = $("tr[arnum="+i+"]").find("input[type!=hidden]").not("[disabled]");
        for (var j=0; j<elements.length; j++) {
            $(elements[j]).attr("tabindex",index);
            index++;
        }
    }
}

// Configure the widgets that archetypes built:
// set id and name to ar-arnum-fieldName fornats
// un-set the readonly attribute on the fields (so that we can search).
function ar_rename_elements(){
    var i, e, elements, arnum;
    var rel_tag = getRelTag();
    elements = $(rel_tag+"[ar_add_arnum_widget]").find("input[type!='hidden']").not("[disabled]");
    for (i = elements.length - 1; i >= 0; i--) {
        e = elements[i];
        arnum = $($(e).parents(rel_tag)).attr("arnum");
        // not :ignore_empty, widgets each get submitted to their own form handlers
        $(e).attr("name", "ar."+arnum+"."+$(e).attr("name")+":record");
        $(e).attr("id", "ar_"+arnum+"_"+e.id);
        $(e).removeAttr("required");
    };
    elements = $(rel_tag+"[ar_add_arnum_widget]").find("input[type='hidden']");
    for (i = elements.length - 1; i >= 0; i--) {
        e = elements[i];
        arnum = $($(e).parents(rel_tag)).attr("arnum");
        $(e).attr("id", "ar_"+arnum+"_"+e.id);
        // not :ignore_empty, widgets each get submitted to their own form handlers
        $(e).attr("name", "ar."+arnum+"."+$(e).attr("name")+":record");
    };
    elements = $(".multiValued-listing");
    for (i = elements.length - 1; i >= 0; i--) {
        e = elements[i];
        var eid = e.id.split("-listing")[0];
        arnum = $($(e).parents(rel_tag)).attr("arnum");
        $(e).attr("id", "ar_"+arnum+"_"+eid+"-listing");
        // not :ignore_empty, widgets each get submitted to their own form handlers
        $(e).attr("name", "ar."+arnum+"."+eid+"-listing");
        $(e).attr("fieldName", "ar."+arnum+"."+eid);
    };
}

// The columnar referencewidgets that we reconfigure use this as their
// select handler.
function ar_referencewidget_select_handler(event, ui){
    /*jshint validthis:true */
    event.preventDefault();

    // Set form values in activated element (must exist in colModel!)
    var fieldName = $(this).attr("name");
    var parts = fieldName.split(".");
    var arnum = "";
    var uid_element = $("#"+fieldName+"_uid");
    var listing_div = $("#"+fieldName+"-listing");
    if (parts.length == 3) {
        fieldName = parts[2].split(":")[0];
        arnum = $(this).attr("id").split("_")[1];
        uid_element = $("#ar_"+arnum+"_"+fieldName+"_uid");
        listing_div = $("#ar_"+arnum+"_"+fieldName+"-listing");
    }
    var skip;

    if(listing_div.length > 0) {
        // add selection to textfield value
        var existing_uids = $(uid_element).val().split(",");
              destroy(existing_uids,"");
              destroy(existing_uids,"[]");
        var selected_value = ui.item[$(this).attr("ui_item")];
        var selected_uid = ui.item.UID;
        if (existing_uids.indexOf(selected_uid) == -1) {
            existing_uids.push(selected_uid);
            $(this).val("");
            $(this).attr("uid", existing_uids.join(","));
            $(uid_element).val(existing_uids.join(","));
                      // insert item to listing
                      var del_btn_src = portal_url+"/++resource++bika.lims.images/delete.png";
                      var del_btn = "<img class='deletebtn' src='"+del_btn_src+"' fieldName='ar."+arnum+"."+fieldName+"' uid='"+selected_uid+"'/>";
                      var new_item = "<div class='reference_multi_item' uid='"+selected_uid+"'>"+del_btn+selected_value+"</div>";
                      $(listing_div).append($(new_item));
        }
        skip = $(uid_element).attr("skip_referencewidget_lookup");
        if (skip !== true){
            $(this).trigger("selected", ui.item.UID);
        }
        $(uid_element).removeAttr("skip_referencewidget_lookup");
        $(this).next("input").focus();
    } else {
        // Set value in activated element (must exist in colModel!)
        $(this).val(ui.item[$(this).attr("ui_item")]);
        $(this).attr("uid", ui.item.UID);
        $(uid_element).val(ui.item.UID);
        skip = $(uid_element).attr("skip_referencewidget_lookup");
        if (skip !== true){
            $(this).trigger("selected", ui.item.UID);
        }
        $(uid_element).removeAttr("skip_referencewidget_lookup");
        $(this).next("input").focus();
    }

    if(fieldName == "Contact"){
        set_cc_contacts(arnum);
    }
    if(fieldName == "SampleType"){
        // selecting a Sampletype - jiggle the SamplePoint element.
        var sp_element = $("#ar_"+arnum+"_SamplePoint");
        sp_element
            .removeClass( "cg-autocomplete-input" )
            .removeAttr( "autocomplete" )
            .removeAttr( "role" )
            .removeAttr( "aria-autocomplete" )
            .removeAttr( "aria-haspopup" );
        var new_sp_element = $(sp_element[0]).clone();
        var sp_parent_node = $(sp_element).parent();
        $(sp_element).remove();
        $(sp_parent_node).append(new_sp_element);
        sp_element = $("#ar_"+arnum+"_SamplePoint");
        // cut kwargs into the base_query
        var sp_base_query = $(sp_element).attr("base_query");
        sp_base_query = $.parseJSON(sp_base_query);
        sp_base_query = $.toJSON(sp_base_query);
        var sp_search_query = {"getSampleTypeTitle": ui.item[$(this).attr("ui_item")]};
        sp_search_query = $.toJSON(sp_search_query);
        sp_element.attr("search_query", sp_search_query);
        ar_referencewidget_lookups(sp_element);
    }
    if(fieldName == "SamplePoint"){
        // selecting a Samplepoint - jiggle the SampleType element.
        var st_element = $("#ar_"+arnum+"_SampleType");
        st_element
            .removeClass( "cg-autocomplete-input" )
            .removeAttr( "autocomplete" )
            .removeAttr( "role" )
            .removeAttr( "aria-autocomplete" )
            .removeAttr( "aria-haspopup" );
        var new_st_element = $(st_element[0]).clone();
        var st_parent_node = $(st_element).parent();
        $(st_element).remove();
        $(st_parent_node).append(new_st_element);
        st_element = $("#ar_"+arnum+"_SampleType");
        // cut kwargs into the base_query
        var st_base_query = $(st_element).attr("base_query");
        st_base_query = $.parseJSON(st_base_query);
        st_base_query = $.toJSON(st_base_query);
        var st_search_query = {"getSamplePointTitle": ui.item[$(this).attr("ui_item")]};
        st_search_query = $.toJSON(st_search_query);
        st_element.attr("search_query", st_search_query);
        ar_referencewidget_lookups(st_element);
    }

    // Selected a Profile
    if(fieldName == "Profile"){
        unsetTemplate(arnum);
        $.ajaxSetup({async:false});
        setAnalysisProfile(arnum, $(this).val());
        $.ajaxSetup({async:true});
        calculate_parts(arnum);
    }

    // Selected a Template
    if(fieldName == "Template"){
        setTemplate(arnum, $(this).val());
    }

    // Selected a sample to create a secondary AR.
    if(fieldName == "Sample"){
        // var e = $("input[name^='ar\\."+arnum+"\\."+fieldName+"']");
        // var Sample = $("input[name^='ar\\."+arnum+"\\."+fieldName+"']").val();
        // var Sample_uid = $("input[name^='ar\\."+arnum+"\\."+fieldName+"_uid']").val();
        // Install the handler which will undo the changes I am about to make
        $(this).blur(function(){
            if($(this).val() === ""){
                // clear and un-disable everything
                var disabled_elements = $("[ar_add_arnum_widget] [id*='ar_"+arnum+"']:disabled");
                $.each(disabled_elements, function(x,disabled_element){
                    $(disabled_element).prop("disabled", false);
                    if($(disabled_element).attr("type") == "checkbox"){
                        $(disabled_element).prop("checked", false);
                    } else {
                        $(disabled_element).val("");
                    }
                });
            }
        });
        // Then populate and disable sample fields
        $.getJSON(window.location.href.replace("/ar_add","") + "/secondary_ar_sample_info",
            {
                "Sample_uid": $(this).attr("uid"),
                "_authenticator": $("input[name='_authenticator']").val()},
            function(data){
                for (var x = data.length - 1; x >= 0; x--) {
                    var fieldname = data[x][0];
                    var fieldvalue = data[x][1];
                    var uid_element = $("#ar_"+arnum+"_"+fieldname+"_uid");
                    $(uid_element).val("");
                    var sample_element = $("#ar_"+arnum+"_"+fieldname);
                    $(sample_element).val("").prop("disabled", true);
                    if($(sample_element).attr("type") == "checkbox" && fieldvalue){
                        $(sample_element).prop("checked", true);
                    } else {
                        $(sample_element).val(fieldvalue);
                    }
                }
            }
        );
    }

    // Selected a SampleType
    if(fieldName == "SampleType"){
        unsetTemplate(arnum);
        set_default_spec(arnum);
        modify_Specification_field_filter(arnum);
        calculate_parts(arnum);
    }

    // Selected a Specification
    if(fieldName == "Specification"){
        reset_spec_field_values(arnum);
    }

    // Triggers 'selected' event (as reference widget)
    $(this).trigger("selected", ui.item.UID);
}

function add_path_filter_to_spec_lookups(){
    for (var arnum=0; arnum<parseInt($("#ar_count").val(), 10); arnum++) {
        var element = $("#ar_"+arnum+"_Specification");
        var bq = $.parseJSON($(element).attr("base_query"));
        bq.path = [$("#bika_setup").attr("bika_analysisspecs_path"),
				   $("#PhysicalPath").attr("here")];
        $(element).attr("base_query", $.toJSON(bq));
    }
}

// we do the referencewidget_lookups differently to the widget default.
// We also include a bunch of ar_add specific on-change stuff, since the
// popup widget takes over the .change event completely.
function ar_referencewidget_lookups(elements){
    add_path_filter_to_spec_lookups();
    var inputs;
    if(elements === undefined){
        inputs = $("input.referencewidget").not(".has_combogrid_widget");
    } else {
        inputs = elements;
    }
    for (var i = inputs.length - 1; i >= 0; i--) {
        var element = inputs[i];
        var options = $.parseJSON($(element).attr("combogrid_options"));
        if(options === "" || options === undefined){
            continue;
        }
        options.select = ar_referencewidget_select_handler;

        if(window.location.href.search("ar_add") > -1){
            options.url = window.location.href.split("/ar_add")[0] + "/" + options.url;
        }
        options.url = options.url + "?_authenticator=" + $("input[name='_authenticator']").val();
        options.url = options.url + "&catalog_name=" + $(element).attr("catalog_name");
        options.url = options.url + "&base_query=" + $(element).attr("base_query");
        options.url = options.url + "&search_query=" + $(element).attr("search_query");
        options.url = options.url + "&colModel=" + $.toJSON( $.parseJSON($(element).attr("combogrid_options")).colModel);
        options.url = options.url + "&search_fields=" + $.toJSON($.parseJSON($(element).attr("combogrid_options")).search_fields);
        options.url = options.url + "&discard_empty=" + $.toJSON($.parseJSON($(element).attr("combogrid_options")).discard_empty);
        $(element).combogrid(options);
        $(element).addClass("has_combogrid_widget");
        $(element).attr("search_query", "{}");
    }
}

function recalc_prices(arnum){
    var include;
    var layout = $("input[id='layout']").val();
    if(arnum){
        // recalculate just this arnum
        var subtotal = 0.00;
        var discount_amount = 0.00;
        var vat = 0.00;
        var total = 0.00;
        var discount = parseFloat($("#member_discount").val());

        $.each($("input[name='ar."+arnum+".Analyses:list:ignore_empty:record']"), function(){
            var disabled = $(this).prop("disabled");
            // For some browsers, `attr` is undefined; for others, its false.  Check for both.
            if (typeof disabled !== "undefined" && disabled !== false) {
                disabled = true;
            } else {
                disabled = false;
            }
            if (layout == 'rows') {
                include = (!(disabled) && $(this).prop("checked") && $(this).hasClass('overlay_field'));
            } else {
                include = (!(disabled) && $(this).prop("checked") && $(this).prop('type') != 'hidden'); 
            }
            if (include) {
                var serviceUID = this.id;
                var form_price = parseFloat($("#"+serviceUID+"_price").val());
                var vat_amount = parseFloat($("#"+serviceUID+"_price").attr("vat_amount"));
                var price;
                if(discount){
                    price = form_price - ((form_price / 100) * discount);
                } else {
                    price = form_price;
                }
                subtotal += price;
                discount_amount += ((form_price / 100) * discount);
                vat += ((price / 100) * vat_amount);
                total += price + ((price / 100) * vat_amount);
            }
        });
        $("#ar_"+arnum+"_subtotal").val(subtotal.toFixed(2));
        $("#ar_"+arnum+"_subtotal_display").val(subtotal.toFixed(2));
        $("#ar_"+arnum+"_discount").val(discount_amount.toFixed(2));
        $("#ar_"+arnum+"_vat").val(vat.toFixed(2));
        $("#ar_"+arnum+"_vat_display").val(vat.toFixed(2));
        $("#ar_"+arnum+"_total").val(total.toFixed(2));
        $("#ar_"+arnum+"_total_display").val(total.toFixed(2));
    } else {
        if (layout == 'columns') {
            for (var arnum=0; arnum<parseInt($("#ar_count").val(), 10); arnum++) {
                recalc_prices(String(arnum));
            }
        }
    }
}

function changeReportDryMatter(){
    /*jshint validthis:true */
    var dm = $("#getDryMatterService");
    var uid = $(dm).val();
    var cat = $(dm).attr("cat");
    var poc = $(dm).attr("poc");
    var rel_tag = getRelTag();
    var arnum = $(this).parents(rel_tag).attr("arnum");
    if ($(this).prop("checked")){
        // only play with service checkboxes when enabling dry matter
        unsetAnalysisProfile(arnum);
        $.ajaxSetup({async:false});
        toggleCat(poc, cat, arnum, [uid], true);
        $.ajaxSetup({async:true});
        var dryservice_cb = $("input[arnum='"+arnum+"']:checkbox").filter("#"+uid);
        $(dryservice_cb).prop("checked",true);
        calcdependencies([$(dryservice_cb)], true);
        calculate_parts(arnum);
    }
    recalc_prices();
}

function saveProfile(){
    /*jshint validthis:true */
    var layout = $("input[id='layout']").val();
    jarn.i18n.loadCatalog('bika');
    var _ = window.jarn.i18n.MessageFactory("bika");
    var arnum = this.id.split("_")[1];
    if (layout == 'rows') {
        var analyses = $("#ar_"+arnum+"_Analyses").parent().find('.overlay_field').filter(".cb");
    } else {
        var analyses = $(".cb").filter('[arnum="'+arnum+'"]').filter(':checked');
    }
    if (analyses.length == 0) {
        alert(_('Please select analyses to be save'));
        return;
    };
    var title;
    do {
        title=prompt(_("Please enter the title of the profile"));
    }
    while(title.length < 2);
    var request_data = 'obj_path=/Plone/bika_setup/bika_analysisprofiles&obj_type=AnalysisProfile&title='+title
    for (var i = 0; i < analyses.length; i++) {
        request_data = request_data+'&Service:list=UID:'+$(analyses[i]).val()
    }
    $.ajax({
        type: "POST",
        dataType: "json",
        url: window.portal_url + "/@@API/create",
        data: request_data,
        success: function(responseText) {
            alert(_('Profile '+title+' has been created successfully'));
        },
        error: function(XMLHttpRequest, statusText) {
            alert(_('Fail:'+statusText));
        },
    });

}

function copy_service(copybutton){
    var e = $("input[arnum='0']").filter("#" + copybutton.id);
    var kw = $(e).attr("keyword");
    var service_uid = $(e).prop("value");
    // get arnum 0 values
    var first_val = $(e).prop("checked");
    var first_min = $("[name='ar.0.min." + service_uid + "']").prop("value");
    var first_max = $("[name='ar.0.max." + service_uid + "']").prop("value");
    var first_error = $("[name='ar.0.error." + service_uid + "']").prop("value");

    var ar_count = parseInt($("#ar_count").val(), 10);
    var affected_elements = [];
    // 0 is the first arnum; we only want to change cols 1 onward.
    for (var arnum = 1; arnum < ar_count; arnum++) {
        unsetTemplate(arnum);
        unsetAnalysisProfile(arnum);
        var other_elem = $("input[arnum='" + arnum + "']").filter("#" + copybutton.id);
        if ((!other_elem.prop("disabled")) && (other_elem.prop("checked") != first_val)) {
            other_elem.prop("checked", first_val ? true : false);
            toggle_spec_fields(other_elem);
            affected_elements.push(other_elem);
        }
        if (first_val) {
            $(".spec_bit.min[arnum='" + arnum + "']").filter("[keyword='" + kw + "']")
                .prop("value", first_min);
            $(".spec_bit.max[arnum='" + arnum + "']").filter("[keyword='" + kw + "']")
                .prop("value", first_max);
            $(".spec_bit.error[arnum='" + arnum + "']").filter("[keyword='" + kw + "']")
                .prop("value", first_error);
        }
        calculate_parts(arnum);
    }
    calcdependencies(affected_elements, true);
    recalc_prices();
}

function copy_analyses(copybutton){
    var first_elem = $("#ar_0_Analyses");
    var hidden_elements = $(first_elem).parent().find('.overlay_field');
    var ar_count = parseInt($("#ar_count").val());
    var affected_elements = [];
    var e, other_elem, other_elem_parent, new_hidden, name;
    // 0 is the first arnum; we only want to change rows 1 onward.
    for (var arnum = 1; arnum < ar_count; arnum++) {
        other_elem = $("#ar_"+arnum+"_Analyses");
        $(other_elem).val($(first_elem).val());
        other_elem_parent = $(other_elem).parent();
        clearHiddenPopupFields(other_elem_parent);
        for (var i = 0; i <  hidden_elements.length; i++) {
            e = hidden_elements[i];
            new_hidden = $(e).clone();
            $(new_hidden[0]).attr('arnum', arnum);
            name = $(e).prop('name');
            if (name !== undefined) {
                name = name.replace('.0.', '.'+arnum+'.');
                $(new_hidden[0]).prop('name', name);
            };
            $(other_elem_parent).append(new_hidden);
        };
        recalc_prices(arnum);
    }
}

function copy_checkbox(copybutton){
    var fieldName = $(copybutton).attr("name");
    var first_val = $("input[name^='ar\\.0\\."+fieldName+"']").prop("checked");
    var ar_count = parseInt($("#ar_count").val(), 10);
    // arnum starts at 1 here; we don't copy into the the first row
    for (var arnum=1; arnum<ar_count; arnum++) {
        var other_elem = $("#ar_" + arnum + "_" + fieldName);
        if ((other_elem.prop("checked")!=first_val)) {
            other_elem.prop("checked",first_val?true:false);
            other_elem.trigger("change");
        }
    }
    $("[id*='_" + fieldName + "']").change();
}

function copyButton(){
    /*jshint validthis:true */
    var fieldName = $(this).attr("name");
    var ar_count = parseInt($("#ar_count").val(), 10);

    if ($(this).attr("name") == "analyses"){
        copy_analyses(this);
    }
    else if ($(this).parent().attr("class") == "service"){
        copy_service(this);
    }

    else if ($("input[name^='ar\\.0\\."+fieldName+"']").attr("type") == "checkbox") {
        copy_checkbox(this);
    }

    // Anything else

    else{
        var first_val = $("input[name^='ar\\.0\\."+fieldName+"']").filter("[type=text]").val();
        // Reference fields have a hidden *_uid field
        var first_uid = $("input[name^='ar\\.0\\."+fieldName+"_uid']").val();
        // multi-valued fields: selection is in {fieldname}-listing
        var first_multi_html = $("div[name^='ar\\.0\\."+fieldName+"-listing']").html();
        // arnum starts at 1 here; we don't copy into the the first row
        for (var arnum=1; arnum<ar_count; arnum++) {
            var other_uid_elem = $("#ar_" + arnum + "_" + fieldName + "_uid");
            if (first_uid !== undefined && first_uid !== null){
                other_uid_elem.val(first_uid);
            }
            var other_multi_div = $("div[name^='ar\\."+arnum+"\\."+fieldName+"-listing']");
            if (first_multi_html !== undefined && first_multi_html !== null){
                 other_multi_div.html(first_multi_html.replace(".0.", "."+arnum+"."));
            }
            // Actual field value
            var other_elem = $("#ar_" + arnum + "_" + fieldName);
            if (!(other_elem.prop("disabled"))) {
                $(other_elem).attr("skip_referencewidget_lookup", true);
                other_elem.val(first_val);
                other_elem.trigger("change");

                if(fieldName == "Contact") {
                    set_cc_contacts(arnum);
                }

                if(fieldName == "Profile"){
                    unsetTemplate(arnum);
                    setAnalysisProfile(arnum, first_val);
                    calculate_parts(arnum);
                }

                if(fieldName == "Template"){
                    setTemplate(arnum, first_val);
                }

                if(fieldName == "SampleType"){
                    unsetTemplate(arnum);
                    calculate_parts(arnum);
                }

                if(fieldName == "Specification"){
                    reset_spec_field_values(arnum);
                }

            }
        }
        //$('[id*=_' + fieldName + "]").change();
    }
}

function toggleCat(poc, category_uid, arnum, selectedservices, force_expand, disable) {
    // selectedservices and arnum are optional.
    // disable is used for field analyses - secondary ARs should not be able
    // to select these
    var layout = $("input[id='layout']").val();
    force_expand = force_expand || false;
    disable = disable || -1;
    if(!arnum && arnum !== 0) { arnum = ""; };

    var th = $("th[poc='"+poc+"']").filter("[cat='"+category_uid+"']");
    var tbody = $("#"+poc+"_"+category_uid);

    if($(tbody).hasClass("expanded")){
        // displaying an already expanded category:
        if(selectedservices){
            var rows = tbody.children();
            for(var i = 0; i < rows.length; i++){
                var service = rows[i];
                var service_uid = $(service).attr("id");
                if(selectedservices.indexOf(service_uid) > -1){
                    var cb = $("input[value="+service_uid+"]").filter("[arnum='"+arnum+"']");
                    $(cb).prop("checked",true);
                    toggle_spec_fields(cb);
                }
            }
            recalc_prices(arnum);
        } else {
            if (force_expand){ $(tbody).toggle(true); }
            else { $(tbody).toggle(); }
        }
    } else {
        if(!selectedservices) selectedservices = [];
        $(tbody).removeClass("collapsed").addClass("expanded");
        //$(th).removeClass("collapsed").addClass("expanded");
        var ar_count = $("#ar_count").attr("value");
        if (layout == 'rows') {
            ar_count = 1;
        };
        var options = {
            "selectedservices": selectedservices.join(","),
            "categoryUID": category_uid,
            "arnum": arnum,
            "disable": disable > -1 ? arnum : -1,
            "ar_count": ar_count,
            "poc": poc
        };
        // possibly remove the fake ar context
        var url = window.location.href.split("/ar_add")[0] + "/analysisrequest_analysisservices";
        $(tbody).load(url, options, function(){
            // analysis service checkboxes
            if (layout == 'columns') {
                $("input[name*='Analyses']").unbind();
                $("input[name*='Analyses']").bind("change", service_checkbox_change);
            } else {
                $("input[class='cb']").bind("change", service_checkbox_change);
            };
            if(selectedservices!=[]){
                recalc_prices(arnum);
                //console.log('toggleCat sevices:'+selectedservices);
                for(i=0;i<selectedservices.length;i++){
                    var service_uid = selectedservices[i];
                    if (service_uid.length > 0) {
                        var e = $("input[value=" + service_uid + "]").filter("[arnum='" + arnum + "']");
                        //console.log('toggleCat: ' + service_uid + ':' + arnum);
                        //TODO Hacked this because togge_spec_fields doesn't do any longer!
                        $(e).prop('checked', 'true');
                        $(e).change();
                        //toggle_spec_fields(e);
                    };
                }
            };
        });
    }
}

function calc_parts_handler(arnum, data){
    // Set new part numbers in hidden form field
    var formparts = $.parseJSON($("#parts").val());
    var parts = data.parts;
    formparts[arnum] = parts;
    $("#parts").val($.toJSON(formparts));
    // write new part numbers next to checkboxes
    for(var p in parts) { if(!parts.hasOwnProperty(p)){ continue; }
        for (var s in parts[p].services) {
            if (!parts[p].services.hasOwnProperty(s)) { continue; }
            $(".partnr_"+parts[p].services[s]).filter("[arnum='"+arnum+"']").empty().append(p+1);
        }
    }
}

function calculate_parts(arnum) {
    // Template columns are not calculated
    if ($("#ar_"+arnum+"_Template").val() !== ""){
        return;
    }
    var st_uid = $("#ar_"+arnum+"_SampleType_uid").val();
    var checked = $("[name^='ar\\."+arnum+"\\.Analyses']").filter(":checked");
    var service_uids = [];
    for(var i=0;i<checked.length;i++){
        var uid = $(checked[i]).attr("value");
        service_uids.push(uid);
    }
    // if no sampletype or no selected analyses:  remove partition markers
    if (st_uid === "" || service_uids.length === 0) {
        $("[class*='partnr_']").filter("[arnum='"+arnum+"']").empty();
        return;
    }
    var request_data = {
            services: service_uids.join(","),
            sampletype: st_uid,
            _authenticator: $("input[name='_authenticator']").val()
    };
    window.jsonapi_cache = window.jsonapi_cache || {};
    var cacheKey = $.param(request_data);
    if (typeof window.jsonapi_cache[cacheKey] === "undefined") {
        $.ajax({
            type: "POST",
            dataType: "json",
            url: window.portal_url + "/@@API/calculate_partitions",
            data: request_data,
            success: function(data) {
                window.jsonapi_cache[cacheKey] = data;
                calc_parts_handler(arnum, data);
            }
        });
    } else {
        var data = window.jsonapi_cache[cacheKey];
        calc_parts_handler(arnum, data);
    }
}

function add_Yes(dlg, element, dep_services){
    /*jshint validthis:true */
    var arnum = $(element).attr("arnum");
    var key, json_key, dep, i;
    var keyed_deps = {};
    for(i = 0; i<dep_services.length; i++){
        dep = dep_services[i];
        key = {
            col: arnum,
            poc: dep.PointOfCapture,
            cat_uid: dep.Category_uid
        };
        json_key = $.toJSON(key);
        if(!keyed_deps[json_key]){
            keyed_deps[json_key] = [];
        }
        keyed_deps[json_key].push(dep.Service_uid);
    }

    var modified_cols = [];
    for(json_key in keyed_deps){
        if (!keyed_deps.hasOwnProperty(json_key)){ continue; }
        key = $.parseJSON(json_key);
        if(!modified_cols[key.col]){
            modified_cols.push(key.col);
        }
        var service_uids = keyed_deps[json_key];
        var tbody = $("#"+key.poc+"_"+key.cat_uid);
        if($(tbody).hasClass("expanded")) {
            // if cat is already expanded, manually select service checkboxes
            $(tbody).toggle(true);
            for(i=0; i<service_uids.length; i++){
                var service_uid = service_uids[i];
                var e = $("input[arnum='"+key.col+"']").filter("#"+service_uid);
                $(e).prop("checked",true);
                toggle_spec_fields(e);
            }
        } else {
            // otherwise, toggleCat will take care of everything for us
            $.ajaxSetup({async:false});
            toggleCat(key.poc, key.cat_uid, key.col, service_uids);
            $.ajaxSetup({async:true});
        }
    }
    recalc_prices();
    for(i=0; i<modified_cols.length; i+=1){
        calculate_parts(modified_cols[i]);
    }
    $(dlg).dialog("close");
    $("#messagebox").remove();


}

function add_No(dlg, element){
    /*jshint validthis:true */
    $(element).prop("checked",false);
    $(dlg).dialog("close");
    $("#messagebox").remove();
}

function calcdependencies(elements, auto_yes) {
    /*jshint validthis:true */
    auto_yes = auto_yes || false;
    jarn.i18n.loadCatalog('bika');
    var _ = window.jarn.i18n.MessageFactory("bika");

    var dep;
    var dep_i, cb;

    var lims = window.bika.lims;

    for(var elements_i = 0; elements_i < elements.length; elements_i++){
        var dep_services = [];  // actionable services
        var dep_titles = [];
        var element = elements[elements_i];
        var arnum = $(element).attr("arnum");
        var service_uid = $(element).attr("id");
        var modified_cols = [];
        // selecting a service; discover dependencies
        if ($(element).prop("checked")){
            var Dependencies = lims.AnalysisService.Dependencies(service_uid);
            for(dep_i = 0; dep_i<Dependencies.length; dep_i++) {
                dep = Dependencies[dep_i];
                if ($("input[arnum='"+arnum+"']").filter("#"+dep.Service_uid).prop("checked")){
                    continue; // skip if checked already
                }
                dep_services.push(dep);
                dep_titles.push(dep.Service);
            }

            if (dep_services.length > 0) {
                if(!modified_cols[arnum]){
                    modified_cols.push(arnum);
                }
                if (auto_yes) {
                    add_Yes(this, element, dep_services);
                } else {
                    var html = "<div id='messagebox' style='display:none' title='" + _("Service dependencies") + "'>";
                    html = html + _("<p>${service} requires the following services to be selected:</p>"+
                                                    "<br/><p>${deps}</p><br/><p>Do you want to apply these selections now?</p>",
                                                    {
                                                        service: $(element).attr("title"),
                                                        deps: dep_titles.join("<br/>")
                                                    });
                    html = html + "</div>";
                    $("body").append(html);
                    $("#messagebox").dialog({
                        width:450,
                        resizable:false,
                        closeOnEscape: false,
                        buttons:{
                            yes: function(){
                                add_Yes(this, element, dep_services);
                            },
                            no: function(){
                                add_No(this, element);
                            }
                        }
                    });
                }
            }
        }
        // unselecting a service; discover back dependencies
        else {
            var Dependants = lims.AnalysisService.Dependants(service_uid);
            if (Dependants.length > 0){
                for (i=0; i<Dependants.length; i++){
                    dep = Dependants[i];
                    cb = $("input[arnum='"+arnum+"']").filter("#"+dep.Service_uid);
                    if (cb.prop("checked")){
                        dep_titles.push(dep.Service);
                        dep_services.push(dep);
                    }
                }
                if(dep_services.length > 0){
                    if (auto_yes) {
                        for(dep_i=0; dep_i<dep_services.length; dep_i+=1) {
                            dep = dep_services[dep_i];
                            service_uid = dep.Service_uid;
                            cb = $("input[arnum='"+arnum+"']").filter("#"+service_uid);
                            $(cb).prop("checked", false);
                            toggle_spec_fields($(cb));
                            $(".partnr_"+service_uid).filter("[arnum='"+arnum+"']").empty();
                            if ($(cb).val() == $("#getDryMatterService").val()) {
                                $("#ar_"+arnum+"_ReportDryMatter").prop("checked",false);
                            }
                        }
                    } else {
                        $("body").append(
                            "<div id='messagebox' style='display:none' title='" + _("Service dependencies") + "'>"+
                            _("<p>The following services depend on ${service}, and will be unselected if you continue:</p><br/><p>${deps}</p><br/><p>Do you want to remove these selections now?</p>",
                                {service:$(element).attr("title"),
                                deps: dep_titles.join("<br/>")})+"</div>");
                        $("#messagebox").dialog({
                            width:450,
                            resizable:false,
                            closeOnEscape: false,
                            buttons:{
                                Yes: function(){
                                    for(dep_i=0; dep_i<dep_services.length; dep_i+=1) {
                                        dep = dep_services[dep_i];
                                        service_uid = dep.Service_uid;
                                        cb = $("input[arnum='"+arnum+"']").filter("#"+service_uid);
                                        $(cb).prop("checked", false);
                                        toggle_spec_fields($(cb));
                                        $(".partnr_"+service_uid).filter("[arnum='"+arnum+"']").empty();
                                        if ($(cb).val() == $("#getDryMatterService").val()) {
                                            $("#ar_"+arnum+"_ReportDryMatter").prop("checked",false);
                                        }
                                    }
                                    $(this).dialog("close");
                                    $("#messagebox").remove();
                                },
                                No:function(){
                                    $(element).prop("checked",true);
                                    toggle_spec_fields($(element));
                                    $(this).dialog("close");
                                    $("#messagebox").remove();
                                }
                            }
                        });
                    }
                }
            }
        }
        recalc_prices();
        for(var i=0; i<modified_cols.length; i+=1){
            calculate_parts(modified_cols[i]);
        }
    }
}

function unsetAnalyses(arnum){
    var layout = $("input[id='layout']").val();
    if (layout == 'columns') {
        $.each($("input[name^='ar."+arnum+".Analyses']"), function(){
            if($(this).prop("checked")) {
                $(this).prop("checked",false);
                toggle_spec_fields($(this));
            }
            $(".partnr_"+this.id).filter("[arnum='"+arnum+"']").empty();
        });
    } else {
        $.each($("input[name^='ar."+arnum+".Analyses']"), function(){
            $(this).attr('value', '');
            var an_parent = $(this).parent();
            clearHiddenPopupFields(an_parent);
        });
    };
}

// function uncheck_partnrs(arnum){
//     // all unchecked services have their part numbers removed
//     var ep = $("[class^='partnr_']").filter("[arnum='"+arnum+"']").not(":empty");
//     for(var i=0;i<ep.length;i++){
//         var em = ep[i];
//         var uid = $(ep[0]).attr("class").split("_")[1];
//         var cb = $("#"+uid);
//         if ( ! $(cb).prop("checked") ){
//             $(em).empty();
//         }
//     }
// }

function unsetAnalysisProfile(arnum){
    if($("#ar_"+arnum+"_Profile").val() !== ""){
        $("#ar_"+arnum+"_Profile").val("");
    }
}


function unsetTemplate(arnum){
    if($("#ar_"+arnum+"_Template").val() !== ""){
        $("#ar_"+arnum+"_Template").val("");
    }
}


function setTemplate(arnum, template_title){
    var range;
    var layout = $("input[id='layout']").val();
    unsetAnalyses(arnum);
    var request_data = {
        portal_type: "ARTemplate",
        title: template_title,
        include_fields: [
            "SampleType",
            "SampleTypeUID",
            "SamplePoint",
            "SamplePointUID",
            "ReportDryMatter",
            "AnalysisProfile",
            "Partitions",
            "Analyses",
            "Prices",
            ]
    };
    window.bika.lims.jsonapi_read(request_data, function(data){
        var template = data.objects[0];
        var request_data, x, i;
        // set our template fields
        $("#ar_"+arnum+"_SampleType").val(template.SampleType);
        $("#ar_"+arnum+"_SampleType_uid").val(template.SampleTypeUID);
        $("#ar_"+arnum+"_SamplePoint").val(template.SamplePoint);
        $("#ar_"+arnum+"_SamplePoint_uid").val(template.SamplePointUID);
        $("#ar_"+arnum+"_reportdrymatter").prop("checked", template.reportdrymatter);
        set_default_spec(arnum);
        // lookup AnalysisProfile
        if(template.AnalysisProfile) {
            request_data = {
                portal_type: "AnalysisProfile",
                title: template.AnalysisProfile,
                include_fields: ["UID"]
            };
            window.bika.lims.jsonapi_read(request_data, function(data){
                $("#ar_"+arnum+"_Profile").val(template.AnalysisProfile);
                $("#ar_"+arnum+"_Profile_uid").val(data.objects[0].UID);
            });
        } else {
                $("#ar_"+arnum+"_Profile").val("");
                $("#ar_"+arnum+"_Profile_uid").val("");
        }

        // scurrel the parts into hashes for easier lookup
        var parts_by_part_id = {};
        var parts_by_service_uid = {};
        for (x in template.Partitions) {
            if (!template.Partitions.hasOwnProperty(x)){ continue; }
            var P = template.Partitions[x];
            P.part_nr = parseInt(P.part_id.split("-")[1], 10);
            P.services = [];
            parts_by_part_id[P.part_id] = P;
        }
        for (x in template.Analyses) {
            if(!template.Analyses.hasOwnProperty(x)){ continue; }
            i = template.Analyses[x];
            parts_by_part_id[i.partition].services.push(i.service_uid);
            parts_by_service_uid[i.service_uid] = parts_by_part_id[i.partition];
        }
        // this one goes through with the form submit
        var parts = [];
        for(x in parts_by_part_id){
            if(!parts_by_part_id.hasOwnProperty(x)){ continue; }
            parts.push(parts_by_part_id[x]);
        }
        var formparts = $.parseJSON($("#parts").val());
        formparts[arnum] = parts;
        $("#parts").val($.toJSON(formparts));

        // lookup the services specified in the template
        request_data = {
            portal_type: "AnalysisService",
            UID: [],
            include_fields: ["PointOfCapture", "CategoryUID", "UID", "Title", "Keyword", "Price", 'VAT']
        };
        for (x in template.Analyses) {
            if (!template.Analyses.hasOwnProperty(x)){ continue; }
            request_data.UID.push(template.Analyses[x].service_uid);
        }
        // save services in hash for easier lookup this
        window.bika.lims.jsonapi_read(request_data, function(data) {
            var e;
            var poc_cat_services = {};
            for(var x in data.objects) {
                if(!data.objects.hasOwnProperty(x)){ continue; }
                var service = data.objects[x];
                var poc_title = service.PointOfCapture;
                if (!(poc_title in poc_cat_services)) {
                    poc_cat_services[poc_title] = {};
                }
                if (!(service.CategoryUID in poc_cat_services[poc_title])) {
                    poc_cat_services[poc_title][service.CategoryUID] = [];
                }
                poc_cat_services[poc_title][service.CategoryUID].push([service.UID, service.Title, service.Keyword, service.Price, service.VAT]);
            }
            // expand categories, select, and enable controls for template services
            var analyses = $("#ar_"+arnum+"_Analyses");
            var total = 0.00;
            var spec_uid = $("#ar_" + arnum + "_Specification_uid").val();
            var an_parent = $(analyses).parent();
            clearHiddenPopupFields(an_parent);
            var titles = [];
            for (var p in poc_cat_services) {
                if (!poc_cat_services.hasOwnProperty(p)){ continue; }
                var poc = poc_cat_services[p];
                for (var cat_uid in poc) {
                    if (!poc.hasOwnProperty(cat_uid)) {continue; }
                    var services = poc[cat_uid];
                    var tbody = $("tbody[id='"+p+"_"+cat_uid+"']");
                    var service;
                    // expand category
                    if(!($(tbody).hasClass("expanded"))) {
                        $.ajaxSetup({async:false});
                        toggleCat(p, cat_uid, arnum);
                        $.ajaxSetup({async:true});
                    }
                    $(tbody).toggle(true);
                    for(i=0;i<services.length;i++){
                        service = services[i];
                        if (layout == 'columns') {
                            // select checkboxes
                            e = $("input[arnum='"+arnum+"']").filter("#"+service[0]);
                            $(e).prop("checked", true);
                            toggle_spec_fields(e);
                        } else {
                            range = getResultRange(
                                        service[0], spec_uid, service[2]);
                            if (range[0] !== "") {
                                titles.push(service[1]);
                                ar_add_create_hidden_analysis(
                                    an_parent, service[0], arnum, p, cat_uid,
                                    range[0], range[1], range[2], 
                                    service[3], service[4]);
                                total = total + parseFloat(service[3]) + (parseFloat(service[3]) * parseFloat(service[4])/100);
                            };
                        }
                    }
                    if (layout == 'columns') {
                        // set part number indicators
                        for(i=0;i<services.length;i++){
                            service = services[i];
                            var partnr = parts_by_service_uid[service[0]].part_nr;
                            e = $(".partnr_"+service[0]).filter("[arnum='"+arnum+"']");
                            $(e).empty().append(partnr);
                        }
                    }
                }
            };
            if (layout == 'rows') {
                $(analyses).attr('value', titles.join(', '));
                $(analyses).attr('name', $(analyses).attr('name').split(':')[0]);
                var discount = $("#member_discount");
                if (discount.length > 0) {
                    discount = parseFloat($(discount).val());
                    total = total * (1-discount/100);
                };
                $("#ar_"+arnum+"_total").val(total.toFixed(2));
            };
        });
    });
    recalc_prices(arnum);
}

function setAnalysisProfile(arnum, profile_title){
    var layout = $("input[id='layout']").val();
    var titles = [];
    var analyses = $("#ar_"+arnum+"_Analyses");
    var spec_uid = $("#ar_" + arnum + "_Specification_uid").val();
    var an_parent = $(analyses).parent();
    var request_data = {
        portal_type: "AnalysisProfile",
        title: profile_title
    };
    window.bika.lims.jsonapi_read(request_data, function(data){
        var profile_objects = data.objects;
        var request_data = {
            portal_type: "AnalysisService",
            title: profile_objects[0].Service,
            include_fields: ["PointOfCapture", "Category", "UID", "Title", "Keyword", "Price", "VAT"]
        };
        window.bika.lims.jsonapi_read(request_data, function(data){
            var i;
            unsetAnalyses(arnum);
            $("#ar_"+arnum+"_ReportDryMatter").prop("checked",false);

            var service_objects = data.objects;
            if (service_objects.length === 0) return;
            var categorised_services = {};
            for (i in service_objects){
                var key = service_objects[i].PointOfCapture + "_" +
                    service_objects[i].Category;
                if(categorised_services[key] === undefined)
                    categorised_services[key] = [];
                categorised_services[key].push(service_objects[i]);
            }

            var total = 0.00;
            for (var poc_cat in categorised_services) {
                var services = categorised_services[poc_cat];
                if (layout == 'columns') {
                    var th = $("th#cat_"+poc_cat);
                    if($(th).hasClass("expanded")){
                        for (i in services){
                            var service = services[i];
                            var service_uid = services[i].UID;
                            var e = $("input[arnum='"+arnum+"']").filter("#"+service_uid);
                            $(e).prop("checked", true);
                            toggle_spec_fields($(e));
                        }
                        recalc_prices(arnum);
                    } else {
                        var poc = poc_cat.split("_")[0];
                        var cat_uid = services[0].Category_uid;
                        var service_uids = [];
                        for(var x = 0; x<services.length;x++){
                            service_uids.push(services[x].UID);
                        }
                        $.ajaxSetup({async:false});
                        toggleCat(poc, cat_uid, arnum, service_uids);
                        $.ajaxSetup({async:true});
                    }
                    $(th).removeClass("collapsed").addClass("expanded");
                } else {
                    var range;
                    var poc = poc_cat.split("_")[0];
                    var cat_uid = services[0].Category_uid;
                    clearHiddenPopupFields(an_parent);
                    for(i = 0; i<services.length;i++){
                        range = getResultRange(
                                    services[i].UID, spec_uid, services[i].Keyword);
                        if (range[0] !== "") {
                            titles.push(services[i].Title);
                            ar_add_create_hidden_analysis(
                                an_parent, services[i].UID, arnum, 
                                poc, cat_uid, range[0], range[1], range[2], 
                                services[i].Price, services[i].VAT);
                            total = total + parseFloat(services[i].Price);
                        };
                    }
                }
                if (layout == 'rows') {
                    $(analyses).attr('value', titles.join(', '));
                    $(analyses).attr('name', $(analyses).attr('name').split(':')[0]);
                    var discount = $("#member_discount");
                    if (discount.length > 0) {
                        discount = parseFloat($(discount).val());
                        total = total * (1-discount/100);
                    };
                    $("#ar_"+arnum+"_total").val(total.toFixed(2));
                };
            }
            calculate_parts(arnum);
        });
    });
}

function service_checkbox_change(){
    /*jshint validthis:true */
    var arnum = $(this).attr("arnum");
    var element = $(this);
    unsetAnalysisProfile(arnum);
    unsetTemplate(arnum);

    // Unselecting Dry Matter Service unsets 'Report Dry Matter'
    if ($(this).val() == $("#getDryMatterService").val() && !$(this).prop("checked")) {
        $("#ar_"+arnum+"_ReportDryMatter").prop("checked",false);
    }

    // unselecting service: remove part number.
    if (!$(this).prop("checked")){
        $(".partnr_"+this.id).filter("[arnum='"+arnum+"']").empty();
    }

    calcdependencies([element]);
    var layout = $("input[id='layout']").val();
    if (layout == 'columns') {
        recalc_prices();
    } else {
        recalc_prices(arnum);
    }
    calculate_parts(arnum);
    toggle_spec_fields(element);

}

function clickAnalysisCategory(){
    /*jshint validthis:true */
    // cat is a category uid, and no arnum is required here.
    toggleCat($(this).attr("poc"), $(this).attr("cat"), $('#arnum').val());
    if($(this).hasClass("expanded")){
        $(this).addClass("collapsed");
        $(this).removeClass("expanded");
    } else {
        $(this).removeClass("collapsed");
        $(this).addClass("expanded");
    }
}

function applyComboFilter(element, filterkey, filtervalue) {
    var base_query=$.parseJSON($(element).attr("base_query"));
    base_query[filterkey] = filtervalue;
    $(element).attr("base_query", $.toJSON(base_query));
    var options = $.parseJSON($(element).attr("combogrid_options"));
    options.url = window.location.href.split("/ar_add")[0] + "/" + options.url;
    options.url = options.url + "?_authenticator=" + $("input[name='_authenticator']").val();
    options.url = options.url + "&catalog_name=" + $(element).attr("catalog_name");
    options.url = options.url + "&base_query=" + $.toJSON(base_query);
    options.url = options.url + "&search_query=" + $(element).attr("search_query");
    options.url = options.url + "&colModel=" + $.toJSON( $.parseJSON($(element).attr("combogrid_options")).colModel);
    options.url = options.url + "&search_fields=" + $.toJSON($.parseJSON($(element).attr("combogrid_options")).search_fields);
    options.url = options.url + "&discard_empty=" + $.toJSON($.parseJSON($(element).attr("combogrid_options")).discard_empty);
    options.force_all="false";
    $(element).combogrid(options);
    $(element).addClass("has_combogrid_widget");
    $(element).attr("search_query", "{}");
}

function fill_column(data) {
    // fields which should not be completed from the source AR.
    var skip_fields = ['Sample', 'Sample_uid'];
    if (data.objects.length > 0) {
        var obj = data.objects[0];
        var col = window.bika.ar_copy_from_col;
        for (var fieldname in obj) {
            if (!obj.hasOwnProperty(fieldname)) {
                continue;
            }
            if (skip_fields.indexOf(fieldname) > -1) {
                continue;
            }
            var fieldvalue = obj[fieldname];
            var el = $("#ar_" + col + "_" + fieldname);
            if (el.length > 0) {
                $(el).val(fieldvalue);
            }
        }
        var services = {};
        var specs = {};
        var poc_name, cat_uid, service_uid, service_uids;
        var i, key;
        for (i = obj.Analyses.length - 1; i >= 0; i--) {
            var analysis = obj.Analyses[i];
            cat_uid = analysis.CategoryUID;
            service_uid = analysis.ServiceUID;
            key = analysis.PointOfCapture + "__" + analysis.CategoryUID;
            if (!(key in services)) {
                services[key] = [];
            }
            services[key].push(service_uid);
            specs[service_uid] = analysis.specification;
        }
        for (key in services) {
            if (!services.hasOwnProperty(key)) {
                continue;
            }
            poc_name = key.split("__")[0];
            cat_uid = key.split("__")[1];
            service_uids = services[key];
            window.toggleCat(poc_name, cat_uid, col, service_uids, true);
            for (i = 0; i < service_uids.length; i++) {
                service_uid = service_uids[i];
                var spec = specs[service_uid];
                if (spec) {
                    $("[name^='ar." + col + ".min." + service_uid + "']").val(spec.min);
                    $("[name^='ar." + col + ".max." + service_uid + "']").val(spec.max);
                    $("[name^='ar." + col + ".error." + service_uid + "']").val(spec.error);
                }
            }
        }
    }
}

function expand_default_categories() {
	$("th.prefill").click();
}

function ar_add_create_hidden_analysis(
        analysis_parent, elem_id, arnum, poc, cat, min, max, err, price, vat) {
    //console.log('ar_add_create_hidden_analysis: ' + arnum + ':' + poc);
    var new_item;
    new_item = '<input type="hidden" id="'+elem_id+'" value="'+elem_id+'" name="ar.'+arnum+'.Analyses:list:ignore_empty:record" class="cb overlay_field" arnum="'+arnum+'" checked="true"/>';
    analysis_parent.append(new_item);
    new_item = '<input type="hidden" uid="'+elem_id+'" name="ar.'+arnum+'.min.'+elem_id+'" value="'+min+'" class="spec_bit min overlay_field"/>';
    analysis_parent.append(new_item);
    new_item = '<input type="hidden" uid="'+elem_id+'" name="ar.'+arnum+'.max.'+elem_id+'" value="'+max+'" class="spec_bit max overlay_field"/>';
    analysis_parent.append(new_item);
    new_item = '<input type="hidden" uid="'+elem_id+'" name="ar.'+arnum+'.error.'+elem_id+'" value="'+err+'" class="spec_bit error overlay_field"/>';
    analysis_parent.append(new_item);
    new_item = '<input type="hidden" class="analysiscategory overlay_field" arnum="'+arnum+'" poc="'+poc+'" cat="'+cat+'"/>';
    analysis_parent.append(new_item);
    new_item = '<input type="hidden" id="'+elem_id+'_price" value="'+price+'" vat_amount="'+vat+'" class="overlay_field"/>';
    analysis_parent.append(new_item);
}

function ar_add_analyses_overlays() {
	var layout = $("input[id='layout']").val();
	if (layout == 'columns') {
		return;
		// Only if the view is the Analysis Request Add View
		if ($(".template-ar_add #analysisrequest_edit_form").length > 0) {

			// jarn.i18n.loadCatalog('bika');
			// var _ = window.jarn.i18n.MessageFactory("bika");
			// jarn.i18n.loadCatalog('bika');
			// var PMF = window.jarn.i18n.MessageFactory("plone");

			// var curDate = new Date();
			// var y = curDate.getFullYear();
			// var limitString = "1900:" + y;
			// var dateFormat = _("date_format_short_datepicker");
			// if (dateFormat == 'date_format_short_datepicker'){
			//  dateFormat = 'yy-mm-dd';
			// }

			ar_rename_elements();
			ar_referencewidget_lookups();
			ar_set_tabindexes();

			$("input[type=text]").prop("autocomplete", "off")

			$(".copyButton").live("click", copyButton);

			$("th[class^='analysiscategory']").click(clickAnalysisCategory);
            expand_default_categories();
            
			$("input[name^='Price']").live("change", recalc_prices);

			$("input[id*='_ReportDryMatter']").change(changeReportDryMatter);

			$(".spec_bit").live("change", function () {
				validate_spec_field_entry(this);
			});

			// AR Add/Edit ajax form submits
			var ar_edit_form = $("#analysisrequest_edit_form");
			if (ar_edit_form.ajaxForm !== undefined) {
				var options = {
					url: window.location.href.split("/portal_factory")[0] + "/analysisrequest_submit",
					dataType: "json",
					data: {"_authenticator": $("input[name='_authenticator']").val()},
					beforeSubmit: function () {
						$("input[class~='context']").prop("disabled", true);
					},
					success: function (responseText) {
						var destination;
						if (responseText.success !== undefined) {
							if (responseText.labels !== undefined) {
								destination = window.location.href
										.split("/portal_factory")[0];
								var ars = responseText.labels;
								var labelsize = responseText.labelsize;
								var q = "/sticker?size=" + labelsize + "&items=";
								q = q + ars.join(",");
								window.location.replace(destination + q);
							}
							else {
								destination = window.location.href
										.split("/portal_factory")[0];
								window.location.replace(destination);
							}
						}
						else {
							var msg = "";
							for (var error in responseText.errors) {
								var x = error.split(".");
								var e;
								if (x.length == 2) {
									e = x[1] + ", Column " + (+x[0]) + ": ";
								}
								else {
									e = "";
								}
								msg = msg + e + responseText.errors[error] + "<br/>";
							}
							window.bika.lims.portalMessage(msg);
							window.scroll(0, 0);
							$("input[class~='context']").prop("disabled", false);
						}
					},
					error: function (XMLHttpRequest, statusText) {
						window.bika.lims.portalMessage(statusText);
						window.scroll(0, 0);
						$("input[class~='context']").prop("disabled", false);
					}
				};
				$("#analysisrequest_edit_form").ajaxForm(options);
			}


			// these go here so that popup windows can access them in our context
			window.recalc_prices = recalc_prices;
			window.calculate_parts = calculate_parts;
			window.toggleCat = toggleCat;

			// Show only the contacts and CC from the selected Client
			$("[id$='_Client']").bind("change", function () {
				var col = this.id.split("_")[1];
				var element = $("#ar_" + col + "_Contact");
				var clientuid = $(this).attr("uid");
				applyComboFilter(element, "getParentUID", clientuid);
				element = $("#ar_" + col + "_CCContact");
				applyComboFilter(element, "getParentUID", clientuid);
				// Filter sample points by client
				element = $("#ar_" + col + "_SamplePoint");
				applyComboFilter(element, "getClientUID",
								 [clientuid,
								  $("#bika_setup").attr("bika_samplepoints_uid")]);
				// Filter template by client
				element = $("#ar_" + col + "_Template");
				applyComboFilter(element, "getClientUID",
								 [clientuid,
								  $("#bika_setup").attr("bika_artemplates_uid")]);
				// Filter Analysis Profile by client
				element = $("#ar_" + col + "_Profile");
				applyComboFilter(element, "getClientUID",
								 [clientuid,
								  $("#bika_setup").attr("bika_analysisprofiles_uid")]);
				// Filter Analysis Spec by client
				element = $("#ar_" + col + "_Specification");
				applyComboFilter(element, "getClientUID",
								 [clientuid,
								  $("#bika_setup").attr("bika_analysisspecs_uid")]);
			});
			// Iterate all the columns to filtrate by client
			for (var col = 0; col < parseInt($("#col_count").val(), 10); col++) {
				var element = $("#ar_" + col + "_Contact");
				var clientuid = $("#ar_" + col + "_Client_uid").val();
				// Initial value of contact list, set by the page's hidden ClientUID.
				applyComboFilter(element, "getParentUID", clientuid);
				element = $("#ar_" + col + "_CCContact");
				applyComboFilter(element, "getParentUID", clientuid);
				// Filter sample points by client
				element = $("#ar_" + col + "_SamplePoint");
				applyComboFilter(element, "getClientUID",
								 [clientuid,
								  $("#bika_setup").attr("bika_samplepoints_uid")]);
				// Filter template by client
				element = $("#ar_" + col + "_Template");
				applyComboFilter(element, "getClientUID",
								 [clientuid,
								  $("#bika_setup").attr("bika_artemplates_uid")]);
				// Filter Analysis Profile by client
				element = $("#ar_" + col + "_Profile");
				applyComboFilter(element, "getClientUID",
								 [clientuid,
								  $("#bika_setup").attr("bika_analysisprofiles_uid")]);
				// Filter Analysis Spec by client
				element = $("#ar_" + col + "_Specification");
				applyComboFilter(element, "getClientUID",
								 [clientuid,
								  $("#bika_setup").attr("bika_analysisspecs_uid")]);
			}

			var copy_from = window.location.href.split("copy_from=");
			if (copy_from.length > 1) {
				copy_from = copy_from[1].split("&")[0];
				copy_from = copy_from.split(",");
				for (var column = 0; column < copy_from.length; column++) {
					window.bika.ar_copy_from_col = column;
					$.ajaxSetup({async: false});
					window.bika.lims.jsonapi_read({
													  catalog_name: "uid_catalog",
													  UID: copy_from[column]
												  }, fill_column);
					$.ajaxSetup({async: true});
				}
			}
		}
	}
}

function analysesOverlaySubmitted(event){
    event.preventDefault();
    window.bika.lims.overlay_submitted = true;
    $('div.close').click();
    return true;
}

$(document).ready(function() {

    // Only if the view is the Analysis Request Add View
    if ($(".template-ar_add #analysisrequest_edit_form").length > 0) {

        ar_rename_elements();
        ar_referencewidget_lookups();
        ar_set_tabindexes();
        ar_add_analyses_overlays();

        $(".copyButton").live("click",  copyButton );
        $("#submit_analyses_button").live("click", analysesOverlaySubmitted);

        $("th[class^='analysiscategory']").live("click", clickAnalysisCategory);

        $("input[name^='Price']").live("change", recalc_prices );

        $("input[id*='_ReportDryMatter']").change(changeReportDryMatter);

        $("input[id*='_save_profile']").click(saveProfile);

        $(".spec_bit").live("change", function() {
            validate_spec_field_entry(this);
        });

        // AR Add/Edit ajax form submits
        var ar_edit_form = $("#analysisrequest_edit_form");
        if (ar_edit_form.ajaxForm !== undefined){
            var options = {
                url: window.location.href.split("/portal_factory")[0] + "/analysisrequest_submit",
                dataType: "json",
                data: {"_authenticator": $("input[name='_authenticator']").val()},
                beforeSubmit: function() {
                    $("input[class~='context']").prop("disabled",true);
                },
                success: function(responseText) {
                    var destination;
                    if(responseText.success !== undefined){
                        if(responseText.labels !== undefined){
                            destination = window.location.href
                                .split("/portal_factory")[0];
                            var ars = responseText.labels;
                            var labelsize = responseText.labelsize;
                            var q = "/sticker?size="+labelsize+"&items=";
                            q = q + ars.join(",");
                            window.location.replace(destination+q);
                        } else {
                            destination = window.location.href
                                .split("/portal_factory")[0];
                            window.location.replace(destination);
                        }
                    } else {
                        var msg = "";
                        for(var error in responseText.errors){
                            var x = error.split(".");
                            var e;
                            if (x.length == 2){
                                e = x[1] + ", AR " + (+x[0]) + ": ";
                            } else if (x.length == 1){
                                e = x[0]  + ": ";
                            } else {
                                e = "";
                            }
                            msg = msg + e + responseText.errors[error] + "<br/>";
                        }
                        window.bika.lims.portalMessage(msg);
                        window.scroll(0,0);
                        $("input[class~='context']").prop("disabled", false);
                    }
                },
                error: function(XMLHttpRequest, statusText) {
                    window.bika.lims.portalMessage(statusText);
                    window.scroll(0,0);
                    $("input[class~='context']").prop("disabled", false);
                }
            };
            $("#analysisrequest_edit_form").ajaxForm(options);
        }

        // these go here so that popup windows can access them in our context
        window.recalc_prices = recalc_prices;
        window.calculate_parts = calculate_parts;
        window.toggleCat = toggleCat;

        var layout = $("input[id='layout']").val();
        if (layout == 'columns') {
            // Show only the contacts and CC from the selected Client
            $("[id$='_Client']").bind("change", function() {
                var arnum = this.id.split("_")[1];
                var element = $("#ar_" + arnum + "_Contact");
                var clientuid = $(this).attr("uid");
                applyComboFilter(element, "getParentUID", clientuid);
                element = $("#ar_" + arnum + "_CCContact");
                applyComboFilter(element, "getParentUID", clientuid);
            });
            // Initial value of contact list, set by the page's hidden ClientUID.
            for (var arnum = 0; arnum < parseInt($("#ar_count").val(), 10); arnum++) {
                var element = $("#ar_" + arnum + "_Contact");
                var clientuid = $("#ar_" + arnum + "_Client_uid").val();
                applyComboFilter(element, "getParentUID", clientuid);
                element = $("#ar_" + arnum + "_CCContact");
                applyComboFilter(element, "getParentUID", clientuid);
            }
        } else {
            // Show only the contacts and CC from the selected Client
            $("[id$='_Client']").bind("change", function() {
                var element = $("#ar_Contact");
                var clientuid = $(this).attr("uid");
                applyComboFilter(element, "getParentUID", clientuid);
                element = $("#ar_CCContact");
                applyComboFilter(element, "getParentUID", clientuid);
                element = $("#ar_InvoiceContact");
                applyComboFilter(element, "getParentUID", clientuid);
            });
            //Initial value of contact list, set by the page's hidden ClientUID
            var element = $("#Contact");
            var clientuid = $("#Client_uid").val();
            applyComboFilter(element, "getParentUID", clientuid);
            element = $("#CCContact");
            applyComboFilter(element, "getParentUID", clientuid);
            element = $("#InvoiceContact");
            applyComboFilter(element, "getParentUID", clientuid);
        }

        var copy_from = window.location.href.split("copy_from=");
        if(copy_from.length > 1){
            copy_from = copy_from[1].split("&")[0];
            copy_from = copy_from.split(",");
            for (var arnum = 0; arnum < copy_from.length; arnum++) {
                window.bika.ar_copy_from_col = arnum;
                $.ajaxSetup({async:false});
                window.bika.lims.jsonapi_read({
                    catalog_name: "uid_catalog",
                    UID: copy_from[arnum]
                }, fill_column);
                $.ajaxSetup({async:true});
            }
        }

    }
});
}(jQuery));
