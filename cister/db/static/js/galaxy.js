$(document).ready(function() {

    //Legenda hover
    $('.legenda_table td').hover(
        function(){
            $(this).parent().addClass("highlight");
            $("."+$(this).attr("highlight")).addClass("highlight");
        },
        function(){
            $("."+$(this).attr("highlight")).removeClass("highlight");
            $(this).parent().removeClass("highlight");
        });

    //Pop up
    $('#popup_button').click(function (event){
        event.preventDefault();
        var url = $(this).attr("href");
        var windowName = "popUp";//$(this).attr("name");
        var windowSize = "width=400,height=400";
        window.open(url, windowName, windowSize);
    });

    if($("#cis_bases_result").length > 0){
        $("#cis_bases_result .location a").each(function(){
            loc = $(this).text().substring(0, 6);
            $(this).parent().attr("highlight", loc);
        });
    }
    $('#cis_bases_result td').hover(
    function(){
        $(this).parent().addClass("highlight");

        $("#galaxy td[region='"+$(this).attr("highlight")+"']").addClass("highlight");
    },
    function(){
        $("#galaxy td[region='"+$(this).attr("highlight")+"']").removeClass("highlight");
        $(this).parent().removeClass("highlight");
    });

});