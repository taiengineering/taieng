(function ($) {
    "use strict";

    //jQuery to collapse the navbar on scroll
    $(window).scroll(function() {
        if ($(".navbar").offset().top > 100) {
            $(".navbar-fixed-top").addClass("top-nav-collapse");
        } else {
            $(".navbar-fixed-top").removeClass("top-nav-collapse");
        }
    });

    /**---------------------------------------
         *  type js
        * -------------------------------------*/
	 if($('.typed').length){
		var typed = $(".typed");
		$(function() {
			typed.typed({
				strings: ["SaaS Landing.", "App Landing.", "Software Landing"],
				typeSpeed: 130,
				loop: true
			});
		});
	}
    /*------------------
        back to top
    ------------------*/
    var btn = $('#back-to-top');

    $(window).scroll(function() {
    if ($(window).scrollTop() > 300) {
        btn.addClass('show');
    } else {
        btn.removeClass('show');
    }
    });

    btn.on('click', function(e) {
    e.preventDefault();
    $('html, body').animate({scrollTop:0}, '300');
    });

})(jQuery);
