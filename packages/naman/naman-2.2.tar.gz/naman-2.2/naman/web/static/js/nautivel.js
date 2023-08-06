


function validation(){

    jQuery.extend(jQuery.validator.messages, {
        required: "Campo requerido",
        remote: "Este campo no es valido",
        email: "El email no es valido",
        url: "La url no es correcta",
        esdate: "La fecha no es valida(dd/mm/yyyy)",
        number: "Numero no valido",
        digits: "Solo digitos",
        creditcard: "Numero de tarjeta no es valido",
        equalTo: "Los valores no son iguales",
        accept: "Expresion no valida",
        maxlength: jQuery.validator.format("Maximo {0} caracteres"),
        minlength: jQuery.validator.format("Minimo {0} caracteres"),
        rangelength: jQuery.validator.format("El valor tiene que tener entre {0} y {1} caracteres"),
        range: jQuery.validator.format("El valor debe ser entre {0} y {1}."),
        max: jQuery.validator.format("El valor debe ser menor o igual a {0}."),
        min: jQuery.validator.format("El valor debe ser mayor o igual a {0}."),
        conv: "Campo requerido"

    });
    $.validator.addMethod(
        "esdate",
        function(value, element) {
            // put your own logic here, this is just a (crappy) example
            var r = /^(\d{1,2})\/(\d{1,2})\/(\d{4})$/;
            var f = r.exec(value);delete r;
            if(!f){delete f, r;return false;}
            if(parseInt(f[1]) < 1 || parseInt(f[1]) > 31){delete f, r;return false}
            if(parseInt(f[2]) < 1 || parseInt(f[2]) > 12){delete f, r;return false}

            return true
        }
    );
    $.validator.addMethod(
        "gtdate",
        function(value, e){
            var r = /^(\d{1,2})\/(\d{1,2})\/(\d{4})$/;
            var f = r.exec(value);
            if(!f){delete f, r;return false;}
            var o = $($(e).attr("gtdate")).val();
            var d1 = new Date(f[3], f[2], f[1])
            var f = r.exec(o)
            if(!f){delete f, r, o, d1;return false;}
            var d2 = new Date(f[3], f[2], f[1])
            if(d1<=d2){delete r,f,o,d1,d2; return false;}
            delete r,f,o,d1,d2;
            return true;
        }, function(params, e) {
            return 'La fecha deber ser posterior a la ' + $(e).attr('gtdate_label')
            }
    );
    $.validator.addMethod(
        "conv",
        function(value, e){
            try{
                $("#id_u-groups option:selected").each(function(){
                    if(
                       ($(this).text() == "Alumnos a Distancia" ||
                       $(this).text() == "Alumnos presenciales") &&
                       ($(e).val() == "" || $(e).val() == undefined)
                       )throw("Bad conv")
                    })
            }catch(e){
                return false;
            }
            return true;
        });
    $("form").validate({})

}
