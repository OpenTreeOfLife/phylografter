BioSync.Clipboard = {

    instances: { }

}

BioSync.Clipboard.clipboard = function( containerId ) { 

    BioSync.Clipboard.instances[ containerId ] = this;

    this.containerId = containerId;

    this.make = BioSync.Common.makeEl;
}

BioSync.Clipboard.clipboard.prototype = {

    default: function( p ) {
        
        this.container =  $('#' + this.containerId).mousedown( BioSync.Common.returnFalse ).addClass('clipboardContainer');
        
        var make = BioSync.Common.makeEl;

        this.dragImage =
            make('img').attr( { 'class': 'clipboardGraftIcon',
                                'src': '/' + BioSync.Common.applicationName + '/static/images/tree.png' } ).appendTo( $('body') ).hide();

        if( p.clipboard.length == 0 ) {

            this.container.append( make('div').attr( { 'class': 'clipboardNoItems' } ).text('No Items on Clipboard') );
        }

        this.items = { };

        for( var i = 0, ii = p.clipboard.length; i < ii; i++ ) {
            this.items[ p.clipboard[i].id ] = this.addItem( { item: p.clipboard[i], index: i } );
        }

        setTimeout( this.checkForScrollbar, 1000, { clipboard: this } );
    },

    viewAndGraft: function( p ) {

        this.dragImage =
            this.make('img').attr( { 'class': 'clipboardGraftIcon',
                                     'src': '/' + BioSync.Common.applicationName + '/static/images/tree.png' } ).appendTo( $('body') ).hide();

        //don't like this line 
        this.viewer = BioSync.TreeGrafter.instances[ this.containerId ];

        this.content = this.make( 'div' ).attr( { 'class': 'clipboardContent' } )
            .mousedown( BioSync.Common.returnFalse );

        this.items = { };

        for( var i = 0, ii = p.clipboard.length; i < ii; i++ ) {
            this.items[ p.clipboard[i].id ] = this.addItem( { item: p.clipboard[i], index: i } );
        }

        this.viewer.addPanel( { content: this.content, name: 'Clipboard', id: 'clipboard' } );

        $( $('.clipboardItem').filter(':last') ).addClass('lastClipboardItem');

        $(document).bind( 'movingClipboardItem', { }, $.proxy( this.checkMovingClipboardItem, this ) );
        $(document).bind( 'clipboardItemDrop', { }, $.proxy( this.clipboardItemDrop, this ) );
    },

    checkMovingClipboardItem: function( p, e ) {

        if( BioSync.Common.isMouseOnElement( { el: this.viewer.container, x: e.x, y: e.y } ) ) {

            this.viewer.movingClipboardItem = true;
            this.viewer.renderObj.handleMovingClipboardItem( e );
        }
    },

    clipboardItemDrop: function( e, p ) {
        
        if( BioSync.Common.isMouseOnElement( { el: this.viewer.container, x: e.x, y: e.y } ) ) {
            
            this.viewer.renderObj.handleClipboardDrop( e, p );
        }

        this.viewer.movingClipboardItem = false;
    },

    addToClipboard: function() {

        var treeViewer = BioSync.TreeViewer.instances[ this.containerId ];

        treeViewer.externalHandlers.addToClipboard = function( p ) {

            var content =
                BioSync.Common.makeEl('div').append(
                    BioSync.ModalBox.makeBasicTextInput( { name: 'name', text: 'Name : ', value: 'Untitled Clipboard Item' } ),
                    BioSync.ModalBox.makeHiddenInput( { name: 'nodeId', value: p.data.nodeId } ),
                    BioSync.ModalBox.makeHiddenInput( { name: 'treeType', value: treeViewer.treeType } ),
                    BioSync.ModalBox.makeBasicActionRow( {
                        submitText: 'Submit',
                        submitArgs: { trigger: 'clipboardItemAdded',
                                      onSuccess: function() { BioSync.Common.notify( { text: 'Node has been added to the clipboard.',
                                                                                       x: treeViewer.myOffset.left + ( treeViewer.myWidth / 2 ),
                                                                                       y: treeViewer.myOffset.top + 10 } ); },
                                      submitUrl: BioSync.Common.makeUrl( { controller: 'plugin_clipboard', argList: ['addItem'] } ) } } ) );

            BioSync.ModalBox.showModalBox( { content: content, title: 'Give this clipboard item a name' } );
        }

        var events = treeViewer.events;
        var event = ( events.nodeRightClick && ( events.nodeRightClick.type.indexOf('Menu') > -1 ) )
            ? events.nodeRightClick : ( events.nodeDoubleClick && ( events.nodeDoubleClick.type.indexOf('Menu') > -1 ) )
                ? events.nodeDoubleClick : undefined;

        if( event ) {

            event.options.push( { text: 'Add To Clipboard', handler: 'addToClipboard', external: true } );

        }
    },

    makeItem: function( p ) {
    
        var make = BioSync.Common.makeEl;

        var myClass = 'clipboardItem ' + ( ( p.index % 2 == 0 ) ? 'odd' : 'even' );

        var nodeTable = ( p.item.clipboard.treeType == 'source' ) ? 'snode' : 'gnode';

        var rv =
            make('div').attr( { 'class': myClass, nodeId: p.item.clipboard.nodeId } ).append(
               make('div').attr( { 'class': 'clipboardItemInfo' } ).append(
                   make('div').attr( { 'class': 'clipboardName' } ).text( p.item.clipboard.name ),
                   make('div').attr( { 'class': '' } ).append(
                       make('div').attr( { 'class': 'clipboardDate' } ).text( p.item.clipboard.creationDate.slice( 0, p.item.clipboard.creationDate.indexOf(' ' ) ) ),
                       make('div').attr( { 'class': 'clipboardDetail' } ).text( 'view detail' ).bind( 'click', { }, $.proxy( this.showDetail, this ) ),
                       make('div').attr( { 'class': 'clear' } ) ) ),
               make('div').attr( { 'class': 'clipboardDelete', clipboardId: p.item.clipboard.id } ).text('x')
                   .bind( 'mousedown', function( e ) { BioSync.Common.symbolDragInfo = undefined; e.stopPropagation(); } )
                   .bind( 'click', $.proxy( this.deleteItem, this ) ),
               make('div').attr( { 'class': 'clear' } ) ).hoverIntent( function() { $( this ).children('.clipboardDelete').css( { 'display': 'inline' } ); },
                                                                     function() { $( this ).children('.clipboardDelete').css( { 'display': 'none' } ) } );


       var detailContainer = make('div').attr( { 'class': 'detailContainer' } ).append(
               make('div').attr( { 'class': 'detailItem' } ).append(
                   make('div').attr( { 'class': 'detailLabel' } ).text( 'Node Count : ' ),
                   make('div').attr( { 'class': 'detailValue' } ).text( Math.floor( ( p.item[ nodeTable ].back - p.item[ nodeTable ].next ) / 2 ) ),
                   make('div').attr( { 'class': 'clear' } ) ),
               make('div').attr( { 'class': 'detailItem' } ).append(
                   make('div').attr( { 'class': 'detailLabel' } ).text( 'Tree Type : ' ),
                   make('div').attr( { 'class': 'detailValue' } ).text( p.item.clipboard.treeType ),
                   make('div').attr( { 'class': 'clear' } ) ) ).hide();
    
        if( nodeTable == 'snode' ) {
            
            detailContainer.append(
                make('div').attr( { 'class': 'detailItem citationDetail', 'title': p.item.study.citation } ).append(
                   make('div').attr( { 'class': 'detailLabel' } ).text( 'Citation : ' ),
                   make('div').attr( { 'class': 'detailValue' } ).text( [ p.item.study.citation.substring(0,20), '...' ].join('') ),
                   make('div').attr( { 'class': 'clear' } ) ) );
        }

        rv.append( detailContainer );

        return rv;
    },

    addItem: function( p ) {

        this.removeNoItemsText();

        var domItem = this.makeItem( { item: p.item, index: p.index } );

        BioSync.Common.applySymbolDrag(
            { el: domItem, img: this.dragImage, moveFunc: 'movingClipboardItem', dropFunc: 'clipboardItemDrop', dropParams: { clipboardId: p.item.clipboard.id } } );
 
        if( p.async ) {
            domItem.hide();
            this.content.append( domItem );
            domItem.show('slow');
        } else { 
            this.content.append( domItem );
        }

        return domItem;
    },

    deleteItem: function( e ) {

        var clipboardId = $( e.target ).attr('clipboardId');

        $.ajax( { url: BioSync.Common.makeUrl( { controller: 'plugin_clipboard', argList: [ 'delete', clipboardId ] } ),
              type: "GET",
              context: this,
              success: this.removeItem } );

    },

    removeItem: function( id ) {
        var clipboard = this;
        clipboard.items[ id ].hide( 'slide', { direction: 'right' }, 1000, function() {
            $(this).empty().remove();
            delete clipboard.items[ id ];
            this.viewer.
            clipboard.checkForNoScroll(); } );
    },

    checkForNoScroll: function( p ) {

        var lastItem = $( $('.clipboardItem').filter(':last') );
        var lastItemOffset = lastItem.position();


        if( this.content.css('height') && ( ( lastItemOffset.top + lastItem.outerHeight( true ) ) < ( this.content.position().top + parseFloat( this.content.css('height') ) ) ) ) {
            this.content.animate( { 'height': '' }, 1000 );
        }

        return;

        var clipboard = this;
        
        for( var nodeId in clipboard.items ) {
            var itemWidth = clipboard.items[ nodeId ].outerWidth( true );
            break;
        }

        if( ( itemWidth == clipboard.content.width() ) &&
              clipboard.hasScrollbar ) {
            
            clipboard.hasScrollbar = false;
        }
    },

    checkForScrollbar: function( p ) {

        var clipboard = p.clipboard;

        var itemWidth;

        for( var nodeId in clipboard.items ) {
            itemWidth = clipboard.items[ nodeId ].outerWidth( true );
            break;
        }


        if( itemWidth < clipboard.content.width() ) {
            clipboard.hasScrollbar = true;
        }
    },

    removeNoItemsText: function( p ) {

        var noItemsText = $('.clipboardNoItems');

        if( noItemsText.length ) { noItemsText.empty().remove(); }
    },

    showDetail: function( e ) {

        var button = $( e.target );

        var clipboardItem = $( button.closest( '.clipboardItem' ) );

        var detailContainer = $( clipboardItem.find('.detailContainer') );
        
        detailContainer.show( 'slide', { direction: 'right' }, 1000 );

        button.text('hide detail').unbind('click').bind('click', { }, $.proxy( this.hideDetail, this ) );
    },

    hideDetail: function( e ) {

        var button = $( e.target );

        var clipboardItem = $( button.closest( '.clipboardItem' ) );

        var detailContainer = $( clipboardItem.find('.detailContainer') );
        
        detailContainer.hide( 'slide', { direction: 'right' }, 1000 );

        button.text('show detail').unbind('click').bind('click', { }, $.proxy( this.showDetail, this ) );
    }
};

