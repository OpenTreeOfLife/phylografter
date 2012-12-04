function draw_canvas(canvas_id, w, h, node_radius, taxid) {
    node_radius = (typeof node_radius==='undefined') ? 10 : node_radius;
    var canvas = Raphael(canvas_id, w, h);
    $.getJSON('fan.json', 'taxid='+taxid, function(data) {
	draw_fan(canvas, node_radius, data, 0.0, 1.0);
    });
}

function draw_fan(canvas, node_radius, data, rotation, scale) {
    var outEdges = {};
    var inEdges = {};
    var fan = canvas.set();
    var nodeset = canvas.set();
    var edgesets = {}; // key = stree; val = set of edge paths

    $.each(data.edges, function(i, edge) {
	var src = data.nodes[edge.source];
	var tgt = data.nodes[edge.target];
	var deg = Raphael.angle(src.x, src.y, tgt.x, tgt.y); //degrees
	if (src.x < tgt.x) { deg = 180.0-deg; }
	edge.deg = deg;
	var oe = outEdges[edge.source];
	oe = oe ? oe : {};
	ov = oe[edge.target];
	ov = ov ? ov : [];
	ov.push(edge);
	oe[edge.target] = ov;
	outEdges[edge.source] = oe;
	var ie = inEdges[edge.target];
	ie = ie ? ie : {};
	iv = ie[edge.source];
	iv = iv ? iv : [];
	iv.push(edge);
	ie[edge.source] = iv;
	inEdges[edge.target] = ie;
	//canvas.path('M'+src.x+','+src.y+' L'+tgt.x+','+tgt.y);
    });
    $.each(data.nodes, function(eid, node) {
	//console.log([node.label, inEdges[node.eid]]);
	var ev = outEdges[node.eid] ? outEdges[node.eid] : {};
	$.each(ev, function(target, edges) {
	    var u = 6;
	    var span = (edges.length-1) * u;
	    var c0 = -span/2;
	    var src = node;
	    var tgt = data.nodes[target];
	    $.each(edges, function(i, edge) {
		var rad = (edge.deg+90) * (Math.PI/180);
		var src_cpx = src.x + Math.cos(rad)*c0;
		var src_cpy = src.y + Math.sin(rad)*c0;
		var tgt_cpx = tgt.x + Math.cos(rad)*c0;
		var tgt_cpy = tgt.y + Math.sin(rad)*c0;
		var midx = src_cpx+(tgt_cpx-src_cpx)/2;
		var midy = src_cpy+(tgt_cpy-src_cpy)/2;
		// console.log([src.label, node.label,
		// 		 src.x, src.y, src_cpx, src_cpy,
		// 		 tgt_cpx, tgt_cpy, node.x, node.y]);
		var p = canvas.path('M'+src.x+','+src.y+
				    'C'+src_cpx+','+src_cpy+','+
				    midx+','+midy+','+
				    midx+','+midy+
				    'C'+midx+','+midy+','+
				    tgt_cpx+','+tgt_cpy+','+
				    tgt.x+','+tgt.y).attr(
					{'stroke':edge.color,
					 'stroke-width': 2,
					 'title': 'stree '+edge.stree});
		p.data('edge', edge);
		var eset = edgesets[edge.stree];
		eset = eset ? eset : canvas.set();
		eset.push(p);
		edgesets[edge.stree] = eset;
		c0 += u;
	    });
	});
    });
    $.each(data.nodes, function(eid, node) {
	var g = canvas.set();
	var radius = node_radius * node.radius;
	circ = canvas.circle(node.x, node.y, radius).
	    attr({fill:node.color}).
	    mouseover(function(e) {
		this.data('glow', this.glow({color:'blue'}));
	    }).
	    mouseout(function(e) {
		var g = this.data('glow');
		this.removeData('glow');
		g.remove();
	    }).
	    data('node', node);
	g.push(circ);
	if (node.label.length > 1) {
	    var off = (node.text_anchor=='start')?15:-15;
	    var txt = canvas.text(node.x+off, node.y, node.label).
		attr({'font-size':20, 'text-anchor': node.text_anchor});
	    circ.data('label', txt);
	    g.push(txt);
	}
	nodeset.push(g);
	if (node.taxid) {
	    g.click(function() {
		var deg = 180-Raphael.angle(0, 0, node.x, node.y);
		var dx = -node.x, dy = -node.y;
		var r = 'r'+(deg)+',0,0';
		var t = 't'+dx+','+dy;
		var scale = data.radius/Math.sin(Raphael.rad(data.angle));
		var s = 's'+scale+','+scale+','+node.x+','+node.y;
		//fan.animate({transform:r+t+s}, 500, '<>');
		fan.animate({transform:r+t+s, opacity:0}, 500, '<>',function() {
		    $.getJSON('fan.json', {'taxid':node.taxid}, function(data) {
			draw_fan(canvas, node_radius, data, 0.0, 1.0);
		    });
		});
	    });
	}
    });
    fan.push(nodeset);
    $.each(edgesets, function(stree, pathset) {
	fan.push(pathset);
    });
    var bbox = fan.getBBox();
    canvas.vbx = bbox.x-10; canvas.vby = bbox.y-10;
    canvas.vbw = bbox.width+20; canvas.vbh = bbox.height+20;
    canvas.setViewBox(canvas.vbx, canvas.vby, canvas.vbw, canvas.vbh, false);
}
