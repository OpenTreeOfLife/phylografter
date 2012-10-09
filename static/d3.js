BioSync.TreeViewer.RenderUtil.d3.forceDirected.prototype = {

    recursivelyCollapseClade: function( p ) {

        var curGroup = this.currentGroup;

        var node = curGroup.nodeInfo[ p.curNodeId ];

       var duration = 250 * p.animMult;
       var rv = duration;

        for( var i = 0, ii = node.nodeObj.children.length; i < ii; i++ ) {
            rv = this.recursivelyCollapseClade( {
                cx: p.cx, cy: p.cy, animMult: p.animMult + 1,
                curNodeId: node.nodeObj.children[i],
                originalNodeInfo: p.originalNodeInfo } );
        }

       node.d3.transition().duration( duration ).attr( 'cx', p.cx ).attr( 'cy', p.cy );

       if( node.label ) {
           node.label.transition().duration( duration ).style( 'opacity', 0 );
       }

       if( node.nodeObj.collapsed ) { 
           curGroup.collapsedNodeIds.splice( curGroup.collapsedNodeIds.indexOf( p.curNodeId ), 1 );
       }

       d3.select( curGroup.link[0][ curGroup.linksByTargetNodeId[ node.nodeObj.nodeId ].index ] ).remove();
       delete curGroup.link[ curGroup.linksByTargetNodeId[ node.nodeObj.nodeId ].index ];
       delete curGroup.linksByTargetNodeId[ node.nodeObj.nodeId ];

       //node.d3.transition().delay( duration + 1000 ).attr( 'display', 'none' );

       p.originalNodeInfo.nodeObj.value += node.nodeObj.value;

       setTimeout( function() {
           delete curGroup.node[0][ curGroup.nodeInfo[ node.index ] ];
           delete curGroup.nodeInfo[ node.nodeObj.nodeId ];
       }, duration );

       return rv;
    },

    eventHandlers: {

        collapseClade: function( e ) {
            
            var renderObj = e.data.renderObj;
            var nodeId = e.data.nodeId;
        
            var curGroup = renderObj.currentGroup;        
            var nodeInfo = curGroup.nodeInfo[ nodeId ];
                
            var cx = parseFloat(nodeInfo.d3.attr('cx'));
            var cy = parseFloat(nodeInfo.d3.attr('cy'));

            curGroup.force.stop();

            var duration;

            for( var i = 0, ii = nodeInfo.nodeObj.children.length; i < ii; i++ ) {
            
                duration = renderObj.recursivelyCollapseClade( {
                    cx: cx, cy: cy, animMult: 1,
                    curNodeId: nodeInfo.nodeObj.children[i],
                    originalNodeInfo: nodeInfo } );
            }

            nodeInfo.nodeObj.children = [];
            nodeInfo.nodeObj.collapsed = true;
            curGroup.collapsedNodeIds.push( nodeId );

            nodeInfo.d3.transition().duration( duration ).attr( 'r', Math.sqrt( nodeInfo.nodeObj.value ) + renderObj.nodeRadius );
            //setTimeout( function() { renderObj.addCollapsedNodeUI( { nodeInfo: nodeInfo } ); }, duration );
            renderObj.addCollapsedNodeUI( { nodeInfo: nodeInfo } );
            setTimeout( function() { curGroup.force.resume(); }, duration + 1000 );
        },

        fixNode: function( e ) {

            var renderObj = e.data.renderObj;

            renderObj.currentGroup.nodeInfo[ e.data.nodeId ].data.fixed = true;
        },

        unFixNode: function( e ) {

            var renderObj = e.data.renderObj;

            renderObj.currentGroup.nodeInfo[ e.data.nodeId ].data.fixed = false;
        },

        expandClade: function( e ) {
    
            var renderObj = e.data.renderObj;
            var nodeId = e.data.nodeId;
        
            var curGroup = renderObj.currentGroup;        
            var expandedNode = curGroup.nodeInfo[ nodeId ].d3;

            var expandedNodeCX = expandedNode.attr( 'cx' );
            var expandedNodeCY = expandedNode.attr( 'cy' );

            curGroup.expandedNodeId = nodeId;
         
            curGroup.force
                .charge( 0 )
                .gravity( 0 )
                .stop();

            curGroup.link.style( 'display', 'none' );
            curGroup.hideLinks = true;

            renderObj.removeCollapsedNodeUI( { nodeId: nodeId } );
    
            curGroup.node.each(
                function( d, i ) {
                    var d3Obj = d3.select(this);
                    if( ( ! renderObj.rootIds[ d.nodeId ] ) && ( d.nodeId != nodeId ) ) {
                        d3Obj.transition().duration(500).attr( 'cx', expandedNodeCX ).attr( 'cy' , expandedNodeCY );
                        d3Obj.transition().delay(500).duration(100).style('display','none'); } } );

            renderObj.hideLabels( { index: curGroup.index,
                                    exceptions: [ nodeId, curGroup.rootId ] } );   

            renderObj.currentGroupIndex += 1;
            renderObj.groups.push( { } );

            renderObj.currentGroup = renderObj.groups[ renderObj.currentGroupIndex ];
            renderObj.currentGroup.index = renderObj.currentGroupIndex;

            $.ajax( { url: BioSync.Common.makeUrl( { controller: 'plugin_treeViewer', argList: [ 'd3ExpandNode' ] } ),
                  type: "GET",
                  context: renderObj.viewer,
                  data: { nodeId: nodeId, groupId: renderObj.currentGroupIndex },
                  success: new Array( renderObj.viewer.handleReceivedTree, renderObj.postExpandClade ) } );
        }
    },

    initialize: function() {

        var viewer = this.viewer;

        this.width = viewer.myWidth;
        this.height = viewer.myHeight;
        this.fill = d3.scale.category20();
        this.nodeRadius = 4;
        this.currentGroupIndex = 0;
        this.groups = [ { } ];
        this.currentGroup = this.groups[0];
        this.currentGroup.index = 0;

        this.leafArrangement =  viewer.viewInfo.leafArrangement || 'default';

        this.container = d3.select( '#' + viewer.containerId )
            .append('svg:svg').attr( 'width',  this.width ).attr( 'height', this.height );

        this.rootIds = { };

        BioSync.Common.disableSelection( $( '#' + viewer.containerId ) );
    },

    addAestheticLinksAndNodes: function() {

        var renderObj = this;
        var curGroup = renderObj.currentGroup;

        curGroup.labelEndNodes = { };
        curGroup.labelEndLinks = { };

        var curNodeIndex = curGroup.nodes.length;

        for( var i = 0, ii = curNodeIndex; i < ii; i++ ) {

            var node = curGroup.nodes[ i ];

            if( node.name ) {

                var hiddenNodeObj = { value: 3, labelEnd: true, children: [ ], name: null, nodeId: null, group: curGroup.index, collapsed: false };
                curGroup.nodes.push( hiddenNodeObj );
                curGroup.labelEndNodes[ node.nodeId ] = hiddenNodeObj;

                var hiddenLink = { target: curNodeIndex, source: i, currentDepth: 1, labelEnd: true };
                curGroup.links.push( hiddenLink );
                curGroup.labelEndLinks[ node.nodeId ] = hiddenLink;
                curNodeIndex++;
            }
        }
    },

    addAncestorNodesToGroup2: function() {

        var renderObj = this;
        var curGroup = renderObj.currentGroup;

        for( var i = 1, ii = renderObj.groups.length; i < ii; i++ ) {
        
            var oldGroup = renderObj.groups[ i - 1 ];
            curGroup.node[0].push( oldGroup.nodeInfo[ oldGroup.rootId ].js );
            curGroup.nodes.push( oldGroup.nodeInfo[ oldGroup.rootId ].data );
            curGroup.nodeInfo[ oldGroup.rootId ] = oldGroup.nodeInfo[ oldGroup.rootId ];

            var nextGroup = renderObj.groups[ i ];

            if( i != ii - 1 ) {

                curGroup.link[0].push( nextGroup.indexedLinks[ nextGroup.rootId ].js );
                curGroup.links.push( nextGroup.indexedLinks[ nextGroup.rootId ].data );
                curGroup.indexedLinks[ nextGroup.rootId ] = nextGroup.indexedLinks[ nextGroup.rootId ];

            } else {

                var data = { source: oldGroup.nodeInfo[ oldGroup.rootId ].data, target: curGroup.nodeInfo[ curGroup.rootId ].data, currentDepth: 1, visible: false };

                var d3Obj = renderObj.container.selectAll('p').data( [ data ] )
                   .enter().append( 'svg:line' )
                   .attr(  "class", "link" )
                   .style( "stroke-width", 1 )
                   .style( 'display', 'none' )
                   .attr("x1", function(d) { return d.source.x; })
                   .attr("y1", function(d) { return d.source.y; })
                   .attr("x2", function(d) { return d.target.x; })
                   .attr("y2", function(d) { return d.target.y; });

                curGroup.link[0].push( d3Obj[0][0] );

                curGroup.indexedLinks[ curGroup.rootId ] = { d3: d3Obj, data: data, sourceNodeId: oldGroup.rootId, js: d3Obj[0][0] };
            }
        }
    },

    addAncestorNodesToGroup: function() {

        var renderObj = this;
        var curGroup = renderObj.currentGroup;

        var curNodeIndex = curGroup.nodes.length - 1;
         
        for( var i = 1, ii = renderObj.groups.length; i < ii; i++ ) {
        
            var oldGroup = renderObj.groups[ i - 1 ];
            curGroup.nodes.push( oldGroup.nodeInfo[ oldGroup.rootId ].data );
            curNodeIndex++;

            if( i == ii - 1 ) { curGroup.links.push( { target: 0, source: curNodeIndex, currentDepth: 5 } ); }
        }
    },

    renderReceivedTree: function() {

        var viewer = this.viewer;
        var renderObj = this;

        var curGroup = this.currentGroup;
        var response = viewer.renderResponse;

        curGroup.rootId = response.rootId;
        curGroup.depth = response.depth;
        curGroup.nodes = response.nodes;
        curGroup.links = response.links;
        
        this.rootIds[ curGroup.rootId ] = true;

        //if( curGroup.index > 0 ) { renderObj.addAncestorNodesToGroup(); }
   
        renderObj.addAestheticLinksAndNodes();
        
        this.initializeLeafNodes();
        
        curGroup.force = d3.layout.force()
           .charge( -1000 )
           .friction( .90 )
           .gravity( .22 )
           .nodes( curGroup.nodes )
           .links( curGroup.links )
           .linkDistance( function( link, index ) { return link.currentDepth * viewer.config.branchLength; } )
           .size( [ this.width, this.height ] )
           .start();

        curGroup.link = this.container.selectAll('p')
           .data( curGroup.links )
         .enter().append("svg:line")
           .attr(  "class", "link" )
           .style( "stroke-width", 1 )
           .attr("x1", function(d) { return d.source.x; })
           .attr("y1", function(d) { return d.source.y; })
           .attr("x2", function(d) { return d.target.x; })
           .attr("y2", function(d) { return d.target.y; });
       
        curGroup.link.filter( function( d, i ) { return d.labelEnd; } ).style( 'display', 'none' );
        
        this.indexLinks();

        curGroup.node = this.container.selectAll('p')
           .data( curGroup.nodes )
         .enter().append("svg:circle")
           .attr("class", "node")
           .attr("cx", function(d) { return d.x; })
           .attr("cy", function(d) { return d.y; })
           .attr("nodeId", function(d) { return d.nodeId; })
           .attr("r", function(d) { return Math.sqrt( d.value ) + renderObj.nodeRadius; } )
           .style("fill", function(d) { return renderObj.fill( d.group ); })
           .call( curGroup.force.drag );

        curGroup.node.filter( function( d, i ) { return d.labelEnd; } ).style( 'display', 'none' );

        this.indexNodes();
        
        if( curGroup.index > 0 ) { renderObj.addAncestorNodesToGroup2(); }

        this.addLabels();
        this.renderCollapsedNodeUI();
        this.dealWithRoot();
        
        var placeNodes = [ this.leafArrangement, 'PlaceLeafNodes' ].join('');

        if( this[placeNodes] ) { this[placeNodes](); }

        curGroup.force.on( 'tick', function() { renderObj.onForce(); } );
    },

    dealWithRoot: function() {

        var renderObj = this;
        var curGroup = renderObj.currentGroup;

        if( curGroup.index == 0 ) {
            
            var rootNode = curGroup.nodeInfo[ curGroup.rootId ];

            rootNode.data.fixed = true;

            var cx = renderObj.width / 2;
            var cy = renderObj.height - rootNode.d3.attr('r');

            rootNode.data.originalX = cx;
            rootNode.data.originalY = cy;

            rootNode.data.x = cx;
            rootNode.data.y = cy;
            rootNode.data.px = cx;
            rootNode.data.py = cy;

            rootNode.d3.attr( 'cy', renderObj.height - rootNode.d3.attr('r') )
                       .attr( 'cx', renderObj.width / 2 );

           renderObj.rootIndicator = this.container.append('svg:text')
               .attr( 'class', 'rootLabel' )
               .attr( 'fill', 'none' )
               .attr( 'text-anchor', 'middle' )
               .attr( 'x', cx )
               .attr( 'y', cy );

           renderObj.rootIndicator.append( 'svg:tspan' ).text( 'root' );
        }
    },

    onForce: function() {

        var renderObj = this;

        var currentGroup = renderObj.currentGroup;

        if( currentGroup.link ) {
        
            currentGroup.link.attr("x1", function(d) { return d.source.x; })
                    .attr("y1", function(d) { return d.source.y; })
                    .attr("x2", function(d) { return d.target.x; })
                    .attr("y2", function(d) { return d.target.y; })
                    .style( 'display', function( d ) { return ( ( currentGroup.hideLinks || d.labelEnd ) && ( ! d.visible ) ) ? 'none' : 'inline'; } );
                
            renderObj.updateLabels();

            currentGroup.node
                .attr( 'cx', function( d ) { return d.x; } )
                .attr( 'cy', function( d ) { return d.y; } );

            renderObj.updateCollapsedNodeUI();
        }
    },

    removeRingMenu: function( e ) {

        var renderObj = e.data.renderObj;
        var curGroup = renderObj.currentGroup;

        for( var i = 0, ii = curGroup.ringMenuOptions.length; i < ii; i++ ) {
            
            renderObj.currentGroup.ringMenuOptions[i].d3.remove();
            renderObj.currentGroup.ringMenuOptions[i].jq.remove();
        }

        delete curGroup.ringMenuOptions;

        curGroup.clickedNodeInfo.jq.unbind( 'click', renderObj.removeRingMenu )
                                   .unbind( 'dblclick', renderObj.removeRingMenu );
                
        renderObj.viewer.container.unbind( 'click', renderObj.removeRingMenu );

        setTimeout(
            function() {
                curGroup.clickedNodeInfo.jq.bind(
                    'dblclick',
                    { renderObj: renderObj, nodeId: curGroup.clickedNodeInfo.d3.attr('nodeId') },
                    renderObj.handleNodeDoubleClick ); }, 500 );

        renderObj.eventHandlers.unFixNode( { data: { renderObj: renderObj, nodeId: curGroup.clickedNodeInfo.data.nodeId } } );
        
        renderObj.currentGroup.force.resume();
    },

    initializeLeafNodes: function() { 
       
        var renderObj = this; 
        var curGroup = renderObj.currentGroup; 
        var nodes = curGroup.nodes;

        curGroup.leafNodes = [ ];
    
        for( var i = 0, ii = nodes.length; i < ii; i++ ) {

            if( ( ! nodes[i].children.length ) && ( ! nodes[i].labelEnd ) ) { curGroup.leafNodes.push( nodes[i] ); }
        }

        if( renderObj.leafArrangement == 'line' || renderObj.leafArrangement == 'circle' ) {

            for( var i = 0, ii = curGroup.leafNodes.length; i < ii; i++ ) {

                curGroup.leafNodes[i].fixed = true;
            }
        }
    },

    defaultPlaceLeafNodes: function() {
    },

    circlePlaceLeafNodes: function() {
        
        var viewer = this.viewer; 
        var config = viewer.config;
        
        var leafCount = this.currentGroup.leafNodes.length;

        var radius = ( this.width < this.height ) ? ( ( this.width - ( 2 * config.horizontalPadding ) ) / 2 )
            : ( ( this.height - ( 2 * config.verticalPadding ) ) / 2 );
        var circumference = 2 * radius * Math.PI;
        
        var separationAngle = 360 / leafCount;
        var separationLine = circumference / leafCount;

        var x = ( this.width / 2 ) + radius;
        var y = this.height / 2;

        var currentAngle = 0;
        var center = { x: this.width / 2, y: this.height / 2 };

        for( var i = 0, ii = leafCount; i < ii; i++ ) {

            var leafNode = this.currentGroup.leafNodes[i];

            var radians =  ( Math.PI / 180 ) * currentAngle;

            x = center.x + Math.cos( radians ) * radius;
            y = center.y + ( Math.sin( radians ) * radius );

            leafNode.x = x;
            leafNode.y = y;
            leafNode.px = x;
            leafNode.py = y;
            
            currentAngle += separationAngle;

        }
    },

    linePlaceLeafNodes: function() {

        var viewer = this.viewer; 
        var config = viewer.config;
        
        var leafCount = this.currentGroup.leafNodes.length;
        
        var spaceNeeded = ( config.verticalTipBuffer * leafCount ) + config.verticalTipBuffer;

        var x =  this.width - config.horizontalPadding - viewer.renderResponse.longestLabel;
        var y = ( this.height - spaceNeeded ) / 2;

        for( var i = 0, ii = leafCount; i < ii; i++ ) {

            var leafNode = this.currentGroup.leafNodes[i];

            leafNode.x = x;
            leafNode.y = y;
            leafNode.px = x;
            leafNode.py = y;

            var r = Math.sqrt( leafNode.value ) + this.nodeRadius;

            if( r < config.verticalTipBuffer ) {

                y = y + config.verticalTipBuffer;

            } else {
                
                y = y + ( r + config.verticalTipBuffer );
            }
        }
    },

    updateCollapsedNodeUI: function( ) {

        var collapsedNodeIds = this.currentGroup.collapsedNodeIds;

        for( var i = 0, ii = collapsedNodeIds.length; i < ii; i++ ) {

            var info = this.currentGroup.nodeInfo[ collapsedNodeIds[ i ] ];

            info.collapsedUI.d3.attr( 'cx', info.data.x )
                               .attr( 'cy', info.data.y );
        }
    },

    renderCollapsedNodeUI: function() {

        var collapsedNodeIds = this.currentGroup.collapsedNodeIds;

        for( var i = 0, ii = collapsedNodeIds.length; i < ii; i++ ) {

            this.addCollapsedNodeUI( { nodeInfo: this.currentGroup.nodeInfo[ collapsedNodeIds[ i ] ] } );
        }
    },

    removeCollapsedNodeUI: function( p ) {

        var renderObj = this;
        var curGroup = renderObj.currentGroup;
        var nodeInfo = curGroup.nodeInfo[ p.nodeId ];

        nodeInfo.collapsedUI.d3.remove();
        nodeInfo.collapsedUI.jq.unbind('dblclick').remove();
        nodeInfo.collapsedUI = null;
    },

    toggleCollapsedNodeUI: function( action ) {

        var collapsedNodeIds = this.currentGroup.collapsedNodeIds;

        for( var i = 0, ii = collapsedNodeIds.length; i < ii; i++ ) {

            this.currentGroup.nodeInfo[ collapsedNodeIds[ i ] ].collapsedUI.d3.style( 'display', ( action == 'hide' ) ? 'none' : 'inline' ); 
        }

    },
    
    hideCollapsedNodeUI: function() { this.toggleCollapsedNodeUI( 'hide' ); }, 
    showCollapsedNodeUI: function() { this.toggleCollapsedNodeUI( 'show' ); }, 

    addCollapsedNodeUI: function( p ) {

        var nodeInfo = p.nodeInfo;

        var renderObj = this;

        var collapsedUI = renderObj.container.append('svg:circle')
            .attr('r', ( Math.sqrt( nodeInfo.data.value ) + renderObj.nodeRadius ) / 2 )
            .attr('cx', nodeInfo.data.px )
            .attr('cy', nodeInfo.data.py )
            .attr('nodeId', nodeInfo.data.nodeId )
            .style( 'stroke', renderObj.viewer.config.collapsedCladeColor )
            .style( 'fill', 'none' )
            .style( 'stroke-width', 2 );

        var jqObj = $( collapsedUI[0] );

        if( renderObj.viewer.events.nodeDoubleClick ) {

            jqObj.bind( 'dblclick', { renderObj: this, nodeId: nodeInfo.data.nodeId }, this.handleNodeDoubleClick );
        }
        
        if( renderObj.viewer.events.nodeRightClick ) {
            
            jqObj.bind( 'mouseup', { renderObj: this, nodeId: nodeInfo.data.nodeId }, this.handleNodeRightClick );
        }

        nodeInfo.collapsedUI = { d3: collapsedUI, jq: jqObj };
    },

    toggleLabels: function( p ) {

        var group = this.groups[ p.index ];

        for( var i = 0, ii = group.labels.length; i < ii; i++ ) {

            var label = group.labels[i];

            label.d3.style( 'display', ( p.action == 'show' ) ? 'inline' : 'none' );

            if( p.exceptions ) {

                for( var j = 0, jj = p.exceptions.length; j < jj; j++ ) {

                    if( label.d3.attr('nodeId') == p.exceptions[ j ] ) {

                        label.d3.style( 'display', ( p.action == 'show' ) ? 'none' : 'inline' );
                    }
                }
            }
        }
    },

    hideLabels: function( p ) { p.action = 'hide'; this.toggleLabels( p ); },
    showLabels: function( p ) { p.action = 'show'; this.toggleLabels( p ); },

    postExpandClade: function() {

        var viewer = this;
        var renderObj = viewer.renderObj;

        var curGroup = renderObj.currentGroup;
        var oldGroup = renderObj.groups[ curGroup.index - 1 ];

        var expandedNode = oldGroup.nodeInfo[ oldGroup.expandedNodeId ].d3;
        var prevRootInfo = oldGroup.nodeInfo[ oldGroup.rootId ];
        var prevRoot = prevRootInfo.d3;

        var expandedNodeCX = parseFloat( expandedNode.attr('cx') );
        var expandedNodeCY = parseFloat( expandedNode.attr('cy') );

        curGroup.force.stop();
        curGroup.node.style( 'display', 'none' );
        curGroup.link.style( 'display', 'none' );
        curGroup.hideLinks = true;
        renderObj.hideCollapsedNodeUI();
       
        renderObj.hideLabels( { index: curGroup.index } );

        for( var rootId in renderObj.rootIds ) {

           d3.select( curGroup.nodeInfo[ rootId ].js )
             .style( 'display', 'inline' );

           if( curGroup.indexedLinks[ rootId ] ) {
                curGroup.indexedLinks[ rootId ].data.visible = true;
            }
        }
        
        var rootNodeInfo = curGroup.nodeInfo[ curGroup.rootId ];
        var rootNode = rootNodeInfo.d3;

        rootNodeInfo.data.px = expandedNodeCX;
        rootNodeInfo.data.x = expandedNodeCX;
        rootNodeInfo.data.py = expandedNodeCY;
        rootNodeInfo.data.y = expandedNodeCY;

        rootNode.style( 'fill', expandedNode.style('fill') )
                .style( 'display', 'inline' )
                .attr( 'cx', expandedNodeCX )
                .attr( 'cy', expandedNodeCY );

        expandedNode.style( 'display', 'none' );

        if( renderObj.rootHasMoved ) {

            var prevInfo = renderObj.groups[0].nodeInfo[ renderObj.groups[0].rootId ];
            prevInfo.d3.attr( 'cx', prevInfo.data.originalX ).attr( 'cy', prevInfo.data.originalY );
        }

        var newCX = prevRootInfo.data.x;
        var newCY = prevRootInfo.data.y - renderObj.viewer.config.branchLength - parseFloat( prevRoot.attr('r') ) - parseFloat( rootNode.attr('r') );
        
        curGroup.node.each(
                function( d, i ) {
                    if( ! renderObj.rootIds[ d.nodeId ] ) {
                        var d3Obj = d3.select(this);
                        d.px = d.x = newCX;
                        d.py = d.y = newCY;
                        d3Obj.attr( 'cx', newCX ).attr( 'cy', newCY ); } } );

        curGroup.indexedLinks[ curGroup.rootId ].d3.transition().delay( 500 ).duration( 250 ).attr( 'x2', newCX ).attr( 'y2', newCY );
        rootNode.transition().delay( 500 ).duration( 250 ).attr( 'cx', newCX ).attr( 'cy', newCY );

        setTimeout( renderObj.animateExpandNode, 2000, { delay: 50, curNode: rootNodeInfo, renderObj: renderObj, future: { x: parseFloat( prevRoot.attr('cx') ), y: parseFloat( newCY ) } } );

        setTimeout(
            function() {

                curGroup.force.start();
                renderObj.showCollapsedNodeUI();
                renderObj.showLabels( { index: curGroup.index } );
                curGroup.hideLinks = false;

            }, 2000 + ( ( curGroup.nodes.length - curGroup.labels.length ) * 50 ) );
    },

    animateExpandNode: function( p ) {

        console.log( 'begin');

        var renderObj = p.renderObj;
        var curNode = p.curNode;
        var d3Node = curNode.d3;

        var angleMult = - 90 / curNode.data.children.length;
        var branchLength = renderObj.viewer.config.branchLength + ( d3Node.attr('r') * 2 ) + 50;

        var delay = p.delay;

        for( var i = 0, ii = curNode.data.children.length; i < ii; i++ ) {

            var angle = ( i * angleMult ) - 45;
            var radians = angle * ( Math.PI / 180 );

            var newX = p.future.x + ( branchLength * Math.cos( radians ) );
            var newY = p.future.y + ( branchLength * Math.sin( radians ) );

            var child = renderObj.currentGroup.nodeInfo[ curNode.data.children[ i ] ];

            child.d3.style( 'display', 'inline' );
            child.d3.transition().delay( p.delay ).duration( 200 ).attr( 'cx', newX ).attr( 'cy', newY );
            child.data.px = child.data.x = newX;
            child.data.py = child.data.y = newY;

            //if( child.label ) { child.label.style( 'display', 'inline' ); }

            p.delay += 50;

            renderObj.animateExpandNode( { delay: p.delay, curNode: child, renderObj: renderObj, future: { x: parseFloat( newX ), y: parseFloat( newY ) } } );
            //setTimeout( renderObj.animateExpandNode, p.delay + 100, { delay: p.delay + 100, curNode: child, renderObj: renderObj, future: { x: parseFloat( newX ), y: parseFloat( newY )} } );
        }
    },

    showCollapseOptions: function( e ) {
        
        if( $('.collapseOption').length ) { return; }

        var nodeInfo = e.data.nodeInfo;
        var renderObj = e.data.renderObj;
        var d3Obj = e.data.d3Obj;

        var strokeWidth = 5;
        var textPad = 5;
        var containerOffset = renderObj.viewer.container.offset();

        var circle = renderObj.container.append('svg:circle')
            .attr( 'r', d3Obj.attr('r') + strokeWidth )
            .attr( 'cx', d3Obj.attr('cx') )
            .attr( 'cy', d3Obj.attr('cy') )
            .attr( 'class', 'collapseOption' )
            .style( 'fill', '#98df8a' )
            .style( 'stroke', 'white' )
            .style( 'stroke-width', strokeWidth );

        var text = renderObj.container.append('svg:text');
        text.append('svg:tspan').text('Collapse Node');
        var textDom = $( text[0] );

        var rect = renderObj.container.append('svg:rect')
            .attr( 'width', textDom.width() + ( 2 * textPad ) )
            .attr( 'height', textDom.height() + ( 2 * textPad ) )
            .attr( 'x', containerOffset.left + d3Obj.attr('cx') + strokeWidth + d3Obj.attr('r')  )
            .attr( 'y', containerOffset.top + d3Obj.attr('cy') );

        text.attr( 'x', rect.attr('x') + textPad )
            .attr( 'y', rect.attr('y') + textPad );

        $( circle[0] ).bind( 'mouseout', { renderObj: renderObj }, renderObj.hideCollapseOptions );
    },
    
    hideCollapseOptions: function( e ) {
       
        e.data.renderObj.container.selectAll('.collapseOption').remove();
    },

    indexNodes: function() {

        var renderObj = this;
        var curGroup = renderObj.currentGroup;

        curGroup.nodeInfo = { };
        curGroup.collapsedNodeIds = [];
        
        curGroup.node.filter( function( d, i ) { return (! d.labelEnd); } ).each(
            function( d, i ) {

                var nodeId = d.nodeId;

                curGroup.nodeInfo[ nodeId ] = { data: d, d3: d3.select(this), jq: $(this), index: i, js: this };

                if( d.collapsed ) { curGroup.collapsedNodeIds.push( nodeId ); }

                if( renderObj.viewer.events.nodeDoubleClick ) {

                    curGroup.nodeInfo[ nodeId ].jq.bind( 'dblclick', { renderObj: renderObj, nodeId: nodeId }, renderObj.handleNodeDoubleClick );
                }
                
                if( renderObj.viewer.events.nodeRightClick ) {
                    
                    curGroup.nodeInfo[ nodeId ].jq.bind( 'mouseup', { renderObj: renderObj, nodeId: nodeId }, renderObj.handleNodeRightClick );
                }
            }
        );
    },

    isFixed: function( nodeInfo ) {

        return ( nodeInfo.data.fixed ) ? 'fixed' : 'unFixed';
    },

    navType: function( nodeInfo ) {

        var nodeId = nodeInfo.d3.attr('nodeId');

        var nodeInfo = this.currentGroup.nodeInfo[ nodeId ].data;

        if( nodeInfo.children.length ) {

            return 'collapse';

        } else if( nodeInfo.collapsed ) {

            return 'expand';

        } else {

            return 'leaf';
        }
    },

    gatherRingMenuOptions: function() {

        var renderObj = this;
        var curGroup = renderObj.currentGroup;
        var eventDefinitions = renderObj.viewer.events.nodeDoubleClick;

        curGroup.ringMenuOptions = [ ];

        for( var i = 0, ii = eventDefinitions.options.length; i < ii; i++ ) {
            
            var option = eventDefinitions.options[ i ];

            if( option.type == 'depends' ) {

                var result = renderObj[ option.test.handler ]( curGroup.nodeInfo[ curGroup.clickedNodeInfo.data.nodeId ] );

                if( option.test[ result ] ) {

                    curGroup.ringMenuOptions.push( option.test[result] );
                }

            } else {
            
                curGroup.ringMenuOptions.push( option );
            }
        }
    },

    createRingMenuOptions: function() {

        var renderObj = this;
        var curGroup = renderObj.currentGroup;
        var options = curGroup.ringMenuOptions;

        var angleMult = 360 / options.length;
        var menuRadius = 50;

        var clickedNodeX = curGroup.clickedNodeInfo.data.x;
        var clickedNodeY = curGroup.clickedNodeInfo.data.y;
        var clickedNodeR = curGroup.clickedNodeInfo.d3.attr( 'r' );

        for( var i = 0, ii = options.length; i < ii; i++ ) {

            var angle = i * angleMult;
            var radians = angle * ( Math.PI / 180 );

            var optionTextCenterX = clickedNodeX + ( menuRadius * Math.cos( radians ) );
            var optionTextCenterY = clickedNodeY + ( menuRadius * Math.sin( radians ) );

            var option = options[ i ];
            
            var d3Obj = renderObj.container.append('svg:text')
                    .attr( 'x', optionTextCenterX )
                    .attr( 'y', optionTextCenterY )
                    .attr( 'class', 'd3EditNodeLabel' )
                    .attr( 'text-anchor', 'middle' );

            option.d3 = d3Obj;

            var tspan = d3Obj.append( 'svg:tspan' ).text( option.text );
   
            var handler = ( option.external )
                ? renderObj.viewer.externalHandlers[ option.handler ]
                : renderObj.eventHandlers[ option.handler ];

            option.jq = $( d3Obj[0] ).bind( 'click', { renderObj: renderObj }, renderObj.removeRingMenu )
                                     .bind( 'click', { optionDef: option, nodeId: curGroup.clickedNodeInfo.data.nodeId, option: option, renderObj: renderObj }, handler );

            var bbox = d3Obj[0][0].getBBox();
            var widthHalved = bbox.width / 2;

            if( ( BioSync.Common.getDistance( {
                point1: { x: clickedNodeX, y: clickedNodeY },
                point2: { x: optionTextCenterX - widthHalved, y: optionTextCenterY } } ) < clickedNodeR ) ||

                ( BioSync.Common.getDistance( {
                point1: { x: clickedNodeX, y: clickedNodeY },
                point2: { x: optionTextCenterX + widthHalved, y: optionTextCenterY } } ) < clickedNodeR ) ) {

                    tspan.remove();

                    var words = option.text.split(' ');

                    for( var j = 0, jj = words.length; j < jj; j++ ) {

                        tspan = d3Obj.append( 'svg:tspan' ).text( words[j] );
                        tspan.attr( 'x', optionTextCenterX );
                        if( j != 0 ) { tspan.attr( 'dy', '1em' ); }
                    }

                    d3Obj.attr( 'y', optionTextCenterY - d3Obj[0][0].getBBox().height / 4 );
            }
        }
    },

    makeWayForRingMenu: function() { 

        var renderObj = this;
        var curGroup = renderObj.currentGroup;

        var clickedNodeX = curGroup.clickedNodeInfo.data.x;
        var clickedNodeY = curGroup.clickedNodeInfo.data.y;

        for( var id in curGroup.nodeInfo ) {

            var curNodeInfo = curGroup.nodeInfo[ id ];

            if( curGroup.clickedNodeInfo.data.nodeId != id ) {

                var curNodeX = curNodeInfo.data.x;
                var curNodeY = curNodeInfo.data.y;

                distance = BioSync.Common.getDistance( { point1: { x: clickedNodeX, y: clickedNodeY },
                                                         point2: { x: curNodeX, y: curNodeY } } );

                if( distance < 200 ) {

                    if( id == renderObj.groups[0].rootId ) { renderObj.rootHasMoved = true; }

                    var angle = Math.atan( ( curNodeY - clickedNodeY ) / ( curNodeX - clickedNodeX ) );
       
                    var dx = ( 200 * Math.cos( angle ) );
                    var dy = ( 200 * Math.sin( angle ) );

                    if( curNodeX < clickedNodeX ) { dx *= -1; dy *= -1; }

                    var newX = clickedNodeX + dx;
                    var newY = clickedNodeY + dy;
                    var r = curNodeInfo.d3.attr('r');
                    
                    curNodeInfo.d3.transition().duration( 500 ).attr( 'cx', newX ).attr( 'cy', newY );

                    if( curNodeInfo.labelInfo ) {

                        var textAnchor = curNodeInfo.labelInfo.d3.attr('text-anchor');
                        var labelDX = renderObj.nodeRadius + 2;
                        var labelDY = curNodeInfo.labelInfo.height / 2;

                        if( ( newX > clickedNodeX ) && ( textAnchor =='end' ) ) {

                            curNodeInfo.labelInfo.d3.attr( 'transform', [ 'translate(', labelDX, labelDY, ')' ].join(' ') )
                                                    .attr( 'text-anchor', 'start' );

                        } else if( ( newX < clickedNodeX ) && ( textAnchor == 'start' ) ) {

                            curNodeInfo.labelInfo.d3.attr( 'transform', [ 'translate(', labelDX * - 1, labelDY, ')' ].join(' ') )
                                                    .attr( 'text-anchor', 'end' );
                        }

                        curNodeInfo.labelInfo.d3.transition().duration( 500 ).attr( 'x', newX + r ).attr( 'y', newY );
                    }

                    if( curNodeInfo.collapsedUI ) {
                        curNodeInfo.collapsedUI.d3.transition().duration( 500 ).attr( 'cx', newX ).attr( 'cy', newY );
                    }

                    //this.ringMenuUpdateAdjacentNodes( { nodeInfo: renderObj.curGroup.nodeInfo[ id ], newCX: newX, newCY: newY } );
                }
            }
        }

        renderObj.container.selectAll("line.link").transition().duration(500).style( 'display', 'none' );
    },

    handleNodeRightClick: function( e ) {

        if( e.which == 3 ) {

            var renderObj = e.data.renderObj;
            var nodeId = e.data.nodeId;
            
            var curGroup = renderObj.currentGroup;
            var event = renderObj.viewer.events.nodeRightClick;

            if( event.type = 'action' ) {
                
                var handler = ( event.external )
                    ? renderObj.viewer.externalHandlers[ event.handler ]
                    : renderObj.eventHandlers[ event.handler ];
               
                handler( { data: { nodeId: e.data.nodeId, renderObj: renderObj } } );
            }
        }
    },

    handleNodeDoubleClick: function( e ) {
        
        var renderObj = e.data.renderObj;
        var nodeId = e.data.nodeId;

        var curGroup = renderObj.currentGroup;

        var eventType = renderObj.viewer.events.nodeDoubleClick.type;

        if( eventType = 'ringMenu' ) {

            var clickedNodeInfo = curGroup.nodeInfo[ nodeId ];

            curGroup.clickedNodeInfo = clickedNodeInfo;

            curGroup.force.stop();

            renderObj.gatherRingMenuOptions();
            renderObj.createRingMenuOptions();

            renderObj.viewer.container.bind( 'click', { renderObj: renderObj }, renderObj.removeRingMenu )

            clickedNodeInfo.jq.bind( 'click', { renderObj: renderObj }, renderObj.removeRingMenu )
                              .unbind( 'dblclick', renderObj.handleNodeDoubleClick )
                              .bind( 'dblclick', { renderObj: renderObj }, renderObj.removeRingMenu );

            renderObj.makeWayForRingMenu();
        }
    },

    ringMenuUpdateAdjacentNodes: function( p ) {

        var nodeInfo = p.nodeInfo;

        var curGroup = this.currentGroup;
        var d3Node = nodeInfo.d3;

       if( currentGroup.linksByTargetNodeId[ nodeInfo.id ] ) {

           var sourceNode =  currentGroup.linksByTargetNodeId[ nodeInfo.id ];
           var d3Source =  currentGroup.linksByTargetNodeId[ nodeInfo.id ];

           var distance = BioSync.Common.getDistance( { point1: { x: newCX, y: newCY },
                                                        point2: { x: d3Source.attr('cx'), y: d3Source.attr('cy') } } );

           //if( distance

       }

         
    },

    indexLinks: function() {

        var renderObj = this;
        var curGroup = this.currentGroup;

        curGroup.indexedLinks = { };
        
        curGroup.link.filter( function( d, i ) { return ( ! d.labelEnd ); } ).each(
            function( d, i ) {
                var targetNodeId = curGroup.nodes[ d.target.index ].nodeId;
                var sourceNodeId = curGroup.nodes[ d.source.index ].nodeId;
                curGroup.indexedLinks[ targetNodeId ] = { d3: d3.select(this), data: d, sourceNodeId: sourceNodeId, js: this }; } );
    },

    addLabels: function() {

        var renderObj = this;
        var viewer = renderObj.viewer;

        var curGroup = renderObj.currentGroup;

        curGroup.labels = [ ];
        
        curGroup.node.filter( function( d, i ) { return ( ( ! d.labelEnd ) && ( d.name ) ); } ).each(
            function( d, i ) {

                var d3Label = renderObj.container.append( 'svg:text' )
                    .attr( 'nodeId', d.nodeId )
                    .attr( 'class', 'defaultCursor' );

                d3Label.append( 'svg:tspan' ).text( d.name );
                
                var bbox = d3Label[0][0].getBBox();

                var jqLabel = $( d3Label[0] ).bind( 'mousedown', function() { return false; } );

                var labelInfo = { d3: d3Label, jq: jqLabel, nodeId: d.nodeId, width: bbox.width, height: bbox.height };

                curGroup.labels.push( labelInfo );
                curGroup.nodeInfo[ d.nodeId ].labelInfo = labelInfo;
        } );               
    },

    updateLabels: function() {

        var renderObj = this;
        var curGroup = renderObj.currentGroup;
        var labels = curGroup.labels;
            
        for( var i = 0, ii = labels.length; i < ii; i++ ) {

            var label = labels[ i ];

            var link = curGroup.indexedLinks[ label.nodeId ];

            var angle = Math.atan( ( link.data.target.y - link.data.source.y ) /
                                   ( link.data.target.x - link.data.source.x ) ) * ( 180 /  Math.PI );
                
            var textAnchor = 'start';
            var dx = renderObj.nodeRadius + 2;

            if( ( ( angle < 0 ) && ( angle > -90 ) && ( link.data.source.y < link.data.target.y ) ) ||
                ( ( angle > 0 ) && ( angle < 90 ) && ( link.data.target.y < link.data.source.y ) ) ) {
            
                textAnchor = 'end'; dx = dx * -1;
            }

            label.d3.attr( 'transform', [ 'translate(', dx, label.height / 2, ')' ].join(' ') )
                     .attr( 'x', ( link.data.target.x ) )
                     .attr( 'y', ( link.data.target.y ) )
                     .attr( 'text-anchor', textAnchor );

            var hiddenNode = curGroup.labelEndNodes[ label.nodeId ];
            var newX = link.data.target.x + dx;
            
            if( textAnchor == 'start' ) { newX += label.width; }
            else { newX -= label.width; }

            hiddenNode.x = newX; hiddenNode.px = newX;
            hiddenNode.y = link.data.target.y; hiddenNode.py = link.data.target.y;
       } 
    }
}


BioSync.TreeViewer.RenderUtil.d3.sunburst.prototype = {

    initialize: function( p ) {

        var viewer = this.viewer;

        this.width = viewer.myWidth;
        this.height = viewer.myHeight;
        this.color = d3.scale.category20();
        this.radius = Math.min( this.width, this.height ) / 2;

        this.container = d3.select( '#' + viewer.containerId )
            .append('svg:svg').attr( 'width',  this.width ).attr( 'height', this.height )
                .append("svg:g")
                    .attr( 'transform', "translate(" + this.width / 2 + "," + this.height / 2 + ")" );

        this.partition = d3.layout.partition()
             .sort( null )
             .size( [2 * Math.PI, this.radius * this.radius] )
             .value( function(d) { return 1; } );

        this.arc = d3.svg.arc()
             .startAngle(function(d) { return d.x; })
             .endAngle(function(d) { return d.x + d.dx; })
             .innerRadius(function(d) { return Math.sqrt(d.y); })
             .outerRadius(function(d) { return Math.sqrt(d.y + d.dy); });

        BioSync.Common.disableSelection( $( '#' + viewer.containerId ) );
    },

    renderReceivedTree: function() {

        var viewer = this.viewer;
        var renderObj = this;

        var response = viewer.renderResponse;

        var path = this.container.data( [ viewer.renderResponse.renderData ] ).selectAll("path")
           .data( this.partition.nodes )
         .enter().append( 'svg:path' )
           .attr("display", function(d) { return d.depth ? null : "none"; }) // hide inner ring
           .attr( "d", this.arc )
           .attr("fill-rule", "evenodd")
           .style("stroke", "#fff")
           .style("fill", function(d) { return renderObj.color((d.children ? d : d.parent).name); } );
    }
}
