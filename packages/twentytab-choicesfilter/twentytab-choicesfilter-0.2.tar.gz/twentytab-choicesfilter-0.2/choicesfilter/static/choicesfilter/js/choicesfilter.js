jQuery(function($){

    $('#id_choicesfilter').on('click', function(){
        var array = $(this).parent().serializeArray();
        var qs = [];
        for(el in array){
            obj = array[el];
            if(obj.value != ""){
                qs.push(obj.name+"="+obj.value);
            }
        }
        window.location.href = "?"+qs.join('&');
    });

});