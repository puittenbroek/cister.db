admin_space = {

    init_sortable : function () {
        $(".tablesorter").tablesorter();
    },
    init_tabs : function () {
        $(".tabs").tabs({ selected: 1 });
    }
}




$(document).ready(function() {

    admin_space.init_sortable();
    admin_space.init_tabs();

});