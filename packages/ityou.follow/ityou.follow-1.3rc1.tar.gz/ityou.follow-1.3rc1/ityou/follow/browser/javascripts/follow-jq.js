$(document).ready(
	function () {
		$("#follow-viewlet").find("a").click(function follow(e){
                e.preventDefault();
				$(this).append($("#kss-spinner").html());
				if($("#follow").is(":visible"))
				{
					add_or_remove = "false";
				}
				else if($("#unfollow").is(":visible"))
				{
					add_or_remove = "true";
				}
		        	$.getJSON("@@ajax-follow", {'action':"set_following", 'fid': $("#author_id").text(), remove : add_or_remove},
		        		function(data) {
		        			if (data) {
		        				$("#follow").toggle();
		        				$("#unfollow").toggle();
		        				$("#follow-viewlet").find("img").detach();
		        			};
		        	});
		});
        // === END ======================================
    }
); 



