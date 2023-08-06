function del_service(id){
  send_url("{%url 'delete_service' %}" + id, function(data){
    if(data == "OK") $("tr[i=" + id+"]").fadeOut()
    });
}

function del_service_form(id) {
  send_url("{%url 'delete_service' %}" + id, function(data){

    window.location="{%url 'home'%}"
    });
}