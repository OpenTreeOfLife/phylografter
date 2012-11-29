function draw_canvas(canvas, w, h) {
    var c = Raphael(canvas, w, h);
    $.getJSON('ncbigraph/fan.json', function(data) {
	c.setStart();
	$.each(data.edges, function(i, edge) {
	    var src = data.nodes[edge.source];
	    var tgt = data.nodes[edge.target];
	    c.path('M'+src.x+','+src.y+' L'+tgt.x+','+tgt.y);
	});
	$.each(data.nodes, function(eid, node) {
	    c.circle(node.x, node.y, 10).attr({fill:node.color});
	    if (node.label.length > 1) {
		var txt = c.text(node.x, node.y, node.label).
		    attr({'font-size':20});
		console.log(txt.getBBox());
	    }
	});
	var s = c.setFinish();
	var bbox = s.getBBox();
	c.setViewBox(bbox.x, bbox.y, bbox.width, bbox.height, true);
    });
}

	      

