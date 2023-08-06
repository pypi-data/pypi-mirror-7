/**
 * Relate widget JS
 */

if (djinn === undefined) {
    var djinn = {};
}


if (djinn.forms === undefined) {
  djinn.forms = {};
}


djinn.forms.relate = {};


/**
 * Initialize the relate widget.
 * @param widget Element to initialize.
 */
djinn.forms.relate.init = function(widget) {

};


/**
 * Handle select on the autosearch results.
 * @param e Event
 * @param ui UI object holding the selected item
 */
djinn.forms.relate.select = function(e, ui) {

    var label = ui.item.label;
    var value =  ui.item.value;
    var widget = $(e.target).parents(".relate");

    djinn.forms.relate.handleElement(widget, label, value);

    var input = $(e.target).parents(".relate").find(".autocomplete");

    input.val("");

    // blur first, then focus for ie...
    if ($.browser.msie) {
      input.blur();
    }

    input.focus();

    e.preventDefault();
};


djinn.forms.relate.handleElement = function(widget, label, value) {

    var tpl = widget.find("ul .tpl").eq(0).clone();

    if (widget.hasClass("multiple")) {
      djinn.forms.addValue(widget.find(".add-list").eq(0), value);
    } else {
      widget.find(".add-list").eq(0).val(value);
    }

    tpl.attr("class", "");
    tpl.attr("style", "");
    tpl.find("span").eq(0).html(label);
    tpl.find("a.delete a.change").attr("data-urn", value);

    if (widget.hasClass("multiple")) {
      widget.find("ul").append(tpl);
    } else {
      widget.find("ul li").last().replaceWith(tpl);
    }

    widget.removeClass("empty");
    
    $(document).trigger("djinn_forms_relate", [widget, value]);
};


$(document).ready(function() {

  $(".relate .autocomplete").each(function() {

    var input = $(this);

    input.val("");
    
    input.autocomplete({
      source: input.data("search_url"),
      minLength: input.data("search_minlength"),
      select: djinn.forms.relate.select,
      focus: function(e, ui) {
        e.preventDefault();
      }
    });
  });

  $(document).on("click", ".relate a.show-popup", function(e) {

    e.preventDefault();

    var link = $(e.currentTarget);
    var widget = link.parents(".relate");

    $.get($(e.currentTarget).attr("href"), function(data) {

      var modal = djinn.contenttypes.show_modal(data);

      modal.on("click", ".search-item", function(e) {

        e.preventDefault();
        e.stopPropagation();

        var search_item = $(e.currentTarget);

        var value = search_item.data("urn");
        var label = search_item.data("title");
        
        djinn.forms.relate.handleElement(widget, label, value);

        modal.modal('close');
      });
    });
  });

  $(document).on("focusout", ".relate.single .autocomplete", function(e) {
    
    var widget = $(e.target).parents(".relate");
    
    widget.removeClass("empty");
  });
  
  $(document).on("click", ".relate.multiple .delete ", function(e) {
    
    e.preventDefault();
    
    var widget = $(e.currentTarget).parents(".relate");
    var record = $(e.currentTarget).parents("li");
    var link = $(e.currentTarget);
    
    djinn.forms.removeValue(widget.find(".add-list").eq(0),
                            link.data("urn"));
    
    djinn.forms.addValue(widget.find(".rm-list").eq(0),
                         link.data("urn"));
    
    if (!record.siblings(":not('.tpl')").size()) {
      widget.addClass("empty");
    }
    
    record.remove();
    
    $(document).trigger("djinn_forms_unrelate", [widget, link.data("urn")]);
  });

  $(document).on("click", ".relate.single .change", function(e) {
    
    e.preventDefault();
    
    var widget = $(e.currentTarget).parents(".relate");
    
    widget.addClass("empty");
    widget.find(".autocomplete").focus();
  });
  
});
