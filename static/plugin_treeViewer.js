BioSync.TreeViewer = { 

    instances: { },

    viewer: function() { return this; },

    Sidebar: {

        phylogram: {

            browse: function( viewer ) { this.viewer = viewer; this.make = BioSync.Common.makeEl; return this; },

            navigate: function( viewer ) {

                this.viewer = viewer;
                this.make = BioSync.Common.makeEl;
                return this;
            }
        }
    },

    ControlPanel: function( viewer ) {

        this.viewer = viewer;
        this.make = BioSync.Common.makeEl;
        return this;
    }
}

BioSync.TreeViewer.viewer.prototype = {

    start: function( p ) {

        this.containerId = p.containerId;
        this.treeType = p.treeType;
        this.menuInfo = p.menuInfo;

        this.events = ( 'eventInfo' in p ) ? p.eventInfo : { };
        
        this.renderType = ( p.viewInfo.renderType ) ? p.viewInfo.renderType : 'phylogram';
        this.viewMode = ( p.viewInfo && p.viewInfo.mode ) ? p.viewInfo.mode : 'browse';
        this.viewInfo = p.viewInfo;
        this.auxPlugins = p.auxPlugins;

        this.allNodesHaveLength = p.allNodesHaveLength;
        this.totalNodes = p.totalNodes;
        
        this.isPreProcessed = p.isTreePreprocessed;

        this.make = BioSync.Common.makeEl;

        this.isModal = ( p.modal == 'True' ) ? true : false;

        this.renderResponse = p.renderInfo;

        this.renderObj = this.getRenderObj();
        
        this.getConfig();

        this.container = $('#' + this.containerId).addClass('treeViewerContainer').height( '100%' ).width( '100%' );

        //not sure where this is getting triggered... but its preventing browser context menu
        $(document).bind( 'contextmenu', BioSync.Common.preventDefault );

        if( document.readyState === "complete" ) {

            this.onWindowLoad();

        } else {

            $(window).load( $.proxy( this.onWindowLoad, this ) );

        }

        return this;
    },

    addPanel: function( p ) {

        if( ! this.sidebar ) {

            BioSync.Common.loadScript( { name: [ this.renderType, 'Sidebar' ].join('') } );
           
            this.sidebar = new BioSync.TreeViewer.Sidebar[ this.renderType ][ this.viewMode ]( this ).initialize();
        }

        this.sidebar.addPanel( p );
    },
    
    togglePanel: function( e ) {

        var target = $( e.target );
        var label;

        if( target.hasClass('controlPanelItemLabel') ) { label = target; }
        else { label = $( target.children()[0] ); }

        var panelContainer = $( $( $( [ ".panelName:contains('", label.attr('name'), "')" ].join('') ).parent() ).parent() );

        if( $( label.parent() ).attr('check') == 'true' )  {

            this.showHeader( panelContainer );

        } else {
            
            panelContainer.hide( 'slide', { direction: 'right' }, 1000 );
        }
    },

    getRenderObj: function( p ) {

        // add error handler for this
        BioSync.Common.loadScript( { name: this.renderType } );

        return new BioSync.TreeViewer.RenderUtil[ this.renderType ][ this.viewMode ]().start( this );
    },

    updateConfig: function( p ) {

        for( var i = 0, ii = p.names.length; i < ii; i++ ) {

            this.config[ p.names[i] ] = p.values[i];
        }

        var onSuccessHandlers = new Array( $.proxy( this.handleConfigResponse, this ) )

        if( p.redraw ) { onSuccessHandlers.push( $.proxy( this.renderObj.redrawTree, this.renderObj ) ); }

        $.ajax( { url: BioSync.Common.makeUrl( { controller: 'plugin_treeViewer', argList: [ 'updateConfig' ] } ),
                  data: { names: p.names.join(','), vals: p.values.join(',') }, 
                  type: 'GET',
                  async: false,
                  success: onSuccessHandlers } );
    },

    getConfig: function() {

        $.ajax( { url: BioSync.Common.makeUrl( { controller: 'plugin_treeViewer', argList: [ 'getConfig' ] } ),
                 type: 'GET', async: false, context: this, success: this.handleConfigResponse } );
    },

    handleConfigResponse: function( response ) { this.config = eval( "(" + response + ")" ); },

    requestAuxilliaryPlugins: function( plugins ) {

        if( !plugins ) { return; }

        for( var i = 0, ii = plugins.length; i < ii; i++ ) {
        
            var plugin = plugins[ i ];
            var id = [ 'pluginContainer' + i ].join('');
        
            this.container.append( this.make('div').attr( { 'id': id  } ) );

            web2py_ajax_page(
                    'get',
                    BioSync.Common.makeUrl( { controller: 'plugin_' + plugin.name, argList: [ [ plugin.use, '.load' ].join('') ] } ),
                    { containerId: this.containerId },
                    id,
                    function() { } );
        }
    },

    assignWrapperHeight: function() {

       var footer = $('#footer');
       BioSync.Common.storeObjPosition( footer, footer );
      
       this.container.height( $(window).height() - ( footer.myHeight + footer.myOffset.top ) );
    },

    onWindowLoad: function() { 

        this.assignWrapperHeight();
     
        BioSync.Common.storeObjPosition( this.container, this );

        this.renderObj.initialize();

        if( this.isModal ) {

            this.container.appendTo( $('#modalBoxForm') );

            BioSync.ModalBox.showModalBox( { content: undefined, title: 'Your Tree', height: '75%' } );
        }

        if( this.renderResponse ) { this.renderObj.renderReceivedTree(); }

        else { this.getTree(); }

        if( this.menuInfo ) {

            BioSync.Common.loadScript( { name: [ 'controlPanel' ].join('') } );
            this.controlPanel = new BioSync.TreeViewer.ControlPanel( this ).initialize( this.menuInfo );
        }

        this.requestAuxilliaryPlugins( this.auxPlugins );
    },

    getTree: function() {

        this.renderObj.getTree();
       
        //still need to deal with this 
        //if( this.sidebar ) { this.sidebar.updateHeaderCoords(); }
    },

    isAncestor: function( p ) {
                    
        return ( ( p.ancestor.next < p.descendant.next ) &&
                 ( p.ancestor.back > p.descendant.back ) ) ? true : false;
    },

    saveColorConfig: function( p ) {
                                           
        var viewer = p.data.viewer;

        var option = $('#colorOptions option:selected').val()
        var value = $('#configCurrentColor').text();

        viewer.config.colorOptions[ option ].value = value;
        viewer.config.colorOptions[ option ].update( { viewer: viewer, value: value } );
    },

    getConfigColorDropdownOptions: function( p ) {

        var viewer = this;
        var elList = [];
        var colorOptions = viewer.config.colorOptions;
        var make = BioSync.Common.makeEl;

        for( var value in colorOptions ) {
            elList.push( make('option').attr( { 'value': value } ).text( colorOptions[value].text ).get(0) );
        }

        return elList;
    },

    handleUserSearch: function( p ) {

        var viewer = p.data.viewer;
        
        var listItems = $('#modalBoxForm').find('.userItem')
        
        if( p.keyCode == 8 || p.keyCode == 46 || String.fromCharCode( p.keyCode ).match( /\w/ ) ) {

            listItems.show();

            var regExp = new RegExp( $('#userSearch').val(), 'gi' );

            for( var i = 0, ii = listItems.length; i < ii; i++ ) {

                var listItem = $( listItems[ i ] );

                if( ! listItem.text().match( regExp ) ) {

                    listItem.hide();
                }
                
            }
        }
    },

    removeUserSearchDefaultText: function( p ) {

        $('#userSearch').select().unbind('focus');

    },

    showModalCollaborationOptions: function( p ) {

        var viewer = p.data.viewer;

        var make = BioSync.Common.makeEl;

        $.ajax( { url: BioSync.Common.makeUrl( { controller: 'plugin_treeGrafter', argList: [ 'getCurrentCollaborators', viewer.treeId ] } ),
                          type: "GET",
                          async: false,
                          context: viewer,
                          success: function( response ) { viewer.collabInfo = eval( "(" + response + ")" ); } } );

        var bodyHeight = $('body').height();
        var bodyWidth = $('body').width();
         
        $('#modalBoxForm').append(
            make('div').append(
                BioSync.ModalBox.makeBasicTextRow( { 'text': 'You are the owner of this grafted tree.  Here, you can specify who has the ability to edit this tree.  Click and drag a name to update their permissions.' } ),
                make('div').attr( { 'class': 'autoMargin' } ).width( bodyWidth / 3 ).append(
                    make('div').attr( { 'class': 'fLeft' } ).append(
                        make('div').text('View Only').attr( { 'class': 'centerText bold' } ).css( { 'padding': '5px' } ),
                            make('div').attr( { 'id': 'viewOnlyContainer', 'class': 'userListContainer' } ).height( bodyHeight / 4 ) ),
                    make('div').attr( { 'class': 'fRight' } ).append(
                        make('div').text('View/Edit').attr( { 'class': 'centerText bold' } ).css( { 'padding': '5px' } ),
                            make('div').attr( { 'id': 'viewEditContainer', 'class': 'userListContainer' } ).height( bodyHeight / 4 ) ),
                    make('div').attr( { 'class': 'clear' } ) ),
                make('div').attr( { 'class': 'padding10 autoMargin' } ).width( bodyWidth / 8 ).append(
                        make('input').attr( { 'id': 'userSearch', 'class': 'centerText autoMargin', 'value': 'search for a user here' } ).width( bodyWidth / 8 )
                                     .bind( 'focus', { viewer: viewer }, viewer.removeUserSearchDefaultText )
                                     .bind( 'keyup', { viewer: viewer }, viewer.handleUserSearch ) ) ) );


        

        for( var attr in viewer.collabInfo ) {

            var container = $( [ '#', attr, 'Container' ].join('') );
            var otherContainer = ( attr == 'viewOnly' ) ? $('#viewEditContainer') : $('#viewOnlyContainer' );

            for( var i = 0, ii = viewer.collabInfo[ attr ].length; i < ii; i++ ) {

                var user = viewer.collabInfo[ attr ][ i ];
                var domObj = make('div').attr( { 'userId': user.id, 'class': 'dashedBorderBottom nowrap userItem' } )
                                        .text( user.name )
                                        .css( { 'padding': '10px 10px 10px 10px' } )
                                        .draggable( { receptacle: otherContainer, receptacleFun: viewer.updatePermissions, receptacleFunParams: { userId: user.id, viewer: viewer }  } );

                container.append( domObj );
            }
        }
      
        BioSync.ModalBox.showModalBox( { content: undefined, title: 'Manage Collaboration' } );

        setTimeout(
            function() {
                if( $('#viewEditContainer').width() > $('#viewOnlyContainer').width() ) {
                    $('#viewOnlyContainer').width( $('#viewEditContainer').width() );
                    $('#viewEditContainer').width( $('#viewEditContainer').width() );
                } else {
                    $('#viewEditContainer').width( $('#viewOnlyContainer').width() );
                    $('#viewOnlyContainer').width( $('#viewOnlyContainer').width() );
                }

                /*BioSync.Common.addHoverCloseIcon( {
                    whiteBackground: true,
                    topRight: true,
                    el: $('#modalBoxForm'),
                    func: function() { BioSync.ModalBox.closeBox(); } } );*/

            }, 2000 );
    },

    updatePermissions: function( p ) {

        var viewer = p.viewer;

        $.ajax( { url: BioSync.Common.makeUrl( { controller: 'plugin_collaboration', argList: [ 'updateCollaboration' ] } ),
                  type: "GET",
                   context: viewer,
                   data: { treeId: viewer.treeId, userId: p.userId },
                   success: function() {
        
                       var selector = [ '.userItem[userId="', p.userId, '"]' ].join('');

                       if( $('#viewEditContainer').find( selector )[0] ) {

                            $( selector ).appendTo( $('#viewOnlyContainer' ) ).show('slow')
                                         .draggable( { receptacle: $('#viewEditContainer'),
                                                       receptacleFun: viewer.updatePermissions,
                                                       receptacleFunParams: { userId: p.userId, viewer: viewer }  } );

                        } else {
                            
                            $( selector ).appendTo( $('#viewEditContainer' ) ).show('slow')
                                         .draggable( { receptacle: $('#viewOnlyContainer'),
                                                       receptacleFun: viewer.updatePermissions,
                                                       receptacleFunParams: { userId: p.userId, viewer: viewer }  } );
                        } } } );
    },

    
};




/*
    collaborateMakeOption: function( p ) {

        var viewer = p.viewer;

        if( viewer.treeType == 'grafted' ) {

            $.ajax( { url: BioSync.Common.makeUrl( { controller: 'plugin_treeGrafter', argList: [ 'isTreeOwner', viewer.treeId ] } ),
                      type: "GET",
                      async: false,
                      context: viewer,
                      data: { },
                      success: function( response ) { viewer.isOwner = eval( "(" + response + ")" ); } } );

            if( viewer.isOwner ) {

                return { text: 'Manage Collaborators', funcParams: { viewer: viewer }, func: new Array( viewer.showModalCollaborationOptions, viewer.menuUtil.hideConfigMenu ) };

            } else {

                return { };
            }

        } else { return { }; }
    },
*/
