function show_vconfig_form() {
    send_url(
        "{%url 'vlanconfig'%}",
        function(data) {
            $("#iface_div").html(data)
            document.getElementById("nvconfig_btn").onclick=null;
            $("#nvconfig_btn").click(function(){save_vlanc();})
            $("#nvconfig_btn").html("Generate")
            $("#niface_btn").fadeOut();$("#niface_btn").remove()
        },
        "machine=" + $("#obj_id").attr("i")
    )
}

function save_vlanc(){

    init_progress();
    data = {
            machine: $("#id_machine").val(),
            needs_backup: $("#id_needs_backup").is(':checked') ? "checked" : "",
            needs_management: $("#id_needs_management").is(':checked')  ? "checked": "",
            csrfmiddlewaretoken: $("#iface_div input[name=csrfmiddlewaretoken]").val()
        }
    $.ajax({
        type: "POST",
        url: "{%url 'vlanconfig'%}",
        data: data,
        beforeSend: function(){progress(30)},
        success: function(data)
        {
            $("#iface_div").html(data);
            toggle_nvlanc_btn()
            show_niface_btn()
        },
        complete: function(){$("[title!=undefined]").tooltip({"animation": "true"});progress(100)},
        error: function(ob){progress(100);show_msg(ob.responseText)}
    });

    return false;

}
