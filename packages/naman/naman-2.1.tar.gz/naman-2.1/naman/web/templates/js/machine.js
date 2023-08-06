function del_machine(id){
  send_url("{%url 'delete_machine' %}" + id, function(data){
    if(data == "OK") $("tr[i=" + id+"]").fadeOut()
    });
}

function del_machine_form(id) {
  send_url("{%url 'delete_machine' %}" + id, function(data){

    window.location="{%url 'home'%}"
    });
}
