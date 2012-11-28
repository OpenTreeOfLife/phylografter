BioSync.TreeViewer.RenderUtil.Column = function( renderObj ) {

    this.renderObj = renderObj;
    this.make = BioSync.Common.makeEl;
    return this;
}

BioSync.TreeViewer.RenderUtil.Column.prototype = {

    config: {

        nodeSelectorDistanceThreshold: 50,
        columnConnectionColor: 'blue',
        columnConnectionWidth: 2,
        nodeNotifyTimeout: 2000,
        nodeNotifyYOffset: 30
    },

    initialize: function( p ) {

        this.index = p.index;

        this.collapsedNodeIds = [ ];

        this.makeColumnElementHierarchy();
        
        BioSync.Common.storeObjPosition( this.container, this );

        this.columnConnections = { ancestor: undefined, descendant: undefined };

        return this;
    },

    makeColumnElementHierarchy: function() {

        this.container =
            this.make('div')
                .css( { 'position': 'absolute', 
                        'box-sizing': 'border-box',
                        '-moz-box-sizing': 'border-box',
                        '-ms-box-sizing': 'border-box',
                        '-webkit-box-sizing': 'border-box' } )
                .height( '100%' );

        this.svgWrapper =
            this.make('div')
               .css( { 'overflow': 'auto',
                       'box-sizing': 'border-box',
                       '-moz-box-sizing': 'border-box',
                       '-ms-box-sizing': 'border-box',
                       '-webkit-box-sizing': 'border-box' } )
               .height( '100%' );
            
        this.svgDiv = this.make('div').css( { 'position': 'absolute' } );

        this.canvas = Raphael( this.svgDiv.get(0), 300, 100 );

        this.container.append( this.svgWrapper.append( this.svgDiv ) );
    },


    renderReceivedClade: function( response ) {

        this.renderClade( eval( '(' + response + ')' ) );
    },

    renderClade: function( cladeInfo ) {

        this.resetColumn();

        this.setElementSizes( cladeInfo.canvas );

        this.rootNodeId = cladeInfo.rootId;
        this.nodeInfo = cladeInfo.nodeInfo;
        this.collapsedNodeIds = cladeInfo.collapsedNodeIds;

        this.path =
            this.canvas.path( cladeInfo.pathString )
                       .attr( { "stroke": this.renderObj.viewer.config.treeColor,
                                "stroke-linecap": 'square',
                                "stroke-width": this.renderObj.viewer.config.pathWidth } );

        this.renderLabels();
        
        this.renderCollapsedNodeUI();
       
        if( this.renderObj.viewer.events.nodeClick || this.renderObj.viewer.events.nodeRightClick ) { this.addNodeSelector(); }
        
        this.verticallyCenterCanvas();
    },

    verticallyCenterCanvas: function( p ) {

        if( this.myHeight > this.svgDiv.height() )  {
            
            this.centerOffset = ( this.myHeight / 2 ) - ( this.svgDiv.height() / 2 );
            this.svgDiv.css( { top: this.centerOffset } );

        } else {

            this.centerOffset = 0;
        }
    },

    verticallyExpandNode: function( p ) {
     
        this.verticallyExpandingNode = p.nodeId;

        this.renderObj.verticallyExpandNode( { column: this, nodeId: p.nodeId } );
    },

    afterVerticalExpand: function() {

        this.renderObj.scrollToNode( { column: this, nodeId: this.verticallyExpandingNode } );

        this.makeSpinAnimationAroundNode( { nodeId: this.verticallyExpandingNode } );

        setTimeout( $.proxy( this.showExpandedNodeDialogue, this ), 1000 );
    },

    showExpandedNodeDialogue: function() {

        this.nodeNotify( { 'text': 'Expanded Node', node: this.nodeInfo[ this.verticallyExpandingNode ] } );
    },

    nodeNotify: function( p ) {

        this.isNodeNotifying = true;

        BioSync.Common.notify( {
            text: p.text,
            appendTo: this.svgDiv,
            timeout: this.config.nodeNotifyTimeout,
            x: p.node.x,
            y: p.node.y + this.config.nodeNotifyYOffset } );

        setTimeout( $.proxy( this.unsetNodeNotifying, this ), this.config.nodeNotifyTimeout );
    },

    unsetNodeNotifying: function() { this.isNodeNotifying = false; },
    
    addNodeSelector: function() {

        var config = this.renderObj.viewer.config;

        this.nodeSelector =
            this.canvas.circle( 0, 0, config.nodeSelectorRadius )
                .attr( { fill: config.nodeSelectorColor,
                         stroke: config.nodeSelectorColor,
                         "fill-opacity": config.nodeSelectorOpacity,
                         "stroke-width": config.pathWidth } ).hide();
                
        $( this.nodeSelector.node ).bind( 'mousedown', { }, $.proxy( this.handleNodeSelectorClick, this ) )
                                   .hover( BioSync.Common.setMouseToPointer, BioSync.Common.setMouseToDefault );

        this.container.bind( 'mousemove', { }, $.proxy( this.updateNodeSelectorPosition, this ) );
    },

    handleNodeSelectorClick: function( p ) {
        
        var viewerEventObj = this.renderObj.viewer.events;

        if( ( p.which == 1 ) && ( viewerEventObj.nodeClick ) ) {

            this[ viewerEventObj.nodeClick.handler ]( viewerEventObj.nodeClick );

        } else if( ( p.which == 3 ) && ( viewerEventObj.nodeRightClick ) ) {
            
            this[ viewerEventObj.nodeRightClick.handler ]( viewerEventObj.nodeRightClick );
        }
    },

    highlightContextMenuOption: function( p ) {

        $( this ).css( { 'background-color': '#FFA500' } );
    },

    removeContextMenuOptionHighlight: function( p ) {

        $( this ).css( { 'background-color': '' } );
    },

    showNodeContextMenu: function( p ) {

        this.nodeContextMenu =
            this.make('div')
                .css( { 'left': this.nodeInfo[ this.closestNodeToMouse.id ].x,
                        'top': this.nodeInfo[ this.closestNodeToMouse.id ].y,
                        'background-color': '#DADADA',
                        'font-size': '.75em',
                        'text-align': 'center',
                        'z-index': 5000,
                        'position': 'absolute',
                        '-moz-border-radius': '10px',
                        'border-radius': '10px',
                        'width': 'auto',
                        'padding': '5px' } )
                .appendTo( this.svgDiv );
        
        this.nodeContextMenuOptionContainer =
            this.make( 'ul' ).css( {
                'margin': 2,
                'padding': 2,
                'background-color': 'white' } ).appendTo( this.nodeContextMenu );

        for( var i = 0, ii = p.options.length; i < ii; i++ ) {

            if( ( this.nodeInfo[ this.closestNodeToMouse.id ].children.length == 0 ) &&
                ( p.options[i].text == 'Collapse Clade' ) ) { continue; }

            this.nodeContextMenuOptionContainer.append(
                this.make('li').css( { 'border-bottom': '1px dotted #E1E1E1',
                                       'white-space': 'nowrap',
                                       'padding': '5px' } )
                               .text( p.options[i].text )
                               .hover( BioSync.Common.setMouseToPointer, BioSync.Common.setMouseToDefault )
                               .hover( this.highlightContextMenuOption, this.removeContextMenuOptionHighlight )
                               .bind( 'click', { }, $.proxy( this.closeNodeContextMenu, this ) )
                               .bind( 'click', { }, BioSync.Common.setMouseToDefault )
                               .bind( 'click', { }, $.proxy( this[ p.options[i].handler ], this ) ) );
        }
   
       $(document).bind( 'click', { }, $.proxy( this.checkForClickOutsideOfNodeContextMenu, this ) );
    },

    nodePreviouslyExpanded: function( p ) {

        this.expandedNodeId = p.nodeId;

        this.collapsedNodeObjs[ this.expandedNodeId ].nodePreviouslyExpanded();
    },

    showEditTaxonDialogue: function( p ) {

        this.recentlyEditedNodeId = p.nodeId;

        this.renderObj.showEditTaxonDialogue( { nodeId: p.nodeId, column: this } );
    },

    handleAddToClipboardOptionClick: function() {

        this.nodeIdToAddToClipboard = this.closestNodeToMouse.id;

        if( this.renderObj.viewer.isLoggedIn ) {

            this.renderObj.showAddToClipboardForm( { column: this, nodeId: this.nodeIdToAddToClipboard } );

        } else {

            BioSync.Common.notify( {
                text: 'Please login to use the clipboard.',
                timeout: 5000,
                x: this.renderObj.viewPanel.myWidth / 2,
                y: this.renderObj.viewPanel.myHeight / 2 } );
        }
    },

    clipboardItemAdded: function() {

        this.renderObj.scrollToNode( { column: this, nodeId: this.nodeIdToAddToClipboard } );

        this.makeSpinAnimationAroundNode( { nodeId: this.nodeIdToAddToClipboard } );

        setTimeout( $.proxy( this.showNodeAddedToClipboardDialogue, this ), 1000 );

    },

    showNodeAddedToClipboardDialogue: function() {

        this.nodeNotify( { 'text': 'Clade Added To Clipboard', node: this.nodeInfo[ this.nodeIdToAddToClipboard ] } );
    },

    handleEditNodeOptionClick: function() {

        this.recentlyEditedNodeId = this.closestNodeToMouse.id;
        
        this.renderObj.showEditNodeForm( { column: this, nodeId: this.recentlyEditedNodeId } );
    },

    afterNodeEdited: function() {

        this.renderObj.scrollToNode( { column: this, nodeId: this.recentlyEditedNodeId } );

        this.makeSpinAnimationAroundNode( { nodeId: this.recentlyEditedNodeId } );

        setTimeout( $.proxy( this.showEditedNodeDialogue, this ), 1000 );
    },

    showEditedNodeDialogue: function() {
        
        this.nodeNotify( { 'text': 'Node Edited', node: this.nodeInfo[ this.recentlyEditedNodeId ] } );
    },

    handleCollapseCladeOptionClick: function() {

        this.recentlyCollapsedNodeId = this.closestNodeToMouse.id;
        
        this.renderObj.collapseClade( { column: this, nodeId: this.closestNodeToMouse.id } );
    },

    collapseExpandedNode: function( p ) {

        this.expandedNodeId = undefined;

        this.renderObj.collapseExpandedNode( { column: this, nodeId: p.nodeId } );
    },

    afterCladeCollapse: function() {

        this.renderObj.scrollToNode( { column: this, nodeId: this.recentlyCollapsedNodeId } );

        this.makeSpinAnimationAroundNode( { nodeId: this.recentlyCollapsedNodeId } );
        
        setTimeout( $.proxy( this.showCollapsedNodeDialogue, this ), 1000 );
    },

    showCollapsedNodeDialogue: function() {
        
        this.nodeNotify( { 'text': 'Collapsed Node', node: this.nodeInfo[ this.recentlyCollapsedNodeId ] } );
    },
        
    makeSpinAnimationAroundNode: function( p ) {

        var canvas = this.canvas;

        var r1 = 10;
        var r2 = 10;
        var strokeWidth = 7;
        var strokeColor = 'red';
        var sectorsCount = 7;
        var cx = this.nodeInfo[ p.nodeId ].x;
        var cy = this.nodeInfo[ p.nodeId ].y;

        var opacity = [ ]; 
        var sectors = [ ];

        var beta = 2 * Math.PI / sectorsCount;
        var pathParams = { 'stroke': strokeColor, "stroke-width": strokeWidth, "stroke-linecap": "round" };

        for( var i = 0; i < sectorsCount; i++ ) {
        
            var alpha = beta * i - Math.PI / 2;
            var cos = Math.cos( alpha );
            var sin = Math.sin( alpha );
            opacity[i] = 1 / sectorsCount * i;
           
            sectors[i] = canvas.path([["M", cx + r1 * cos, cy + r1 * sin], ["L", cx + r2 * cos, cy + r2 * sin]]).attr(pathParams);
        }

        var tick;
        ( function ticker() {
              opacity.unshift( opacity.pop() );
              
              for( var i = 0; i < sectorsCount; i++ ) {
                  sectors[i].attr("opacity", opacity[i]);
              }
              
              canvas.safari();
              
              tick = setTimeout(ticker, 1000 / sectorsCount);
        } )();

        setTimeout( function() { clearTimeout( tick ); for( var i = 0; i < sectorsCount; i++ ) { sectors[i].remove(); } }, 4000 );
    },

    resetColumn: function() {

        this.canvas.clear();

        this.container.unbind( 'mousemove', { }, $.proxy( this.updateNodeSelectorPosition, this ) );

        for( var i = 0, ii = this.collapsedNodeIds.length; i < ii; i++ ) {

            this.collapsedNodeObjs[ this.collapsedNodeIds[ i ] ].hiddenHover.empty().remove();

            delete this.collapsedNodeObjs[ this.collapsedNodeIds[ i ] ];
        }

        this.svgDiv.css( { top: 0 } );
    },

    emptyColumn: function() {

        this.resetColumn();

        this.container.empty().remove();
    },

    hideColumn: function( p ) {

        if( p.onSuccess ) {
        
            this.container.hide( 'slow', p.onSuccess );

        } else {
        
            this.container.hide( 'slow' );
        }
    },

    checkForClickOutsideOfNodeContextMenu: function( e ) {
        
        if( ( this.nodeContextMenu ) && ( ! BioSync.Common.isMouseOnElement( { x: e.pageX, y: e.pageY, el: this.nodeContextMenu } ) ) ) {

            this.closeNodeContextMenu();
        }
    },

    closeNodeContextMenu: function() {
    
       $(document).unbind( 'click', { }, $.proxy( this.checkForClickOutsideOfNodeContextMenu, this ) );

       this.nodeContextMenu.empty().remove();

       delete this.nodeContextMenu;
    },

    isACollapsedNodeMenuVisible: function() {

        for( var i = 0, ii = this.collapsedNodeIds.length; i < ii; i++ ) {
       
            if( this.collapsedNodeObjs[ this.collapsedNodeIds[ i ] ].isMenuVisible ) {

                return true;
            }
        }

        return false;
    },

    updateNodeSelectorPosition: function( p ) {

        if( BioSync.Common.isModalBoxVisible() ||
            BioSync.Common.symbolDragInfo ||
            this.isACollapsedNodeMenuVisible() ||
            this.isNodeNotifying ||
            this.nodeContextMenu ||
            this.hoveringLabel || 
            this.renderObj.isViewPanelHorizontallyScrolling ||
            this.renderObj.isViewPanelVerticallyScrolling ) { this.nodeSelector.hide(); return; }

        this.closestNodeToMouse = this.findNodeClosestToMouse( {
            coords: this.translateDOMPointToCanvas( { x: p.pageX, y: p.pageY } ),
            currentNodeId: this.rootNodeId } );

        if( ( this.closestNodeToMouse.distance < this.config.nodeSelectorDistanceThreshold ) &&
            ( this.collapsedNodeIds.indexOf( this.closestNodeToMouse.id ) == -1 ) ) {

            this.nodeSelector.attr( {
                cx: this.nodeInfo[ this.closestNodeToMouse.id ].x,
                cy: this.nodeInfo[ this.closestNodeToMouse.id ].y } ).show().toFront();

        } else {

            this.nodeSelector.hide();
        }

    },

    translateDOMPointToCanvas: function( p ) {

        return { x: p.x - ( this.myPosition.left + this.renderObj.viewPanel.myOffset.left - this.renderObj.viewPanel.scrollLeft() ),
                 y: p.y - ( this.myPosition.top + this.centerOffset + this.renderObj.viewPanel.myOffset.top - this.renderObj.viewPanel.scrollTop() ) }
    },

    findNodeClosestToMouse: function( p ) {

        var currentNode = this.nodeInfo[ p.currentNodeId ];

        var distance = Math.sqrt( Math.pow( p.coords.x - currentNode.x, 2) + Math.pow( p.coords.y - currentNode.y, 2) );

        if( !p.currentDistance || ( distance < p.currentDistance ) ) { p.currentDistance = distance; p.closestId = p.currentNodeId; }

        var childCount = currentNode.children.length;
        
        if( childCount ) {

            var recursiveParams =
                { coords: p.coords,
                  closestId: p.closestId,
                  currentDistance: p.currentDistance };

            if( p.coords.y < this.nodeInfo[ currentNode.children[0] ].y ) {
                recursiveParams.currentNodeId = currentNode.children[0];
                var result = this.findNodeClosestToMouse( recursiveParams );
                if( result.id != p.closestId ) { return { distance: result.distance, id: result.id }; }
            }

            else if( p.coords.y > this.nodeInfo[ currentNode.children[ childCount - 1] ].y ) {
                recursiveParams.currentNodeId = currentNode.children[ childCount - 1];
                var result = this.findNodeClosestToMouse( recursiveParams );
                if( result.id != p.closestId ) { return { distance: result.distance, id: result.id }; }
            }

            else {
                for( var i = 0, ii = childCount; i < ii; i++ ) {
                   recursiveParams.currentNodeId = currentNode.children[ i ];
                   var result = this.findNodeClosestToMouse( recursiveParams );
                   if( result.id != p.closestId ) {
                       recursiveParams.closestId = p.closestId = result.id;
                       recursiveParams.currentDistance = p.currentDistance = result.distance;
                   }
                }
            }
        }

        return { id: p.closestId, distance: p.currentDistance }
    },

    setElementSizes: function( box ) {

        this.container.width( box.width );
        this.canvas.setSize( box.width, box.height );
        this.svgDiv.width( box.width ).height( box.height );

        BioSync.Common.storeObjPosition( this.container, this );
    },

    makeNodeLabel: function( p ) {
   
        return this.canvas.text( p.node.x + p.config.tipLabelBuffer,
                                 p.node.y,
                                 p.node.text )
                           .attr( { "stroke": 'none',
                                    "fill": p.config.treeColor,
                                    "font-family": p.config.fontFamily,
                                    "font-size": p.config.fontSize.value,
                                    "text-anchor": "start" } );
    },

    makeLabelBackdrop: function( p ) {

        var boundingBox = p.label.getBBox();

        var top = p.node.y - ( boundingBox.height / 2 );
        var left = p.node.x - boundingBox.width;

        p.label.attr( { x: left + p.config.nonTipLabelBuffer, y: top } );

        return this.canvas.rect( left + this.renderObj.viewer.config.nonTipLabelBuffer,
                                 top - ( boundingBox.height / 2 ), boundingBox.width, boundingBox.height )
                            .attr( { 'fill': p.config.internalLabelBackdropColor,
                                     'fill-opacity': p.config.internalLabelBackdropOpacity,
                                     'stroke': '' } );
    },

    renderLabels: function() {

        var config = this.renderObj.viewer.config;

        var viewerEventObj = this.renderObj.viewer.events;

        this.labels = [ ];
         
        for( var nodeId in this.nodeInfo ) {

            var node = this.nodeInfo[ nodeId ];

            if( node.text ) {

                node.raphaelLabel = this.makeNodeLabel( { node: node, config: config } );

                if( viewerEventObj.labelClick || viewerEventObj.labelRightClick ) {

                    var clickHandlers = { left: { }, right: { } };

                    if( viewerEventObj.labelClick ) {

                       clickHandlers.left = { func: $.proxy( this[ viewerEventObj.labelClick ], this ),
                                              params: { nodeId: nodeId } };
                    }

                    if( viewerEventObj.labelRightClick ) {

                       clickHandlers.right = { func: $.proxy( this[ viewerEventObj.labelRightClick ], this ),
                                               params: { nodeId: nodeId } };
                    }

                    $( node.raphaelLabel.node ).bind( 'click', clickHandlers, BioSync.Common.handleBothClicks )
                                   .hover( BioSync.Common.setMouseToPointer, BioSync.Common.setMouseToDefault )
                                   .hover( $.proxy( this.setHoveringLabel, this ), $.proxy( this.unsetHoveringLabel, this ) );
                }

                if( node.children.length ) {

                    node.labelBackdrop = this.makeLabelBackdrop( { label: node.raphaelLabel, node: node, config: config } );
                    node.raphaelLabel.toFront();
                }

                this.labels.push( { raphaelLabel: node.raphaelLabel, nodeId: nodeId } );

            }
        }
    },

    setHoveringLabel: function() { this.hoveringLabel = true; },
    unsetHoveringLabel: function() { this.hoveringLabel = false; },

    renderCollapsedNodeUI: function() {

        if( ! BioSync.TreeViewer.RenderUtil.Column.CollapsedNode ) {
            BioSync.Common.loadScript( { name: 'phylogramColumnCollapsedNode' } );
        }

        this.collapsedNodeObjs = { };

        for( var i = 0, ii = this.collapsedNodeIds.length; i < ii; i++ ) {

            this.collapsedNodeObjs[ this.collapsedNodeIds[ i ] ] =
                new BioSync.TreeViewer.RenderUtil.Column.CollapsedNode( this ).initialize( {
                    nodeId: this.collapsedNodeIds[ i ],
                    nodeInfo: this.nodeInfo[ this.collapsedNodeIds[ i ] ] } );
        }
    },

    horizontallyExpandNode: function( p ) {

        if( this.expandedNodeId ) {
                   
            this.collapsedNodeObjs[ this.expandedNodeId ].collapseHorizontal();
        }

        if( p && p.bubbleUp ) {
            
            this.renderObj.horizontallyExpandNode( { nodeId: p.nodeId, column: this } );
        }

        this.expandedNodeId = p.nodeId;
    },

    afterNavigateToNode: function() {

        this.renderObj.scrollToNode( { column: this, nodeId: this.nodeIdToFocusOn } );

        this.makeSpinAnimationAroundNode( { nodeId: this.nodeIdToFocusOn } );
    },

    updateDescendantConnection: function() {

        var hiddenHover = this.collapsedNodeObjs[ this.expandedNodeId ].hiddenHover;

        var y = hiddenHover.myPosition.top + ( hiddenHover.myHeight / 2 );

        var points = this.descendantConnectionCoords = {
            x1: hiddenHover.myPosition.left + hiddenHover.myWidth,
            y1: y,
            x2: this.myWidth,
            y2: y };

        this.columnConnections.descendant =
            this.canvas.path( [ "M", points.x1, " ", points.y1, "L", points.x2, " ", points.y2 ].join('') )
                       .attr( { 'opacity': 0.1,
                                'stroke': this.config.columnConnectionColor,
                                'stroke-width': this.config.columnConnectionWidth } );
    },

    updateAncestorConnection: function() {

        var ancestorColumn = this.renderObj.columns[ this.index - 1 ];

        var points = this.ancestorConnectionCoords =
            { x1: this.nodeInfo[ this.rootNodeId ].x,
              y1: this.nodeInfo[ this.rootNodeId ].y,
              x2: this.renderObj.viewer.config.horizontalPadding / 2,
              y2: this.nodeInfo[ this.rootNodeId ].y,
              x3: this.renderObj.viewer.config.horizontalPadding / 2,
              y3: ancestorColumn.descendantConnectionCoords.y1 - ( this.centerOffset - ancestorColumn.centerOffset ),
              x4: 0,
              y4: ancestorColumn.descendantConnectionCoords.y1 - ( this.centerOffset - ancestorColumn.centerOffset ) };

        if( points.y3 > this.svgDiv.height() ) {

            this.setElementSizes( { width: this.svgDiv.width(), height: points.y3 + this.renderObj.viewer.config.verticalPadding } );
        }
        
        if( points.y3 < 0 ) {

            this.centerOffset += points.y3;
            this.svgDiv.css( { top: this.centerOffset } );

            this.setElementSizes( { width: this.svgDiv.width(), height: this.svgDiv.height() - points.y3 } );
            points.y3 = points.y4 = 0;
        }

        this.columnConnections.ancestor =
            this.canvas.path( [ "M", points.x1, " ", points.y1,
                                "L", points.x2, " ", points.y2,
                                "L", points.x3, " ", points.y3,
                                "L", points.x4, " ", points.y4 ].join('') )
                       .attr( { 'opacity': 0.1,
                                'stroke': this.config.columnConnectionColor,
                                'stroke-width': this.config.columnConnectionWidth } );
    },

    removeDescendantConnection: function() {

        this.columnConnections.descendant.remove();    
    },

    scrollToMe: function() { this.renderObj.scrollToColumn( { column: this } ); },

    isShowingCollapsedNodeDialogue: function() {
        
        for( var nodeId in this.collapsedNodeObjs ) {

            var obj = this.collapsedNodeObjs[ nodeId ];

            if( obj.isMenuVisible ) { return true; }
        }

        return false;
    }
}
