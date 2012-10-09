function hbranch_clicked(nid, url, modal_id, modal_cid) {
	$('#'+modal_id).css('top', $(window).scrollTop()+'px');
	$('#'+modal_id).css('left', $(window).scrollLeft()+'px');
	$('#'+modal_id).css('height', $(window).height()+'px');
	$('#'+modal_id).css('width', $(window).width()+'px');
	$('#'+modal_cid).css('opacity', 1);
	$('#'+modal_cid).load(url, function() {
		$('#updateform').submit(
			function() {
				form_submitted(nid, url, modal_id, modal_cid);
				return false;
			});
		});
	$('#'+modal_id).fadeIn();
}

function form_submitted(nid, url, modal_id, modal_cid) {
	var form = $('#updateform');
	var qs = form.serialize();
	$('#'+modal_cid).load(form.attr('action') + '?' + qs);
	$('#'+modal_id).fadeOut();
}

$(document).ready() { function() {
		$('#tree_container').load();
	}
}
