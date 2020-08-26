/* Module for copying other field inputs. This will copy
 * data from a selected author into the contact person fields.
 *
 */

this.ckan.module('envidat-author-order', function (jQuery, _) {
  return {
    options: {
      /* The selector used for each custom field wrapper */
     fieldSelector: '.envidat-author-order-controls'
    },

    /* Initializes the module and attaches custom event listeners. This
     * is called internally by ckan.module.initialize().
     *
     * Returns nothing.
     */
    initialize: function () {

      if (!jQuery('html').hasClass('ie7')) {
        jQuery.proxyAll(this, /_on/);

        var onFocusFn = this._onFocus;
        var num_authors = this.getNumAuthors();

        var plusSign = $('#composite-repeating-div-author').find('.fa-plus').first()

        if (!(plusSign.hasClass( "author-order-init" ))) {
            $('#composite-repeating-div-author').find('.fa-plus').first()
            $('#composite-repeating-div-author').find('.fa-plus').on('change', onFocusFn)

            for (var j = 1; j <= num_authors; j++) {
                $("#author-" + j + "-order").on('focus', onFocusFn);
                $("#author-" + j + "-order").removeAttr('disabled')
                this.updateSelectAuthors(j, true);
            }
            plusSign.addClass("author-order-init")
            plusSign.attr('id', 'plus-sign-add-author')
        }
      }
    },
    getNumAuthors: function(){
    	var num_authors = $('#composite-repeating-div-author').find('.fa-minus').length;
    	return num_authors
    },
    /* updates the options in the select dropdown */
    updateSelectAuthors: function(j, force){

	    var num_authors = this.getNumAuthors();
        var author_select = $("#author-" + j + "-order");

        optionsAsString = "";
        for (var i = 1; i <= num_authors; i++) {
            if ((i == j) && (force)) {
                optionsAsString += "<option value='" + i + "' selected=''> " + i + "</option>";
            }
            else {
                optionsAsString += "<option value='" + i + "'> " + i + "</option>";
            }
        }
        author_select.find('option').remove().end().append($(optionsAsString));

	    return
    },
    /* Event handler called when the select is focused */
    _onFocus: function (event) {
	    var num_authors = this.getNumAuthors();

        if (event.currentTarget.id === "plus-sign-add-author") {
               this.updateSelectAuthors(num_authors, true);
        }
        else {
            for (var i = 1; i <= num_authors; i++) {
                if (event.currentTarget.id === "author-" + i + "-order"){
                    this.updateSelectAuthors(i, false);
                    return
                }
            }
        }
    }
  };
});


