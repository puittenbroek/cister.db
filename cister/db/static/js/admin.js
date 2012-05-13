admin_space = {

    text_extraction : function (node) {
        title = node.title;
        if (title != "") {
           title = title.split(" ")[0];
           return title;
        }  else {
	   return node.innerHTML;
        }
    },


    init_sortable : function () {
        $(".tablesorter").tablesorter({
        textExtraction : admin_space.text_extraction,
	});
    },
    init_tabs : function () {
        $(".tabs").tabs({ selected: 1 });
    }
}




$(document).ready(function() {
    admin_space.init_sortable();
    admin_space.init_tabs();
});
