$(document).ready(function() {

    $("#cis_base_filters a").click(function(){
        $.cookie('search', '',{
            path:'/'
        });
    });
    $("#cis_fleet_filters a").click(function(){
        $.cookie('search', '',{
            path:'/'
        });
    });


    $(".guild_blobdetail th").click(function(){
       var gid = $(this).parent().parent().parent().parent().attr("id");
       console.log("Gid::: " + gid);
       $("."+gid).toggle();
    });
});