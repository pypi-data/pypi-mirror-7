/**
 * Keyword widget JS
 */

if (djinn === undefined) {
    var djinn = {};
}


if (djinn.forms === undefined) {
  djinn.forms = {};
}


djinn.forms.keyword = {};


djinn.forms.keyword.appendKw = function(widget, val) {

  var input = widget.find("input[type=hidden]");

  widget.find("ul").append('<li data-value="' + val + '">' + val + '<a href="#" class="delete">&times;</a></li>');
  djinn.forms.addValue(input, val, true, " "); 
};


djinn.forms.keyword.select = function(e, ui) {

  var value =  ui.item.value;
  var widget = $(e.target).parents(".keyword");
  var input = widget.find(".new_kw");

  djinn.forms.keyword.appendKw(widget, value);

  input.val("");
};


$(document).ready(function() {

  $(".new_kw").each(function() {

    var input = $(this);

    input.autocomplete({
      source: input.data("search_url"),
      minLength: input.data("search_minlength"),
      select: djinn.forms.keyword.select,
      focus: function(e, ui) {
        e.preventDefault();
      }
    });
  });

  $(document).on("click", ".keyword ul", function(e) {

    $(e.currentTarget).find("input").focus();
  });

  $(document).on("keydown", ".new_kw", function(e) {

    var input = $(e.currentTarget);
    var widget = input.parents(".keyword");

    if (e.keyCode == 13) {
      e.preventDefault();
    }

    if (e.keyCode == 13 || e.keyCode == 32) {
      djinn.forms.keyword.appendKw(widget, $(e.currentTarget).val());

      input.val("");
    }
  });

  $(document).on("click", ".keyword .delete", function(e) {

    e.preventDefault();

    var widget = $(e.currentTarget).parents(".keyword");
    var input = widget.find("input[type=hidden]");

    var elt = $(e.currentTarget).parents("li");

    djinn.forms.removeValue(input, elt.data('value'), " ");

    elt.remove();
  });
});
