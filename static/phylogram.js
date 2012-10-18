BioSync.TreeViewer.RenderUtil = {

    phylogram: {
    
        browse: function() {

            BioSync.Common.loadCSS( { name: 'jquery-ui-1.8.5.custom' } );
            return this;
        },
        
        navigate: function() {
           
            BioSync.Common.loadCSS( { name: 'jquery-ui-1.8.5.custom' } );
            return this;
        }
    }
}

BioSync.TreeViewer.RenderUtil.phylogram.navigate.prototype = {

    config: {

        scrollTime: 1000
    },

    start: function( viewer ) {

        this.viewer = viewer;
        this.make = BioSync.Common.makeEl;

        BioSync.Common.loadScript( { name: 'phylogramColumn' } );

        return this;
    },

    getTree: function() {

        $.ajax( { url: BioSync.Common.makeUrl( { controller: 'plugin_treeViewer', argList: [ 'getTree' ] } ),
                 type: 'GET', success: new Array( $.proxy( this.handleGetCladeResponse, this ), $.proxy( this.getCladeSuccess, this ) ) } );
        
        this.displayResponseTimeForLargeClades( { nodeCount: this.viewer.totalNodes } );
    },

    handleGetCladeResponse: function( response ) {

        var responseObj = eval( '(' + response + ')' );

        for( var i = 0, ii = responseObj.length; i < ii; i++ ) {

            this.addColumn( { inSession: true } ).renderClade( responseObj[ i ] );

            if( i != 0 ) {

                this.columns[ i - 1 ].nodePreviouslyExpanded( { nodeId: this.columns[ i ].rootNodeId } );

                this.columns[ i - 1 ].updateDescendantConnection();
                this.columns[ i ].updateAncestorConnection();
            }
        }

        this.scrollToColumn( { column: this.columns[ responseObj.length - 1 ] } );
    },

    getCladeSuccess: function() { $( document ).trigger( 'getCladeSuccess' ); },

    showEditTaxonDialogue: function( p ) {

        BioSync.ModalBox.getUrlForm( {
            url: BioSync.Common.makeUrl( { controller: 'snode', argList: [ 'editSnodeTaxon.load', p.nodeId ] } ),
            title: 'Edit Taxon',
            successTrigger: 'nodeEdited' } );
        
        this.recentlyEditedColumn = p.column;
        
        $( document ).bind( 'nodeEdited', { }, $.proxy( this.afterNodeEdited, this ) )
                     .bind( 'nodeEdited', { }, $.proxy( this.unbindNodeEdited, this ) );
    },

    showAddToClipboardForm: function( p ) {

        var content =
            this.make('div').append(
                BioSync.ModalBox.makeBasicTextInput( { name: 'name', text: 'Name : ', value: 'Untitled Clipboard Item' } ),
                BioSync.ModalBox.makeHiddenInput( { name: 'nodeId', value: p.nodeId } ),
                BioSync.ModalBox.makeBasicActionRow( {
                    submitText: 'Submit',
                    submitArgs: { trigger: 'clipboardItemAdded',
                                  submitUrl: BioSync.Common.makeUrl( { controller: 'plugin_treeViewer', argList: ['addItemToClipboard'] } ) } } ) );

        BioSync.ModalBox.showModalBox( { content: content, title: 'Give this clipboard item a name' } );   

        $( document ).bind( 'clipboardItemAdded', { }, $.proxy( p.column.clipboardItemAdded, p.column ) )
                     .bind( 'clipboardItemAdded', { }, $.proxy( this.unbindClipboardItemAdded, this ) );
    },

    showEditNodeForm: function( p ) {

        BioSync.ModalBox.getUrlForm( {
            url: BioSync.Common.makeUrl( { controller: 'snode', argList: [ 'update_snode.load', p.nodeId ] } ),
            title: 'Edit Node',
            successTrigger: 'nodeEdited' } );

        this.recentlyEditedColumn = p.column;

        $( document ).bind( 'nodeEdited', { }, $.proxy( this.afterNodeEdited, this ) )
                     .bind( 'nodeEdited', { }, $.proxy( this.unbindNodeEdited, this ) );
    },

    afterNodeEdited: function() {

        this.refreshColumn( {
            column: this.recentlyEditedColumn,
            onSuccess: [ $.proxy( this.recentlyEditedColumn.afterNodeEdited, this.recentlyEditedColumn ) ] } );
    },

    unbindClipboardItemAdded: function() { $( document ).unbind( 'clipboardItemAdded' ) },

    unbindNodeEdited: function() { $( document ).unbind( 'nodeEdited' ); },

    collapseClade: function( p ) {
                
        var successHandlers = new Array(
            $.proxy( p.column.renderReceivedClade, p.column ),
            $.proxy( p.column.afterCladeCollapse, p.column ) );

        if( p.column.index != 0 ) { successHandlers.push( $.proxy( p.column.updateAncestorConnection, p.column ) ); }

        if( p.column.expandedNodeId ) {

            var expandedNode = p.column.nodeInfo[ p.column.expandedNodeId ];

            if( this.viewer.isAncestor( { ancestor: p.column.nodeInfo[ p.nodeId ], descendant: expandedNode } ) ) {
    
                p.column.expandedNodeId = undefined;
                this.removeColumns( { start: p.column.index + 1, end: this.columns.length - 1 } );

            } else {

                successHandlers = successHandlers.concat( [
                    $.proxy( p.column.showExpandedNodeUI, p.column ),
                    $.proxy( p.column.updateDescendantConnection, p.column ) ] );
            }
        }

        $.ajax( { url: BioSync.Common.makeUrl( { controller: 'plugin_treeViewer', argList: [ 'collapseClade' ] } ),
                  type: "GET",
                  data: { nodeId: p.nodeId, columnIndex: p.column.index },
                  success: successHandlers } );
    },

    hasVerticalScrollbar: function() {
        
        var columnWrapperHeight = this.columnWrapper.height();

        for( var i = 0, ii = this.columns.length; i < ii; i++ ) {

            if( this.columns[i].svgDiv.height() > columnWrapperHeight ) { return true; }
        }

        return false;
    },

    hasHorizontalScrollbar: function() {

        if( ( this.viewPanel.myRight - BioSync.Common.scrollbarWidth ) <
            this.columns[ this.columns.length - 1 ].myRight ) {

            return true;
        }

        return false;
    },

    updateBranchLength: function( value ) {

        this.viewer.updateConfig( { names: [ 'branchLengthStyle' ], values: [ value ], redraw: true } );
    },

    scrollToNode: function( p ) {

        var columnRight = p.column.myPosition.left + p.column.myWidth;

        var viewPanelScrollLeft = this.viewPanel.scrollLeft();
        var viewPanelScrollTop = this.viewPanel.scrollTop();
        
        var horizontalDifference = columnRight - ( this.viewPanel.myWidth + viewPanelScrollLeft );

        var nodeY = p.column.nodeInfo[ p.nodeId ].y + p.column.centerOffset;
        
        var scrollParameters = { time: this.config.scrollTime };

        if( horizontalDifference > 0 ) {
          
            scrollParameters.left = [ '+=', horizontalDifference ].join('');
        }

        scrollParameters.top = nodeY - ( this.viewPanel.myHeight / 2 );

        if( scrollParameters.top || scrollParameters.left ) {
            this.scrollViewPanel( scrollParameters );
        }
    },

    scrollViewPanel: function( p ) {

        var animationParameters = { };
        var successFun = undefined;

        if( ( p.left != undefined ) && ( p.top != undefined ) ) {

            successFun = $.proxy( this.unsetBothScrolls, this );
            animationParameters = { scrollLeft: p.left, scrollTop: p.top };
            this.isViewPanelHorizontallyScrolling = true;
            this.isViewPanelVerticallyScrolling = true;

        } else if( p.left != undefined ) {

            animationParameters.scrollLeft = p.left;
            successFun = $.proxy( this.unsetHorizontalScroll, this );
            this.isViewPanelHorizontallyScrolling = true;

        } else if( p.top != undefined ) {
            animationParameters.scrollTop = p.top;
            successFun = $.proxy( this.unsetVerticalScroll, this );
            this.isViewPanelVerticallyScrolling = true;
        }

        this.viewPanel.animate( animationParameters, p.time, 'swing', successFun );
    },

    unsetHorizontalScroll: function() { this.isViewPanelHorizontallyScrolling = false; },
    unsetVerticalScroll: function() { this.isViewPanelVerticallyScrolling = false; },
    unsetBothScrolls: function() { this.isViewPanelVerticallyScrolling = this.isViewPanelHorizontallyScrolling = false; },

    collapseExpandedNode: function( p ) {

        this.removeColumns( { start: p.column.index + 1, end: this.columns.length - 1 } );

        p.column.removeDescendantConnection();

        this.scrollToColumn( { column: p.column } );
    },
     
    horizontallyExpandNode: function( p ) {

        if( p.column.expandedNodeId ) {

            this.collapseExpandedNode( { column: p.column, nodeId: p.column.expandedNodeId } );
        }

        var newColumn = this.addColumn( { rootNodeId: p.nodeId } );
        
        var ajaxParameters = { nodeId: p.nodeId, columnIndex: p.column.index };

        var onSuccessFunctions =
            new Array(
                this.getCladeSuccess,
                $.proxy( newColumn.renderReceivedClade, newColumn ),
                $.proxy( p.column.updateDescendantConnection, p.column ),
                $.proxy( newColumn.updateAncestorConnection, newColumn ),
                $.proxy( newColumn.scrollToMe, newColumn ) );

        if( p.navigateToNodeId ) {

            p.column.collapsedNodeObjs[ p.nodeId ].horizontallyExpandNode();
            p.column.horizontallyExpandNode( { nodeId: p. nodeId } );

            newColumn.nodeIdToFocusOn = p.navigateToNodeId;

            onSuccessFunctions.push( $.proxy( newColumn.afterNavigateToNode, newColumn ) );

            ajaxParameters.navigateToNodeId = p.navigateToNodeId;
        }

        $.ajax( { url: BioSync.Common.makeUrl( { controller: 'plugin_treeViewer', argList: [ 'horizontallyExpandNode' ] } ),
                  type: "GET",
                  data: ajaxParameters,
                  success: onSuccessFunctions } );

        var nodeInfo = p.column.nodeInfo[ p.nodeId ];
        this.displayResponseTimeForLargeClades( { nodeCount: Math.floor( ( nodeInfo.back - nodeInfo.next ) / 2 ) } );
    },

    displayResponseTimeForLargeClades: function( p ) {

        if( p.nodeCount > this.viewer.config.largeCladeThreshold ) {

            var seconds = Math.floor( p.nodeCount / this.viewer.config.nodesProcessedPerSecond );

            BioSync.Common.notify( {
                text: [ 'This clade is large ( ', p.nodeCount, ' nodes ) and has not been pre processed.  Please wait about ', seconds, ' seconds for it to load.' ].join(''),
                timeoutTrigger: 'getCladeSuccess',
                x: this.viewer.myOffset.left + ( this.viewer.myWidth / 2 ),
                y: this.viewer.myOffset.top + 10 } ); 
        }
    },

    getCladeSuccess: function() { $(document).trigger( 'getCladeSuccess' ); },

    scrollToColumn: function( p ) {

        var columnRight = p.column.myPosition.left + p.column.myWidth;
        var viewPanelWidth = this.viewPanel.width();
        var viewPanelScroll = this.viewPanel.scrollLeft();

        var scrollParameters = { top: 0, time: 1000 };

        var difference = columnRight - ( viewPanelWidth + viewPanelScroll );

        if( difference > 0 ) {
           
            scrollParameters.left = [ '+=', difference ].join('');
        }
            
        this.scrollViewPanel( scrollParameters );
    },

    updateMaxTips: function() {

        if( this.viewer.controlPanel ) {
            
            $.ajax( { url: BioSync.Common.makeUrl( { controller: 'plugin_treeViewer', argList: [ 'getMaxTips' ] } ),
                      type: "GET",
                      success: new Array( $.proxy( this.setMaxTips, this ), $.proxy( this.viewer.controlPanel.updateMaxTips, this.viewer.controlPanel ) ) } );
        }
    },

    setMaxTips: function( value ) {

        this.viewer.config.maxTips.value = parseInt( value );
    },

    verticallyExpandNode: function( p ) { 

        var successHandlers = new Array(
            $.proxy( p.column.renderReceivedClade, p.column ),
            $.proxy( p.column.afterVerticalExpand, p.column ) );

        if( p.column.index != 0 ) { successHandlers.push( $.proxy( p.column.updateAncestorConnection, p.column ) ); }
        
        if( p.column.expandedNodeId ) {

            if( p.column.expandedNodeId == p.nodeId ) {

                this.removeColumns( { start: p.column.index + 1, end: this.columns.length - 1 } );

            } else {
                
                successHandlers.concat( [ $.proxy( p.column.updateDescendantConnection, p.column ) ] );
            }
        }

        successHandlers.push( $.proxy( this.updateMaxTips, this ) );

        $.ajax( { url: BioSync.Common.makeUrl( { controller: 'plugin_treeViewer', argList: [ 'verticallyExpandNode' ] } ),
                  type: "GET",
                  data: { ancestorIds: this.getAncestorIds( { column: p.column, nodeId: p.nodeId } ).join(':'),
                          nodeId: p.nodeId, columnIndex: p.column.index },
                  success: successHandlers } );
        
        var nodeInfo = p.column.collapsedNodeObjs[ p.nodeId ].nodeInfo;
        var descendantCount = Math.floor( ( nodeInfo.back - nodeInfo.next ) / 2 );

        this.displayResponseTimeForLargeClades( { nodeCount: descendantCount } );
    },

    getAncestorIds: function( p ) {

        var ancestorIds = [ ];

        var nodeId = p.nodeId;
        var parentId = p.column.nodeInfo[ nodeId ].parent;

        while( parentId ) {

            ancestorIds.push( parentId );

            nodeId = parentId;

            parentId = p.column.nodeInfo[ nodeId ].parent;
        }

        return ancestorIds;
    },

    //not being used (zoom)
    changeTreeSize: function( p ) {

        for( var i = 0, ii = this.columns.length; i < ii; i++ ) {

            var center = { x: this.columns[i].canvas.width / 2, y: this.columns[i].canvas.height / 2 };

            var newCanvasSize = { x: this.columns[i].canvas.width * p.ratio,
                                  y: this.columns[i].canvas.height * p.ratio };

            var oldPathBBox = this.columns[i].path.getBBox();

            this.columns[i].path.scale( p.ratio, p.ratio, center.x, center.y );

            var newPathBBox = this.columns[i].path.getBBox();

            var newPathCoords = { x: ( oldPathBBox.x / this.columns[i].canvas.width ) * newCanvasSize.x,
                                  y: ( oldPathBBox.y / this.columns[i].canvas.height ) * newCanvasSize.y };
            
            var translate = { x: newPathCoords.x - newPathBBox.x,
                              y: newPathCoords.y - newPathBBox.y };
            
            this.columns[i].path.translate( translate.x, translate.y );
            var newPathBBox = this.columns[i].path.getBBox();

            for( var j = 0, jj = this.columns[i].labels.length; j < jj; j++ ) {

                var labelInfo = this.columns[ i ].labels[ j ];
                var label = labelInfo.raphaelLabel;
            
                var x = ( ( label.attr('x') - oldPathBBox.x ) * p.ratio ) + newPathBBox.x;
                var y = ( ( label.attr('y') - oldPathBBox.y ) * p.ratio ) + newPathBBox.y;

                label.attr( { 'x': x, 'y': y,
                              'font-size': label.attr('font-size') * p.ratio,
                              'stroke-width': label.attr('stroke-width') * p.ratio } );
            }

            for( var j = 0, jj = this.columns[i].collapsedNodeIds.length; j < jj; j++ ) {

                var info = this.columns[i].nodeInfo[ this.columns[i].collapsedNodeIds[j] ].hiddenHover;

                info.path.scale( p.ratio, p.ratio, center.x, center.y );
                info.path.translate( translate.x, translate.y );
                
                info.label.attr( { 'x': ( ( info.label.attr('x') - oldPathBBox.x ) * p.ratio ) + newPathBBox.x,
                                   'y': ( ( info.label.attr('y') - oldPathBBox.y ) * p.ratio ) + newPathBBox.y,
                                   'font-size': info.label.attr('font-size') * p.ratio,
                                   'stroke-width': info.label.attr('stroke-width') * p.ratio } );

                info.el.css( { left: ( ( parseFloat( info.el.css('left') ) - oldPathBBox.x ) * p.ratio ) + newPathBBox.x,
                               top: ( ( parseFloat( info.el.css('top') ) - oldPathBBox.y ) * p.ratio ) + newPathBBox.y } )
                       .width( info.el.width() * p.ratio )
                       .height( info.el.height() * p.ratio );
            }

            this.setCanvasSize( this.columns[i], newCanvasSize.x, newCanvasSize.y );
            this.alignColumns( { index: i } );
            this.centerColumn( { index: i } );

            if( this.columns[ i+1 ] ) {
                this.columnConnections[i][0].scale( p.ratio, p.ratio, center.x, center.y );
                this.columnConnections[i][0].translate( translate.x, translate.y );
            }

            if( this.columns[ i - 1 ] ) {
                var canvas = this.columns[ i ].canvas;
                this.columnConnections[ i - 1 ][1].scale( p.ratio, p.ratio, center.x, center.y );
                this.columnConnections[ i - 1 ][1].translate( translate.x, translate.y );
            }

        }
    },

    refreshColumn: function( p ) {

        var successHandlers = new Array( $.proxy( p.column.renderReceivedClade, p.column ) );

        if( p.onSuccess ) { successHandlers = successHandlers.concat( p.onSuccess ); }

        if( p.column.index != 0 ) { successHandlers.push( $.proxy( p.column.updateAncestorConnection, p.column ) ); }
  
        if( p.column.expandedNodeId ) {

            successHandlers.push( $.proxy( p.column.showExpandedNodeUI, p.column ) );
            successHandlers.push( $.proxy( p.column.updateDescendantConnection, p.column ) );
        }

        $.ajax( { url: BioSync.Common.makeUrl( { controller: 'plugin_treeViewer', argList: [ 'refreshColumn' ] } ),
                  type: "GET", data: { columnIndex: p.column.index },
                  success: successHandlers } );
    },

    removeColumns: function( p ) {

        if( ! p.keepInSession ) {

            $.ajax( { url: BioSync.Common.makeUrl( { controller: 'plugin_treeViewer', argList: [ 'removeColumns' ] } ),
                      type: "GET", async: true,
                      data: { start: p.start, end: p.end } } );
        }

        for( var i = p.end, ii = p.start; i >= ii; i-- ) {
            
            this.removeColumn( { index: i } );
        }

        this.updateColumnWrapper();
    },

    removeColumn: function( p ) {

        var column = this.columns[ p.index ];

        column.hideColumn( { onSuccess: $.proxy( column.emptyColumn, column ) } );

        this.columns.splice( p.index, 1 );
    },

    initialize: function() {

        var viewer = this.viewer;

        this.viewPanel = this.make('div').attr( { 'class': 'viewPanel' } )
                                         .height( '100%' )
                                         .width( viewer.myWidth );

        this.columnWrapper =
            this.make('div').attr( { 'class': 'columnWrapper' } )
                            .height( '100%' )
                            .width( '100%' );

        viewer.container.append( this.viewPanel.append( this.columnWrapper ) );

        
        this.columns = [ ];
        this.columnConnections = [];
       
        BioSync.Common.storeObjPosition( this.viewPanel, this.viewPanel );
    },

    addColumn: function( p ) {
    
        if( ! p.inSession ) {

            $.ajax( { url: BioSync.Common.makeUrl( { controller: 'plugin_treeViewer', argList: [ 'addColumn' ] } ),
                      data: { rootNodeId: p.rootNodeId }, type: "GET", async: false } );
        }

        var columnObj = this.getColumnObj();

        this.columns.push( columnObj );

        this.columnWrapper.append( columnObj.container );
        
        this.alignColumns();
        
        this.updateColumnWrapper();
        
        this.columnConnections.push( [] );

        return columnObj;
    },

    getColumnObj: function() {

        return new BioSync.TreeViewer.RenderUtil.Column( this ).initialize( { index: this.columns.length } );
    },

    insertNewColumn: function( p ) {

        if( p.index > this.columns.length - 1 ) { this.addNewColumn(); return; }

        //var column = this.makeColumn();
        var column = new BioSync.TreeViewer.Column( this ).initialize()
        
        column.index = p.index;

        this.columns.splice( p.index, 0,  column );

        column.container.insertBefore( this.columns[ p.index + 1 ].container );
        BioSync.Common.storeObjPosition( column.container, column );
        
        this.columnConnections.splice( p.index, 0, [] );
        
        this.addCanvas();
    },

    alignColumns: function( p ) {

        for( var i = 0, ii = this.columns.length; i < ii; i++ ) {
            this.alignColumn( { index: i } );
        }
    },

    alignColumn: function( p ) {
    
        if( p.index == 0 ) {
            this.columns[ p.index ].container.css( { left: 0 } );
        } else {
            var prevColumn = this.columns[ p.index - 1 ];
            this.columns[ p.index ].container.css( { left: prevColumn.myPosition.left + prevColumn.myWidth } );
            BioSync.Common.storeObjPosition( this.columns[ p.index ].container, this.columns[ p.index ] );
        }
    },

    addNewColumn: function() {

        var column = this.makeColumn();
        
        column.index = this.columns.length;

        this.columns.push( column );

        this.columnWrapper.append( column.container );
        BioSync.Common.storeObjPosition( column.container, column );

        this.addCanvas();

        this.columnConnections.push( [] );

        this.alignColumn( { index: column.index } );
        
        this.updateColumnWrapper();
    },

    redrawTree: function() {

        this.removeColumns( { start: 0, end: this.columns.length - 1, keepInSession: true } );

        this.getTree();
    },

    updateColumnWrapper: function() {

        if( this.columns.length ) {
            var rightmostColumn = this.columns[ this.columns.length - 1 ];
            var wrapperWidth = rightmostColumn.myPosition.left + rightmostColumn.myWidth;
            this.columnWrapper.width( wrapperWidth );
        }
    },

    navigateToNode: function( p ) {

        for( var i = 0, ii = this.columns.length; i < ii; i++ ) {

            var column = this.columns[i];

            if( column.nodeInfo[ p.nodeId ] ) {

                this.scrollToNode( { column: column, nodeId: p.nodeId } );

                column.makeSpinAnimationAroundNode( { nodeId: p.nodeId } );

                return;
            }

            for( var nodeId in column.collapsedNodeObjs ) {

                if( this.viewer.isAncestor( { ancestor: column.nodeInfo[ nodeId ], descendant: p } ) ) {

                    if( column.expandedNodeId == nodeId ) {    

                        break;

                    } else {
                       
                        this.horizontallyExpandNode( { column: column, nodeId: nodeId, navigateToNodeId: p.nodeId } );

                        return;
                    }
                }
            }
        }
    },

    getNodePathString: function( p ) {

        if( p.nodeInfo.isCollapsed ) { return ''; }

        var pathString = new BioSync.Common.StringBuffer();

        var childCount = p.nodeInfo.children.length;

        pathString.append( [ "M", p.nodeInfo.x, " ", p.nodeInfo.y, "l", p.nodeInfo.dx, " 0" ].join("") );

        if( childCount ) {

            if( childCount == 1 ) {

                var tipSep = this.viewer.config.verticalTipBuffer;

                var childY = p.column.nodeInfo[ p.nodeInfo.children[0] ].y;
                var lastChildY = p.column.nodeInfo[ p.nodeInfo.children[ childCount-1 ] ].y;

                pathString.append( [ "M", p.nodeInfo.x, " ", childY - ( tipSep / 4 ) , "l0 ", ( tipSep / 2 ) ].join("") );

            } else {
                
                var firstChildY = p.column.nodeInfo[ p.nodeInfo.children[0] ].y;
                var lastChildY = p.column.nodeInfo[ p.nodeInfo.children[ childCount-1 ] ].y;

                pathString.append( [ "M", p.nodeInfo.x, " ", firstChildY, "L", p.nodeInfo.x, " ", lastChildY ].join("") );
            }
        }

        return pathString.toString();
    },

    getCladePathString: function( p ) {

        var pathString = new BioSync.Common.StringBuffer();

        pathString.append( this.getNodePathString( p ) );

        if( ! p.nodeOnly ) {

            for( var i = 0, ii = p.nodeInfo.children.length; i < ii; i++ ) {
                pathString.append( this.getCladePathString( { column: p.column, nodeInfo: p.column.nodeInfo[ p.nodeInfo.children[i] ] } ) );    
            }
        }

        return pathString.toString();

    },

    unHighlightClade: function( p ) {

        for( var i = 0, ii = this.columns.length; i < ii; i++ ) {

            if( this.columns[i].currentHighlight ) {

                for( var j = 0, jj = this.columns[i].currentHighlight.length; j < jj; j++ ) {
                    this.columns[i].currentHighlight[j].remove();
                }
            }
        }
    },

    highlightClade: function( p ) {

        var nodeInfo = p.column.nodeInfo[ p.nodeId ];

        var selectionPath = this.getCladePathString( { column: p.column, nodeInfo: nodeInfo, nodeOnly: p.nodeOnly } );

        var canvasObj = p.column.canvas.path( selectionPath ).attr( {
            stroke: ( p.color ) ? p.color : 'red',
            "stroke-linecap": 'square',
            "stroke-width": this.viewer.config.pathWidth } );

        if( ! p.column.currentHighlight ) { p.column.currentHighlight = new Array(); }

        p.column.currentHighlight.push( canvasObj );

        if( p.column.index < this.columns.length - 1 ) {

            var expandedNodeId = p.column.container.find('.expanded').attr('nodeId');
            var expandedNode = p.column.nodeInfo[ expandedNodeId ];

            if( this.viewer.isAncestor( { ancestor: nodeInfo, descendant: expandedNode } ) ) {

                for( var i = p.column.index + 1, ii = this.columns.length; i < ii; i++ ) {
                
                    this.highlightClade( { column: this.columns[i], nodeId: this.columns[i].rootId, color: p.color } );
                }
            }
        }
    },

    handleNodeClick: function( p ) {

        var renderObj = p.data.renderObj;
        var viewer = renderObj.viewer;
        var eventObj = viewer.events;

        if( p.which == 3 && viewer.events.nodeRightClick ) {

            var eventObj = viewer.events.nodeRightClick;

            if( eventObj.type == 'contextMenu' ) {

                var options = [];

                for( var i = 0, ii = eventObj.options.length; i < ii; i++ ) {

                    var option = eventObj.options[ i ];

                    var handler = ( option.external )
                        ? viewer[ option.handler ]
                        : renderObj[ option.handler ];

                    options.push( { text: option.text,
                                    action: handler,
                                    params: { optionDef: option,
                                              column: p.data.column,
                                              renderObj: renderObj,
                                              nodeId: $( this ).attr('nodeId') } } );
                }
                    
                BioSync.OptionsMenu.makeContextMenu( { coords: { x: p.pageX, y: p.pageY }, options: options } );
            }
        }
    },


    updateNodeSelector: function( p ) {

        var renderObj = p.data.renderObj;
        var column = p.data.column;
        var nodeSelector = column.nodeSelector;

        if( $('#modalBoxContainer' ).is(':visible') ) { return true; }

        if( BioSync.Common.isContextMenuVisible() || BioSync.Common.symbolDragInfo || renderObj.viewPanel.hasClass('scrolling') ) { nodeSelector.hide(); return true; }

        var closestNodeInfo = renderObj.getClosestNode( {
            coords: renderObj.translateDOMToCanvas( { x: p.pageX, y: p.pageY, column: column } ),
            currentNodeId: column.rootId,
            column: column } );

        if( ( closestNodeInfo.distance < 50 ) && ( column.collapsedNodeIds.indexOf( closestNodeInfo.id ) == -1 ) ) {

            nodeSelector.attr( { cx: column.nodeInfo[ closestNodeInfo.id ].x, cy: column.nodeInfo[ closestNodeInfo.id ].y } ).show().toFront();
            $( nodeSelector.node ).attr( { 'nodeId': closestNodeInfo.id } );

        } else {

            nodeSelector.hide();
        }
    },

    getClosestNode: function( p ) {

        var nodeDict = p.column.nodeInfo;
        var currentNode = nodeDict[ p.currentNodeId ];

        var distance = Math.sqrt( Math.pow( p.coords.x - currentNode.x, 2) + Math.pow( p.coords.y - currentNode.y, 2) );

        if( !p.currentDistance || ( distance < p.currentDistance ) ) { p.currentDistance = distance; p.closestId = p.currentNodeId; }

        var childCount = currentNode.children.length;
        
        if( childCount ) {

            var recursiveParams =
                { coords: p.coords,
                  column: p.column,
                  closestId: p.closestId,
                  currentDistance: p.currentDistance };

            if( p.coords.y < nodeDict[ currentNode.children[0] ].y ) {
                recursiveParams.currentNodeId = currentNode.children[0];
                var result = this.getClosestNode( recursiveParams );
                if( result.id != p.closestId ) { return { distance: result.distance, id: result.id }; }
            }

            else if( p.coords.y > nodeDict[ currentNode.children[ childCount - 1] ].y ) {
                recursiveParams.currentNodeId = currentNode.children[ childCount - 1];
                var result = this.getClosestNode( recursiveParams );
                if( result.id != p.closestId ) { return { distance: result.distance, id: result.id }; }
            }

            else {
                for( var i = 0, ii = childCount; i < ii; i++ ) {
                   recursiveParams.currentNodeId = currentNode.children[ i ];
                   var result = this.getClosestNode( recursiveParams );
                   if( result.id != p.closestId ) {
                       recursiveParams.closestId = p.closestId = result.id;
                       recursiveParams.currentDistance = p.currentDistance = result.distance;
                   }
                }
            }
        }

        return { id: p.closestId, distance: p.currentDistance };
    },

    translateDOMToCanvas: function( p ) {
    
        var column = p.column;

        return { x: p.x - ( column.myPosition.left + this.viewPanel.myOffset.left - this.viewPanel.scrollLeft() ),
                 y: p.y - ( column.myPosition.top + this.viewPanel.myOffset.top + column.centerOffset - this.viewPanel.scrollTop() ) }
    }
};
