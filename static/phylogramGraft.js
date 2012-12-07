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


BioSync.TreeGrafter.RenderUtil.phylogram.navigate.prototype.showGraftEditStatus = function() {

    this.showTreeEditStatus( { preSuccessText: 'Adding child, updating database',
                               successText: 'Added' } );
}

BioSync.TreeGrafter.RenderUtil.phylogram.navigate.prototype.showReplaceEditStatus = function() {
    
    this.showTreeEditStatus( { preSuccessText: 'Replacing clade, updating database',
                               successText: 'Replaced' } );
}

BioSync.TreeGrafter.RenderUtil.phylogram.navigate.prototype.showPruneEditStatus = function() {

    this.showTreeEditStatus( { preSuccessText: 'Pruning tree, updating database',
                               successText: 'Pruned' } );
}

BioSync.TreeGrafter.RenderUtil.phylogram.navigate.prototype.showTreeEditStatus = function( p ) {

    var modal = BioSync.ModalBox;

    var content =
        this.make( 'div' ).attr( { 'class': 'treeEditStatus' } ).append(
            this.make( 'span' ).text( p.preSuccessText ) );

    var myDoc = $(document);

    modal.showModalBox( { content: content, width: ( myDoc.width() / 2 )  } );

    var successFunctions = new Array( $.proxy( this.unHighlightClade, this ) );

    if( ( this.viewer.treeType == 'source' ) ) {

        successFunctions.push( $.proxy( this.viewer.updateUrl, this.viewer ) );
    }
    
    successFunctions.push( $.proxy( this.getTreeAfterEdit, this ) );

    BioSync.Common.dotDotDotText( {
        content: content,
        minimumTime: 2000,
        stopTrigger: 'editSuccess',
        stopText: p.successText,
        stopFunction: successFunctions } );
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

BioSync.TreeGrafter.RenderUtil.phylogram.navigate.prototype.getClipboardForCladeGraft = function( p ) {

    this.graftingColumn = p.column;
    this.graftingOntoNodeId = p.nodeId;
    this.treeEditType = 'graft';

    this.highlightClade( { column: p.column, nodeId: this.graftingOntoNodeId, nodeOnly: true } );

    $.ajax( { url: BioSync.Common.makeUrl( { controller: 'plugin_clipboard', argList: [ 'getClipboard' ] } ),
              type: "GET", data: { },
              success: new Array( $.proxy( this.showModalClipboardForTreeEdit, this ) ) } );
}

BioSync.TreeGrafter.RenderUtil.phylogram.navigate.prototype.showModalClipboardForTreeEdit = function( response ) {

    var clipboardInfo = eval( '(' + response + ')' );
    
    var modal = BioSync.ModalBox;

    var clipboardItems = this.make('div');
    var graftedClipboardItems = this.make('div');

    var css = { 'float': 'left', 'text-align': 'center', margin: '5px 0px', 'font-weight': 'bold' };

    var modalBoxWidth = this.viewer.windowWidth * .75;

    var instructionText = modalText = undefined;

    if( this.treeEditType == 'graft' ) {

        this.clipboardSubmitButton = this.graftButton = this.make('span').text( 'Add Child' ).css( { 'color': 'grey' } ).attr( { 'active': 'no' } );
        this.clipboardSubmitAction = this.askForGraftCladeInfo;
        instructionText = "Here are your clipboard items.  Click on an item to select it.  To add an item in this list as a child to the selected node in the tree, click the 'Add Child' button below.";
        modalText = 'Add Clipboard Item to Tree';

    } else {

        this.clipboardSubmitButton = this.replaceButton = this.make('span').text( 'Replace' ).css( { 'color': 'grey' } ).attr( { 'active': 'no' } );
        this.clipboardSubmitAction = this.askForReplaceCladeInfo;
        instructionText = "Here are your clipboard items.  Click on an item to select it.  To replace the clade in the tree with an item in this list, click the 'Replace' button below.";
        modalText = 'Replace Clade with Clipboard Item';
    }

    $('#modalBoxForm').append(
        this.make( 'div' ).append(
            this.make( 'div' ).append(
                BioSync.ModalBox.makeBasicTextRow( { text: instructionText } ),
                this.make('div').css( { 'text-align': 'center',
                                        'font-size': '20px',
                                        'color': 'steelBlue',
                                        'margin-bottom': '10px',
                                        'padding': '10px' } ).text( 'Source Tree Clipboard Items' ),
                this.make( 'div' ).css( { 'border': '1px solid black',
                                          'padding': '10px',
                                          'border-radius': '5px' } ).append( 
                    this.make( 'div' ).width( modalBoxWidth * .25 ).css( css ).text( 'Name' ),
                    this.make( 'div' ).width( modalBoxWidth * .10 ).css( css ).text( 'Descendants' ),
                    this.make( 'div' ).width( modalBoxWidth * .15 ).css( css ).text( 'Date Created' ),
                    this.make( 'div' ).width( modalBoxWidth * .45 ).css( css ).text( 'Study' ),
                    this.make( 'div' ).css( { 'clear': 'both' } ),
                    clipboardItems
                ),

                this.make( 'div' ).width( '100%' ).css( { 'margin': '25px 0px', 'border': '1px solid green' } ),

                this.make('div').css( { 'text-align': 'center',
                                        'font-size': '20px',
                                        'color': 'steelBlue',
                                        'margin-bottom': '10px',
                                        'padding': '10px' } ).text( 'Grafted Tree Clipboard Items' ),

                this.make( 'div' ).css( { 'border': '1px solid black',
                                          'padding': '10px',
                                          'border-radius': '5px' } ).append( 
                    this.make( 'div' ).width( modalBoxWidth * .20 ).css( css ).text( 'Name' ),
                    this.make( 'div' ).width( modalBoxWidth * .20 ).css( css ).text( 'Descendants' ),
                    this.make( 'div' ).width( modalBoxWidth * .20 ).css( css ).text( 'Date Created' ),
                    this.make( 'div' ).width( modalBoxWidth * .20 ).css( css ).text( 'Grafted Tree Name' ),
                    this.make( 'div' ).css( { 'clear': 'both' } ),
                    graftedClipboardItems
                ),


                this.make( 'div' ).attr( { 'class': 'actionRow' } ).css( { 'padding-bottom': '10px' } ).append(
                    this.make('div').attr( { 'class': 'twoOpt modalBoxSubmit' } )
                                    .css( { 'float': 'left' } ).append(
                        this.graftButton ),
                    this.make('div').attr( { 'class': 'twoOpt' } )
                                    .css( { 'float': 'left', 'color': 'steelBlue' } ).append(
                        this.make('span').attr( { 'class': 'modalBoxCancel' } )
                                         .hover( BioSync.Common.setMouseToPointer, BioSync.Common.setMouseToDefault )
                                        .text( 'Cancel' )
                                        .bind( 'click', { }, BioSync.ModalBox.closeBox )
                                        .bind( 'click', { }, $.proxy( this.unHighlightClade, this ) ) ) )
            )
        )
    );

    delete css['font-weight'];
    delete css['font-size'];

    this.clipboardItems = { };

    for( var i = 0, ii = clipboardInfo.sourceList.length; i < ii; i++ ) {

        var item = clipboardInfo.sourceList[ i ];

        this.clipboardItems[ item[0] ] = {
            type: 'source',
            id: item[8],
            studyDiv: this.make('div').width( modalBoxWidth * .45 ).css( css )
                                      .css( { 'white-space': 'nowrap', 'overflow': 'hidden', 'text-overflow': 'ellipsis' } ).append(
                          this.make( 'span' ).text( item[7] /*.substr( 0, 50 ) */ ).attr( { 'title': item[7] } )
                                       .hover( BioSync.Common.underlineText, BioSync.Common.removeTextUnderline )
                                       .bind( 'click', { studyId: item[6] }, $.proxy( this.openNewStudyWindow, this ) ) ) }

        clipboardItems.append(
            this.make( 'div' ).attr( { 'clipboardId': item[0] } )
                              .hover( BioSync.Common.setMouseToPointer, BioSync.Common.setMouseToDefault )
                              .hover( $.proxy( this.giveGreyBackground, this ), $.proxy( this.removeGreyBackground, this ) )
                              .bind( 'click', { }, $.proxy( this.selectClipboardItem, this ) ).append(
                this.make('div').width( modalBoxWidth * .25 )
                                .css( css )
                                .text( item[2] )
                                .attr( { 'title': item[2] } )
                                .css( { 'white-space': 'nowrap', 'overflow': 'hidden', 'text-overflow': 'ellipsis' } ),
                this.make('div').width( modalBoxWidth * .10 ).css( css ).text( ( Math.floor( ( item[5] - item[4] - 1 ) / 2 ) ) ),
                this.make('div').width( modalBoxWidth * .15 ).css( css ).text( item[3] ),
                this.clipboardItems[ item[0] ].studyDiv, 
                this.make( 'div' ).css( { 'clear': 'both' } )
            )
        );
       
    }

    for( var i = 0, ii = clipboardInfo.graftedList.length; i < ii; i++ ) {

        var item = clipboardInfo.graftedList[ i ];

        this.clipboardItems[ item[0] ] = { type: 'grafted', id: item[7] }; 

        graftedClipboardItems.append(
            this.make( 'div' ).attr( { 'clipboardId': item[0] } )
                              .hover( BioSync.Common.setMouseToPointer, BioSync.Common.setMouseToDefault )
                              .hover( $.proxy( this.giveGreyBackground, this ), $.proxy( this.removeGreyBackground, this ) )
                              .bind( 'click', { }, $.proxy( this.selectClipboardItem, this ) ).append(
                this.make('div').width( modalBoxWidth * .21 )
                                .css( css )
                                .text( item[2] )
                                .attr( { 'title': item[2] } )
                                .css( { 'white-space': 'nowrap', 'overflow': 'hidden', 'text-overflow': 'ellipsis' } ),
                this.make('div').width( modalBoxWidth * .21 ).css( css ).text( ( Math.floor( ( item[5] - item[4] - 1 ) / 2 ) ) ),
                this.make('div').width( modalBoxWidth * .21 ).css( css ).text( item[3] ),
                this.make('div').width( modalBoxWidth * .21 ).css( css )
                       .css( { 'white-space': 'nowrap', 'overflow': 'hidden', 'text-overflow': 'ellipsis' } ).append(
                    this.make( 'span' ).text( item[6] ).attr( { 'title': item[6] } )
                ),
                this.make( 'div' ).css( { 'clear': 'both' } )
            )
        );
    }

    BioSync.ModalBox.showModalBox( {
            width: modalBoxWidth,
            title: modalText } );

    var viewer = this.viewer;
    var clipboardItemsInfo = this.clipboardItems;

    setTimeout( function() {

        var modalBoxContent = $('#modalBoxContent');
        var heightDifference = modalBoxContent.outerHeight( true ) - viewer.windowHeight;

        if( heightDifference > 0 ) {

           var sourceListHeight = clipboardItems.outerHeight( true ); 
           var graftedListHeight = graftedClipboardItems.outerHeight( true ); 

           var sourceRatio = sourceListHeight / ( graftedListHeight + sourceListHeight );
           var graftedRatio = graftedListHeight / ( graftedListHeight + sourceListHeight );

           clipboardItems.height( clipboardItems.height() - 30 - ( sourceRatio * heightDifference ) )
                         .css( { 'overflow': 'auto' } );

           graftedClipboardItems.height( graftedClipboardItems.height() - 30 - ( graftedRatio * heightDifference ) )
                                .css( { 'overflow': 'auto' } );

           for( var clipboardId in clipboardItemsInfo ) {

                if( clipboardItemsInfo[ clipboardId ].studyDiv ) {

                    clipboardItemsInfo[ clipboardId ].studyDiv.width( clipboardItemsInfo[ clipboardId ].studyDiv.width() - BioSync.Common.scrollbarWidth );
                }
           }

           modalBoxContent.css( { top: ( ( $(document).height() - ( modalBoxContent.outerHeight( true ) ) ) / 2 ) } );

        } }, 2000 );
}

BioSync.TreeGrafter.RenderUtil.phylogram.navigate.prototype.getClipboardForCladeReplace = function( p ) {

    this.replacingColumn = p.column;
    this.replacedNodeId = p.nodeId;
    this.treeEditType = 'replace';

    this.highlightClade( { column: p.column, nodeId: p.nodeId } );

    $.ajax( { url: BioSync.Common.makeUrl( { controller: 'plugin_clipboard', argList: [ 'getClipboard' ] } ),
              type: "GET", data: { },
              success: new Array( $.proxy( this.showModalClipboardForTreeEdit, this ) ) } );
}

BioSync.TreeGrafter.RenderUtil.phylogram.navigate.prototype.giveGreyBackground = function( e ) {
    $( e.delegateTarget ).css( { 'background-color': '#F0F0F0' } );
}

BioSync.TreeGrafter.RenderUtil.phylogram.navigate.prototype.removeGreyBackground = function( e ) {

    if( ( this.selectedClipboardItem ) && ( e.delegateTarget == this.selectedClipboardItem.get(0) ) ) { return; }

    $( e.delegateTarget ).css( { 'background-color': '' } );
}

BioSync.TreeGrafter.RenderUtil.phylogram.navigate.prototype.selectClipboardItem = function( e ) {

    var el = $( e.delegateTarget );

    if( this.selectedClipboardItem ) { this.selectedClipboardItem.css( { 'background-color': '' } ); }
    
    if( ( this.selectedClipboardItem ) && ( this.selectedClipboardItem.get(0) == e.delegateTarget ) ) {

        this.clipboardSubmitButton.unbind( 'mouseenter' ).unbind( 'mouseleave' ).css( { 'color': 'grey' } ).attr( { 'active': 'no' } );
        delete this.selectedClipboardItem;

    } else {
       
        this.selectedClipboardItem = el.css( { 'background-color': '#F0F0F0' } );

        if( this.clipboardSubmitButton.attr( 'active' ) == 'no' ) {

            this.clipboardSubmitButton.css( { 'color': 'steelBlue' } )
                              .hover( BioSync.Common.setMouseToPointer, BioSync.Common.setMouseToDefault )
                              .attr( { 'active': 'yes' } )
                              .bind( 'click', { }, BioSync.ModalBox.closeBox )
                              .bind( 'click', { }, $.proxy( this.clipboardSubmitAction, this ) );
        }
    }
}

BioSync.TreeGrafter.RenderUtil.phylogram.navigate.prototype.openNewStudyWindow = function( e ) {

    window.open( BioSync.Common.makeUrl( { controller: 'study', argList: [ 'view', e.data.studyId ] } ) );

    e.preventDefault();  e.stopPropagation();
}

BioSync.TreeGrafter.RenderUtil.phylogram.navigate.prototype.addNewGraftedTreeDialogueToContent = function( p ) {

    var modal = BioSync.ModalBox;

    $( p.content.children().last() ).before(
        this.make('div').append( 
            modal.makeBasicTextRow( { 'text': '' } ),
            modal.makeBasicTextRow( { 'text': "This action will create a new 'grafted' tree.  Please give it a name and description" } ),
            modal.makeBasicTextInput( { text: 'Grafted Tree Name : ', name: 'treeName', value: 'Untitled Grafted Tree' } ),
            modal.makeBasicTextInput( { text: 'Description : ', name: 'treeDescription', value: '' } ) ) );
}

BioSync.TreeGrafter.RenderUtil.phylogram.navigate.prototype.askForReplaceCladeInfo = function( p ) {

    var modal = BioSync.ModalBox;

    var clipboardId = this.selectedClipboardItem.attr( 'clipboardId' );

    var successArray = new Array( $.proxy( this.treeEditSuccess, this ) );

    var content = this.make('div').append(
        modal.makeBasicTextRow( { text: 'Please provide a comment on your replace action.' } ),
        modal.makeBasicTextInput( { text: 'Comment : ', name: 'comment', value: '' } ),
        modal.makeHiddenInput( { name: 'replacedNodeId', value: this.replacedNodeId } ),
        modal.makeHiddenInput( { name: 'columnIndex', value: this.replacingColumn.index } ),
        modal.makeHiddenInput( { name: 'replacingNodeId', value: this.clipboardItems[ clipboardId ].id } ),
        modal.makeHiddenInput( { name: 'replacingNodeTreeType', value: this.clipboardItems[ clipboardId ].type } ),
        modal.makeBasicActionRow( {
             onClick:  $.proxy( this.showReplaceEditStatus, this ),
             onCancel: $.proxy( this.unHighlightClade, this ),
             submitText: 'Continue',
             submitArgs: { onSuccess: successArray,
                           submitUrl: BioSync.Common.makeUrl( { controller: 'plugin_treeGrafter', argList: [ 'replaceClade' ] } ) } } ) );

    if( this.viewer.treeType == 'source' ) {
        
        this.addNewGraftedTreeDialogueToContent( { content: content } );
    }

    BioSync.ModalBox.showModalBox( { content: content, title: 'Replace Clade' } );

}

BioSync.TreeGrafter.RenderUtil.phylogram.navigate.prototype.askForGraftCladeInfo = function( p ) {

    var modal = BioSync.ModalBox;

    var clipboardId = this.selectedClipboardItem.attr( 'clipboardId' );

    var successArray = new Array( $.proxy( this.treeEditSuccess, this ) );
    
    var content = this.make('div').append(
        modal.makeBasicTextRow( { text: 'Please provide a comment on your graft action.' } ),
        modal.makeBasicTextInput( { text: 'Comment : ', name: 'comment', value: '' } ),
        modal.makeHiddenInput( { name: 'graftingOntoNodeId', value: this.graftingOntoNodeId } ),
        modal.makeHiddenInput( { name: 'columnIndex', value: this.graftingColumn.index } ),
        modal.makeHiddenInput( { name: 'graftingNodeId', value: this.clipboardItems[ clipboardId ].id } ),
        modal.makeHiddenInput( { name: 'graftingNodeTreeType', value: this.clipboardItems[ clipboardId ].type } ),
        modal.makeBasicActionRow( {
             onClick:  $.proxy( this.showGraftEditStatus, this ),
             onCancel: $.proxy( this.unHighlightClade, this ),
             submitText: 'Continue',
             submitArgs: { onSuccess: successArray,
                           submitUrl: BioSync.Common.makeUrl( { controller: 'plugin_treeGrafter', argList: [ 'graftClade' ] } ) } } ) );

    if( this.viewer.treeType == 'source' ) {
        
        this.addNewGraftedTreeDialogueToContent( { content: content } );
    }

    BioSync.ModalBox.showModalBox( { content: content, title: 'Graft Clade' } );

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
        
        this.addNewGraftedTreeDialogueToContent( { content: content } );
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
