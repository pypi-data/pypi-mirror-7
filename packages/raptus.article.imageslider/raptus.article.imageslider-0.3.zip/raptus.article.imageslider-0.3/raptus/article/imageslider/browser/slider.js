/*
* follows best practices from http://net.tutsplus.com/tutorials/javascript-ajax/principles-of-maintainable-javascript/
*/


//IE Fallback if console does not exist
if(!window.console) {console={}; console.log = function(){};}


//our namespace
var raptus = raptus || {};


(function($) {
    /*
    * private scope
    */


    raptus.imageslider = (function () {


        var DEBUG = true;

        // available after initialization
        var api = null;

        var log = function(data) {
            if (DEBUG) {console.log("imageslider", data);}
        };


        var resizeScrollable = function(scrollable) {
            /*
             * resize the width of all list-items to the width of the scrollable
             * and set the height of the scrollable to the height of the biggest
             * list-item.
             * (idea taken from http://cooshtee.com/blog/2013/04/making-jquery-tools-scrollable-responsive/)
             */

            var scrollableWidth = scrollable.width();
            scrollable.find('li').css('width', scrollableWidth);


            // find highest child element and use it's height
            // taken from http://stackoverflow.com/a/13332924/810427
            function thisHeight(){
                return $(this).height();
            }
            var bannerHeight = Math.max.apply(Math, scrollable.find('li').map(thisHeight))
            scrollable.css('height', bannerHeight);

            // Use the api to reposition the slide once it's been resized (if the browser is resized)
            var currentSlide = api.getIndex();
            api.seekTo(currentSlide, 50);
        };



        var initScrollable = function (slider, autoscroll) {
            /**
             * initialize the .scrollable within the container slider as a
             * responsive scrollable
             *
             * set autoscroll to a dictionary containing autoscroll
             * configuration parameters to enable the autoscroll plugin
             *
             * returns the api so additional configuration can be done
             * after initialization.
             * (http://jquerytools.org/documentation/scrollable/#api)
             *
             * also exposes the api as raptus.imageslider.api
             *
             * eg:
             * var api = initScrollable($('.imageSliderTeaser'));
             * api.getConf()['speed'] = 200;
             */

            if (typeof interval === 'undefined') { interval = 1000; }

            var scrollable = slider.find('.scrollable');



            //Initiate scrollable as normal
            api = scrollable.scrollable().data('scrollable');


            // move to the slide (optionally given in the url)
            seekScrollable();

            // Call our responsive function
            resizeScrollable(scrollable);

            // Call our responsive function every time the browser window is resized
            slider.resize(function() {
                resizeScrollable(scrollable);
            });

            // add navigator (useless in case template has no div.navi)
            scrollable.navigator();

            if (autoscroll && (api.getSize()>1) ) {
                log("more than one item and autoscrolling activated");
                api.getConf()['circular'] = true;
                scrollable.autoscroll(autoscroll);
            }


            return api;

        };

        /**
         * if an anchor is given in the url, move the scrollable given as param
         * api to the given position
         *
         * example anchor: #story-1
         * will call api.seekTo(0)
         */
        var seekScrollable = function() {
            var hash = null;
            if(window.location.hash && api != null) {
                //http://stackoverflow.com/a/13703384/810427
                //http://stackoverflow.com/a/6682514/810427
                var hash = window.location.hash.substring(1);
                console.log('got positional argument for scollable: ' + hash)
            } else {
                return;
            }
            var pos = parseInt(hash.replace(/slide-([0-9]*)\S*/, '$1'));
            api.seekTo(pos-1, 0);
        }

        var init = function () {
            //initScrollable($('.imageSliderTeaser'));
        };



        // Return the public facing methods for the App
        return {
            init: init,
            initScrollable: initScrollable
        };

    }());

    $(function() {
        /*
        * on document ready
        */
        raptus.imageslider.init();

    });

})(jQuery);