BioSync.Collaboration = {

    instances: { }

};

BioSync.Collaboration.collaboration = function( p ) {

    this.container = $('#' + p.containerId);

    this.idCommentMapping = { };
    
    var make = BioSync.Common.makeEl;

    var bodyWidth = $('body').width();
    var bodyHeight = $('body').height();

    this.container.append( make('div').attr( { 'class': 'pageHeader centerText' } ).text('Here you will find a list of the trees that you own.  To allow others to edit one of your trees, please drag and drop their names into the edit box with the appropriate tree selected.') );

    var userTreeContainer = make('div').attr( { 'class': 'userTreeContainer nowrap' } ).appendTo( this.container );

    var contentContainer = make('div').attr( { 'class': 'autoMargin' } ).width( bodyWidth / 4 ).appendTo( userTreeContainer );
    var treeNameContainer = make('div').attr( { 'class': 'fLeft' } ).appendTo( contentContainer );
    var userTreeHeader = make('div').attr( { 'class': 'centerText bold userTreeHeader' } ).text('Trees You Own').appendTo( treeNameContainer );
    var userTreeList = make('div').attr( { 'class': 'scrollable treeList' } ).height( bodyHeight / 8 ).appendTo( treeNameContainer );

    for( var i = 0, ii = p.userTrees.length; i < ii; i++ ) {

        var info = p.userTrees[i];

        userTreeList.append( make('div').attr( { 'treeId': info.id, 'class': 'treeItem' } ).text( info.title ).bind( 'click', { collabModule: this }, this.updateTreeSelection ) );

        this.idCommentMapping[ info.id ] = info.comment;
    }

    var commentField = make('div').attr( { 'class': 'fRight' } ).append(
        make('span').attr( { 'class': 'commentLabel bold' } ).text( 'Comment : ' ),
        make('span').attr( { 'id': 'commentValue' } ) ).appendTo( contentContainer );


    contentContainer.append( make('div').attr( { 'class': 'clear' } ) );

    userTreeList.width( userTreeList.outerWidth( true ) + BioSync.Common.scrollbarWidth )

    var userInfoContainer = make('div').attr( { 'class': 'userInfoContainer' } ).append(
        make('div').attr( { 'class': 'autoMargin' } ).width( bodyWidth / 4 ).append(
            make('div').attr( { 'class': 'fLeft' } ).append(
                make('div').text('View Only').attr( { 'class': 'centerText bold' } ).css( { 'padding': '5px' } ),
                    make('div').attr( { 'id': 'viewOnlyContainer', 'class': 'userListContainer' } ).height( bodyHeight / 4 ) ),
            make('div').attr( { 'class': 'fRight' } ).append(
                make('div').text('View/Edit').attr( { 'class': 'centerText bold' } ).css( { 'padding': '5px' } ),
                    make('div').attr( { 'id': 'viewEditContainer', 'class': 'userListContainer' } ).height( bodyHeight / 4 ) ),
            make('div').attr( { 'class': 'clear' } ) ),
        make('div').attr( { 'class': 'padding10 autoMargin' } ).width( bodyWidth / 8 ).append(
                make('input').attr( { 'id': 'userSearch', 'class': 'centerText autoMargin', 'value': 'search for a user here' } ).width( bodyWidth / 8 )
                             .bind( 'focus', { collabModule: this }, this.removeUserSearchDefaultText )
                             .bind( 'mouseup', { collabModule: this }, function(e) { e.preventDefault(); } )
                             .bind( 'keyup', { collabModule: this }, this.handleUserSearch ) ) );

    this.container.append( userInfoContainer );
    
    $( userTreeList.children()[0] ).click();
}

BioSync.Collaboration.collaboration.prototype = {

    removeUserSearchDefaultText: function() { $('#userSearch').select(); }, //.unbind('focus'); },
    
    handleUserSearch: function( p ) {

        var collabModule = p.data.collabModule;
        
        var listItems = collabModule.container.find('.userItem')
        
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

    updateTreeSelection: function( p ) {

        var collabModule = p.data.collabModule;
        var clickedDiv = $(this);

        collabModule.container.find('.selected').removeClass('selected');

        clickedDiv.addClass('selected');

        var text = ( collabModule.idCommentMapping[ clickedDiv.attr('treeId') ] )
            ? collabModule.idCommentMapping[ clickedDiv.attr('treeId') ]
            : 'No comment provided';

        $('#commentValue').text( text );

        $.ajax( { url: BioSync.Common.makeUrl( { controller: 'plugin_treeGrafter', argList: [ 'getCurrentCollaborators', clickedDiv.attr('treeId') ] } ),
                  type: "GET",
                  async: false,
                  context: collabModule,
                  success: collabModule.updateUserLists } );
    },

    updateUserLists: function( response ) {

        var response = eval( "(" + response + ")" );
        var collabModule = this;

        for( var attr in response ) {

            var container = $( [ '#', attr, 'Container' ].join('') );
            var otherContainer = ( attr == 'viewOnly' ) ? $('#viewEditContainer') : $('#viewOnlyContainer' );

            for( var i = 0, ii = response[ attr ].length; i < ii; i++ ) {

                var user = response[ attr ][ i ];

                var domObj = BioSync.Common.makeEl('div').attr( { 'userId': user.id, 'class': 'dashedBorderBottom nowrap userItem' } )
                                        .text( user.name )
                                        .css( { 'padding': '10px 10px 10px 10px' } )
                                        .draggable( { receptacle: otherContainer, receptacleFun: collabModule.updatePermissions, receptacleFunParams: { userId: user.id, collabModule: collabModule }  } )
                                        .appendTo( container ); 
            }
        }

        setTimeout(
            function() {
                if( $('#viewEditContainer').width() > $('#viewOnlyContainer').width() ) {
                    $('#viewOnlyContainer').width( $('#viewEditContainer').width() );
                    $('#viewEditContainer').width( $('#viewEditContainer').width() );
                } else {
                    $('#viewEditContainer').width( $('#viewOnlyContainer').width() );
                    $('#viewOnlyContainer').width( $('#viewOnlyContainer').width() );
                }
            }, 2000 );
    },

    updatePermissions: function( p ) {

        var collabModule = p.collabModule;

        var treeId = collabModule.container.find('.selected').attr('treeId');

        $.ajax( { url: BioSync.Common.makeUrl( { controller: 'plugin_treeViewer', argList: [ 'updateCollaboration' ] } ),
                  type: "GET",
                   context: collabModule,
                   data: { treeId: treeId, userId: p.userId },
                   success: function() {
        
                       var selector = [ '.userItem[userId="', p.userId, '"]' ].join('');

                       if( $('#viewEditContainer').find( selector )[0] ) {

                            $( selector ).appendTo( $('#viewOnlyContainer' ) ).show('slow')
                                         .draggable( { receptacle: $('#viewEditContainer'),
                                                       receptacleFun: collabModule.updatePermissions,
                                                       receptacleFunParams: { userId: p.userId, collabModule: collabModule }  } );

                        } else {
                            
                            $( selector ).appendTo( $('#viewEditContainer' ) ).show('slow')
                                         .draggable( { receptacle: $('#viewOnlyContainer'),
                                                       receptacleFun: collabModule.updatePermissions,
                                                       receptacleFunParams: { userId: p.userId, collabModule: collabModule }  } );
                        } } } );
    }
}
