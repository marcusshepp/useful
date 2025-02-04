/*-----------------------------------------------------------------
Theme Name: Fresheat
Author: Gramentheme
Author URI: https://themeforest.net/user/gramentheme 
Version: 1.0.0 
Description: Fresheat food & Restaurant Html Template  <

-------------------------------------------------------------------
JS TABLE OF CONTENTS
-------------------------------------------------------------------

        01. Mobile Menu 
        02. Sidebar Toggle 
        03. Body Overlay  
        04. Sticky Header   
        05. Counterup 
        06. Wow Animation 
        07. Set Background Image Color & Mask  
        08. Banner Slider
        09. Best food items Slider 
        10. Testimonial Slider 
        11. Blog Slider 
        12. Gallery Slider 
        13. Popular Dishes Slider 
        14. Faq Slider     
        15. Client Slider 
        16. Popular Dishes Tab 
        17. MagnificPopup  view 
        18. Back to top   
        19. Progress Bar Animation 
        20. Mouse Cursor  
        21. Time Countdown  
        22. Range sliger 
        23. Select onput
        24. Quantity Plus Minus
        25. Search Popup
        26. Preloader   

------------------------------------------------------------------*/

(function ($) {
    "use strict";

    $(document).ready(function () {


        /*-----------------------------------
          01. Mobile Menu  
        -----------------------------------*/
        $('#mobile-menu').meanmenu({
            meanMenuContainer: '.mobile-menu',
            meanScreenWidth: "1199",
            meanExpand: ['<i class="far fa-plus"></i>'],
        });



        /*-----------------------------------
          02. Sidebar Toggle  
        -----------------------------------*/
        $(".offcanvas__close,.offcanvas__overlay").on("click", function () {
            $(".offcanvas__info").removeClass("info-open");
            $(".offcanvas__overlay").removeClass("overlay-open");
        });
        $(".sidebar__toggle").on("click", function () {
            $(".offcanvas__info").addClass("info-open");
            $(".offcanvas__overlay").addClass("overlay-open");
        });



        /*-----------------------------------
          03. Body Overlay 
        -----------------------------------*/
        $(".body-overlay").on("click", function () {
            $(".offcanvas__area").removeClass("offcanvas-opened");
            $(".df-search-area").removeClass("opened");;
            $(".body-overlay").removeClass("opened");
        });



        /*-----------------------------------
          04. Sticky Header 
        -----------------------------------*/
        $(window).scroll(function () {
            if ($(this).scrollTop() > 150) {
                $("#header-sticky").addClass("sticky open");
            } else {
                $("#header-sticky").removeClass("sticky open");
            }
        });



        /*-----------------------------------
          05. Counterup 
        -----------------------------------*/
        $(".counter-number").counterUp({
            delay: 10,
            time: 1000,
        });



        /*-----------------------------------
          06. Wow Animation 
        -----------------------------------*/
        new WOW().init();



        /*-----------------------------------
          07. Set Background Image & Mask   
        -----------------------------------*/
        if ($("[data-bg-src]").length > 0) {
            $("[data-bg-src]").each(function () {
                var src = $(this).attr("data-bg-src");
                $(this).css("background-image", "url(" + src + ")");
                $(this).removeAttr("data-bg-src").addClass("background-image");
            });
        }


        if ($('[data-mask-src]').length > 0) {
            $('[data-mask-src]').each(function () {
                var mask = $(this).attr('data-mask-src');
                $(this).css({
                    'mask-image': 'url(' + mask + ')',
                    '-webkit-mask-image': 'url(' + mask + ')'
                });
                $(this).addClass('bg-mask');
                $(this).removeAttr('data-mask-src');
            });
        };



        /*-----------------------------------
           08. Banner Slider
        -----------------------------------*/
        // Function to initialize Swiper with animation
        function initializeSlider(sliderClass, nextBtnClass, prevBtnClass, paginationClass) {
            const sliderInit = new Swiper(sliderClass, {
                loop: true,
                slidesPerView: 1,
                effect: "fade",
                speed: 4000,
                autoplay: {
                    delay: 5000,
                    disableOnInteraction: false,
                },
                navigation: {
                    nextEl: nextBtnClass,
                    prevEl: prevBtnClass,
                },
                pagination: {
                    el: paginationClass, // Use the passed paginationClass
                    clickable: true,
                    renderBullet: function (index, className) {
                        return '<span class="' + className + '">' + (index + 1) + '</span>';
                    },
                },
            });

            function animated_swiper(selector, init) {
                const animated = function animated() {
                    $(selector + " [data-animation]").each(function () {
                        let anim = $(this).data("animation");
                        let delay = $(this).data("delay");
                        let duration = $(this).data("duration");
                        $(this)
                            .removeClass("anim" + anim)
                            .addClass(anim + " animated")
                            .css({
                                webkitAnimationDelay: delay,
                                animationDelay: delay,
                                webkitAnimationDuration: duration,
                                animationDuration: duration,
                            })
                            .one("animationend", function () {
                                $(this).removeClass(anim + " animated");
                            });
                    });
                };
                animated();
                init.on("slideChange", function () {
                    $(selector + " [data-animation]").removeClass("animated");
                });
                init.on("slideChange", animated);
            }

            animated_swiper(sliderClass, sliderInit);
        }

        // Initialize multiple sliders
        initializeSlider(".banner-slider", ".arrow-prev", ".arrow-next", ".pagination-class");
        initializeSlider(".banner2-slider", ".arrow-prev2", ".arrow-next2", ".pagination-class2");
        initializeSlider(".banner3-slider", ".arrow-prev3", ".arrow-next3", ".pagination-class3");



        /*-----------------------------------
            09. Best food items Slider     
        -----------------------------------*/
        if ($('.bestFoodItems-slider').length > 0) {
            const bestFoodSlider = new Swiper(".bestFoodItems-slider", {
                spaceBetween: 30,
                speed: 2000,
                loop: true,
                autoplay: {
                    delay: 2000,
                    disableOnInteraction: false,
                },
                breakpoints: {
                    1499: {
                        slidesPerView: 4,
                    },
                    1399: {
                        slidesPerView: 4,
                    },
                    1199: {
                        slidesPerView: 4,
                    },
                    991: {
                        slidesPerView: 4,
                    },
                    767: {
                        slidesPerView: 3,
                    },
                    575: {
                        slidesPerView: 1,
                    },
                    0: {
                        slidesPerView: 1,
                    },
                },
                pagination: {
                    el: '.bestFoodItems-pagination',
                    clickable: true,
                    bulletClass: 'swiper-pagination-bullet', // Bullet class
                    bulletActiveClass: 'swiper-pagination-bullet-active', // Active bullet class
                },
            });
        }



        /*-----------------------------------
            10. Testimonial Slider     
        -----------------------------------*/
        if ($('.testmonialSliderOne').length > 0) {
            const testmonialSliderOne = new Swiper(".testmonialSliderOne", {
                spaceBetween: 30,
                speed: 2000,
                loop: true,
                autoplay: {
                    delay: 2000,
                    disableOnInteraction: false,
                },
                navigation: {
                    nextEl: ".arrow-next",
                    prevEl: ".arrow-prev",
                },
                breakpoints: {
                    575: {
                        slidesPerView: 1,
                    },
                    0: {
                        slidesPerView: 1,
                    },
                },
            });
        }

        if ($('.testimonialSliderTwo').length > 0) {
            const testimonialSliderTwo = new Swiper(".testimonialSliderTwo", {
                spaceBetween: 30,
                speed: 2000,
                loop: true,
                autoplay: {
                    delay: 2000,
                    disableOnInteraction: false,
                },
                navigation: {
                    nextEl: ".arrow-next",
                    prevEl: ".arrow-prev",
                },
                breakpoints: {
                    575: {
                        slidesPerView: 1,
                    },
                    0: {
                        slidesPerView: 1,
                    },
                },
            });
        }

        if ($('.testmonialSliderThree').length > 0) {
            const testmonialSliderThree = new Swiper(".testmonialSliderThree", {
                spaceBetween: 30,
                speed: 2000,
                loop: true,
                autoplay: {
                    delay: 2000,
                    disableOnInteraction: false,
                },
                navigation: {
                    nextEl: ".arrow-next",
                    prevEl: ".arrow-prev",
                },
                breakpoints: {
                    767: {
                        slidesPerView: 2,
                    },
                    575: {
                        slidesPerView: 1,
                    },
                    0: {
                        slidesPerView: 1,
                    },
                },
            });
        }



        /*-----------------------------------
            11. Blog Slider     
        -----------------------------------*/
        if ($('.blogSliderOne').length > 0) {
            const blogSliderOne = new Swiper(".blogSliderOne", {
                spaceBetween: 30,
                speed: 2000,
                loop: true,
                autoplay: {
                    delay: 2000,
                    disableOnInteraction: false,
                },
                navigation: {
                    nextEl: ".arrow-next",
                    prevEl: ".arrow-prev",
                },
                breakpoints: {
                    1199: {
                        slidesPerView: 3,
                    },
                    767: {
                        slidesPerView: 2,
                    },
                    575: {
                        slidesPerView: 1,
                    },
                    0: {
                        slidesPerView: 1,
                    },
                },
            });
        }



        /*-----------------------------------
           12. Gallery Slider     
       -----------------------------------*/
        if ($('.gallerySliderOne').length > 0) {
            const gallerySliderOne = new Swiper(".gallerySliderOne", {
                spaceBetween: 30,
                speed: 2000,
                loop: true,
                centerSlides: true,
                autoplay: {
                    delay: 2000,
                    disableOnInteraction: false,
                },
                breakpoints: {
                    992: {
                        slidesPerView: 4,
                    },
                    767: {
                        slidesPerView: 3,
                    },
                    575: {
                        slidesPerView: 2,
                    },
                    0: {
                        slidesPerView: 1,
                    },
                },
            });
        }



        /*-----------------------------------
            13. Popular Dishes Slider     
        -----------------------------------*/
        if ($('.popularDishesSliderOne').length > 0) {
            const popularDishesSliderOne = new Swiper(".popularDishesSliderOne", {
                spaceBetween: 30,
                speed: 2000,
                loop: true,
                centerSlides: true,
                autoplay: {
                    delay: 2000,
                    disableOnInteraction: false,
                },
                breakpoints: {
                    992: {
                        slidesPerView: 3,
                    },
                    767: {
                        slidesPerView: 3,
                    },
                    575: {
                        slidesPerView: 2,
                    },
                    0: {
                        slidesPerView: 1,
                    },
                },
            });
        }


        /*-----------------------------------
            14. Faq Slider     
        -----------------------------------*/
        if ($('.faq-slider').length > 0) {
            const faqSlider = new Swiper(".faq-slider", {
                spaceBetween: 30,
                speed: 2000,
                loop: true,
                centerSlides: true,
                autoplay: {
                    delay: 2000,
                    disableOnInteraction: false,
                },
                navigation: {
                    nextEl: ".arrow-next",
                    prevEl: ".arrow-prev",
                },
            });
        }



        /*-----------------------------------
            15. Client Slider     
        -----------------------------------*/
        if ($('.clientSliderOne').length > 0) {
            const popularDishesSliderOne = new Swiper(".clientSliderOne", {
                spaceBetween: 30,
                speed: 2000,
                loop: true,
                centerSlides: true,
                autoplay: {
                    delay: 2000,
                    disableOnInteraction: false,
                },
                breakpoints: {
                    992: {
                        slidesPerView: 6,
                    },
                    767: {
                        slidesPerView: 5,
                    },
                    575: {
                        slidesPerView: 3,
                    },
                    0: {
                        slidesPerView: 1,
                    },
                },
            });
        }



        /*-----------------------------------
            16. Popular Dishes Tab       
        -----------------------------------*/
        $(document).ready(function () {
            // Function to deactivate all tabs
            function deactivateAllTabs() {
                $('.nav-link').removeClass('active').attr('aria-selected', 'false');
                $('.tab-pane').removeClass('active show');
            }

            // Add event listeners to all tabs
            $('.nav-link').on('click', function () {
                deactivateAllTabs(); // Deactivate all tabs
                $(this).addClass('active').attr('aria-selected', 'true'); // Activate the clicked tab

                const target = $(this).data('bs-target');
                if (target) {
                    $(target).addClass('active show'); // Show the corresponding tab content
                }
            });
        });



        /*-----------------------------------
            17. MagnificPopup  view    
        -----------------------------------*/
        $(".popup-video").magnificPopup({
            type: "iframe",
            removalDelay: 260,
            mainClass: 'mfp-zoom-in',
        });

        $(".img-popup").magnificPopup({
            type: "image",
            gallery: {
                enabled: true,
            },
        });




        /*-----------------------------------
           18. Back to top    
        -----------------------------------*/
        $(window).scroll(function () {
            if ($(this).scrollTop() > 20) {
                $("#back-top").addClass("show");
            } else {
                $("#back-top").removeClass("show");
            }
        });
        $("#back-top").click(function () {
            $("html, body").animate({ scrollTop: 0 }, 800);
            return false;
        });



        /*-----------------------------------
            19. Progress Bar Animation 
        -----------------------------------*/
        $('.progress-bar').each(function () {
            var $this = $(this);
            var progressWidth = $this.attr('style').match(/width:\s*(\d+)%/)[1] + '%';

            $this.waypoint(function () {
                $this.css({
                    '--progress-width': progressWidth,
                    'animation': 'animate-positive 1.8s forwards',
                    'opacity': '1'
                });
            }, { offset: '75%' });
        });



        /*-----------------------------------
            20. Mouse Cursor    
        -----------------------------------*/
        function mousecursor() {
            if ($("body")) {
                const e = document.querySelector(".cursor-inner"),
                    t = document.querySelector(".cursor-outer");
                let n,
                    i = 0,
                    o = !1;
                (window.onmousemove = function (s) {
                    o ||
                        (t.style.transform =
                            "translate(" + s.clientX + "px, " + s.clientY + "px)"),
                        (e.style.transform =
                            "translate(" + s.clientX + "px, " + s.clientY + "px)"),
                        (n = s.clientY),
                        (i = s.clientX);
                }),
                    $("body").on("mouseenter", "a, .cursor-pointer", function () {
                        e.classList.add("cursor-hover");
                        t.classList.add("cursor-hover");
                    }),
                    $("body").on("mouseleave", "a, .cursor-pointer", function () {
                        ($(this).is("a") && $(this).closest(".cursor-pointer").length) ||
                            (e.classList.remove("cursor-hover"),
                                t.classList.remove("cursor-hover"));
                    }),
                    (e.style.visibility = "visible"),
                    (t.style.visibility = "visible");
            }
        }
        $(function () {
            mousecursor();
        });




        /*-----------------------------------
            21. Time Countdown  
        -----------------------------------*/
        // Set the end date and time for the countdown
        var countdownDate = new Date("2025-12-31T23:59:59").getTime();

        // Update the countdown every second
        var countdownFunction = setInterval(function () {

            // Get current date and time
            var now = new Date().getTime();

            // Calculate the remaining time
            var distance = countdownDate - now;

            // Calculate days, hours, minutes, and seconds
            var days = Math.floor(distance / (1000 * 60 * 60 * 24));
            var hours = Math.floor((distance % (1000 * 60 * 60 * 24)) / (1000 * 60 * 60));
            var minutes = Math.floor((distance % (1000 * 60 * 60)) / (1000 * 60));
            var seconds = Math.floor((distance % (1000 * 60)) / 1000);

            // Display the result in the elements with corresponding IDs
            $('#days').text(days < 10 ? '0' + days : days);
            $('#hours').text(hours < 10 ? '0' + hours : hours);
            $('#minutes').text(minutes < 10 ? '0' + minutes : minutes);
            $('#seconds').text(seconds < 10 ? '0' + seconds : seconds);

            // If the countdown is over, clear the interval and display "EXPIRED"
            if (distance < 0) {
                clearInterval(countdownFunction);
                $(".clock-wrapper").html("EXPIRED");
            }

        }, 1000);



        /*-----------------------------------
            22. Range slider 
        -----------------------------------*/
        function getVals() {
            let parent = this.parentNode;
            let slides = parent.getElementsByTagName("input");
            let slide1 = parseFloat(slides[0].value);
            let slide2 = parseFloat(slides[1].value);
            if (slide1 > slide2) {
                let tmp = slide2;
                slide2 = slide1;
                slide1 = tmp;
            }

            let displayElement = parent.getElementsByClassName("rangeValues")[0];
            displayElement.innerHTML = "$" + slide1 + " - $" + slide2;
        }

        window.onload = function () {
            let sliderSections = document.getElementsByClassName("range-slider");
            for (let x = 0; x < sliderSections.length; x++) {
                let sliders = sliderSections[x].getElementsByTagName("input");
                for (let y = 0; y < sliders.length; y++) {
                    if (sliders[y].type === "range") {
                        sliders[y].oninput = getVals;
                        sliders[y].oninput();
                    }
                }
            }
        }

        progressBar: () => {
            const pline = document.querySelectorAll(".progressbar.line");
            const pcircle = document.querySelectorAll(".progressbar.semi-circle");
            pline.forEach(e => {
                const line = new ProgressBar.Line(e, {
                    strokeWidth: 6,
                    trailWidth: 6,
                    duration: 3000,
                    easing: 'easeInOut',
                    text: {
                        style: {
                            color: 'inherit',
                            position: 'absolute',
                            right: '0',
                            top: '-30px',
                            padding: 0,
                            margin: 0,
                            transform: null
                        },
                        autoStyleContainer: false
                    },
                    step: (state, line) => {
                        line.setText(Math.round(line.value() * 100) + ' %');
                    }
                });
                let value = e.getAttribute('data-value') / 100;
                new Waypoint({
                    element: e,
                    handler: function () {
                        line.animate(value);
                    },
                    offset: 'bottom-in-view',
                })
            });
            pcircle.forEach(e => {
                const circle = new ProgressBar.SemiCircle(e, {
                    strokeWidth: 6,
                    trailWidth: 6,
                    duration: 2000,
                    easing: 'easeInOut',
                    step: (state, circle) => {
                        circle.setText(Math.round(circle.value() * 100));
                    }
                });
                let value = e.getAttribute('data-value') / 100;
                new Waypoint({
                    element: e,
                    handler: function () {
                        circle.animate(value);
                    },
                    offset: 'bottom-in-view',
                })
            });
        }

        const rangeInput = document.querySelectorAll(".range-input input"),
            priceInput = document.querySelectorAll(".price-input input"),
            range = document.querySelector(".slider .progress");
        let priceGap = 1000;

        priceInput.forEach((input) => {
            input.addEventListener("input", (e) => {
                let minPrice = parseInt(priceInput[0].value),
                    maxPrice = parseInt(priceInput[1].value);

                if (maxPrice - minPrice >= priceGap && maxPrice <= rangeInput[1].max) {
                    if (e.target.className === "input-min") {
                        rangeInput[0].value = minPrice;
                        range.style.left = (minPrice / rangeInput[0].max) * 100 + "%";
                    } else {
                        rangeInput[1].value = maxPrice;
                        range.style.right = 100 - (maxPrice / rangeInput[1].max) * 100 + "%";
                    }
                }
            });
        });

        rangeInput.forEach((input) => {
            input.addEventListener("input", (e) => {
                let minVal = parseInt(rangeInput[0].value),
                    maxVal = parseInt(rangeInput[1].value);

                if (maxVal - minVal < priceGap) {
                    if (e.target.className === "range-min") {
                        rangeInput[0].value = maxVal - priceGap;
                    } else {
                        rangeInput[1].value = minVal + priceGap;
                    }
                } else {
                    priceInput[0].value = minVal;
                    priceInput[1].value = maxVal;
                    range.style.left = (minVal / rangeInput[0].max) * 100 + "%";
                    range.style.right = 100 - (maxVal / rangeInput[1].max) * 100 + "%";
                }
            });
        });


        /*--------------------------------------------------
          23. Select onput
      ---------------------------------------------------*/
        if ($('.single-select').length) {
            $('.single-select').niceSelect();
        }



        /*--------------------------------------------------
          24. Quantity Plus Minus
      ---------------------------------------------------*/
        $(".quantity-plus").each(function () {
            $(this).on("click", function (e) {
                e.preventDefault();
                var $qty = $(this).siblings(".qty-input");
                var currentVal = parseInt($qty.val());
                if (!isNaN(currentVal)) {
                    $qty.val(currentVal + 1);
                }
            });
        });

        $(".quantity-minus").each(function () {
            $(this).on("click", function (e) {
                e.preventDefault();
                var $qty = $(this).siblings(".qty-input");
                var currentVal = parseInt($qty.val());
                if (!isNaN(currentVal) && currentVal > 1) {
                    $qty.val(currentVal - 1);
                }
            });
        });



        /*--------------------------------------------------
          25. Search Popup
      ---------------------------------------------------*/
        const $searchWrap = $(".search-wrap");
        const $navSearch = $(".nav-search");
        const $searchClose = $("#search-close");

        $(".search-trigger").on("click", function (e) {
            e.preventDefault();
            $searchWrap.animate({ opacity: "toggle" }, 500);
            $navSearch.add($searchClose).addClass("open");
        });

        $(".search-close").on("click", function (e) {
            e.preventDefault();
            $searchWrap.animate({ opacity: "toggle" }, 500);
            $navSearch.add($searchClose).removeClass("open");
        });

        function closeSearch() {
            $searchWrap.fadeOut(200);
            $navSearch.add($searchClose).removeClass("open");
        }

        $(document.body).on("click", function (e) {
            closeSearch();
        });

        $(".search-trigger, .main-search-input").on("click", function (e) {
            e.stopPropagation();
        });

    }); // End Document Ready Function


    /*-----------------------------------
        26. Preloader   
    -----------------------------------*/

    function loader() {
        $(window).on('load', function () {
            // Animate loader off screen
            $(".preloader").addClass('loaded');
            $(".preloader").delay(600).fadeOut();
        });
    }

    loader();


})(jQuery); // End jQuery

