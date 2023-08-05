/*******************************************************************
 *                  sample.js
 *******************************************************************/
;(function (exports) {
    'use strict';

    /************************************************************
     *                  Sample gclass.
     ************************************************************/

    /********************************************
     *      Auxiliary
     ********************************************/

    /********************************************
     *      Configure events
     ********************************************/
    function configure_dom_events(self) {
        /*
         *  Get our DOM elements
         */
        self.$button = $('#mybutton');

        if (!self.$button.length) {
            alert("Fallo interno sessions.js");
        }

        /*
         *  Configure events
         *  Convert DOM events into gobj events.
         */
        self.$button.on("click", self, function(event){
            event.stopImmediatePropagation();
            event.preventDefault();
            var self = event.data;
            var kw = {
            };
            self.send_event(self, 'EV_EVENT', kw);
        });

        return 1;
    }


    /***************************************************************
     *      Actions
     ***************************************************************/
    function ac_action(self, event) {
        data = event.kw.data;
        return 1;
    }

    /********************************************
     *      Config
     ********************************************/
    var APLIC_CONFIG = {
        // Id of dom element parent. It has preference over parent gobj.
        parent_dom_id: ''
    };

    /********************************************
     *      Machine
     ********************************************/
    var APLIC_FSM = {
        'event_list': [
            'EV_EVENT: top input: top output'
        ],
        'state_list': [
            'ST_IDLE'
            ],
        'machine': {
            'ST_IDLE':
            [
                ['EV_EVENT',        ac_action,      undefined]
            ]
        }
    }

    /********************************************
     *      Class
     ********************************************/
    var Sample = GObj.__makeSubclass__();
    var proto = Sample.prototype; // Easy access to the prototype
    proto.__init__= function(name, parent, kw, gaplic) {
        this.name = name || '';  // set before super(), to put the same smachine name
        this.gclass_name = 'Sample';
        GObj.prototype.__init__.call(this, APLIC_FSM, APLIC_CONFIG);
        __update_dict__(this.config, kw || {});
        return this;
    };
    proto.start_up= function() {
        //**********************************
        //  start_up
        //**********************************
        var self = this;

        configure_dom_events(self);
    }

    proto.go_out= function() {
        //************************************************
        //  Finish zone.
        //  In this point, all childs
        //  and subscriptions are already deleted.
        //************************************************
        var self = this;
    }


    /************************************************
     *          Expose to the global object
     ************************************************/
    exports.Sample = Sample;

}(this));

