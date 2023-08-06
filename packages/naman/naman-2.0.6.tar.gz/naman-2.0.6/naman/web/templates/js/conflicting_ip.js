function show_conflictip_form() {
    var d = document.createElement("div")
    $(d).attr("id", "ci_modal")
    $("body").append($(d))
    $(d).addClass("modal fade in")
    load_url("#ci_modal", "{%url 'conflictingip_modal'%}")
    $(d).modal({show: true, keyboard: true})
    $(d).on('hidden.bs.modal', function () {$(d).remove()})
    delete d;
}

function save_conflictingip() {
    init_progress()
    $.ajax({
        url: "{%url 'conflictingip_modal'%}",
        method: "POST",
        data: $("#fconflictingip").serialize(),
        beforeSend: function(){progress(30)},
        success: function(data, ts, xhr){
            if (data == "OK") {
                $("#close_ci_modal_btn").click();
                return
            }
            $("#ci_modal").html(data)
        },
        complete: function(){$("[title!=undefined]").tooltip({"animation": "true"});progress(100)},
        error: function(ob){show_msg(ob.responseText)}
    });
    drop_progress();
}
