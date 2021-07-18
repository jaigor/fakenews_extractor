$(document).ready(function(){
  $("#id_f_source_type").change(function(){
    var selectedType = $(this).children("option:selected").val();
    if(selectedType == "1"){
        $("#f_entire_link").show();
    }
    else{
        $("#f_entire_link").hide();
    }
  });
  $("#id_s_source_type").change(function(){
    var selectedType = $(this).children("option:selected").val();
    if(selectedType == "1"){
        $("#s_entire_link").show();
    }
    else{
        $("#s_entire_link").hide();
    }
  });
});