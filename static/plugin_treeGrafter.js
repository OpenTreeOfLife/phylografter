BioSync.TreeGrafter = {

    instances: { },

    viewer: function() { return this; },

    RenderUtil: {

        phylogram: {

            browse: function() { return this; },

            navigate: function() { return this; }
        },
    },
    
    checkClipboardItemDrop: function( p, q ) {

        var grafters = BioSync.TreeViewer.instances;

        for( var containerId in grafters ) {

            var grafter = grafters[ containerId ];

            if( grafter.graftNodeId ) {

                grafter.handleClipboardItemDrop( q );
                break;
            }
        }
    },

    checkMovingClipboardItem: function( p, q ) {

        var grafters = BioSync.TreeGrafter.instances;

        for( var containerId in grafters ) {

            var grafter = grafters[ containerId ];

            if( BioSync.Common.isMouseOnElement( { el: grafter.container, x: q.x, y: q.y } ) ) {

                grafter.renderObj.handleMovingClipboardItem( { x: q.x, y: q.y } );
                break;
            }
        }
    }
}

BioSync.TreeGrafter.viewer.prototype = new BioSync.TreeViewer.viewer();
BioSync.TreeGrafter.viewer.constructor = BioSync.TreeGrafter.viewer;
BioSync.TreeGrafter.viewer.prototype.super = BioSync.TreeViewer.viewer.prototype;

BioSync.TreeGrafter.viewer.prototype.onWindowLoad = function() {

    $.proxy( this.super.onWindowLoad, this )();

    if( this.treeType == 'grafted' ) { this.getGraftHistory(); }

}

BioSync.TreeGrafter.viewer.prototype.getGraftHistory = function() {

    $.ajax( { url: BioSync.Common.makeUrl( { controller: 'plugin_treeGrafter', argList: [ 'getGtreeGraftHistory' ] } ),
              type: "GET",
              data: { treeId: this.treeId },
              success: $.proxy( this.renderObj.handleGraftHistory, this.renderObj ) } );
}

BioSync.TreeGrafter.viewer.prototype.getRenderObj = function() {

        // add error handler for this
        BioSync.Common.loadScript( { name: this.renderType } );
        BioSync.Common.loadScript( { name: [ this.renderType, 'Graft' ].join('') } );

        return new BioSync.TreeGrafter.RenderUtil[ this.renderType ][ this.viewMode ]().start( this );
}

//older stuff down below

BioSync.TreeViewer.viewer.prototype.updateGraftColor = function( p ) {

    var viewer = this;
    var graftHistory = viewer.graftHistory[ p.nodeId ];

    graftHistory.color = p.value;

    var borderString = Math.floor( viewer.style.pathWidth * 2 ) + 'px solid ' + p.value;

    $('.legendItem[nodeid="' + p.nodeId + '"] .legendLineColor' ).css( { 'border-bottom': borderString, 'border-top': borderString } );

    for( var i = 0, ii = graftHistory.paths.length; i < ii; i++ ) {
        graftHistory.paths[i].attr( { stroke: p.value, fill: p.value } );
    }

    BioSync.Common.notify( { text: 'Changes Saved',
                             timeout: 1000,
                             x: viewer.containerOffset.left + ( viewer.containerWidth / 2 ),
                             y: viewer.containerOffset.top + 10 } );
}

BioSync.TreeViewer.viewer.prototype.getGrafterColorOptions = function( p ) {

    var viewer = p.viewer;

    var colorOptions = viewer.config.colorOptions;
   
    if( colorOptions.cladogram ) { 
        delete colorOptions.cladogram;
    }

    var index = 1;

    for( var nodeId in viewer.graftHistory ) {

        colorOptions[ [ 'graftColor', index ].join('') ] =
            { text: [ 'Graft Color #', index ].join(''),
              update: ( function(id) { return function( p ) { p.viewer.updateGraftColor( { nodeId: id, value: p.value } ); }; } )(nodeId),
              value: viewer.graftHistory[ nodeId ].color };

        index++;
    }
    
    viewer.config.colorOptions = colorOptions;

    return colorOptions;
}

BioSync.TreeViewer.viewer.prototype.getConfigColorDropdownOptions = function( p ) {
        
    var viewer = this;
    var elList = [];
    var colorOptions = viewer.getGrafterColorOptions( { viewer: viewer } );
    var make = BioSync.Common.makeEl;

    for( var value in colorOptions ) {
        elList.push( make('option').attr( { 'value': value } ).text( colorOptions[value].text ).get(0) );
    }

    return elList;
}

BioSync.TreeViewer.viewer.prototype.getGraftConfirmation = function( response ) {

    var response = eval( "(" + response + ")" );
    var viewer = this;
    var graftInfo = viewer.graftInfo;

    response.viewer = viewer;

    if( viewer.currentColumnIndex != viewer.graftColumnIndex ) {
        viewer.renderUtil.collapseNode( { data: { viewer: viewer, columnIndex: viewer.graftColumnIndex } } );
        viewer.currentColumnIndex = viewer.graftColumnIndex;
    }

    var currentColumn = viewer.columns[ viewer.currentColumnIndex ];
    currentColumn.container.find('.hiddenHover').unbind('mouseenter mouseleave');
    currentColumn.container.unbind('mousemove');
    currentColumn.nodeSelector.hide();
    
    var affectedClade = ( graftInfo.graftType == 'graft' || graftInfo.graftType == 'replace' )
        ? currentColumn.nodeInfo[ currentColumn.nodeInfo[ graftInfo.affectedNodeId ].parent ] : '';

    var affectedCladePath = BioSync.TreeViewer.RenderUtil.Common.getCladePathString( {
        node: affectedClade,
        nodeInfo: currentColumn.nodeInfo } );

    currentColumn.path.attr( { stroke: '#DADADA' } );
    graftInfo.affectedCladePath = currentColumn.canvas.path( affectedCladePath ).attr( { stroke: 'orange', "stroke-width": viewer.style.pathWidth } );

    viewer.renderUtil.updateColumns( { clickedIndex: viewer.graftColumnIndex, viewer: viewer } );
    
    currentColumn = viewer.columns[ viewer.currentColumnIndex ];
    
    response.noNodeSelector = true; 
    viewer.renderUtil.renderReceivedTree( response );
    
    currentColumn.container.hide();
    
    graftInfo.newCladePath = currentColumn.canvas.path( currentColumn.path.attr('path') ).attr( { stroke: 'orange', "stroke-width": viewer.style.pathWidth } );

    var clipboardCladePath = BioSync.TreeViewer.RenderUtil.Common.getCladePathString( {
        node: currentColumn.nodeInfo[ graftInfo.clipboardNodeId ],
        nodeInfo: currentColumn.nodeInfo } );
    
    graftInfo.clipboardCladePath = currentColumn.canvas.path( clipboardCladePath ).attr( { stroke: 'blue', "stroke-width": viewer.style.pathWidth } );
    
    viewer.renderUtil.animateGraft( { viewer: viewer } );
}

BioSync.TreeViewer.viewer.prototype.clipboardGraft = function( p ) { 

    var viewer = p.data.viewer;
               
    var nodeInfo =  viewer.columns[ viewer.graftColumnIndex ].nodeInfo;

    viewer.graftInfo = { 'graftType': p.data.action,
                         'clipboardNodeId': p.data.dropNodeId,
                         'treeType': viewer.treeType,
                         'treeId': viewer.treeId,
                         'affectedCladeId': nodeInfo[ p.data.nodeId ].parent,
                         'affectedNodeId': p.data.nodeId };
    
    var revertInfo = $('.graftAuditContainer.disabledItem');

    if( revertInfo.length ) { viewer.graftInfo.editId = $( revertInfo[0] ).attr( 'editId' ); }

    var url = ( viewer.viewMode == 'navigate' ) ? 'navigateGetGraftView' : 'browseGetGraftView';

    $.ajax( { url: BioSync.Common.makeUrl( { controller: 'plugin_treeGrafter', argList: [ url ] } ),
              type: "GET",
              context: viewer,
              data: viewer.graftInfo,
              success: viewer.getGraftConfirmation } );
}

BioSync.TreeViewer.viewer.prototype.updateURL = function() { 

    $.ajax( { url: BioSync.Common.makeUrl( { controller: 'plugin_treeGrafter', argList: [ 'updateURL' ] } ),
              type: "GET",
              success: $.proxy( this.handleUpdateURLResponse, this ) } );
}

BioSync.TreeViewer.viewer.prototype.handleUpdateURLResponse = function( response ) { 

    response = eval( [ "(", response, ")" ].join('') );
    
    this.treeId = response.treeId;
    this.treeType = response.treeType;

    window.history.pushState( { }, 'Phylografter', BioSync.Common.makeUrl( { 'controller': 'gtree', argList: [ 'backbone', [ this.treeId, '?treeType=', this.treeType ].join('') ] } ) ); 
}

BioSync.TreeViewer.viewer.prototype.handleGraftResponse = function( response ) { 

    var response = eval( "(" + response + ")" );
    var viewer = this;

    response.renderInfo.viewer = viewer;

    if( viewer.treeType == 'source' ) { window.location.hash = response.treeId; }

    viewer.treeType = 'grafted';
    viewer.treeId = response.treeId;

    viewer.renderUtil.renderReceivedTree( response.renderInfo );

    viewer.container.trigger( 'graftSuccess', { } );
}

BioSync.TreeViewer.viewer.prototype.handleClipboardItemDrop = function( p ) {

    var replaceParams = { dropNodeId: p.dropNodeId, nodeId: this.graftNodeId, viewer: this, action: 'replace' };
    var addSiblingParams = { dropNodeId: p.dropNodeId, nodeId: this.graftNodeId, viewer: this, action: 'graft' };

    BioSync.OptionsMenu.makeContextMenu(
        { coords: p.dropCoords, options: [
            { 'text': 'Replace Clade', 'action': this.clipboardGraft, 'params': replaceParams },
            { 'text': 'Add Sibling', 'action': this.clipboardGraft, 'params': addSiblingParams } ] } );

    $(document).bind( 'contextMenuClosed', { viewer: this }, this.handleGraftingMenuClose );
}

BioSync.TreeViewer.viewer.prototype.handleGraftingMenuClose = function( p ) {
    p.data.viewer.removeGraftInfo();
    $(document).unbind( 'contextMenuClosed', BioSync.TreeGrafter.handleGraftingMenuClose );
}

BioSync.TreeViewer.viewer.prototype.removeGraftInfo = function( p ) {
    this.graftSvgPath.remove();
    this.graftSvgPath = undefined;
    this.graftNodeId = undefined;
}


BioSync.TreeViewer.RenderUtil.phylogram.navigate.renderTree = function( p ) {

    var viewer = p.viewer;

    viewer.getTree( { viewer: viewer } );

    if( viewer.treeType =='grafted' ) { 
        
        //hack for webkit (jquery synch ajax?) bug
        //don't think i need this anymore
        if( ! viewer.columns[ viewer.currentColumnIndex ].nodeInfo ) {

            var date = new Date();
            var curDate = null;

            do { curDate = new Date(); } 
            while(curDate-date < 500);
        }
        
        //viewer.getGraftHistory( { viewer: viewer } );
    }
}

BioSync.TreeViewer.RenderUtil.phylogram.navigate.verticallyExpandNode = function( p ) {
                
    var viewer = p.data.viewer;

    var clickedColumn = viewer.columns[ p.data.columnIndex ];
    var rootId = clickedColumn.rootId;

    viewer.renderUtil.updateColumns( { clickedIndex: p.data.columnIndex, viewer: viewer } );
                
    $.ajax( { url: BioSync.Common.makeUrl( { controller: 'plugin_treeViewer', argList: [ 'verticallyExpandNode' ] } ),
              type: "GET",
              context: viewer,
              data: { nodeId: p.data.nodeId, rootId: rootId, collapsedNodeIds: clickedColumn.collapsedNodeIds.join(':'), treeType: viewer.treeType },
              success: new Array(
                viewer.renderUtil.handleVerticalExpandResponse,
                ( p.success ) ? p.success : function() { },
                function() { $(document).trigger('verticallyExpandNodeSuccess', { viewer: viewer } ); } ) } );

    $('body').find('div.expandOptionContainer:visible').hide();
}

BioSync.TreeViewer.RenderUtil.phylogram.navigate.expandNode = function( p ) {

    var viewer = p.data.viewer;
    
    viewer.renderUtil.updateColumns( { clickedIndex: p.data.columnIndex, viewer: viewer } );

    var controller = ( viewer.treeType == 'grafted' ) ? 'plugin_treeGrafter' : 'plugin_treeViewer';
    
    $.ajax( { url: BioSync.Common.makeUrl( { controller: controller, argList: [ 'navigateExpandNode' ] } ),
              type: "GET",
              context: viewer,
          data: { nodeId: p.data.nodeId },
              success: new Array( viewer.handleReceivedTree,
                      function() { viewer.renderUtil.addAnimations( {
                                        viewer: viewer, clickedHover: $(p.target).closest('div.hiddenHover') } );
                                   viewer.container.trigger('expandNodeSuccess', { } ); },
                      ( p.success ) ? p.success : function() { },
                      function() {  } ) } );
                
    $('body').find('div.expandOptionContainer:visible').hide();
}


BioSync.TreeViewer.RenderUtil.phylogram.navigate.moveCurrentColumn = function( p ) {
    var viewer = p.viewer;
    var prevColumn = viewer.columns[ viewer.currentColumnIndex - 1 ];

    var extraOffset = ( viewer.graftInfo && ( viewer.graftColumnIndex != viewer.currentColumnIndex - 1 ) ) ? 50 : 0;
    extraOffset = 0;

    viewer.columns[ viewer.currentColumnIndex ].container.css( {
        'top': 0,
        'left': prevColumn.containerWidth + prevColumn.containerPosition.left + extraOffset } );
}

BioSync.TreeViewer.RenderUtil.phylogram.navigate.animateGraft = function( p ) {

    var viewer = p.viewer;
    var currentColumn = viewer.columns[ viewer.currentColumnIndex ];
    var prevColumn = viewer.columns[ viewer.currentColumnIndex - 1 ];
    var graftInfo = viewer.graftInfo;

    var make = BioSync.Common.makeEl;

    var graftContainerWidth = 50;
    var graftContainerHeight = 100;
    var graftContainerWidthBy2 = 25;
    var graftContainerHeightBy2 = 50;

    graftInfo.animateGraftContainer = make('div').attr( { 'class': 'animateGraftContainer' } )
                                                 .css( { top: ( viewer.containerHeight / 2 ) - graftContainerHeightBy2, left: currentColumn.containerPosition.left } )
                                                 .width( graftContainerWidth ).insertBefore( currentColumn.container );
    
    currentColumn.container.css( { top: 0, left: prevColumn.containerWidth + prevColumn.containerPosition.left + graftContainerWidth } );
    currentColumn.containerOffset.left = currentColumn.containerOffset.left + graftContainerWidth;
    currentColumn.containerRight = currentColumn.containeRight + graftContainerWidth;
    currentColumn.containerPosition.left = currentColumn.containerPosition.left + graftContainerWidth;

    graftInfo.animateGraftCanvas = Raphael( graftInfo.animateGraftContainer.get(0), 50, 100 );
    graftInfo.animateGraftPath = graftInfo.animateGraftCanvas.path(  "M0 25L" ).attr( { stroke: 'blue', "stroke-width": 2 } );

    graftInfo.graftButton =
        graftInfo.animateGraftCanvas.text( graftContainerWidthBy2, 20, [ 'Approve\n', BioSync.Common.capitalizeFirstLetter( graftInfo.graftType ) ].join('') )
                                    .attr( { opacity: 0, stroke: '#275B90', fill: '#275B90', "stroke-width": .5, "font-size": 12 } );
                                                    
    graftInfo.cancelButton =
        graftInfo.animateGraftCanvas.text( graftContainerWidthBy2, 80, [ 'Cancel\n', BioSync.Common.capitalizeFirstLetter( graftInfo.graftType ) ].join('') )
                                    .attr( { opacity: 0, stroke: '#275B90', fill: '#275B90', "stroke-width": .5, "font-size": 12 } );

    graftInfo.animateGraftPath.animate( { path: "M0 50L 45 50L 35 60M45 50 L 35 40" }, 2000 );
    
    var revertInfo = $('.graftAuditContainer.disabledItem');

    $( graftInfo.graftButton.node ).bind( 'mouseover', { el: graftInfo.animateGraftContainer }, BioSync.Common.addHoverPointer );
    $( graftInfo.graftButton.node ).bind( 'mouseout', { el: graftInfo.animateGraftContainer }, BioSync.Common.removeHoverPointer );
    $( graftInfo.graftButton.node ).bind( 'click', { viewer: viewer }, ( revertInfo.length ) ? viewer.addressUnsavedChanges : viewer.renderUtil.approveGraft );
    
    $( graftInfo.cancelButton.node ).bind( 'mouseover', { el: graftInfo.animateGraftContainer }, BioSync.Common.addHoverPointer );
    $( graftInfo.cancelButton.node ).bind( 'mouseout', { el: graftInfo.animateGraftContainer }, BioSync.Common.removeHoverPointer );
    $( graftInfo.cancelButton.node ).bind( 'click', { viewer: viewer }, viewer.renderUtil.cancelGraft );

    setTimeout( viewer.renderUtil.showCurrentColumn, 2000, { currentColumn: currentColumn } ); 
    setTimeout( viewer.renderUtil.showGraftOptions, 4000, { viewer: viewer } ); 
                
    viewer.columnWrapper.width( currentColumn.containerPosition.left + currentColumn.containerWidth );

    viewer.renderUtil.scrollCheck( { viewer: viewer } );
}

BioSync.TreeViewer.viewer.prototype.addressUnsavedChanges = function( p ) { 
  
    var viewer = p.data.viewer;
    var auditModule = viewer.graftAuditModule;
    var graftInfo = viewer.graftInfo;

    var make = BioSync.Common.makeEl;
    var form = BioSync.ModalBox;
   
    var content = make('div').append(
       form.makeBasicTextRow( { text: [ 'Before your ', graftInfo.graftType, ' action is commited, you need to address the current revisions made to the tree.' ].join('') } ),
       form.makeBasicTextRow( { text: "Would you like to revert the current grafted tree to a former state ('edit'), or would you prefer to create a new tree ('fork') ?" } ),
       form.makeRadioButtonRow( { name: 'saveType', options: [ { value: 'edit', text: 'Edit : ', func: function() { $('#forkContent').hide() }, default: true },
                                                               { value: 'fork', text: 'Fork : ', func: function() { $('#forkContent').show() } } ] } ),
       form.makeHiddenInput( { name: 'editId', value: $( auditModule.container.find('.disabledItem')[0] ).attr('editId') } ),
       make('div').attr( { 'id': 'forkContent' } ).append(
           form.makeBasicTextInput( { name: 'treeName', text: 'Tree Name : ', value: 'Untitled Grafted Tree' } ),
           form.makeBasicLongTextInput( { name: 'treeComment', text: 'Tree Description : ', value: '' } )
       ).hide(),
       form.makeBasicTextRow( { text: [ 'Based on your decision above, the ', graftInfo.graftType, " action will be committed to either the updated version of this tree ('edit'), or to the new tree ('fork')." ].join('') } ),
       form.makeBasicTextInput( { name: 'graftComment', text: [ BioSync.Common.capitalizeFirstLetter( graftInfo.graftType ),'  Comment : ' ].join(''), value: '' } ),
       form.makeHiddenInput( { name: 'clipboardNodeId', value: graftInfo.clipboardNodeId } ),
       form.makeHiddenInput( { name: 'affectedNodeId', value: graftInfo.affectedNodeId } ),
       form.makeHiddenInput( { name: 'affectedCladeId', value: graftInfo.affectedCladeId } ),
       form.makeHiddenInput( { name: 'graftType', value: graftInfo.graftType } ),
       form.makeHiddenInput( { name: 'treeId', value: viewer.treeId } ),
       form.makeHiddenInput( { name: 'treeType', value: viewer.treeType } ),
       form.makeBasicActionRow( { submitText: [ 'Save tree then ', graftInfo.graftType ].join(''),
                                  submitArgs: { context: viewer, onSuccess: viewer.handleSavedChanges,
                                                submitUrl: BioSync.Common.makeUrl( { controller: 'plugin_graftAudit', argList: [ 'saveChangesAndGraft' ] } ) } } ) );

    BioSync.ModalBox.showModalBox( { title: 'Unsaved Changes', content: content } );
}


BioSync.TreeViewer.viewer.prototype.handleSavedChanges = function( response ) {

    var viewer = this;

    viewer.renderUtil.cancelGraft( { data: { viewer: viewer } } );
    viewer.renderUtil.updateColumns( { clickedIndex: -1, viewer: viewer } );

    var response = eval( "(" + response + ")" );

    response.renderInfo.viewer = viewer;

    if( viewer.treeId != response.treeId ) { window.location.hash = response.treeId; }

    viewer.treeId = response.treeId;

    viewer.renderUtil.renderReceivedTree( response.renderInfo );

    viewer.container.trigger( 'graftSuccess', { } );
}


BioSync.TreeViewer.RenderUtil.phylogram.navigate.showGraftOptions = function( p ) {

    var graftInfo = p.viewer.graftInfo;

    graftInfo.graftButton.animate( { opacity: 1 }, 750 );
    graftInfo.cancelButton.animate( { opacity: 1 }, 750 );
}

BioSync.TreeViewer.RenderUtil.phylogram.navigate.approveGraft = function( p ) {

    var viewer = p.data.viewer;
    var graftInfo = viewer.graftInfo;

    var make = BioSync.Common.makeEl;
    var form = BioSync.ModalBox;
               
    var struct = ( viewer.treeType == 'source' )
        ? { content: make('div').append(
                form.makeBasicTextRow( { text: [ 'A ', graftInfo.graftType, ' action on a source tree requires the creation of a \'grafted\' tree' ].join('') } ),
                form.makeBasicTextInput( { name: 'treeName', text: 'Tree Name : ', value: 'Untitled Grafted Tree' } ),
                form.makeBasicLongTextInput( { name: 'treeComment', text: 'Tree Description : ', value: '' } ),
                form.makeBasicTextInput( { name: 'graftComment', text: 'Graft Comment : ', value: '' } ) ),
            title: 'Create Grafted Tree' }

        : { content: make('div').append(
                form.makeBasicTextRow( { text: [ 'Please provide a comment to describe your ', graftInfo.graftType, '.' ].join('') } ),
                form.makeBasicTextInput( { name: 'graftComment', text: 'Comment : ', value: '' } ) ),
            title: BioSync.Common.capitalizeFirstLetter( graftInfo.graftType ) };

    struct.content.append(
          form.makeHiddenInput( { name: 'clipboardNodeId', value: graftInfo.clipboardNodeId } ),
          form.makeHiddenInput( { name: 'affectedNodeId', value: graftInfo.affectedNodeId } ),
          form.makeHiddenInput( { name: 'affectedCladeId', value: graftInfo.affectedCladeId } ),
          form.makeHiddenInput( { name: 'graftType', value: graftInfo.graftType } ),
          form.makeHiddenInput( { name: 'treeId', value: viewer.treeId } ),
          form.makeHiddenInput( { name: 'treeType', value: viewer.treeType } ),
          form.makeHiddenInput( { name: 'viewMode', value: viewer.viewMode } ),
          form.makeBasicActionRow( {
              submitText: 'Create Tree',
              submitArgs: { context: viewer, 
                            onSuccess: new Array( function() { viewer.renderUtil.cancelGraft( { data: { viewer: viewer } } );
                                                               viewer.renderUtil.updateColumns( { clickedIndex: -1, viewer: viewer } ); },
                                                  viewer.handleGraftResponse ),
                            submitUrl: BioSync.Common.makeUrl( { controller: 'plugin_treeGrafter', argList: [ 'commitGraftAction' ] } ) } } ) );

    BioSync.ModalBox.showModalBox( { title: struct.title, content: struct.content } );
}


BioSync.TreeViewer.RenderUtil.phylogram.navigate.cancelGraft = function( p ) {

    var viewer = p.data.viewer;
    var currentColumn = viewer.columns[ viewer.graftColumnIndex ];
    var graftInfo = viewer.graftInfo;

    if( graftInfo.graftType != 'prune' ) {

        viewer.currentColumnIndex = viewer.graftColumnIndex;
        viewer.renderUtil.removeColumns( { clickedIndex: viewer.graftColumnIndex, viewer: viewer } );

        currentColumn.container.find('.hiddenHover').hover( viewer.showDescendantInfo, viewer.hideDescendantInfo );
        currentColumn.container.bind( 'mousemove', { viewer: viewer, column: currentColumn, nodeSelector: currentColumn.nodeSelector }, viewer.renderUtil.updateNodeSelector );
        currentColumn.path.attr( { stroke: viewer.style.color } );
   
        graftInfo.affectedCladePath.remove(); 
        graftInfo.newCladePath.remove();
        graftInfo.clipboardCladePath.remove();
        graftInfo.animateGraftCanvas.clear();
    }

    delete viewer.graftInfo;
}

BioSync.TreeViewer.RenderUtil.phylogram.navigate.handleClipboardItemMovement = function( p ) {

    var viewer = p.viewer;

    if( viewer.graftInfo ) { return; }
    if( viewer.graftSvgPath ) { viewer.removeGraftInfo(); }

    for( var i = 0, ii = viewer.columns.length; i < ii; i++ ) {

        var column = viewer.columns[i];

        if( BioSync.Common.isMouseOnElement( { el: column.container, x: p.x, y: p.y } ) ) {
    
            var closestNodeInfo =
                    viewer.getClosestNode( {
                        coords: this.DOMToCanvasCoords( { viewer: viewer, currentColumn: column, x: p.x, y: p.y } ),
                        node: column.nodeInfo[ column.rootId ],
                        nodeId: column.rootId,
                        nodeInfo: column.nodeInfo } );

            if( closestNodeInfo.distance < 25 ) {
                var pathString = BioSync.TreeViewer.RenderUtil.Common.getCladePathString( { node: closestNodeInfo.node, nodeInfo: column.nodeInfo } );
                viewer.graftSvgPath = column.canvas.path( pathString ).attr( { stroke: 'orange', "stroke-width": viewer.style.pathWidth } );
                viewer.graftNodeId = closestNodeInfo.id;
                viewer.graftColumnIndex = i;
            }

            break;
        }
    }
};




$(document).bind( 'clipboardItemDrop', { }, BioSync.TreeGrafter.checkClipboardItemDrop ); 
$(document).bind( 'movingClipboardItem', { }, BioSync.TreeGrafter.checkMovingClipboardItem );
