function draw_canvas(canvas, w, h, node_radius) {
    node_radius = (typeof node_radius==='undefined')?10:node_radius;
    var c = Raphael(canvas, w, h);
    $.getJSON('ncbigraph/fan.json', function(data) {
	var outEdges = {};
	var inEdges = {};
	c.setStart();
	$.each(data.edges, function(i, edge) {
	    var src = data.nodes[edge.source];
	    var tgt = data.nodes[edge.target];
	    var theta = Raphael.angle(src.x, src.y, tgt.x, tgt.y);
	    if (src.x < tgt.x) theta = 180.0-theta;
	    edge.theta = theta;
	    var oe = outEdges[edge.source];
	    oe = oe ? oe : [];
	    oe.push(edge);
	    outEdges[edge.source] = oe;
	    var ie = inEdges[edge.target];
	    ie = ie ? ie : [];
	    ie.push(edge);
	    inEdges[edge.target] = ie;
	    //c.path('M'+src.x+','+src.y+' L'+tgt.x+','+tgt.y);
	});
	$.each(data.nodes, function(eid, node) {
	    //console.log([node.label, inEdges[node.eid]]);
	    var edges = inEdges[node.eid] ? inEdges[node.eid] : [];
	    if (edges.length > 0) {
		var u = 10;
		var span = (edges.length-1) * u;
		var c0 = -span/2;
		$.each(edges, function(i, edge) {
		    var src = data.nodes[edge.source];
		    var rad = (edge.theta+90) * (Math.PI/180);
		    var src_cpx = src.x + Math.cos(rad)*c0;
		    var src_cpy = src.y + Math.sin(rad)*c0;
		    var tgt_cpx = node.x + Math.cos(rad)*c0;
		    var tgt_cpy = node.y + Math.sin(rad)*c0;
		    // console.log([src.label, node.label,
		    // 		 src.x, src.y, src_cpx, src_cpy,
		    // 		 tgt_cpx, tgt_cpy, node.x, node.y]);
		    c.path('M'+src.x+','+src.y+
		    	   'C'+src_cpx+','+src_cpy+','+
		    	   tgt_cpx+','+tgt_cpy+','+
		    	   node.x+','+node.y).
			attr({'stroke':edge.color,
			      'stroke-width': 2});
		    c0 += u;
		});
	    }
	});
	$.each(data.nodes, function(eid, node) {
	    var radius = node_radius * node.radius;
	    circ = c.circle(node.x, node.y, radius).
		attr({fill:node.color}).
		mouseover(function(e) {
		    this.data('glow', this.glow({color:'blue'}));
		}).
		mouseout(function(e) {
		    var g = this.data('glow');
		    this.removeData('glow');
		    g.remove();
		});
	    if (node.label.length > 1) {
		var off = (node.text_anchor=='start')?15:-15;
		var txt = c.text(node.x+off, node.y, node.label).
		    attr({'font-size':20, 'text-anchor': node.text_anchor});
		circ.data('label', txt);
	    }
	});
	var s = c.setFinish();
	var bbox = s.getBBox();
	c.setViewBox(bbox.x, bbox.y, bbox.width, bbox.height, true);
    });
}

	      

