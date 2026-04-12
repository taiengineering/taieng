(function($) {
   "use strict";

    $(document).ready(function () {

        /**-------------------------------------------
         *  Navbar fix
         * -----------------------------------------*/
        $(document).on('click', '.navbar-area .navbar-nav li.menu-item-has-children>a', function (e) {
            e.preventDefault();
        })
       
        /*-------------------------------------
            menu
        -------------------------------------*/
        $('.navbar-area .menu').on('click', function() {
            $(this).toggleClass('open');
            $('.navbar-area .navbar-collapse').toggleClass('sopen');
        });
    
        // mobile menu
        if ($(window).width() < 992) {
            $(".in-mobile").clone().appendTo(".sidebar-inner");
            $(".in-mobile ul li.menu-item-has-children").append('<i class="fas fa-chevron-right"></i>');
            $('<i class="fas fa-chevron-right"></i>').insertAfter("");

            $(".menu-item-has-children a").on('click', function(e) {
                // e.preventDefault();

                $(this).siblings('.sub-menu').animate({
                    height: "toggle"
                }, 300);
            });
        }

        var menutoggle = $('.menu-toggle');
        var mainmenu = $('.navbar-nav');
        
        menutoggle.on('click', function() {
            if (menutoggle.hasClass('is-active')) {
                mainmenu.removeClass('menu-open');
            } else {
                mainmenu.addClass('menu-open');
            }
        });

        /*--------------------------------------------------
            select onput
        ---------------------------------------------------*/
        if ($('.single-select').length){
            $('.single-select').niceSelect();
        }


        /* -----------------------------------------------------
            Variables
        ----------------------------------------------------- */
        var leftArrow = '<i class="fa fa-arrow-left"></i>';
        var leftAngle = '<i class="fa fa-angle-left"></i>';
        var rightArrow = '<i class="fa fa-arrow-right"></i>';
        var rightAngle = '<i class="fa fa-angle-right"></i>';
        var backButton = '<button class="slide-arrow prev-arrow"><i class="fa fa-angle-left"></i></button>';
        var nextButton = '<button class="slide-arrow next-arrow"><i class="fa fa-angle-right"></i></button>';

    
        /*------------------------------------------------
            nx-slider
        ------------------------------------------------*/
        /**screenshot-slider**/
        $('.screenshot-slider').owlCarousel({
            loop:true,
            margin:0,
            nav:true,
            dots: false,
            center: true,
            smartSpeed:1500,
            navText: [leftArrow,rightArrow],
            responsive:{
                0:{
                    items:1
                },
                767:{
                    items:2,
                    center:false
                },
                768:{
                    items:3
                },
                1023:{
                    items:2,
                    center: false
                },
                1200:{
                    items:3
                }
            }
        })

        /**app-screen-slider**/
        $('.app-screenshot-slider').owlCarousel({
            loop:true,
            margin:30,
            nav:false,
            dots: true,
            center: true,
            smartSpeed:1500,
            navText: [leftArrow,rightArrow],
            responsive:{
                0:{
                    items:1
                },
                575:{
                    items:1
                },
                768:{
                    items:3
                },
                1024:{
                    items:3
                },
                1200:{
                    items:3
                }
            }
        })

        $('.screenshot-slider-2').owlCarousel({
            loop:true,
            margin:30,
            nav:true,
            dots: false,
            center: true,
            smartSpeed:1500,
            navText: [leftArrow,rightArrow],
            responsive:{
                0:{
                    items:1
                },
                575:{
                    items:1
                },
                768:{
                    items:3
                },
                1024:{
                    items:3
                },
                1200:{
                    items:3
                }
            }
        })

        /**team-slider**/
        $('.team-slider').owlCarousel({
            loop:true,
            margin: -20,
            nav:true,
            dots: false,
            smartSpeed:1500,
            navText: [leftArrow,rightArrow],
            responsive:{
                0:{
                    items:1
                },
                600:{
                    items:1
                },
                1000:{
                    items:3
                }
            }
        })

        /**service-slider**/
        $('.service-slider').owlCarousel({
            loop:true,
            margin: 30,
            nav:true,
            dots: false,
            smartSpeed:1500,
            navText: [leftArrow,rightArrow],
            responsive:{
                0:{
                    items:1
                },
                600:{
                    items:2
                },
                1000:{
                    items:3
                }
            }
        })

        /**client-slider**/
        $('.client-slider').owlCarousel({
            loop:true,
            margin: 0,
            nav:true,
            dots: false,
            smartSpeed:1500,
            navText: [leftArrow,rightArrow],
            responsive:{
                0:{
                    items:1
                },
                767:{
                    items:3
                },
                1000:{
                    items:5
                }
            }
        })

        /***testimonial-slider-2***/
        $('.testimonial-slider-for').slick({
            slidesToShow: 1,
            slidesToScroll: 1,
            fade: true,
            asNavFor: '.testimonial-slider-nav'
        });
        $('.testimonial-slider-nav').slick({
            slidesToShow: 5,
            slidesToScroll: 1,
            centerMode: true,
            centerPadding: 0,
            asNavFor: '.testimonial-slider-for',
            dots: false,
            arrows: true,
            prevArrow: backButton,
            nextArrow: nextButton,
            focusOnSelect: true,
            responsive: [
                {
                    breakpoint: 1024,
                    settings: {
                    slidesToShow: 3,
                    }
                },
                {
                    breakpoint: 575,
                    settings: {
                    slidesToShow: 2,
                    slidesToScroll: 2
                    }
                },
                {
                    breakpoint: 480,
                    settings: {
                    slidesToShow: 1,
                    slidesToScroll: 1
                    }
                }
            ]
        });

        /***testimonial-slider-3***/
        $('.testimonial-slider-for-2').slick({
            slidesToShow: 1,
            slidesToScroll: 1,
            speed: 1000,
            fade: true,
            dots: false,
            arrows: false,
            asNavFor: '.testimonial-slider-nav-2'
        });
        $('.testimonial-slider-nav-2').slick({
            slidesToShow: 1,
            slidesToScroll: 1,
            speed: 1000,
            centerMode: true,
            centerPadding: 0,
            asNavFor: '.testimonial-slider-for-2',
            dots: false,
            arrows: false,
            focusOnSelect: true,
        });
        $('a[data-slide]').click(function(e) {
            e.preventDefault();
            var slideno = $(this).data('slide');
            $('.testimonial-slider-nav-2').slick('slickGoTo', slideno - 1);
        });

        /* -------------------------------------------------------------
         fact counter
         ------------------------------------------------------------- */
        $('.counter').counterUp({
            delay: 15,
            time: 2000
        });

        /***pricing-switch & tab***/
        var e = document.getElementById("filt-monthly"),
            d = document.getElementById("filt-hourly"),
            t = document.getElementById("switcher"),
            m = document.getElementById("monthly"),
            y = document.getElementById("hourly");


        if ($('.pricing-tabs').length){
            e.addEventListener("click", function(){
              t.checked = false;
              e.classList.add("toggler--is-active");
              d.classList.remove("toggler--is-active");
              m.classList.remove("hide");
              y.classList.add("hide");
            });

            d.addEventListener("click", function(){
              t.checked = true;
              d.classList.add("toggler--is-active");
              e.classList.remove("toggler--is-active");
              m.classList.add("hide");
              y.classList.remove("hide");
            });

            t.addEventListener("click", function(){
              d.classList.toggle("toggler--is-active");
              e.classList.toggle("toggler--is-active");
              m.classList.toggle("hide");
              y.classList.toggle("hide");
            });
        }

        /*------------------------------------------------
            Magnific JS
        ------------------------------------------------*/
        $('.play-btn').magnificPopup({
            type: 'iframe',
            removalDelay: 260,
            mainClass: 'mfp-zoom-in',
        });
        $.extend(true, $.magnificPopup.defaults, {
            iframe: {
                patterns: {
                    youtube: {
                        index: 'youtube.com/',
                        id: 'v=',
                        src: 'https://www.youtube.com/embed/Wimkqo8gDZ0'
                    }
                }
            }
        });

        /*--------------------------------------------
            Search Popup
        ---------------------------------------------*/
        var bodyOvrelay =  $('#body-overlay');
        var searchPopup = $('#search-popup');

        $(document).on('click','#body-overlay',function(e){
            e.preventDefault();
        bodyOvrelay.removeClass('active');
            searchPopup.removeClass('active');
        });
        $(document).on('click','.search',function(e){
            e.preventDefault();
            searchPopup.addClass('active');
        bodyOvrelay.addClass('active');
        });

        /**featured-accordion**/
        $('.accordion-item').on('click',function(e){
            $('.accordion-item').removeClass('active');
            $(this).toggleClass('active');
        });

        /*------------------
           back to top
        ------------------*/
        $(document).on('click', '.back-to-top', function () {
            $("html,body").animate({
                scrollTop: 0
            }, 2000);
        });

    });

    $(window).on("scroll", function() {
        /*---------------------------------------
        sticky menu activation && Sticky Icon Bar
        -----------------------------------------*/

        var mainMenuTop = $(".navbar-area");
        if ($(window).scrollTop() >= 1) {
            mainMenuTop.addClass('navbar-area-fixed');
        }
        else {
            mainMenuTop.removeClass('navbar-area-fixed');
        }
        
        var ScrollTop = $('.back-to-top');
        if ($(window).scrollTop() > 1000) {
            ScrollTop.fadeIn(1000);
        } else {
            ScrollTop.fadeOut(1000);
        }
    });


    $(window).on('load', function () {

        /*-----------------
            preloader
        ------------------*/
        var preLoder = $("#preloader");
        preLoder.fadeOut(0);

        /*-----------------
            back to top
        ------------------*/
        var backtoTop = $('.back-to-top')
        backtoTop.fadeOut();

        /*---------------------
            Cancel Preloader
        ----------------------*/
        $(document).on('click', '.cancel-preloader a', function (e) {
            e.preventDefault();
            $("#preloader").fadeOut(500);
        });

    });


})(jQuery);