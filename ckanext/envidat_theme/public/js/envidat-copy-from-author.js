/* Module for copying other field inputs. This will copy
 * data from a selected author into the contact person fields.
 *
 */

this.ckan.module('envidat-copy-from-author', function (jQuery, _) {
  return {
    options: {
      /* The selector used for each custom field wrapper */
     fieldSelector: '.envidat-copy-from-author-controls'
    },

    /* Initializes the module and attaches custom event listeners. This
     * is called internally by ckan.module.initialize().
     *
     * Returns nothing.
     */
    initialize: function () {

      if (!jQuery('html').hasClass('ie7')) {
        jQuery.proxyAll(this, /_on/);

        var onChangeFn = this._onChange;
        var onFocusFn = this._onFocus;
        var fieldContainers = this.el.find(this.options.fieldSelector);

        this.updateSelectAuthors();
        this.disableCopyAuthor();

        $(fieldContainers).find(".fa-refresh").each(function() { $(this).on('change', ':checkbox', onChangeFn);});
        $(fieldContainers).find(".fa-check").each(function() { $(this).on('change', ':checkbox', onChangeFn);});

        $("#envidat-copy-from-author-select").on('change', onChangeFn);
        $("#envidat-copy-from-author-select").on('focus', onFocusFn);

      }
    },
    getNumAuthors: function(){
    	var num_authors = $('#composite-repeating-div-author').find('.fa-minus').length;
    	return num_authors
    },
    /* updates the options in the select dropdown */
    updateSelectAuthors: function(){

        var fieldContainers = this.el.find(this.options.fieldSelector);

	var author_select = $(fieldContainers).find("#envidat-copy-from-author-select");
	var num_authors = this.getNumAuthors();

	var optionsAsString = "";
	// include blank as initially selected
	optionsAsString += "<option value=''>Select...</option>";

	for (var i = 1; i <= num_authors; i++) {
		optionsAsString += "<option value='" + i + "'> Author " + i + "</option>";
	}
	author_select.find('option').remove().end().append($(optionsAsString));

	this.disableCopyAuthor();

	return
    },
    /* checks if the selected author is valid and returns it, returns false if not */
    getValidAuthorSelected: function () {
        var fieldContainers = this.el.find(this.options.fieldSelector);
	var selected_author = $(fieldContainers).find("#envidat-copy-from-author-select").val();
	var num_authors = this.getNumAuthors();

	if (selected_author.length>0 && parseInt(selected_author)<=num_authors) {
		return selected_author;
   	} else {
   		return false;
	}
    },
    /* Enable/disable the ok button */
    enableCopyAuthor: function () {
        var fieldContainers = this.el.find(this.options.fieldSelector);
	$(fieldContainers).find(".fa-check").each(function() { $(this).removeAttr("disabled");});
	$(fieldContainers).find(".envidat-copy-from-author-ok").each(function() { $(this).removeAttr("disabled");});    	
    },
    disableCopyAuthor: function () {
        var fieldContainers = this.el.find(this.options.fieldSelector);
	$(fieldContainers).find(".fa-check").each(function() { $(this).attr("disabled", 'true');});
	$(fieldContainers).find(".envidat-copy-from-author-ok").each(function() { $(this).attr("disabled", 'true');});
    },
    /* Copies the information from one of the authors in the contact person fields */
    /*
    */
	doCopyAuthor: function (authorNum) {
        var mantainer_inputs = $('#composite-div-maintainer').find(':input').filter('.form-control');

        var authors_inputs = $('#composite-repeating-div-author').find(':input');

        mantainer_inputs.each(function() {
		var maintainer_field_id = this.id
            	var author_field_id = maintainer_field_id.replace('maintainer', 'author-' + authorNum)
        	var author_field_value = $('#' + author_field_id).val();

        	$(this).val(author_field_value);
        });
    },
    /* Event handler called when the select is focused */
    _onFocus: function (event) {
    	if (event.currentTarget.id === "envidat-copy-from-author-select"){
    		this.updateSelectAuthors();
    	}
    },
    /* Event handler called when the checkboxes or select are changed */
    _onChange: function (event) {
    	var fieldContainers = this.el.find(this.options.fieldSelector);

	// Refresh authors in select dropdown
	if (event.currentTarget.id === "envidat-copy-from-author-reload"){
   		this.updateSelectAuthors();
	    	return;
	}

	// Do copy from author
	if (event.currentTarget.id === "envidat-copy-from-author-ok"){
		var selected_author = this.getValidAuthorSelected()

		if (selected_author) {
			this.doCopyAuthor(selected_author);
   		} else {
			this.updateSelectAuthors();
		}
	    	return;
	    }
	// enable copy button
	if (event.currentTarget.id === "envidat-copy-from-author-select"){
		var selected_author = this.getValidAuthorSelected()
	        if (selected_author) {
	            this.enableCopyAuthor();
		} else {
	            this.disableCopyAuthor();
		}
		return
	}
    }
  };
});


