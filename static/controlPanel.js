/*
    This page contains javascript code for the control panel object in Phylografter's tree viewer.  Currently, 2013/01/15, the object is created in static/plugin_treeViewer.js, on line 194 : 
        BioSync.Common.loadScript( { name: [ 'controlPanel' ].join('') } );
        this.controlPanel = new BioSync.TreeViewer.ControlPanel( this ).initialize( this.menuInfo );

    The first line of code is an ajax call that loads this very file into the client's javascript parser and is evaluated.  The second line of code instantiates a ControlPanel object and stores it in the 'controlPanel' attribute of the tree viewer.
*/


//This is the control panel constructor.  The tree viewer javascript object gets passed in so it can be referenced later.  The make function allows the control panel to make DOM elements with less code.

BioSync.TreeViewer.ControlPanel = function( viewer ) {

    this.viewer = viewer;
    this.make = BioSync.Common.makeEl;
    return this;
}

    
//The prototype contains attributes and functions available to an object.  Below, we define the attributes and functions our Control Panel object will have.

BioSync.TreeViewer.ControlPanel.prototype = {

    //each option in the control panel is itself another object.  Here, we define the constructors for the control panel menu items.
    options: {

        search: function( controlPanel ) {

            this.controlPanel = controlPanel;
            this.make = controlPanel.make;
            return this;
        },

        branchLength: function( controlPanel ) {

            this.controlPanel = controlPanel;
            this.make = controlPanel.make;
            return this;
        },

        treeSize: function( controlPanel ) {

            this.controlPanel = controlPanel;
            this.make = controlPanel.make;
            return this;
        },

        graftOption: function( controlPanel ) {

            this.controlPanel = controlPanel;
            this.make = controlPanel.make;
            return this;
        }
    },


    //configuration settings.  Most of these could be set using classes and .css files, but I do it here so its all in one place when I'm absolutely positioning elements and have to take into account their padding and margins.  Its foolish to have to update the values in both the .css and javascript files.  These could probably be better named, apoologies.

    config: { leftBuffer: 10,
              rightBuffer: 20,
              bottomBuffer: 10,
              optionContainerLeftBuffer: 20,
              optionContainerMargin: 2,
              panelButtonPadding: 5,
              labelBorderRadius: '5px',
              zIndex: 5001,
              matchingLabelListZIndex: 5002,
              sliderSize: 100 },


    //removes the control panel button from the DOM.  This is used when the control panel needs to be refreshed in order to account for new options that may be available after user interaction.
    remove: function() {

        this.panelButton.remove();
    },

    
    // this is called right after the constructor.  It initializes the control panel, creating the hover option in the corner of the tree viewer, then calling a function to create the menu options
    initialize: function( controlPanelInfo ) {

         this.panelButton =
            this.make('div')
                .css( { 'position': 'absolute',
                        'left': 0,
                        'top': 0,
                        'padding': this.config.panelButtonPadding,
                        'border-right': '1px solid black',
                        'border-bottom': '1px solid black',
                        '-moz-border-bottom-right-radius': '10px',
                        'border-bottom-right-radius': '10px',
                        'z-index': this.config.zIndex,
                        'background-color': 'white',
                        'white-space': 'nowrap',
                        'opacity': 1 } )
                .hoverIntent( $.proxy( this.showControlPanel, this ), $.proxy( this.hideControlPanel, this ) )
                .appendTo( this.viewer.container );

        this.panelButtonLabel =
            this.make( 'div' )
                .text( 'control panel' )
                .hover( BioSync.Common.setMouseToPointer, BioSync.Common.setMouseToDefault )
                .appendTo( this.panelButton );

        this.createMenuOptions( { options: controlPanelInfo.options } );

        return this;
    },

    
    // when the control panel is hovered with a mouse, this function is called, it displays the menu options
    showControlPanel: function() {

        this.panelButtonLabel.css( { 'font-weight': 'bold' } );

        this.optionContainer.show();
    },
   
    // when the mouse leaves the control panel, this function is called, it hides the menu options
    hideControlPanel: function( ) {

        this.panelButtonLabel.css( { 'font-weight': 'normal' } );

        this.optionContainer.hide();
    },

    // this function is used by outside functions to update the control panel.  for example, when a collapsed clade is vertically expanded, this changes the number of max tips in a column.  this means the max tips ui in the control panel must also be changed.  This is where it happens -- it calls the menu option's function to complete the task.
    updateMaxTips: function() {

        if( this.optionObjs.treeSize ) {

            this.optionObjs.treeSize.updateMaxTips();
        }
    },


    // this function iterates through each menu item and creates it.  Also, if an option exists over multiple lines, it makes sure that it is positioned to the right enough, so that it doesn't obscure the vision of other menu items.
    createMenuOptions: function( p ) {
                
        this.optionObjs = { };
        
        this.optionContainer =
            this.make('div')
                .css( { 'padding-left': this.config.optionContainerLeftBuffer,
                        'padding-top': 10,
                        'margin': this.config.optionContainerMargin } )
                .appendTo( this.panelButton )

        for( var i = 0, ii = p.options.length; i < ii; i++ ) {

            this.optionObjs[ p.options[i].name ] = new this.options[ p.options[i].name ]( this ).initialize();
        }

        for( var i = 0, ii = p.options.length; i < ii; i++ ) {

            if( this.optionObjs[ p.options[i].name ].multiLineOptionContainer ) {

                this.optionObjs[ p.options[i].name ].multiLineOptionContainer.css( { 'left': this.rightMostContainer } );
            }
        }

        this.optionContainer.hide();
    },

    // when a menu item is created, it calls this function in order to make the container and label, the control panel keeps track of which menu item is the widest, or "rightMost", so that it is easier to position elements
    makeOptionContainer: function( p ) {

        var container =
            this.make('div')
                .css( { 'position': 'relative', 'padding': '5px' } )
                .hoverIntent( $.proxy( p.obj.handleMouseOverContainer, p.obj ), $.proxy( p.obj.handleMouseOutOfContainer, p.obj ) )
                .appendTo( this.optionContainer );

        var label =
            this.make( 'span' )
                .text( p.label )
                .css( { 'padding': '5px',
                        '-moz-border-radius': this.config.labelBorderRadius,
                        'border-radius': this.config.labelBorderRadius } )
                .hover( BioSync.Common.setMouseToPointer, BioSync.Common.setMouseToDefault )
                .appendTo( container );

        if( ! this.rightMostContainer ) { this.rightMostContainer = 0; }

        var containerWidth = container.outerWidth( true );

        if( ( containerWidth ) > this.rightMostContainer ) { this.rightMostContainer = containerWidth; }

        return [ container, label ];
    },

    // when a menu item is hovered upon by a mouse, its own menu is displayed on the screen.  This function checks that the height of the control panel is enough to cover the newly expanded menu item.
    checkOptionContainerHeight: function( p ) { 
        
        var optionContainerOffset = this.optionContainer.offset();
        var subOptionContainerOffset = p.subOptionContainer.offset();

        var difference =
            ( subOptionContainerOffset.top + p.subOptionContainer.outerHeight( true ) ) -
            ( optionContainerOffset.top + this.optionContainer.outerHeight( true ) );

        if( difference > 0 ) {
        
            this.optionContainer.height(
                this.optionContainer.height() +
                difference );
        }
    }
}


//Here is the object definition of the graft option menu item.  It has two sub menu items : 'View Tree Edits' and 'Let Colleagues Edit Tree'.
BioSync.TreeViewer.ControlPanel.prototype.options.graftOption.prototype = {

    config: {

        padding: 5    
    },

    // This is called when creating the object.  The menu is only shown when the tree viewer is showing a grafted tree.  Anyone can view the tree edits.  Only the person who created the tree gives edit privileges to others.
    initialize: function() {

        if( this.controlPanel.viewer.treeType == 'grafted' ) {

            var rv =
                this.controlPanel.makeOptionContainer( {
                    obj: this,
                    label: 'graft options > ' } );
       
            this.container = rv[0];
            this.label = rv[1];

            this.graftAudit =
                this.make('span').text( 'View Tree Edits' )
                                 .hover( BioSync.Common.setMouseToPointer, BioSync.Common.setMouseToDefault )
                                 .hover( BioSync.Common.underlineText, BioSync.Common.removeTextUnderline )
                                 .bind( 'click', { }, $.proxy( this.handleViewTreeEditClick, this ) );

            if( ( this.controlPanel.viewer.isLoggedIn ) &&
                ( this.controlPanel.viewer.treeCreator == [ this.controlPanel.viewer.userInfo.firstName,
                                                            this.controlPanel.viewer.userInfo.lastName ].join(' ') ) ) {
            
                this.shareTree =
                    this.make('span').html( 'Let Colleagues Edit Tree' )
                                     .hover( BioSync.Common.setMouseToPointer, BioSync.Common.setMouseToDefault )
                                     .hover( BioSync.Common.underlineText, BioSync.Common.removeTextUnderline )
                                     .bind( 'click', { }, $.proxy( this.handleShareTreeClick, this ) );
            }

            this.selectionContainer =
                this.make('div').css( { 'padding': [ '0px ', this.config.padding, 'px' ].join(''),
                                        'position': 'absolute',
                                        'top': 0,
                                        'left': this.label.outerWidth( true ) } ).append(
                    this.make('div').css( { 'padding': this.config.padding } ).append( this.graftAudit ),
                    this.make('div').css( { 'padding': this.config.padding } ).append( this.shareTree ) )
                .hoverIntent( function() { }, $.proxy( this.handleMouseOutOfSelectionContainer, this ) )
                .appendTo( this.container )
                .hide();

            this.multiLineOptionContainer = this.selectionContainer;
        }

        return this;
    },

    // when a user clicks on the 'View Tree Edits' button, this function is called.  It makes a call to /plugin_treeGrafter/getGtreeGraftHistory in order to retrieve the edits made regarding this tree from the server
    handleViewTreeEditClick: function( e ) {

        this.selectionContainer.hide();

        $.ajax( { url: BioSync.Common.makeUrl( { controller: 'plugin_treeGrafter', argList: [ 'getGtreeGraftHistory' ] } ),
                  type: "GET",
                  success: $.proxy( this.showModalTreeEdits, this ) } );
    },

   
    // this function handles the response from 'handleViewTreeEditClick' above.  The response is evaluated, then a bunch of DOM elements are created and displayed in a modal dialogue box.  This isn't the best written code (should be more modular) as it was recently written to get it done fast.
    showModalTreeEdits: function( response ) {

        var data = eval( '(' + response + ')' );

        this.treeEditContainer =
            this.make('div').append(
                this.make('div').css( { 'padding-bottom': '20px' } ).append(
                    this.make('div')
                      .text( 'Edit Type' )
                      .width( '10%' )
                      .css( { 'float': 'left',
                              'text-align': 'center',
                              'font-weight': 'bold',
                              'font-size': '16px' } ),
                    this.make('div')
                      .text( 'Comment' )
                      .width( '50%' )
                      .css( { 'float': 'left',
                              'text-align': 'center',
                              'font-weight': 'bold',
                              'font-size': '16px' } ),
                    this.make('div')
                      .text( 'User' )
                      .width( '15%' )
                      .css( { 'float': 'left',
                              'text-align': 'center',
                              'font-weight': 'bold',
                              'font-size': '16px' } ),
                    this.make('div')
                      .text( 'Date' )
                      .width( '15%' )
                      .css( { 'float': 'left',
                              'text-align': 'center',
                              'font-weight': 'bold',
                              'font-size': '16px' } ),
                    this.make('div')
                      .width( '10%' )
                      .css( { 'clear': 'both' } ) ) );

        for( var i = 0, ii = data.length; i < ii; i++ ) {

            var dataRow = this.make( 'div' ).attr( { 'class': 'dataRow' } ).css( { 'padding': '5px' } ).append(
                    this.make('div')
                      .css( { 'float': 'left',
                              'text-align': 'center' } )
                      .width( '10%' )
                      .text( BioSync.Common.capitalizeFirstLetter( data[i].gtree_edit.action ) ),
                    this.make('div')
                      .css( { 'float': 'left',
                              //'white-space': 'nowrap',
                              //'overflow': 'hidden',
                              //'text-overflow': 'ellipsis',
                              'text-align': 'center' } )
                      .width( '50%' )
                      .text( data[i].gtree_edit.comment ),
                    this.make('div')
                      .css( { 'float': 'left',
                              'text-align': 'center' } )
                      .width( '15%' )
                      .text( [ data[i].auth_user.first_name, data[i].auth_user.last_name ].join(' ') ),
                    this.make('div')
                      .css( { 'float': 'left',
                              'text-align': 'center' } )
                      .width( '15%' )
                      .text( data[i].gtree_edit.mtime )
                );

            if( ( i != 0 ) && ( this.controlPanel.viewer.userInfo && this.controlPanel.viewer.userInfo.canEdit ) ) {

                dataRow.append(
                    this.make('div')
                      .css( { 'float': 'left',
                              'color': 'green',
                              'text-align': 'center' } )
                      .text( 'Revert Edit' )
                      .width( '10%' )
                      .bind( 'click', { editId: data[i].gtree_edit.id }, $.proxy( this.showTreeBeforeEdit, this ) )
                      .bind( 'click', { }, BioSync.ModalBox.closeBox )
                      .bind( 'click', { }, BioSync.Common.setMouseToDefault )
                      .hover( BioSync.Common.setMouseToPointer, BioSync.Common.setMouseToDefault )
                      .hover( BioSync.Common.underlineText, BioSync.Common.removeTextUnderline ),
                    
                    this.make('div').css( { 'clear': 'both' } )
                );

            } else {
               
                dataRow.append( this.make('div').css( { 'clear': 'both' } ).width('10%') );
            }

            this.treeEditContainer.append( dataRow );
        }

        var content = this.make('div').append( this.treeEditContainer );

        BioSync.ModalBox.showModalBox( {
            content: content,
            width: this.controlPanel.viewer.windowWidth * .75,
            height: this.controlPanel.viewer.windowHeight * .75,
            title: 'Tree Edits' } );

        //this is done so that multiline rows are evenly spaced
        setTimeout(
            function() { $( $('.dataRow').children() ).css( { 'position': 'relative', top: $( dataRow.children()[1] ).height() / 2 } ) },
            1500 );
    },

   
    // this is called when someone clicks the 'Revert Edit' button.  It makes an ajax call to retrieve the state of the tree before that edit.  To plugin_treeGrafter/showTreeBeforeEdit.  When the tree is returned, the node selector is disabled, so the user can only look at the tree instead of making edits to it.
    showTreeBeforeEdit: function( e ) {
    
        var renderObj = this.controlPanel.viewer.renderObj;

        this.currentEditId = e.data.editId;

        $.ajax( { url: BioSync.Common.makeUrl( { controller: 'plugin_treeGrafter', argList: [ 'showTreeBeforeEdit' ] } ),
                  type: "GET",
                  data: e.data,
                  success: new Array( function() { renderObj.removeColumns( { start: 1, end: renderObj.columns.length - 1, keepInSession: true } ); },
                           $.proxy( renderObj.columns[0].renderReceivedClade, renderObj.columns[0] ),
                           $.proxy( renderObj.disableNodeSelector, renderObj ),
                           $.proxy( this.showRevertEditDialogue, this ) ) } );
    },

    // this function is one of many that occurs after the response from 'showTreeBeforeEdit' arrives.  The renderObj's 'renderReceivedClade' function handles the response in order to display the tree of before the selected edit.  This function adds UI to the top of the tree viewer, asking the user if they want to revert the tree to this state, or cancel the action.
    showRevertEditDialogue: function( ) {

        this.hideOption();

        this.revertEditContainer =
            this.make( 'div' ).css( { 'position': 'absolute', 'z-index': '10000' } ).append(
                this.make( 'span' )
                  .text( 'Revert tree to this state ?' )
                  .css( { 'font-weight': 'bold',
                          'padding-right': '20px',
                          'font-size': '16px' } ),
                this.make( 'span' )
                  .text( 'Yes' )
                  .hover( BioSync.Common.setMouseToPointer, BioSync.Common.setMouseToDefault )
                  .hover( BioSync.Common.underlineText, BioSync.Common.removeTextUnderline )
                  .bind( 'click', { }, $.proxy( this.revertEdit, this ) )
                  .css( { 'color': 'green',
                           'margin': '5px 10px' } ),
                this.make( 'span' )
                  .text( 'Cancel' )
                  .hover( BioSync.Common.setMouseToPointer, BioSync.Common.setMouseToDefault )
                  .hover( BioSync.Common.underlineText, BioSync.Common.removeTextUnderline )
                  .bind( 'click', { }, $.proxy( this.cancelRevertEdit, this ) )
                  .css( { 'color': 'green',
                          'margin': '5px 10px' } ) ).appendTo( this.controlPanel.viewer.renderObj.viewPanel );

        this.revertEditContainer.css( {
            'left': ( this.controlPanel.viewer.renderObj.viewPanel.myWidth - this.revertEditContainer.outerWidth( true ) ) / 2,
            'top': 10 } );

        this.controlPanel.viewer.renderObj.viewPanel.animate( { scrollTop: 0 }, 'slow' );
    },

    // called when our user clicks the 'Cancel' link regarding a reversion of a tree edit.  This function cancels the tree reversion process and gets the current 'head' of the grafted tree
    cancelRevertEdit: function() {

        this.revertEditContainer.remove();

        this.controlPanel.viewer.renderObj.redrawTree();
    },

   
    // called when the user clicks the 'Revert' link regarding a reversion of a tree edit.  This function makes a call to the server to revert the current grafted tree to a previous state.  Call made to /plugin_treeGrafter/revertEdit.
    revertEdit: function() {

        $.ajax( { url: BioSync.Common.makeUrl( { controller: 'plugin_treeGrafter', argList: [ 'revertEdit' ] } ),
                  type: "GET",
                  data: { editId: this.currentEditId },
                  success: $.proxy( this.revertEditSuccess, this ) } );
    },

    // This function is called after a successful reversion of an edit.  It enables the node selector and displays a notification for 5 seconds.
    revertEditSuccess: function() {

        this.revertEditContainer.remove();

        this.controlPanel.viewer.renderObj.enableNodeSelector();

        BioSync.Common.notify( {
            text: 'Edit Reverted.',
            timeout: 5000,
            x: this.controlPanel.viewer.renderObj.viewPanel.myWidth / 2,
            y: this.controlPanel.viewer.renderObj.viewPanel.myHeight / 2 } );
    },

    //  This function is called when the creator of the grafted tree wants to edit the privileges for other users regarding the tree
    handleShareTreeClick: function( e ) {

        $.ajax( { url: BioSync.Common.makeUrl( { controller: 'plugin_treeGrafter', argList: [ 'getGtreeSharingInfo' ] } ),
                  type: "GET",
                  success: $.proxy( this.showModalTreeSharingDialogue, this ) } );
    },

    // gives the DOM element that triggered this function a grey background
    giveGreyBackground: function( e ) {
        $( e.delegateTarget ).css( { 'background-color': '#F0F0F0' } );
    },

    // removes the grey background on the DOM element that triggered this function unless of course, it is the element that is already selected
    removeGreyBackground: function( e ) {

        if( ( this.selectedUser ) && ( e.delegateTarget == this.selectedUser.get(0) ) ) { return; }

        $( e.delegateTarget ).css( { 'background-color': '' } );
    },

    
    // this function is called when a user clicks on a name in the 'Share Tree with Colleagues' option, the currently selected user has a grey background
    selectUser: function( e ) {

        var el = $( e.delegateTarget );

        if( this.selectedUser ) { this.selectedUser.css( { 'background-color': '' } ); }
        
        if( ( this.selectedUser ) && ( this.selectedUser.get(0) == e.delegateTarget ) ) {

            delete this.selectedUser;

        } else {
           
            this.selectedUser = el.css( { 'background-color': '#F0F0F0' } );
        }
    },


    // this function handles the response from 'plugin_treeGrafter/getGtreeSharingInfo'.  It creates two boxes, each with a list of users.  One box holds the users that have edit privileges, the other box holds users that do not have edit privileges.  The user can select another user by clicking on their name, then click on an arrow to move them to a different box.  There is also a text input to filter the list of users.  This is all displayed in a modal box.
    showModalTreeSharingDialogue: function( response ) {

        var data = eval( '(' + response + ')' );

        var modal = BioSync.ModalBox;

        this.nonEditUserBox =
            this.make( 'div' ).height( this.controlPanel.viewer.windowHeight * .40 )
                              .css( { 'overflow': 'auto',
                                      'margin': '10px 5px',
                                      'border': '1px solid black' } );

        this.editUserBox =
            this.make( 'div' ).height( this.controlPanel.viewer.windowHeight * .40 )
                              .css( { 'overflow': 'auto',
                                      'margin': '10px 5px',
                                      'border': '1px solid black' } );

        for( var i = 0, ii = data.notSharedWith.length; i < ii; i++ ) {

            this.nonEditUserBox.append(
                this.make( 'div' )
                    .attr( { 'userId': data.notSharedWith[i].id } )
                    .text( [ data.notSharedWith[i].first_name, data.notSharedWith[i].last_name ].join(' ') )
                    .css( { 'padding': '5px', 'text-align': 'center' } )
                    .bind( 'click', { }, $.proxy( this.selectUser, this ) )
                    .hover( BioSync.Common.setMouseToPointer, BioSync.Common.setMouseToDefault )
                    .hover( $.proxy( this.giveGreyBackground, this ), $.proxy( this.removeGreyBackground, this ) )
            );
        }

        for( var i = 0, ii = data.sharedWith.length; i < ii; i++ ) {

            this.editUserBox.append(
                this.make( 'div' )
                    .attr( { 'userId': data.sharedWith[i].id } )
                    .text( [ data.sharedWith[i].first_name, data.sharedWith[i].last_name ].join(' ') )
                    .css( { 'padding': '5px', 'text-align': 'center' } )
                    .bind( 'click', { }, $.proxy( this.selectUser, this ) )
                    .hover( BioSync.Common.setMouseToPointer, BioSync.Common.setMouseToDefault )
                    .hover( $.proxy( this.giveGreyBackground, this ), $.proxy( this.removeGreyBackground, this ) )

            );
        }

        this.searchInput =
            this.make( 'input' ).attr( { 'type': 'text' } )
                                .bind( 'keyup', { }, $.proxy( this.handleUserSearchKeyUp, this ) );

        var searchContainer = this.searchContainer =
            this.make( 'div' )
                .css( { 'padding-top': '40px',
                        'position': 'relative',
                        'float': 'left',
                        'margin': '0 auto' } ).append(
                    this.make( 'span' ).text( 'Search : ' ),
                    this.searchInput );

        $('#modalBoxForm').append(
            this.make( 'div' ).append(
                this.make('div').css( { 'float': 'left',
                                        'font-weight': 'bold',
                                        'font-size': '16px',
                                        'text-align': 'center' } )
                                  .width( '50%' )
                                  .text( 'Read Only' ),
                this.make('div').css( { 'float': 'left',
                                        'font-weight': 'bold',
                                        'font-size': '16px',
                                        'text-align': 'center' } )
                                  .width( '50%' )
                                  .text( 'Able to Edit' ),
                this.make('div').css( { 'clear': 'both' } ) ),
            this.make( 'div' ).append(
                this.make('div').css( { 'float': 'left' } )
                                  .width( '50%' ).append(
                    this.nonEditUserBox ),
                this.make('div').css( { 'float': 'left' } )
                                  .width( '50%' ).append(
                    this.editUserBox ),
                this.make('div').css( { 'clear': 'both' } ) ),
            this.make( 'div' ).append(
                this.make('div').css( { 'float': 'left' } )
                                  .width( '50%' ).append(
                    this.make( 'div' ).css( { 'text-align': 'center',
                                              'font-weight': 'bold',
                                              'border': '1px solid green',
                                              'border-radius': '10px',
                                              'margin': '0 auto',
                                              'padding': '3px 0px',
                                              'font-size': '20px' } )
                                      .width( '50%' )
                                      .hover( BioSync.Common.setMouseToPointer, BioSync.Common.setMouseToDefault )
                                      .hover( function() { $(this).css( { 'background-color': '#F0F0F0' } ) }, function() { $(this).css( { 'background-color': 'white' } ) } )
                                      .bind( 'click', { }, $.proxy( this.giveEditPermission, this ) )
                                      .text(' > ') ),
                this.make('div').css( { 'float': 'left' } )
                                  .width( '50%' ).append(
                    this.make( 'div' ).css( { 'text-align': 'center',
                                              'font-weight': 'bold',
                                              'border': '1px solid green',
                                              'border-radius': '10px',
                                              'margin': '0 auto',
                                              'padding': '3px 0px',
                                              'font-size': '20px' } )
                                      .width( '50%' )
                                      .hover( BioSync.Common.setMouseToPointer, BioSync.Common.setMouseToDefault )
                                      .hover( function() { $(this).css( { 'background-color': '#F0F0F0' } ) }, function() { $(this).css( { 'background-color': 'white' } ) } )
                                      .bind( 'click', { }, $.proxy( this.removeEditPermission, this ) )
                                      .text(' < ') ),
                this.make('div').css( { 'clear': 'both' } ) ),
            this.make('div').append( this.searchContainer, this.make('div').css({'clear':'both'}) ) );

            BioSync.ModalBox.showModalBox( {
                width: this.controlPanel.viewer.windowWidth * .75,
                height: this.controlPanel.viewer.windowHeight * .75,
                title: 'Give Edit Permission to Others' } );

            var controlPanel = this.controlPanel;

            setTimeout(

                function() {
                    
                    var searchContainerWidth = searchContainer.outerWidth( true );

                    searchContainer.css( { 'left': ( ( controlPanel.viewer.windowWidth * .75 ) - searchContainerWidth ) / 2 } );

                }, 2000 );
    },

   
    // this function is called when someone begins typing while the user permissions search is focused.  KeyCodes 8 and 46 refer to the backspace and delete keys respectively. The function ignores typing keys that are not 'word' characters as defined by javascript, as well as the backspace and delete keys.  If an acceptable key is pressed, the function waits 500 milliseconds before calling the function 'showOnlyMatchingUsers', which actually filters the two user lists.  
    handleUserSearchKeyUp: function( e ) {

        if( e.keyCode == 8 || e.keyCode == 46 || String.fromCharCode( e.keyCode ).match( /\w/ ) ) {

            if( this.userInputTimeout ) { clearTimeout( this.userInputTimeout ); }

            this.userInputTimeout = setTimeout( $.proxy( this.showOnlyMatchingUsers, this ), 500 );
        }
    },

    //As described in the function above ( handleUserSearch ), this function filters the two user permissions lists based on the text in the search box.
    showOnlyMatchingUsers: function( e ) {

        var value = this.searchInput.val().toLowerCase();

        var boxes = [ 'nonEditUserBox', 'editUserBox' ];

        for( var j = 0, jj = 2; j < jj; j++ ) {

            var userDivs = this[ boxes[j] ].children();

            for( var i = 0, ii = userDivs.length; i < ii; i++ ) {
           
                var div = $( userDivs[i] );

                if( div.text().toLowerCase().indexOf( value ) == -1 ) {

                    div.hide();

                } else {
                    
                    div.show();

                }
                
            }
        }
    },

    //This function refers to the UI involving the setting of permissions for a user for a particular grafted tree.  When the user clicks the '<' button, "moving" an individual from the 'Able to Edit', to the 'Read Only' box, this function is called.  If there is a user selected in the Able to Edit box, an ajax request is made to remove the edit permissions for the particular user. 
    removeEditPermission: function( e ) {

       if( ! this.selectedUser ) { return; } 

       if( this.editUserBox.find( this.selectedUser ).length ) {

            $.ajax( { url: BioSync.Common.makeUrl( { controller: 'plugin_treeGrafter', argList: [ 'removeEditPermission' ] } ),
                      data: { userId: this.selectedUser.attr('userId') },
                      type: "POST",
                      success: $.proxy( this.removeEditPermissionSuccess, this ) } );
       }
    },

    //Similar to the 'giveEditPermission' function, giveEditPermission makes an ajax request to give a user edit privileges to the tree.
    giveEditPermission: function( e ) {

       if( ! this.selectedUser ) { return; } 

       if( this.nonEditUserBox.find( this.selectedUser ).length ) {

            $.ajax( { url: BioSync.Common.makeUrl( { controller: 'plugin_treeGrafter', argList: [ 'giveEditPermission' ] } ),
                      data: { userId: this.selectedUser.attr('userId') },
                      type: "POST",
                      success: $.proxy( this.giveEditPermissionSuccess, this ) } );
       }
    },

    //Called when the 'removeEditPermission' ajax request was successful.  This function manipulates the DOM to show this visually.
    removeEditPermissionSuccess: function() {

        var optionObj = this;

        this.selectedUser.hide( 'slow',
            function() { optionObj.selectedUser.appendTo( optionObj.nonEditUserBox ).show( 'slow' ); }
        );
    },

    //Called when the 'giveEditPermission' ajax request was successful.  This function manipulates the DOM to show this visually.
    giveEditPermissionSuccess: function() {

        var optionObj = this;

        this.selectedUser.hide( 'slow',
            function() { optionObj.selectedUser.appendTo( optionObj.editUserBox ).show( 'slow' ); }
        );
    },

    //This function is called when the mouse leaves the sub menu with the 'View Edit and Share With Colleagues' options.  If it is also outside of the top level menu item 'Graft Options', the sub menu is hidden.
    handleMouseOutOfSelectionContainer: function( e ) {

        if( ( ! BioSync.Common.isMouseOnElement( { x: e.pageX, y: e.pageY, el: this.container } ) ) ) {
            
            this.hideOption();
        }
    },

    //This function is called when the mouse hovers over the 'Graft Options' menu item.  It sets the background to light grey, shows the submenu, sets the width of the control panel to include the submenu, and checks to see if the heigh of the control panel needs to change.
    handleMouseOverContainer: function( e ) {

        this.label.css( { 'background-color': 'lightGrey' } );

        this.selectionContainer.show();

        this.controlPanel.optionContainer.width(
            this.label.outerWidth( true ) +
            this.selectionContainer.outerWidth( true ) + 
            this.controlPanel.config.optionContainerLeftBuffer );

        this.controlPanel.checkOptionContainerHeight( { subOptionContainer: this.selectionContainer } );
    },

    //This function is called when the mouse leaves the 'Graft Options' menu container, if the mouse is also not hovering the sub menu, then the option is hidden.
    handleMouseOutOfContainer: function( e ) {
        
        if( ( ! BioSync.Common.isMouseOnElement( { x: e.pageX, y: e.pageY, el: this.selectionContainer } ) ) ) {
            
            this.hideOption();
        }
    },

    //hides the 'Graft Options' sub menu
    hideOption: function( e ) {

        this.label.css( { 'background-color': 'white' } );
        
        this.selectionContainer.hide();
       
        this.controlPanel.optionContainer.css( { 'width': '' } );
    },
}


//Here is the object definition of the 'tree size' menu item.
BioSync.TreeViewer.ControlPanel.prototype.options.treeSize.prototype = {

    // these are configuration settings, notice the 'option' attribute, this is where you define the submenu options.  name refers to the sub menu item text, viewerConfigName corresponds to the attribute used in the session.config ( controlPanel.viewer.config on the client ), min and max are the minimum and maximum values for the corresponding slider control.
    config: {

        optionPadding: '5px',
        containerPadding: '5px',
        sliderSize: 100,
        sliderTopOffset: 7,
        valueChangeTimeout: 1000,

        options: {

            branchLength: {
                name: 'branch length',
                viewerConfigName: 'branchLength',
                min: 5,
                max: 200
            },
            
            verticalTipBuffer: {
                name: 'vertical tip buffer',
                viewerConfigName: 'verticalTipBuffer',
                min: 5,
                max: 200
            },
            
            fontSize: {
              name: 'font size',
              viewerConfigName: 'fontSize',
              min: 5,
              max: 50,
              handleOnChange: 'updateFontSize',
            },
            
            maxTips: {
              name: 'max tips (per column)',
              viewerConfigName: 'maxTips',
              min: 5,
              max: 500,
              handleOnChange: 'handleMaxTipsOnChange',
            }
         }
    },

    //This is called right after the menu item object is created, it creates all of the DOM elements associated with the tree size option
    initialize: function() {

        var rv =
                this.controlPanel.makeOptionContainer( {
                    obj: this,
                    label: 'tree sizing > ' } );
       
        this.container = rv[0];
        this.label = rv[1];
        
        this.sizingOptionsContainer =
            this.make( 'div' ).css( { 'position': 'absolute', 
                                      'z-index': this.controlPanel.config.zIndex,
                                      'padding': [ '0px ', this.config.containerPadding ].join(''),
                                      'top': 0,
                                      'left': this.label.outerWidth( true ) } )
                              .hoverIntent( $.proxy( this.handleMouseOverOptionList, this ), $.proxy( this.handleMouseOutOfOptionList, this ) )
                              .appendTo( this.container );
            
        this.multiLineOptionContainer = this.sizingOptionsContainer;

        for( var optionName in this.config.options ) {

            var option = this.config.options[ optionName ];

            option.valueBox =
                this.make('input')
                    .attr( { 'type': 'text' } )
                    .width( 30 )
                    .css( { 'float': 'left',
                            'text-align': 'center',
                            'padding': [ '0px', this.config.optionPadding ].join(' ' ) } )
                    .val( this.controlPanel.viewer.config[ option.viewerConfigName ].value )
                    .bind( 'keyup', option, $.proxy( this.handleValueChange, this ) )
                    .bind( 'keypress', option, $.proxy( this.filterAlphaKeyPress, this ) );

            option.labelDiv =
                this.make('div')
                    .css( { 'float': 'left', padding: [ '0px', this.config.optionPadding ].join(' ' ) } )
                    .text( option.name + ' : ' );

            option.slider =
                this.make('div').css( { 'top': this.config.sliderTopOffset } )
                                .slider( { max: option.max,
                                           min: option.min,
                                           value: this.controlPanel.viewer.config[ option.viewerConfigName ].value,
                                           slide: $.proxy( this.handleSlide, option.valueBox ) } )
                                .bind( 'slidechange',
                                       { name: option.viewerConfigName },
                                       ( option.handleOnChange ) ? $.proxy( this[ option.handleOnChange ], this ) : $.proxy( this.updateConfig, this ) );

            option.container =
                this.make('div')
                  .css( { 'padding': this.config.optionPadding } )
                  .appendTo( this.sizingOptionsContainer )
                  .append(
                    option.labelDiv,
                    this.make('div').css( { 'padding': [ '0px', this.config.optionPadding ].join(' ' ),
                                            'float': 'left',
                                            'width': this.config.sliderSize } )
                                    .append( option.slider ),
                    option.valueBox,
                    this.make('div').attr( { 'class': 'clear' } ) );

            //adding 15 to the width below so that if the numbers constituting the value div change
            //such that it increases the value div width - we needn't worry
            option.container.css( {'width':
                option.valueBox.outerWidth( true ) + 15 +
                option.labelDiv.outerWidth( true ) +
                this.config.sliderSize +
                ( parseInt( this.config.optionPadding ) * 2 ) } );
        }

        this.container.width( this.label.outerWidth( true ) + parseInt( this.config.containerPadding ) );

        this.sizingOptionsContainer.hide();

        $('.ui-slider-handle').hover( BioSync.Common.setMouseToPointer, BioSync.Common.setMouseToDefault );

        return this;
    },

    //This function is called when a user tries to enter a new value into a configuration text box.  The function ignores anything that is not a number or a backspace or a delete.
    filterAlphaKeyPress: function( e ) {

        var key = e.keyCode || e.which;

        if( e.keyCode == 8 || e.keyCode == 46 ) { return true; }

        key = String.fromCharCode( key );

        var regex = /[0-9]|/;

        if( !regex.test( key ) ) {
        
            e.returnValue = false;

            if( e.preventDefault ) { e.preventDefault(); }
        }
    },

    //This function is called when a user is entering data into a configuration text box.  Rather than call 'updateValue' after every key up event, it waits a number of milleseconds -- 'valueChangeTimeout' -- for no key up event to take place before calling 'updateValue'.
    handleValueChange: function( e ) {

        if( e.data.userInputTimeout ) { clearTimeout( e.data.userInputTimeout ); }

        e.data.userInputTimeout = setTimeout( $.proxy( this.updateValue, e.data ), this.config.valueChangeTimeout );
    },

    //This updates the slider value when a user updates the configuration via the text box.
    updateValue: function() {

        if( this.valueBox.val() < this.slider.slider( 'option', 'min' ) ) {

            this.valueBox.val( this.slider.slider( 'option', 'min' ) );
        }

        this.slider.slider( 'option', 'value', this.valueBox.val() );
    },
    
    handleMouseOverOptionList: function( e ) {
    },
   
    //When the mouse leaves the sub menu, this function is called.  If the mouse is also not over the menu item, it removes the sub menu from view.
    handleMouseOutOfOptionList: function( e ) {

        if( ( ! BioSync.Common.isMouseOnElement( { x: e.pageX, y: e.pageY, el: this.container } ) ) ) {
            
            this.hideOption();
        }
    },

    //This is called when the user updates the max tips option from outside the control panel.  Right now, this is only possible after a vertical expand on a collapsed node.  It uninds the slider event, changes the slider, sets the value box, and resets the slider event.
    updateMaxTips: function() {

        var optionObj = this.config.options.maxTips;

        optionObj.slider.unbind( 'slidechange' );

        optionObj.slider.slider( 'option', 'value', this.controlPanel.viewer.config.maxTips.value );

        optionObj.valueBox.val( this.controlPanel.viewer.config.maxTips.value );
                                       
        optionObj.slider.bind(
            'slidechange', { name: 'maxTips' }, ( optionObj.handleOnChange ) ? $.proxy( this[ optionObj.handleOnChange ], this ) : $.proxy( this.updateConfig, this ) );
    },

    //If a tree size option config does not have a specific 'handleOnChange' attribute that corresponds to an event, this generic function is called.  It calls the viewer's update config event which updates the configuration on the client and on the server.  If the redraw parameter is set to true, then the tree is refreshed to show the updated options.
    updateConfig: function( e, ui ) {

        if( this.controlPanel.viewer.config[ e.data.name ].value != ui.value ) {
        
            this.controlPanel.viewer.updateConfig( { names: [ e.data.name ], values: [ ui.value ], redraw: true } );
        }
    },

    //Called when the max tips slider or text value is changed.
    handleMaxTipsOnChange: function( e, ui ) {

        var optionObj = this.config.options.maxTips;

        var currentValue = this.controlPanel.viewer.config.maxTips.value;
        var newValue = ui.value;

        if( newValue > currentValue ) {
            
            $.ajax( { url: BioSync.Common.makeUrl( { controller: 'plugin_treeViewer', argList: [ 'uncollapseNodes' ] } ),
                      type: "POST", async: false } );
        }

        this.updateConfig( e, ui );
    },
   
    //Called when the font size slider or text value is changed.
    updateFontSize: function( e, ui ) {
         
        BioSync.Common.style.fontSize = ui.value;
        BioSync.Common.setTextWidthMetric();

        this.updateConfig( e, ui );        
    },

    //Called when a slider is slid.
    handleSlide: function( e, ui ) { this.val( ui.value ); },

    
    //This function is called when the mouse leaves the 'tree size' menu item.  If the mouse is not hovering the sub menu, then the option is hidden.
    handleMouseOutOfContainer: function( e ) {

        if( ( ! BioSync.Common.isMouseOnElement( { x: e.pageX, y: e.pageY, el: this.sizingOptionsContainer } ) ) ) {
            
            this.hideOption();
        }
    },

    //Called when the mouse is over the menu item.
    handleMouseOverContainer: function( e ) {

        this.label.css( { 'background-color': 'lightGrey' } );

        this.sizingOptionsContainer.show();

        this.controlPanel.optionContainer.width(
            this.label.outerWidth( true ) +
            this.sizingOptionsContainer.outerWidth( true ) + 
            this.controlPanel.config.optionContainerLeftBuffer );

        var optionContainerOffset = this.controlPanel.optionContainer.offset();
        var sizingContainerOffset = this.sizingOptionsContainer.offset();

        var difference =
            ( sizingContainerOffset.top + this.sizingOptionsContainer.outerHeight( true ) ) -
            ( optionContainerOffset.top + this.controlPanel.optionContainer.outerHeight( true ) );

        if( difference > 0 ) {
        
            this.controlPanel.optionContainer.height(
                this.controlPanel.optionContainer.height() +
                difference );
        }
    },

    //Hides the tree size sub menu
    hideOption: function() {

        this.label.css( { 'background-color': 'white' } );
        
        this.sizingOptionsContainer.hide();
       
        this.controlPanel.optionContainer.css( { 'width': '', 'height': '' } );
    }

}



//Here is the object definition of the 'branch length' menu item.
BioSync.TreeViewer.ControlPanel.prototype.options.branchLength.prototype = {

    config: {

        padding: 5    
    },


    //Called after the object is created, note that it only shows up when all of the branches in a tree have a branch length.
    initialize: function() {

        if( this.controlPanel.viewer.allNodesHaveLength ) {

            var rv =
                this.controlPanel.makeOptionContainer( {
                    obj: this,
                    label: 'branch length > ' } );
       
            this.container = rv[0];
            this.label = rv[1];

            this.branchLengthStyle = this.controlPanel.viewer.config.branchLengthStyle;

            var smoothHtml, scaleHtml;

            if( this.branchLengthStyle == 'smooth' ) {

                smoothHtml = [ 'smooth', BioSync.Common.htmlCodes.check ].join( ' ' );
                scaleHtml = 'scale';

            } else {
                
                smoothHtml = 'smooth';
                scaleHtml = [ 'scale', BioSync.Common.htmlCodes.check ].join( ' ' );
            }

            this.smoothSpan =
                this.make('span').html( smoothHtml )
                                 .hover( BioSync.Common.setMouseToPointer, BioSync.Common.setMouseToDefault )
                                 .bind( 'click', { }, $.proxy( this.handleSmoothClick, this ) );

            this.scaleSpan =
                this.make('span').html( scaleHtml )
                                 .hover( BioSync.Common.setMouseToPointer, BioSync.Common.setMouseToDefault )
                                 .bind( 'click', { }, $.proxy( this.handleScaledClick, this ) );

            this.selectionContainer =
                this.make('div').css( { 'padding': [ '0px ', this.config.padding, 'px' ].join(''),
                                        'position': 'absolute',
                                        'top': 0,
                                        'left': this.label.outerWidth( true ) } ).append(
                    this.make('div').css( { 'padding': this.config.padding } ).append( this.smoothSpan ),
                    this.make('div').css( { 'padding': this.config.padding } ).append( this.scaleSpan ) )
                .hoverIntent( function() { }, $.proxy( this.handleMouseOutOfSelectionContainer, this ) )
                .appendTo( this.container )
                .hide();

            this.multiLineOptionContainer = this.selectionContainer;
        }

        return this;
    },

    //Called when the mouse leaves the sub menu, hides the option when the mouse is not hovering the menu item.
    handleMouseOutOfSelectionContainer: function( e ) {

        if( ( ! BioSync.Common.isMouseOnElement( { x: e.pageX, y: e.pageY, el: this.container } ) ) ) {
            
            this.hideOption();
        }
    },

    //Called when the mouse enters the menu item, shows the sub menu
    handleMouseOverContainer: function( e ) {

        this.label.css( { 'background-color': 'lightGrey' } );

        this.selectionContainer.show();

        this.controlPanel.optionContainer.width(
            this.label.outerWidth( true ) +
            this.selectionContainer.outerWidth( true ) + 
            this.controlPanel.config.optionContainerLeftBuffer );
    },

    //Called when the mouse leaves the menu item, hides the options when the mouse is not hovering the sub menu.
    handleMouseOutOfContainer: function( e ) {
        
        if( ( ! BioSync.Common.isMouseOnElement( { x: e.pageX, y: e.pageY, el: this.selectionContainer } ) ) ) {
            
            this.hideOption();
        }
    },

    //Hides the sub menu.
    hideOption: function( e ) {

        this.label.css( { 'background-color': 'white' } );
        
        this.selectionContainer.hide();
       
        this.controlPanel.optionContainer.css( { 'width': '' } );
    },

    //Called when the user clicks the 'smooth' branch length option, calls the render object's ( static/phylogram.js ) updateBranchLength method.
    handleSmoothClick: function() {

        if( this.branchLengthStyle == 'smooth' ) { return; }

        this.branchLengthStyle = 'smooth';

        this.smoothSpan.html( [ 'smooth', BioSync.Common.htmlCodes.check ].join( ' ' ) );
        this.scaleSpan.html('scale');
        
        this.controlPanel.viewer.renderObj.updateBranchLength( this.branchLengthStyle );
    },

    //Called when the user clicks the 'scale' branch length option
    handleScaledClick: function() {

        if( this.branchLengthStyle == 'scale' ) { return; }

        this.branchLengthStyle = 'scale';

        this.scaleSpan.html( [ 'scale', BioSync.Common.htmlCodes.check ].join( ' ' ) );
        this.smoothSpan.html('smooth');
        
        this.controlPanel.viewer.renderObj.updateBranchLength( this.branchLengthStyle );
    }
}


//Here is the object definition of the 'search' menu item.
BioSync.TreeViewer.ControlPanel.prototype.options.search.prototype = {

    config: {

        borderRadius: '5px',
        pixelsBetweenLabelAndSearch: 15,
        labelListMaxHeight: '150px',
        initialSearchContainerWidth: 100,
        pageButtonOffsetTop: 2,
        searchInputPadding: 5,
        searchInputBorderWidth: 1,
        searchInputMarginRight: 5,
        hoverBridgeHeight: 40
    },

    //Called after the object is created.  This function creates the DOM elements for the search menu item.
    initialize: function() {

        var rv =
            this.controlPanel.makeOptionContainer( {
                obj: this,
                label: 'search > ' } );
       
        this.container = rv[0];
        this.searchLabel = rv[1];

        this.searchContainer =
            this.make('div')
                .css( { 'position': 'absolute',
                        'padding': '0px',
                        'z-index': this.controlPanel.config.matchingLabelListZIndex,
                        'top': this.config.searchInputBorderWidth,
                        'left': this.searchLabel.outerWidth( true ) + this.config.pixelsBetweenLabelAndSearch } )
                .width( this.config.initialSearchContainerWidth )
                .keyup( $.proxy( this.handleKeyUp, this ) )
                .mouseleave( $.proxy( this.handleMouseOutOfSearch, this ) )
                .appendTo( this.container );

        //This hover bridge is used as an invisible DOM element that let's us know that the mouse is still near our menu item even if its not directly hovering over the menu.  If the mouse is still near our search menu item, we do not want to hide it.
        this.hoverBridge =
            this.make('div')
                .css( { 'position': 'absolute',
                        'top': -( this.config.hoverBridgeHeight ) } )
                .height( this.config.hoverBridgeHeight )
                .appendTo( this.searchContainer );

        this.searchInput =
            this.make('input')
                .attr( { 'type': 'text', 'value': 'label or taxon' } )
                .css ( { 'padding': this.config.searchInputPadding,
                         '-moz-border-radius': this.config.borderRadius,
                         'border-radius': this.config.borderRadius,
                         'border-width': this.config.searchInputBorderWidth,
                         'height': '12px !important',
                         'width': '!important',
                         'text-align': 'left' } )
                .appendTo( this.searchContainer );

        this.alignSearchWithContainer();

        BioSync.Common.removeTextFirstFocus( { el: this.searchInput } );

        this.matchingLabelList =
            this.make('div')
                .css( { 'position': 'absolute',
                        'left': 0,
                        'z-index': this.controlPanel.config.matchingLabelListZIndex,
                        'top': this.searchInput.outerHeight( true ),
                        'text-align': 'center',
                        'border': '1px solid #CEE8F0',
                        'max-height': this.config.labelListMaxHeight,
                        'overflow': 'auto' } )
                .appendTo( this.searchContainer )
                .hide();

        this.searchContainer.hide();

        this.container.height( this.searchLabel.outerHeight( true ) )
                      .width( this.searchLabel.outerWidth( true ) + this.config.pixelsBetweenLabelAndSearch );

        return this;
    },

    //Called when the mouse is over the menu item, shows the search input box and sizes the control panel.
    handleMouseOverContainer: function() {

       this.searchLabel.css( { 'background-color': 'lightGrey' } );

       this.searchContainer.show();

       this.controlPanel.optionContainer.width(
        this.searchLabel.outerWidth( true ) +
        this.searchContainer.outerWidth( true ) + 
        this.controlPanel.config.optionContainerLeftBuffer );
    },

    //Called when the mouse is no longer hovering over the menu item, hides the menu item
    handleMouseOutOfContainer: function() {

       this.searchLabel.css( { 'background-color': 'white' } );
       
       this.searchContainer.hide();
       
       this.controlPanel.optionContainer.css( { 'width': '' } );
    },

    //Called when the mouse of not hovering the search sub menu, if it was also not hovering the 'search' part, the menu was hidden. 
    handleMouseOutOfSearch: function( e ) {

        if( ( ! BioSync.Common.isMouseOnElement( { x: e.pageX, y: e.pageY, el: this.container } ) ) ) {

            this.resetElements();
            this.searchInput.val('label or taxon').blur();
            BioSync.Common.removeTextFirstFocus( { el: this.searchInput } );
        }
    },

    //Called when a user uses the arrow keys to traverse the search options. 
    handleArrowAndMouseSearch: function() {

        //if there is a mouse cursor visible
        if( ! this.matchingLabelList.hasClass('noCursor') ) {

            this.matchingLabelList.addClass('noCursor');

            //mouseenter happens with invisible mouse
            $('.searchResult').unbind( 'mouseenter mouseleave' );

            //make everything normal when mouse moves again
            this.setSearchMouseMove();
        }
    },

    
    //This function binds mouse hover on the search results.  This menu item has two modes for searching, using the mouse, or the arrows.
    setSearchHover: function() {
        
        $('.searchResult').unbind( 'mouseenter mouseleave' ).hover( $.proxy( this.searchResultHoverIn, this ), $.proxy( this.searchResultHoverOut, this ) );
    },

    //Called when the mouse hovers over a search result.  Styles the search result, sets it to a variable.
    searchResultHoverIn: function( e ) {

        this.unStyleCurrentlySelected();
        this.currentlySelected = $( e.target );
        this.styleCurrentlySelected();
    },

    //Called when the mouse leaves a search result.
    searchResultHoverOut: function( e ) {

        this.unStyleCurrentlySelected();
    },

   
    //This is called when someone uses the arrow keys to traverse through the search results.  It automatically scrolls the result container, so that you can see the newly selected search result.
    handleSearchAutoScroll: function( p ) {

        //scrolling makes the mouse move, it may be a bad idea to unbind this document wide...
        //$(document).unbind('mousemove');
        $(document).unbind( 'mousemove', $.proxy( this.handleMouseMoveInSearch, this ) );

        //scroll and on success function
        this.matchingLabelList.animate( { scrollTop: '+=' + p.scroll }, 250, 'linear', $.proxy( this.setSearchMouseMove, this ) );
    },

    //This is called to handle mouse movement while in arrow key search mode.
    setSearchMouseMove: function() {

        $( document ).bind( 'mousemove', { }, $.proxy( this.handleMouseMoveInSearch, this ) );
    },

    //Called when the mouse moves during arrow search mode, makes the mouse visible, and changes modes.
    handleMouseMoveInSearch: function() {

        this.matchingLabelList.removeClass('noCursor');

        this.setSearchHover();
    },

    //Styles the currently selected search result
    styleCurrentlySelected: function() {

        this.currentlySelected.css( {
            'background-color': '#EAEAEA' } );
    },

    //Removes styling from the currently selected search result.
    unStyleCurrentlySelected: function( p ) {

        if( this.currentlySelected ) {
            this.currentlySelected.css( {
                'background-color': 'white' } );
        }
    },

    //This function is called when the javascript 'keyup' event occurs in the search box
    handleKeyUp: function( e ) {

        var that = this;

        //enter button pressed
        if( e.keyCode == 13 ) {

            this.currentlySelected.click();

        //down arrow pressed
        } else if( e.keyCode == 40 ) {

            this.handleArrowAndMouseSearch();

            if( this.currentlySelected ) {

                if( this.currentlySelected.attr('nodeId') != $('.searchResult').filter(':last').attr('nodeId') ) {

                    this.unStyleCurrentlySelected();

                    this.currentlySelected = this.currentlySelected.next();
                    this.styleCurrentlySelected();

                    if( this.currentlySelected.offset().top + this.currentlySelected.outerHeight( true ) >
                        this.matchingLabelList.offset().top + this.matchingLabelList.outerHeight( true ) ) {

                        this.handleSearchAutoScroll( { scroll: this.currentlySelected.outerHeight( true ) } );
                    }
                }

            } else {

                this.currentlySelected =  $( $('.searchResult')[0] );
                this.styleCurrentlySelected();
            }
            
        //up arrow pressed
        } else if( e.keyCode == 38 ) {
            
            this.handleArrowAndMouseSearch();

            if( this.currentlySelected ) {

                if( this.currentlySelected.attr('nodeId') != $( $('.searchResult')[0] ).attr('nodeId') ) {

                    this.unStyleCurrentlySelected();

                    this.currentlySelected = this.currentlySelected.prev();
                    this.styleCurrentlySelected();

                    if( this.currentlySelected.offset().top < this.matchingLabelList.offset().top ) {

                        this.handleSearchAutoScroll( { scroll: -( this.currentlySelected.outerHeight( true ) ) } );
                    }

                } else {

                    this.unStyleCurrentlySelected();
                    this.currentlySelected = undefined;
                }
            }
           
        //letter is pressed
        } else if( e.keyCode == 8 || e.keyCode == 46 || String.fromCharCode( e.keyCode ).match( /\w/ ) ) {

            if( this.userInputTimeout ) { clearTimeout( this.userInputTimeout ); }

            this.userInputTimeout = setTimeout( $.proxy( this.getMatchingLabels, this ), 500 );
        }
    },
  
    //Called when valid input occurs in the search box and 500 milliseconds have occurred without more typing.  Calls 'makeSearchRequest' if the box isn't empty, which makes the ajax call to get the results.
    getMatchingLabels: function() {

        if( this.searchInput.val() != '' ) {

            this.labelPage = 1;

            this.makeSearchRequest();


        } else {

            this.matchingLabelList.empty();
            this.currentlySelected = undefined;
            this.matchingLabelList.empty().css( { 'height': '', 'width': '' } );
            this.searchContainer.width( this.config.initialSearchContainerWidth );
            this.alignSearchWithContainer();
            this.setOptionContainerWidth(); 
        }
    },

    //Makes an ajax request to retrieve matching labels/taxa
    makeSearchRequest: function() {

        $.ajax( { url: BioSync.Common.makeUrl( { controller: 'plugin_treeViewer', argList: [ 'getMatchingDescendantLabels' ] } ),
                  type: "GET", data: { value: this.searchInput.val(), next: 1, page: this.labelPage }, success: $.proxy( this.handleMatchingLabels, this ) } );
    },

    //Called when a user clicks on a search result.  It calls the render object's navigateToNode function.
    labelSelected: function( e ) {

        var el = $( $( e.target ).closest( "[nodeId]" ) );

        this.controlPanel.viewer.renderObj.navigateToNode( { nodeId: el.attr('nodeId'), next: el.attr('next'), back: el.attr('back') } );
        this.controlPanel.viewer.controlPanel.hideControlPanel();
    },

    //This function handles a search request.
    handleMatchingLabels: function( response ) {

        if( this.searchInput.is(':hidden') ) { return; }

        this.resetElements();

        var responseData = eval( '(' + response + ')' );

        var matchingLabels = responseData.rows;
        var totalMatched = responseData.total;

        if( ! matchingLabels.length ) {

            this.matchingLabelList.append(
                this.make('div')
                    .css( { 'padding': '1px 5px 1px 3px',
                            'font-size': '10px',
                            'text-align': 'left', 'font-weight': 'bold' } )
                    .text( 'No Matching Labels or Taxa Found' ) );
        } else {

            var text;

            if( totalMatched > matchingLabels.length ) {

                var start = ( ( this.labelPage - 1 ) * this.controlPanel.viewer.config.collapsedCladeSearchPageLength ) + 1;
                var end = this.labelPage * this.controlPanel.viewer.config.collapsedCladeSearchPageLength;
                if( end > totalMatched ) { end = totalMatched; }

                text = [ start, ' - ', end ].join('');

                if( end < totalMatched ) {

                    this.nextPageButton = this.make('div')
                        .text( '>' )
                        .hover( this.handlePageArrowHover, this.handlePageArrowOut )
                        .css( { 'position': 'absolute','font-weight': 'bold' } )
                        .hover( BioSync.Common.setMouseToPointer, BioSync.Common.setMouseToDefault )
                        .bind( 'click', { }, $.proxy( this.nextPageClick, this ) );
                }

                if( this.labelPage > 1 ) {

                    this.prevPageButton = this.make('div')
                        .text( '<' )
                        .hover( this.handlePageArrowHover, this.handlePageArrowOut )
                        .css( { 'position': 'absolute','font-weight': 'bold' } )
                        .hover( BioSync.Common.setMouseToPointer, BioSync.Common.setMouseToDefault )
                        .bind( 'click', { }, $.proxy( this.prevPageClick, this ) );
                }

            } else {

                text = matchingLabels.length;
            }

            this.labelListHeader = 
                this.make('div').css( { 'background-color': 'white' } ).append(
                    this.make('span')
                    .css( { 'padding-top': '1px',
                            'padding-left': BioSync.Common.scrollbarWidth * 2,
                            'padding-right': BioSync.Common.scrollbarWidth * 2,
                            'z-index': this.controlPanel.config.matchingLabelListZIndex,
                            'padding-bottom': '3px',
                            'text-align': 'center',
                            'font-size': '10px',
                            'font-weight': 'bold' } )
                    .text( [ text, ' of ', totalMatched, ' Descendant Labels Found' ].join('') ) );

            this.matchingLabelList.append( this.labelListHeader );
        }
        
        for( var i = 0, ii = responseData.rows.length; i < ii; i++ ) {

            var row = responseData.rows[i];

            var label = row[1].replace( '_', ' ' );
            var taxon = row[2];

             var text = ( taxon == label )
                ? label
                : ( ( taxon ) && ( label ) )
                    ? [ 'Taxon: ', taxon, ' - Label: ', label ].join('')
                    : ( taxon )
                        ? taxon
                        : label;

            this.matchingLabelList.append(
                this.make('div')
                    .attr( { 'class': 'searchResult', 'nodeId': row[0], 'next': row[3], 'back': row[4] } )
                    .css( { 'padding': '2px 5px',
                            'background-color': 'white',
                            'z-index': this.controlPanel.config.matchingLabelListZIndex,
                            'font-size': '10px'} )
                    .text( text )
                    .hover( $.proxy( this.searchResultHoverIn, this ), $.proxy( this.searchResultHoverOut, this ) )
                    .hover( BioSync.Common.setMouseToPointer, BioSync.Common.setMouseToDefault )
                    .click( $.proxy( this.labelSelected, this ) ) );
        }

        this.sizeElementsAfterSearch();

        this.positionPageButtons();
    },

    //positions the forward and back page buttons
    positionPageButtons: function() {
        
        if( this.nextPageButton ) {

            this.nextPageButton.css( {
                'left': this.matchingLabelList.outerWidth( true ) -
                        this.nextPageButton.outerWidth( true ) -
                        ( BioSync.Common.scrollbarWidth * 2 ),
                'top': this.config.pageButtonOffsetTop } )
                .appendTo( this.labelListHeader );
        }

        if( this.prevPageButton ) {

            this.prevPageButton.css( {
                'left': BioSync.Common.scrollbarWidth,
                'top': this.config.pageButtonOffsetTop } )
                .appendTo( this.labelListHeader );
        }
    },

    //After the search results are displayed, this function sets DOM element sizes so that everything looks ok.
    sizeElementsAfterSearch: function() {
        
        if( this.matchingLabelList.outerHeight( true ) > parseInt( this.config.labelListMaxHeight ) ) {
            this.matchingLabelList.width( this.matchingLabelList.outerWidth( true ) + BioSync.Common.scrollbarWidth );
        }

        this.searchContainer.width( this.matchingLabelList.outerWidth( true ) );

        this.alignSearchWithLabelList();

        this.setOptionContainerHeight();
        this.setOptionContainerWidth(); 
    },

    //This function makes sure that the control panel's height contains the search results.
    setOptionContainerHeight: function() {
    
        var optionContainerOffset = this.controlPanel.optionContainer.offset();
        var matchingLabelListOffset = this.matchingLabelList.offset();

        var difference =
            ( optionContainerOffset.top + this.controlPanel.optionContainer.outerHeight( true ) ) -
            ( matchingLabelListOffset.top + this.matchingLabelList.outerHeight( true ) );

        if( difference < 0 ) {

            this.controlPanel.optionContainer.height(
                this.controlPanel.optionContainer.outerHeight() - difference );
        }
    },

    //This function makes sure that the control panel's width contains the search results.
    setOptionContainerWidth: function() {

        this.controlPanel.optionContainer.width(
            this.searchLabel.outerWidth( true ) +
            this.config.pixelsBetweenLabelAndSearch +
            this.searchContainer.outerWidth( true ) );
    },
       
    //This function aligns the search box with the result list after results come back from the server
    alignSearchWithLabelList: function() {

        var offset = ( this.config.searchInputPadding * 2 ) +
            ( this.config.searchInputBorderWidth * 2 );

        var width = this.matchingLabelList.outerWidth( true ) - offset;

        this.searchInput.width( width );
        this.hoverBridge.width( width );
    },

    //This function aligns the search box with the control panel container.
    alignSearchWithContainer: function() {

        var width = this.searchContainer.outerWidth( true ) - this.config.searchInputMarginRight;
        this.searchInput.width( width );
        this.hoverBridge.width( width );
    },

    //This function resets the menu item to a fresh state.
    resetElements: function() {

        this.currentlySelected = undefined;
        this.matchingLabelList.empty().show().css( { 'height': '', 'width': '' } );
        this.searchContainer.width( this.config.initialSearchContainerWidth );
        this.alignSearchWithContainer();
        this.controlPanel.optionContainer.css( { 'height': '', 'width': '' } );
        this.nextPageButton = this.prevPageButton = undefined;
    },

    //This function is called when the next page arrow is clicked.
    nextPageClick: function() {

        this.labelPage++;

        this.makeSearchRequest();
    },

    //This function is called when the previous page arrow is clicked.
    prevPageClick: function() {

        this.labelPage--;

        this.makeSearchRequest();
    }
}
