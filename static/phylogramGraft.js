BioSync.TreeGrafter.RenderUtil = {

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

BioSync.TreeGrafter.RenderUtil.phylogram.navigate.prototype = new BioSync.TreeViewer.RenderUtil.phylogram.navigate();
BioSync.TreeGrafter.RenderUtil.phylogram.navigate.constructor = BioSync.TreeGrafter.RenderUtil.phylogram.navigate;
BioSync.TreeGrafter.RenderUtil.phylogram.navigate.prototype.super = BioSync.TreeViewer.RenderUtil.phylogram.navigate.prototype;

BioSync.TreeGrafter.RenderUtil.phylogram.navigate.prototype.start = function( viewer ) {

    this.viewer = viewer;
    this.make = BioSync.Common.makeEl;

    BioSync.Common.loadScript( { name: 'phylogramColumn' } );
    BioSync.Common.loadScript( { name: 'phylogramColumnGraft' } );

    return this;
}

BioSync.TreeGrafter.RenderUtil.phylogram.navigate.prototype.getColumnObj = function() {

    return new BioSync.TreeGrafter.RenderUtil.Column( this ).initialize( { index: this.columns.length } );
}

BioSync.TreeGrafter.RenderUtil.phylogram.navigate.prototype.showCollapseDetail = function( e ) {

    if( this.viewer.movingClipboardItem ) { return; }

    else { $.proxy( this.super.showCollapseDetail, this )(e); }
}

BioSync.TreeGrafter.RenderUtil.phylogram.navigate.prototype.removeGraftInfo = function() {

    this.graftSvgPath.remove();
    this.graftSvgPath = undefined;
    this.graftNodeId = undefined;
}

BioSync.TreeGrafter.RenderUtil.phylogram.navigate.prototype.makeShowEditLegend = function( p ) {

    var content = this.make('div').attr( { 'class': 'legendContainer' } );

    for( var i = 0, ii = p.items.length; i < ii; i++ ) {

        content.append(
            this.make('div').css( {
                'border-top': [ Math.floor( (this.viewer.config.pathWidth / 2) ), 'px solid ', p.items[i].color ].join(''),
                'border-bottom': [ Math.floor( (this.viewer.config.pathWidth / 2) ), 'px solid ', p.items[i].color ].join(''),
                'padding': '0px 10px',
                'height': '0px',
                'float': 'left',
                'margin-top': '8px',
                'margin-right': '4px',
                'width': '25px' } ),
            this.make('span').css( { 'white-space': 'nowrap' } ).text( p.items[i].text ),
            this.make('div').attr( { 'class': 'clear' } ) );
    }

    BioSync.Common.notify( {
        timeoutTrigger: 'doneViewingEdit',
        content: content,
        x: p.column.myOffset.left + ( p.column.myWidth / 2 ),
        y: p.column.svgDiv.offset().top - 50 } );

        //y: p.column.myOffset.top + ( this.viewer.config.verticalPadding / 2 ) + ( p.column.centerOffset / 2 ) } );

}

BioSync.TreeGrafter.RenderUtil.phylogram.navigate.prototype.annotatePrePrune = function() {

    var affectedCladeId = this.showAction.affectedCladeId;
    var affectedNodeId = this.showAction.affectedNodeId;
    
    var column = this.columns[0];
    
    $(document).trigger('showingPreEdit');

    this.makeShowEditLegend( {
        column: column,
        items: [ { color: this.viewer.config.primaryShowEditColor, text: 'Clade Before Prune' },
                 { color: this.viewer.config.secondaryShowEditColor, text: 'Pruned' } ] } );
    
    this.highlightClade( { column: column, nodeId: affectedCladeId, color: this.viewer.config.primaryShowEditColor } );
    this.highlightClade( { column: column, nodeId: affectedNodeId, color: this.viewer.config.secondaryShowEditColor } );

    this.getPostEditClade();
}

BioSync.TreeGrafter.RenderUtil.phylogram.navigate.prototype.annotatePreReplace = function() {

    var affectedCladeId = this.showAction.affectedCladeId;
    var affectedNodeId = this.showAction.affectedNodeId;
    
    var column = this.columns[0];
    
    $(document).trigger('showingPreEdit');

    this.makeShowEditLegend( {
        column: column,
        items: [ { color: this.viewer.config.primaryShowEditColor, text: 'Clade Before Replace' },
                 { color: this.viewer.config.secondaryShowEditColor, text: 'Replaced' } ] } );
    
    this.highlightClade( { column: column, nodeId: affectedCladeId, color: this.viewer.config.primaryShowEditColor } );
    this.highlightClade( { column: column, nodeId: affectedNodeId, color: this.viewer.config.secondaryShowEditColor } );

    this.getPostEditClade();
}

BioSync.TreeGrafter.RenderUtil.phylogram.navigate.prototype.annotatePreGraft = function() {

    var affectedCladeId = this.showAction.affectedCladeId;
    
    var column = this.columns[0];
    
    $(document).trigger('showingPreEdit');

    this.makeShowEditLegend( {
        column: column,
        items: [ { color: this.viewer.config.primaryShowEditColor, text: 'Clade Before Graft' } ] } );
    
    this.highlightClade( { column: column, nodeId: affectedCladeId, color: this.viewer.config.primaryShowEditColor } );

    this.getPostEditClade();
}

BioSync.TreeGrafter.RenderUtil.phylogram.navigate.prototype.annotatePostPrune = function( e ) {

    $(document).trigger('showingPostEdit');

    var affectedCladeId = this.showAction.affectedCladeId;
    var prunedCladeId = this.showAction.affectedNodeId;

    column = this.columns[1];
    
    this.highlightClade( { column: column, nodeId: affectedCladeId, color: this.viewer.config.primaryShowEditColor } );

    this.makeShowEditLegend( { column: column, items: [ { color: this.viewer.config.primaryShowEditColor, text: 'Clade After Prune' } ] } );
}

BioSync.TreeGrafter.RenderUtil.phylogram.navigate.prototype.annotatePostReplace = function( e ) {

    $(document).trigger('showingPostEdit');

    column = this.columns[1];
   
    this.highlightClade( { column: column, nodeId: this.showAction.affectedCladeId, color: this.viewer.config.primaryShowEditColor } );
    this.highlightClade( { column: column, nodeId: this.showAction.targetGnode, color: this.viewer.config.tertiaryShowEditColor } );

    this.makeShowEditLegend( {
        column: column,
        items: [ { color: this.viewer.config.primaryShowEditColor, text: 'Clade After Replace' },
                 { color: this.viewer.config.tertiaryShowEditColor, text: 'Replacing Clade' } ] } );
}

BioSync.TreeGrafter.RenderUtil.phylogram.navigate.prototype.annotatePostGraft = function( e ) {

    $(document).trigger('showingPostEdit');

    column = this.columns[1];
   
    this.highlightClade( { column: column, nodeId: this.showAction.affectedCladeId, color: this.viewer.config.primaryShowEditColor } );
    this.highlightClade( { column: column, nodeId: this.showAction.targetGnode, color: this.viewer.config.secondaryShowEditColor } );

    this.makeShowEditLegend( {
        column: column,
        items: [ { color: this.viewer.config.primaryShowEditColor, text: 'Clade After Graft' },
                 { color: this.viewer.config.secondaryShowEditColor, text: 'Grafted Clade' } ] } );
}

BioSync.TreeGrafter.RenderUtil.phylogram.navigate.prototype.showReplace = function() {

    var el = this.editEl;
    var affectedCladeId = this.showAction.affectedCladeId;
    var replacingCladeId = el.attr('targetGnode');

    var column = this.columns[0];
    
    $(document).trigger('showEdit');

    this.highlightClade( { column: column, nodeId: affectedCladeId, color: this.viewer.config.primaryShowEditColor } );
    this.highlightClade( { column: column, nodeId: replacingCladeId, color: this.viewer.config.secondaryShowEditColor } );
    
    this.makeShowEditLegend( {
        column: column,
        items: [ { color: this.viewer.config.primaryShowEditColor, text: 'Affected Clade' },
                 { color: this.viewer.config.secondaryShowEditColor, text: 'Replacing Clade' } ] } );

    this.addNewColumn();

    $.ajax( { url: BioSync.Common.makeUrl( { controller: 'plugin_treeGrafter', argList: [ 'getOldClade' ] } ),
              type: "GET", data: { treeId: this.viewer.treeId, nodeId: affectedCladeId, editId: el.attr('editId') },
              success: new Array( $.proxy( this.viewer.handleReceivedTree, this.viewer ), $.proxy( this.showReplaceUI, this ) )  } );
}

BioSync.TreeGrafter.RenderUtil.phylogram.navigate.prototype.showReplaceUI = function( e ) {

    var el = this.editEl;
    var affectedCladeId = this.showAction.affectedCladeId;
    var replacedCladeId = el.attr('affectedNodeId');

    column = this.columns[1];
    
    this.highlightClade( { column: column, nodeId: affectedCladeId, color: this.viewer.config.primaryShowEditColor } );
    this.highlightClade( { column: column, nodeId: replacedCladeId, color: this.viewer.config.secondaryShowEditColor } );
    
    this.makeShowEditLegend( {
        column: column,
        items: [ { color: this.viewer.config.primaryShowEditColor, text: 'Affected Clade' },
                 { color: this.viewer.config.secondaryShowEditColor, text: 'Replaced Clade' } ] } );
}

BioSync.TreeGrafter.RenderUtil.phylogram.navigate.prototype.showGraft = function() {

    var el = this.editEl;
    var affectedCladeId = this.showAction.affectedCladeId;

    $(document).trigger('showEdit');

    this.highlightClade( { column: this.columns[0], nodeId: affectedCladeId, color: this.viewer.config.primaryShowEditColor } );
    
    this.makeShowEditLegend( { column: this.columns[0], items: [ { color: this.viewer.config.primaryShowEditColor, text: 'Affected Clade' } ] } );

    this.addNewColumn();

    $.ajax( { url: BioSync.Common.makeUrl( { controller: 'plugin_treeViewer', argList: [ 'getClade' ] } ),
              type: "GET", data: { treeId: this.viewer.treeId, nodeId: affectedCladeId },
              success: new Array( $.proxy( this.viewer.handleReceivedTree, this.viewer ), $.proxy( this.showGraftUI, this ) )  } );
}

BioSync.TreeGrafter.RenderUtil.phylogram.navigate.prototype.showGraftUI = function( e ) {

    var el = this.editEl;
    var affectedCladeId = this.showAction.affectedCladeId;
    var graftedCladeId = el.attr('targetGnode');
    var column = this.columns[1];
     
    this.highlightClade( { column: column, nodeId: affectedCladeId, color: this.viewer.config.primaryShowEditColor, nodeOnly: true } );
    this.highlightClade( { column: column, nodeId: graftedCladeId, color: this.viewer.config.secondaryShowEditColor } );

    this.makeShowEditLegend( {
        column: column,
        items: [ { color: this.viewer.config.primaryShowEditColor, text: 'Affected Clade' },
                 { color: this.viewer.config.secondaryShowEditColor, text: 'New Clade' } ] } );
}

BioSync.TreeGrafter.RenderUtil.phylogram.navigate.prototype.undoEditAction = function( e ) {

    var target = $( e.target );
    var domEl = target.closest('.graftHistoryItem');

    var that = this;

    if( domEl.attr('originalTreeType') == 'source' ) {

        var modal = BioSync.ModalBox;
        
        var onClick = function() {
            BioSync.Common.notify( {
                text: 'Deleting Grafted Tree',
                timeoutTrigger: 'deleteGTreeSuccess',
                dotdotdot: true,
                x: that.viewer.myOffset.left + ( that.viewer.myWidth / 2 ),
                y: that.viewer.myOffset.top + 10 } ); };
        
        var notify = function() {
            BioSync.Common.notify( {
                text: 'Tree has been deleted.',
                x: that.viewer.myOffset.left + ( that.viewer.myWidth / 2 ),
                y: that.viewer.myOffset.top + ( that.viewer.myHeight / 2 ) } ); }

        var modalContent = this.make('div').append(
                modal.makeBasicTextRow( { text: 'As this is the first edit to the tree, an undo action would result in deletion of this grafted tree.  Would you like to continue?' } ),
                modal.makeHiddenInput( { name: 'treeId', value: this.viewer.treeId } ),
                modal.makeBasicActionRow( {
                     onClick:  onClick,
                     submitText: 'Yes',
                     submitArgs: { onSuccess:
                        new Array(
                            function() { $(document).trigger('deleteGTreeSuccess'); },
                            notify,
                            function() { setTimeout( function() { window.location = BioSync.Common.makeUrl( { controller: 'gtree', argList: [ 'index' ] } ); }, 2000 ); } ),
                                   submitUrl: BioSync.Common.makeUrl( { controller: 'plugin_treeGrafter', argList: [ 'deleteGtree' ] } ) } } ) );
    
        BioSync.ModalBox.showModalBox( { content: modalContent, title: 'Delete this tree?' } );
    }
}

BioSync.TreeGrafter.RenderUtil.phylogram.navigate.prototype.doneViewingEditAction = function( e ) {

    var target = $( e.target );

    target.unbind('click').text( 'view' ).bind( 'click', {}, $.proxy( this.viewEditAction, this ) ).removeClass('viewingThisAction');

    $(document).trigger('doneViewingEdit');
    
    if( ! this.viewAnotherAction ) {
    
        this.removeColumns( { start: 0, end: this.columns.length - 1 } );

        this.showAction = undefined;
    
        this.addNewColumn();
        
        this.viewer.getTreeById()
    }
}

BioSync.TreeGrafter.RenderUtil.phylogram.navigate.prototype.viewEditAction = function( e ) {

    var target = $( e.target );
    
    if( $('.viewingThisAction').length ) {

        this.viewAnotherAction = true;
        $('.viewingThisAction').click();
        this.viewAnotherAction = false;
    }

    target.unbind('click').text( 'done viewing' ).bind( 'click', { }, $.proxy( this.doneViewingEditAction, this ) ).addClass('viewingThisAction');

    var domEl = target.closest('.graftHistoryItem');

    this.showAction = {
        affectedCladeId: domEl.attr('affectedCladeId'), editId: domEl.attr('editId'), editEl: domEl, affectedNodeId: domEl.attr('affectedNodeId'),
        action: domEl.attr('action'), capitalAction: BioSync.Common.capitalizeFirstLetter( domEl.attr('action') ), targetGnode: domEl.attr('targetGnode')
    };

    /*
    BioSync.Common.notify( {
        text: [ 'Getting Pre-', this.showAction.capitalAction, ' Clade' ].join(''),
        timeoutTrigger: 'showingPreEdit',
        dotdotdot: true,
        x: this.viewer.myOffset.left + ( this.viewer.myWidth / 2 ),
        y: this.viewer.myOffset.top + 10 } );
    */
  
    this.removeColumns( { start: 0, end: this.columns.length - 1 } );
    
    this.addNewColumn();

    $.ajax( { url: BioSync.Common.makeUrl( { controller: 'plugin_treeGrafter', argList: [ 'getPreEditClade' ] } ),
              type: "GET", data: { treeId: this.viewer.treeId, editId: this.showAction.editId },
              success: new Array( $.proxy( this.viewer.handleReceivedTree, this.viewer ),
                                  $.proxy( this[ [ 'annotatePre', this.showAction.capitalAction ].join('') ], this ) ) } );
}

BioSync.TreeGrafter.RenderUtil.phylogram.navigate.prototype.getPostEditClade = function( p ) {

    this.addNewColumn();

    $.ajax( { url: BioSync.Common.makeUrl( { controller: 'plugin_treeGrafter', argList: [ 'getPostEditClade' ] } ),
              type: "GET", data: { editId: this.showAction.editId },
              success: new Array( $.proxy( this.viewer.handleReceivedTree, this.viewer ), $.proxy( this[ [ 'annotatePost', this.showAction.capitalAction ].join('') ], this ) )  } );
}


BioSync.TreeGrafter.RenderUtil.phylogram.navigate.prototype.showPruneEditStatus = function() {

    var modal = BioSync.ModalBox;

    var content =
        this.make( 'div' ).attr( { 'class': 'treeEditStatus' } ).append(
            this.make( 'span' ).text( 'Pruning tree, updating database' ) );

    var myDoc = $(document);

    modal.showModalBox( { content: content, width: ( myDoc.width() / 2 )  } );

    var successFunctions = new Array( $.proxy( this.unHighlightClade, this ) );

    if( ( this.viewer.treeType == 'source' ) ) {

        successFunctions = successFunctions.concat( [ $.proxy( this.viewer.updateUrl, this.viewer ), $.proxy( this.getTreeAfterEdit, this ) ] );

    } else {

        successFunctions.push( $.proxy( this.getColumnAfterEdit, this ) );
    }

    BioSync.Common.dotDotDotText( {
        content: content,
        minimumTime: 2000,
        stopTrigger: 'editSuccess',
        stopText: 'Pruned',
        stopFunction: successFunctions } );
}

BioSync.TreeGrafter.RenderUtil.phylogram.navigate.prototype.getColumnAfterEdit = function() {

    var content = this.make( 'div' ).attr( { 'class': 'treeEditStatus' } ).append( this.make( 'span' ).text( 'Getting updated column' ) );

    BioSync.ModalBox.contentContainer.append( content );
    
    BioSync.Common.dotDotDotText( {
        content: content,
        minimumTime: 2000,
        stopTrigger: 'getCladeSuccess',
        stopFunction: new Array( BioSync.ModalBox.closeBox ),
        stopText: 'Received Column' } );

    this.refreshColumn( { column: this.prunedColumn } );
}

BioSync.TreeGrafter.RenderUtil.phylogram.navigate.prototype.getTreeAfterEdit = function() {

    var content = this.make( 'div' ).attr( { 'class': 'treeEditStatus' } ).append( this.make( 'span' ).text( 'Getting updated tree' ) );

    BioSync.ModalBox.contentContainer.append( content );
    
    BioSync.Common.dotDotDotText( {
        content: content,
        minimumTime: 2000,
        stopTrigger: 'getCladeSuccess',
        stopFunction: new Array( BioSync.ModalBox.closeBox ),
        stopText: 'Received Tree' } );
  
    this.redrawTree();
}

BioSync.TreeGrafter.RenderUtil.phylogram.navigate.prototype.preProcessEditedTree = function() {

    var content = this.make( 'div' ).attr( { 'class': 'treeEditStatus' } ).append( this.make( 'span' ).text( 'Preprocessing Tree for Viewing' ) );

    BioSync.ModalBox.contentContainer.append( content );
    
    BioSync.Common.dotDotDotText( {
        content: content,
        minimumTime: 2000,
        stopTrigger: 'preprocessSuccess',
        stopFunction: new Array( $.proxy( this.redrawTree, this ), $.proxy( this.viewer.sidebar.hideAnyPanelContent, this.viewer.sidebar ), $.proxy( this.viewer.getGraftHistory, this.viewer ), BioSync.ModalBox.closeBox ),
        stopText: 'Tree Preprocessed' } );

    $.ajax( { url: BioSync.Common.makeUrl( { controller: 'plugin_treeGrafter', argList: [ 'preProcessEditedTree' ] } ),
              type: "GET", 
              success: new Array( $.proxy( this.preprocessSuccess, this ) ) } );
}

BioSync.TreeGrafter.RenderUtil.phylogram.navigate.prototype.preprocessSuccess = function() {
    
    $( document ).trigger( 'preprocessSuccess' );
}

BioSync.TreeGrafter.RenderUtil.phylogram.navigate.prototype.treeEditSuccess = function() {

    $( document ).trigger( 'editSuccess' );
}

BioSync.TreeGrafter.RenderUtil.phylogram.navigate.prototype.editAction = function( p ) {

    var renderObj = this;
    var treeType = renderObj.viewer.treeType;

    var modal = BioSync.ModalBox;

    this.editActionString = p.data.action;

    var successArray = new Array( $.proxy( renderObj.treeEditSuccess, renderObj ) );

    var modalContent = renderObj.make('div').append(
        modal.makeBasicTextRow( { text: [ 'Please provide a comment on your ', p.data.action, ' action.' ].join('') } ),
        modal.makeBasicTextInput( { text: 'Comment : ', name: 'comment', value: '' } ),
        modal.makeHiddenInput( { name: 'affectedNodeId', value: p.data.nodeId } ),
        modal.makeHiddenInput( { name: 'clipboardNodeId', value: p.data.clipboardNodeId } ),
        modal.makeBasicActionRow( {
             onClick:  $.proxy( this.showTreeEditStatus, this ),
             submitText: 'Continue',
             submitArgs: { onSuccess: successArray,
                           submitUrl: BioSync.Common.makeUrl( { controller: 'plugin_treeGrafter', argList: [ [ p.data.action, 'Clade' ].join('') ] } ) } } ) );

    if( treeType == 'source' ) {
        $( modalContent.children().last() ).before( renderObj.make('div').append( 
            modal.makeBasicTextRow( { 'text': '' } ),
            modal.makeBasicTextRow( { 'text': "This action will create a new 'grafted' tree.  Please give it a name and description" } ),
            modal.makeBasicTextInput( { text: 'Grafted Tree Name : ', name: 'treeName', value: 'Untitled Grafted Tree' } ),
            modal.makeBasicTextInput( { text: 'Description : ', name: 'treeDescription', value: '' } ) ) );
    }
       
    modal.showModalBox( { content: modalContent,
                          title: [ BioSync.Common.capitalizeFirstLetter( p.data.action ), ' Clade' ].join(''),
                          onClose: new Array( $.proxy( renderObj.unHighlightClade, renderObj ) ) } );
}

BioSync.TreeGrafter.RenderUtil.phylogram.navigate.prototype.handleClipboardDrop = function( e, p ) {

    if( ! this.graftSvgPath ) { return; }

    BioSync.OptionsMenu.makeContextMenu(
        { coords: p.dropCoords, clickAway: $.proxy( this.removeGraftInfo, this ),
          options: [
                { 'text': 'Replace Clade', 'action': $.proxy( this.editAction, this ),
                  'params': { action: 'replace', clipboardNodeId: p.clipboardId, nodeId: this.graftNodeId } },
                { 'text': 'Add Sibling', 'action': $.proxy( this.editAction, this ),
                  'params': { action: 'graft', clipboardNodeId: p.clipboardId, nodeId: this.graftNodeId } } ] } );
}

BioSync.TreeGrafter.RenderUtil.phylogram.navigate.prototype.handleMovingClipboardItem = function( e ) {

    if( this.graftSvgPath ) { this.removeGraftInfo(); }

    for( var i = 0, ii = this.columns.length; i < ii; i++ ) {

        var column = this.columns[i];

        if( BioSync.Common.isMouseOnElement( { el: column.container, x: e.x, y: e.y } ) ) {
    
            var closestNodeInfo =
                    this.getClosestNode( {
                        coords: this.translateDOMToCanvas( { column: column, x: e.x, y: e.y } ),
                        currentNodeId: column.rootId,
                        column: column } );

            if( closestNodeInfo.distance < 25 ) {

                var pathString = this.getCladePathString( { column: column, nodeInfo: column.nodeInfo[ closestNodeInfo.id ] } );

                this.graftSvgPath = column.canvas.path( pathString ).attr( { stroke: 'orange', "stroke-width": this.viewer.config.pathWidth } );

                this.graftNodeId = closestNodeInfo.id;

                this.graftColumnIndex = i;
            }

            break;
        }
    }
}

BioSync.TreeGrafter.RenderUtil.phylogram.navigate.prototype.pruneClade = function( p ) {

    var modal = BioSync.ModalBox;

    this.prunedColumn = p.column;
    this.prunedNodeId = p.nodeId;

    this.highlightClade( { column: p.column, nodeId: p.nodeId } );
    
    var successArray = new Array( $.proxy( this.treeEditSuccess, this ) );

    var content = this.make('div').append(
        modal.makeBasicTextRow( { text: 'Please provide a comment on your prune action.' } ),
        modal.makeBasicTextInput( { text: 'Comment : ', name: 'comment', value: '' } ),
        modal.makeHiddenInput( { name: 'nodeId', value: p.nodeId } ),
        modal.makeHiddenInput( { name: 'columnIndex', value: p.column.index } ),
        modal.makeBasicActionRow( {
             onClick:  $.proxy( this.showPruneEditStatus, this ),
             onCancel: $.proxy( this.unHighlightClade, this ),
             submitText: 'Continue',
             submitArgs: { onSuccess: successArray,
                           submitUrl: BioSync.Common.makeUrl( { controller: 'plugin_treeGrafter', argList: [ 'pruneClade' ] } ) } } ) );

    if( this.viewer.treeType == 'source' ) {

        $( content.children().last() ).before( this.make('div').append( 
            modal.makeBasicTextRow( { 'text': '' } ),
            modal.makeBasicTextRow( { 'text': "This action will create a new 'grafted' tree.  Please give it a name and description" } ),
            modal.makeBasicTextInput( { text: 'Grafted Tree Name : ', name: 'treeName', value: 'Untitled Grafted Tree' } ),
            modal.makeBasicTextInput( { text: 'Description : ', name: 'treeDescription', value: '' } ) ) );
    }

    BioSync.ModalBox.showModalBox( { content: content, title: 'Prune Clade' } );
}

BioSync.TreeGrafter.RenderUtil.phylogram.navigate.prototype.handleGraftHistory = function( response ) {

    var response = eval( "(" + response + ")" );

    //var graftHistory = this.graftHistory = { };

    if( $('.graftHistoryContent').length ) {
      
        //bad - need to create right panel obj 
        var target = $( ".panelName:contains('Graft')" ).next();

        this.viewer.removePanel( { target: target } );
    }

    var content = this.make( 'div' ).attr( { 'class': 'graftHistoryContent' } )
        .mousedown( BioSync.Common.returnFalse );

    var make = this.make;

    for( var i = 0, ii = response.length; i < ii; i++ ) {

        var item = response[ i ];

        //add navigate to node?

        content.append(
            make('div').attr( { 'class': 'graftHistoryItem', 'editId': item.gtree_edit.id, 'action': item.gtree_edit.action, targetGnode: item.gtree_edit.target_gnode,
                                'affectedNodeId': item.gtree_edit.affected_node_id, 
                                'affectedCladeId': item.gtree_edit.affected_clade_id, 'originalTreeType': item.gtree_edit.originalTreeType } ).append(
                make('div').attr( { 'class': 'graftHistoryDetailContainer' } ).append( 
                    make('div').attr( { 'class': 'graftHistoryLabel' } ).text( 'action : ' ),
                    make('div').attr( { 'class': 'graftHistoryValue' } ).text( item.gtree_edit.action ),
                    make('div').attr( { 'class': 'clear' } ) ),
                make('div').attr( { 'class': 'graftHistoryDetailContainer' } ).append( 
                    make('div').attr( { 'class': 'graftHistoryLabel' } ).text( 'by : ' ),
                    make('div').attr( { 'class': 'graftHistoryValue' } ).text( [ item.auth_user.first_name, item.auth_user.last_name ].join(' ' ) ),
                    make('div').attr( { 'class': 'clear' } ) ),
                make('div').attr( { 'class': 'graftHistoryDetailContainer' } ).append( 
                    make('div').attr( { 'class': 'graftHistoryLabel' } ).text( 'comment : ' ),
                    make('div').attr( { 'class': 'graftHistoryValue' } ).text( item.gtree_edit.comment ),
                    make('div').attr( { 'class': 'clear' } ) ),
                make('div').attr( { 'class': 'graftHistoryActionContainer' } ).append( 
                    make('div').attr( { 'class': 'graftHistoryAction' } ).text( 'view' ).bind( 'click', {}, $.proxy( this.viewEditAction, this ) ),
                    make('div').attr( { 'class': 'graftHistoryAction' } ).text( 'undo' ).bind( 'click', {}, $.proxy( this.undoEditAction, this ) ),
                    make('div').attr( { 'class': 'clear' } ) ) ) );
    }

    this.viewer.addPanel( { content: content, name: 'Graft History' } );
}
