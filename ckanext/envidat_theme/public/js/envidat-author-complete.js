/* Module for copying other field inputs. This will copy
 * data from a selected author into the contact person fields.
 *
 */

this.ckan.module('envidat-author-complete', function (jQuery, _) {
  return {
    options: {
      /* The selector used for each custom field wrapper */
     fieldSelector: '.envidat-author-complete-controls'
    },

    /* Initializes the module and attaches custom event listeners. This
     * is called internally by ckan.module.initialize().
     *
     * Returns nothing.
     */
    initialize: function () {

      if (!jQuery('html').hasClass('ie7')) {
        jQuery.proxyAll(this, /_on/);

        // get all the autocomplete buttons
        var onChangeFn = this._onChange;
        var fieldContainers = this.el.find(this.options.fieldSelector);
        $(fieldContainers).find(".fa-refresh").each(function() { $(this).on('change', ':checkbox', onChangeFn);});
      }
    },
    /* Autofills the information of the designed author from other datasets or ORCID */
    /*
    */
	doCompleteAuthor: function (index) {
       // get the author's email
	   var authorEmail = $('#author-' + index + '-email').val();
       if(authorEmail) {
           // call the designed api call
           $.get(
                "/api/action/envidat_get_author_data",
                {email : authorEmail},
                function(data) {
                     var author_data = data.result
                     if (author_data) {
                        // copy the info in the fields
                        jQuery.each(author_data, function(i, val) {
                            if ((i != 'email') && (i != 'data_credit')){
                                var authorField = $('#author-' + index + '-' + i);
                                if (!(authorField.val())) {
                                    authorField.val(val)
                                }
                            }
                        });
                    }
                }
            );
        } else {
            console.warn("Author " + index + " has no valid email")
        }
    },
    /* Event handler called when the checkboxes or select are changed */
    _onChange: function (event) {
        // call data auto-completion for the author
        if (/^author-[0-9]*-autocomplete$/.test(event.currentTarget.id)){
            var index = this._getIndex(event.currentTarget.id)
            this.doCompleteAuthor(index);
            return;
        }
    },
    _getIndex: function(fieldName) {
        var index = parseInt(fieldName.split('-')[1])
        return index;
    }
  };
});


