
if(typeof jQuery.fn.autocompletehtml != 'function') {

(function($) {

$.fn.autocompletehtml = function() {
	var $text = $(this), sizeul = true;
	this.data("autocomplete")._renderItem = function _renderItemHTML(ul, item) {
		if(sizeul) {
			if(ul.css('max-width')=='none') ul.css('max-width',$text.outerWidth());
			sizeul = false;
		}
		return $("<li></li>")
			.data("item.autocomplete", item)
			.append("<a>" + item.match + "</a>")
			.appendTo(ul);
	};
	return this;
}
$.fn.autocompleteselect = function(options) {

	return this.each(function() {
		var id = this.id;
		var $this = $(this);

		var $text = $("#"+id+"_text");
		var $deck = $("#"+id+"_on_deck");

		function receiveResult(event, ui) {
			if ($this.val()) {
				kill();
			}
			$this.val(ui.item.pk);
			$text.val('');
			addKiller(ui.item.repr, null, ui.item.url);
			$deck.trigger("added");
			$this.change();
			return false;
		}

		function addKiller(repr, pk, url) {
			killer_id = "kill_" + pk + id;
			killButton = '<span class="ui-icon ui-icon-trash" id="'+killer_id+'">X</span> ';
			if (repr) {
				$deck.empty();
				if (url){
					repr = '<a href="' + url + '" target="_blank">' + repr + '</a>';
				}
				$deck.append("<div>" + killButton + repr + "</div>");
			} else {
				$("#"+id+"_on_deck > div").prepend(killButton);
			}
			$("#" + killer_id).click(function() {
				if (options.confirm_text){
					var delete_item = confirm(options.confirm_text);
					if (delete_item) {
						kill();
						$deck.trigger("killed");
					}
				} else {
					kill();
					$deck.trigger("killed");
				}
			});
		}

		function kill() {
			$this.val('');
			$this.change();
			$deck.children().fadeOut(1.0).remove();
		}

		options.select = receiveResult;
		$text.autocomplete(options);
		$text.autocompletehtml();

		if (options.initial) {
			its = options.initial;
			addKiller(its[0], its[1]);
		}

		$this.bind('didAddPopup', function(event, pk, repr) {
			ui = { item: { pk: pk, repr: repr } };
			receiveResult(null, ui);
		});

		$this.change(function (ev) {
			var pk, repr, ui;
			if (typeof ev.cloneSource !== 'undefined') {
				pk = ev.cloneSource.val();
				// depends on addKiller implementation
				repr = ev.cloneSource.next().children('div').children().slice(1);
				repr = $.map(repr, function (el) {
					return el.outerHTML;
				}).join('');
				ui = { item: { pk: pk, repr: repr } };
				receiveResult(null, ui);
			}
		});
	});
};

$.fn.autocompleteselectmultiple = function(options) {
	return this.each(function() {
		var id = this.id;

		var $this = $(this);
		var $text = $("#"+id+"_text");
		var $deck = $("#"+id+"_on_deck");

		function receiveResult(event, ui) {
			pk = ui.item.pk;
			prev = $this.val();

			if (prev.indexOf("|"+pk+"|") == -1) {
				$this.val((prev ? prev : "|") + pk + "|");
				addKiller(ui.item.repr, pk, ui.item.url);
				$text.val('');
				$deck.trigger("added");
				$this.change();
			}

			return false;
		}

		function addKiller(repr, pk, url) {
			killer_id = "kill_" + pk + id;
			killButton = '<span class="ui-icon ui-icon-trash" id="'+killer_id+'">X</span> ';
			var item_content = null;
			if (url) {
				item_content = '<div id="'+ id +'_on_deck_' + pk + '">' +
					killButton + '<a href="' + url + '" target="_blank">' + repr + '</a></div>';
			} else {
				item_content = '<div id="'+id+'_on_deck_'+pk+'">' + killButton + repr + ' </div>';
			}
			$deck.append(item_content);

			$("#"+killer_id).click(function() {
				if (options.confirm_text){
					var delete_item = confirm(options.confirm_text);
					if (delete_item) {
						kill(pk);
						$deck.trigger("killed");
					}
				} else {
					kill(pk);
					$deck.trigger("killed");
				}
			});
		}

		function kill(pk) {
			$this.val($this.val().replace("|" + pk + "|", "|"));
			$("#"+id+"_on_deck_"+pk).fadeOut().remove();
		}

		options.select = receiveResult;
		$text.autocomplete(options);
		$text.autocompletehtml();

		if (options.initial) {
			$.each(options.initial, function(i, its) {
				addKiller(its[0], its[1]);
			});
		}

		$this.bind('didAddPopup', function(event, pk, repr) {
			ui = { item: { pk: pk, repr: repr } }
			receiveResult(null, ui);
		});
	});
};

window.addAutoComplete = function (prefix_id, callback ) { /*(html_id)*/
	/* detects inline forms and converts the html_id if needed */
	var prefix = 0;
	var html_id = prefix_id;
	if(html_id.indexOf("__prefix__") != -1) {
		// Some dirty loop to find the appropriate element to apply the callback to
		while ($('#'+html_id).length) {
			html_id = prefix_id.replace(/__prefix__/, prefix++);
		}
		html_id = prefix_id.replace(/__prefix__/, prefix-2);
		// Ignore the first call to this function, the one that is triggered when
		// page is loaded just because the "empty" form is there.
		if ($("#"+html_id+", #"+html_id+"_text").hasClass("ui-autocomplete-input"))
			return;
	}
	callback(html_id);
}
/*	the popup handler
	requires RelatedObjects.js which is part of the django admin js
	so if using outside of the admin then you would need to include that manually */
window.didAddPopup = function (win,newId,newRepr) {
	var name = windowname_to_id(win.name);
	$("#"+name).trigger('didAddPopup',[html_unescape(newId),html_unescape(newRepr)]);
	win.close();
}

})(jQuery);

}
