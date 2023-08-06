var contactfacetednav = {};

contactfacetednav.selectionchange = jQuery.Event('selectionchange');

contactfacetednav.init = function() {
    contactfacetednav.status_messages = null;
    Backbone.emulateHTTP = true;
    Backbone.emulateJSON = true;
    jQuery('body').on('click', '#contacts-selectall', function() {
        if(contactfacetednav.contacts.selection().length > 0){
            contactfacetednav.contacts.unselectAll();
        } else {
            contactfacetednav.contacts.selectAll();
        }
    });

    jQuery(Faceted.Events).bind(Faceted.Events.AJAX_QUERY_SUCCESS, function() {
        jQuery('#contacts-facetednav-batchactions').each(function(){
            if (!Faceted.b_start_changed) {
                contactfacetednav.contacts = new contactfacetednav.Contacts();
            } else {
                contactfacetednav.contacts.each(function(contact) {
                    contact.render();
                });
            }
            contactfacetednav.contacts.render();
            jQuery('.contact-entry input').click(function() {
                var input = jQuery(this);
                var uid = input.attr('id').split('-')[1];
                var contact = contactfacetednav.contacts.get(uid);
                var selected = input.attr('checked') == 'checked';
                contact.setSelected(selected);
                contact.render();
            });
            contactfacetednav.show_messages();
        });
        jQuery('#faceted-add-contact a').prepOverlay({
            subtype: 'ajax',
            filter: common_content_filter,
            formselector: '#form',
            closeselector: '[name="form.buttons.cancel"]',
            noform: function(el, pbo) {
                Faceted.Form.do_form_query();
                return 'close';},

        });
    });
};

contactfacetednav.store_overlay_messages = function(el){
    contactfacetednav.status_messages = jQuery(el).find('.portalMessage');
};

contactfacetednav.show_messages = function(){
    if(contactfacetednav.status_messages !== null){
        jQuery('#contacts-facetednav-batchactions').prepend(contactfacetednav.status_messages);
        contactfacetednav.status_messages = null;
    }
};

contactfacetednav.Contact = Backbone.Model.extend({

    defaults : {
        id : "?????????????????",
        path : "?????????????????",
        selected : false,
    },

    initialize : function Contact() {
        this.bind('change', this.render);
    },

    setSelected : function(value) {
        this.set({
            'selected' : value
        });
    },

    isSelected : function() {
        return this.get('selected');
    },

    getPath : function() {
        return this.get('path');
    },

    render : function() {
        var input = jQuery('#contact-' + this.get('id'));
        if (input.length === 0) {
            // Not in current page
            return;
        }
        else if (this.isSelected()) {
            input.prop('checked', true);
        }
        else{
            input.prop('checked', false);
        }

    }
});

contactfacetednav.Contacts = Backbone.Collection.extend({
    model : contactfacetednav.Contact,
    initialize : function() {
        this.bind('change', this.render);
        this.fetch({
            success : function(model, response) {
                model.each(function(contact) {
                    contact.render();
                });
            }
        });
    },
    url : function() {
        return 'json-contacts?' + jQuery.param(Faceted.SortedQuery());
    },
    selectAll: function(){
        this.each(function(contact){
            contact.setSelected(true);
        });
    },
    unselectAll: function(){
        this.each(function(contact){
            contact.setSelected(false);
        });
    },
    selection: function(){
        return this.filter(function(contact){
            return contact.isSelected();
        });
    },
    selection_uids: function(){
        var uids = [];
        var selection = this.selection();
        for(var num in selection){
            uids.push(selection[num].id);
        }
        return uids;
    },
    selection_pathes: function(){
        var uids = [];
        var selection = this.selection();
        for(var num in selection){
            uids.push(selection[num].getPath());
        }
        return uids;
    },
    hasSelection: function(){
        return this.selection().length > 0;
    },
    render: function(){
        var selection_length = this.selection().length;
        var select_all_button = jQuery('#contacts-selectall');
        if(selection_length===0){
            jQuery('.contacts-buttons input').attr('disabled', true);
            select_all_button.attr('title', select_all_button.attr('data-select-all-msg'));
            select_all_button.attr('value', select_all_button.attr('data-select-all-msg'));
        }
        else{
            jQuery('.contacts-buttons input').attr('disabled', false);
            select_all_button.attr('title', select_all_button.attr('data-unselect-all-msg'));
            select_all_button.attr('value', select_all_button.attr('data-unselect-all-msg'));
        }
        jQuery('#contacts-selection-num .num').text(selection_length);
    }
});


jQuery(document).ready(contactfacetednav.init);

contactfacetednav.serialize_uids = function(uids){
    /* Helpers to prepare sending uids list the more convenient way
     */
    return jQuery.param({'uids:list': uids}, true);
};

contactfacetednav.serialize_pathes = function(pathes){
    /* Helpers to prepare sending pathes list the more convenient way
     */
    return jQuery.param({'pathes:list': pathes}, true);
};

contactfacetednav.delete_selection = function(confirm_msg){
    var uids = contactfacetednav.contacts.selection_uids();
    confirm_msg = confirm_msg.replace('$num', uids.length);
    if(confirm(confirm_msg)){
        var base_url = jQuery('base').attr('href');
        jQuery.post(base_url + '/delete_selection',
                    contactfacetednav.serialize_uids(uids),
                    function(fails){Faceted.Form.do_form_query();}
        );
    }
};

contactfacetednav.excel_export = function(){
    var uids = contactfacetednav.contacts.selection_uids();
    var url = portal_url + '/@@collective.excelexport?excelexport.policy=search';
    var form = jQuery('<form action="' + url + '" method="post"></form>');

    for(var num in uids){
        form.append('<input type="hidden" name="UID:list" value="' + uids[num] + '" />');
    }
    jQuery('body').append(form);
    form.submit();
    form.remove();
};

jQuery(Faceted.Events).bind(Faceted.Events.AJAX_QUERY_SUCCESS, function(){
    jQuery('#faceted-results .delete-contact').each(function(){
        var link = jQuery(this);
        link.prepOverlay({
                subtype: 'ajax',
                filter: common_content_filter,
                formselector: '#delete_confirmation',
                closeselector: '[name="cancel"]',
                noform: function(el, pbo) {
                    Faceted.Form.do_form_query();
                    return 'close';},
              });
    });
    jQuery('#faceted-results .edit-contact').each(function(){
        var link = jQuery(this);
        link.prepOverlay({
                subtype: 'ajax',
                filter: common_content_filter,
                formselector: '#form',
                closeselector: '[name="form.button.cancel"]',
                noform: function(el, pbo) {
                    Faceted.Form.do_form_query();
                    return 'close';},
              });
    });
});