$(document).ready(function() {

    if($("#cis_bases_result").length > 0){
        $("#cis_bases_result .location a").each(function(){
            loc = $(this).text().substring(0, 9);
            $(this).parent().attr("highlight", loc);
        });
    }
    $('#cis_bases_result td').hover(
        function(){
            $(this).parent().addClass("highlight");
            $("#region img[system='"+$(this).attr("highlight")+"']").addClass("highlight");
        },
        function(){
            $("#region img[system='"+$(this).attr("highlight")+"']").removeClass("highlight");
            $(this).parent().removeClass("highlight");
        });

});