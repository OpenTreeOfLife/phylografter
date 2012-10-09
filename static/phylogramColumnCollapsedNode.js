BioSync.TreeViewer.Column.CollapsedNode.prototype = {

    config: {
        strokeWidth: 1,
        expandIconWidth: 20,
        expandIconHeight: 20,
        optionPadding: '5px',
        searchInputWidth: "90%",
        menuShadowWidth: 5,
        optionFontSize: '14px',
        hiddenHoverBorder: 1,
        hiddenHoverLeftTruncation: 5,
        hiddenHoverZIndex: 5000,
        menuZIndex: 5001,
        addedLabelBuffer: 4
    },

    initialize: function( p ) {

        this.renderObj = this.column.renderObj;
        this.viewer = this.renderObj.viewer;

        this.nodeId = p.nodeId;
        this.nodeInfo = p.nodeInfo;

        this.makeCollapseUI();

        this.makeHiddenHover();
   
        this.makeLabel(); 
    
        this.makeMenu();

        return this;
    },

    makeCollapseUI: function() {

        this.collapseUI = this.column.canvas.path( this.nodeInfo.collapsed.pathString ).attr( {
            'stroke': this.viewer.config.collapsedCladeColor,
            'stroke-width': this.config.strokeWidth,
            'fill': this.viewer.config.collapsedCladeColor } );
    },

    makeHiddenHover: function() {

        var height = ( this.nodeInfo.collapsed.collapseUIHeightByTwo * 2 < this.renderObj.viewer.config.verticalTipBuffer.value )
            ? this.renderObj.viewer.config.verticalTipBuffer.value
            : this.nodeInfo.collapsed.collapseUIHeightByTwo * 2;

        var hoverWidth;
        var minimumWidth = this.viewer.config.minimumCollapsedUIWidth;
        var leftPos;

        if( this.nodeInfo.collapsed.branching == 'scaled' ) {

            hoverWidth = minimumWidth;

            leftPos = this.nodeInfo.x + this.viewer.config.scaledBranchingCollapseUIBuffer;

        } else {

            hoverWidth = -( this.nodeInfo.dx ) - this.config.hiddenHoverLeftTruncation;

            if( hoverWidth < minimumWidth ) { hoverWidth = minimumWidth; }

            leftPos = this.nodeInfo.x - hoverWidth;
        }

        this.hiddenHover = this.make('div').attr( { nodeId: this.nodeId } )
                .height( height - ( this.config.hiddenHoverBorder * 2 ) )
                .width( hoverWidth )
                .css( { top: this.nodeInfo.y - ( height / 2 ),
                        left: leftPos,
                        'position': 'absolute',
                        'z-index': this.config.hiddenHoverZIndex,
                        'white-space': 'nowrap',
                        'font-size': 'small' } )
                    .appendTo( this.column.svgDiv );
    
        this.bindHiddenHover();

        BioSync.Common.storeObjPosition( this.hiddenHover, this.hiddenHover );
    },

    makeLabel: function() {
  
        var xCoord = this.nodeInfo.x + this.viewer.config.tipLabelBuffer;

        if( this.nodeInfo.collapsed.branching == 'scaled' ) {

            xCoord += this.viewer.config.scaledBranchingCollapseUIBuffer + this.viewer.config.minimumCollapsedUIWidth;
        }

        this.text =
            this.column.canvas.text( xCoord, this.nodeInfo.y, this.nodeInfo.collapsed.text )
                .attr( { stroke: 'none',
                         fill: this.viewer.config.treeColor,
                         "font-family": this.viewer.config.fontFamily,
                         "font-size": this.viewer.config.fontSize.value,
                         "text-anchor": "start" } );

        // the text is only the node count when the collapsed node already has a label
        // here we move the collapsed node text ( node count ) next to the label already associated with the node
        if( this.nodeInfo.text ) {
            this.text.attr( { x: this.nodeInfo.raphaelLabel.getBBox().x + this.nodeInfo.raphaelLabel.getBBox().width + this.config.addedLabelBuffer } );
        }
    },
   
    makeMenu: function() { 

        var boxShadowText = [ "0 0 ", this.config.menuShadowWidth, "px ", this.config.menuShadowWidth, "px #888" ].join('');

        this.menu =
            this.make('div')
               .css( { 'top': -( this.nodeInfo.collapsed.collapseUIHeightByTwo ),
                       'left': this.hiddenHover.width(),
                       '-moz-box-shadow': boxShadowText,
                       '-webkit-box-shadow': boxShadowText,
                       'box-shadow': boxShadowText,
                       'background-color': 'white',
                       'font-size': '0.75em',
                       'text-align': 'center',
                       'z-index': this.config.menuZIndex,
                       'position': 'absolute',
                       '-moz-border-radius': '10px',
                       'border-radius': '10px',
                       'padding': '5px' } )
               .appendTo( this.hiddenHover );

        this.menu.attr( { 'topPos': this.menu.css('top'), 'leftPos': this.menu.css('left') } ).css( { top: -1000, left: -1000 } );
            
        this.menuHeader =
            this.make('div')
                .attr( { 'class': 'centerText' } )
                .text( this.nodeInfo.collapsed.text )
                .css( { 'font-size': 'medium',
                        'background-color': 'white',
                        'margin-bottom': '5px',
                        'border-bottom': '1px dotted black' } )
                .appendTo( this.menu );

        this.makeHorizontalOption();
        this.makeVerticalOption();

        //don't like this
        this.menu.width( this.menu.outerWidth( true ) + 25 ); 

        if( this.viewer.config.collapsedCladeSearchThreshold < this.nodeInfo.collapsed.descendantLabelCount ) {
            
            this.addSearchOption();

        } else {

            this.addDescendantLabelOption();
        }

        this.positionLabelList();

        this.makeHoverBridge();

        this.positionMenu();

        this.labelListWrapper.hide();

        this.menu.hide();
    },

    makeVerticalOption: function() {
    
        this.verticalOption =
            this.make('div').attr( { 'class': 'expandOption menuOptionItem' } )
                            .css( { 'padding': this.config.optionPadding,
                                    'background-color': 'white' } ).append(
                this.make('div').attr( { 'class': 'fLeft' } ).height( this.config.expandIconHeight ).width( this.config.expandIconWidth ).append(
                    this.make('div').attr( { 'class': 'vertExpandUI' } ) ),
                    this.make('div').attr( { 'class': 'fLeft' } ).text( 'Expand Vertically' ).css( { 'font-size': this.config.optionFontSize } ),
                    this.make('div').attr( { 'class': 'clear' } ) )
                  .bind( 'click', { }, $.proxy( this.hideMenu, this ) )
                  .bind( 'click', { }, $.proxy( this.expandVertical, this ) );

        this.menu.append( this.verticalOption );
    },

    makeHorizontalOption: function() {

        var data = ( this.nodeId != this.column.expandedNodeId ) ?
            { class: 'horiExpandUI', text: 'Expand Horizontally', handler: $.proxy( this.expandHorizontal, this ) } :
            { class: 'collapseUI', text: 'Collapse Clade', handler: $.proxy( this.collapseHorizontal, this ) };

        this.horizontalOptionIcon = this.make('div').attr( { 'class': data.class } );

        this.horizontalOptionText = this.make('div').attr( { 'class': 'fLeft optionText' } )
                                                    .text( data.text ).css( { 'font-size': this.config.optionFontSize } );

        this.horizontalOption =
            this.make('div').attr( { 'class': 'expandOption menuOptionItem' } )
                            .css( { 'padding': this.config.optionPadding,
                                    'background-color': 'white' } )
                            .bind( 'click', { }, $.proxy( this.hideMenu, this ) )
                            .bind( 'click', { }, data.handler ).append(
                this.make('div').attr( { 'class': 'fLeft' } )
                       .height( this.config.expandIconHeight )
                       .width( this.config.expandIconWidth ).append( this.horizontalOptionIcon ),
                this.horizontalOptionText,
                this.make('div').attr( { 'class': 'clear' } ) );

        this.menu.append( this.horizontalOption );
    },

    expandHorizontal: function() {

        this.column.horizontallyExpandNode( { bubbleUp: true, nodeId: this.nodeId } );
       
        this.horizontallyExpandNode();
    },

    horizontallyExpandNode: function() {
        
        this.expanded = true;

        this.horizontalOptionIcon.removeClass( 'horiExpandUI' ).addClass( 'collapseUI' );
        this.horizontalOptionText.text( 'Collapse Clade' );

        this.horizontalOption
            .unbind( 'click', $.proxy( this.expandHorizontal, this ) )
            .bind( 'click', { }, $.proxy( this.collapseHorizontal, this ) );

        this.addExpandStyleToHiddenHover();
    },

    collapseHorizontal: function() {

        this.column.collapseExpandedNode( { nodeId: this.nodeId } );
        
        this.expanded = false;

        this.horizontalOptionIcon.removeClass( 'collapseUI' ).addClass( 'horiExpandUI' );
        this.horizontalOptionText.text( 'Expand Horizontally' );

        this.horizontalOption
            .unbind( 'click', $.proxy( this.collapseHorizontal, this ) )
            .bind( 'click', { }, $.proxy( this.expandHorizontal, this ) );

        this.removeStyleFromHiddenHover();
    },

    expandVertical: function() {

        this.column.verticallyExpandNode( { nodeId: this.nodeId } );
    },

    showDescendantLabels: function() {

        document.body.style.cursor = 'default';

        this.descendantLabelsOption.css( { 'font-weight': 'bold', 'background-color': 'lightGrey' } );

        this.labelListWrapper.show();
        
        this.scrollForLabelList();
    },

    hideDescendantLabels: function() {
        
        this.descendantLabelsOption.css( { 'font-weight': 'normal', 'background-color': 'white' } );

        this.labelListWrapper.hide();
    },

    positionLabelList: function() {
        
        var menuOffset = this.menu.offset();

        var menuHeight = this.menu.outerHeight( true );
        var menuWidth = this.menu.outerWidth(true );

        this.labelListWrapper.css( { 'height': '', width: '' } );
        
        var labelListWrapperHeight = this.labelListWrapper.outerHeight( true );
        var labelListWrapperWidth = this.labelListWrapper.outerWidth( true );

        var labelListWrapperLeft = menuWidth + ( this.config.menuShadowWidth * 2 );
        var labelListWrapperTop = 0;
        
        var heightDiff = menuHeight - labelListWrapperHeight;

        if( heightDiff < 0 ) {

            this.labelListWrapper.height( this.menu.height() );
            this.labelListWrapper.width( this.labelListWrapper.outerWidth( true ) + BioSync.Common.scrollbarWidth );

        } else {

           labelListWrapperTop = heightDiff;
            this.labelListWrapper.css( { 'width': '' } );
        }
        
        this.labelListWrapper.css( { top: labelListWrapperTop, left: labelListWrapperLeft } );

        if( this.nextPage ) {

            //not good ( hard coding 5 )
            this.nextPage.css( { 'left': this.labelList.width() - this.nextPage.outerWidth( true ) - ( BioSync.Common.scrollbarWidth * 2 ), 'top': 5 } )
                .appendTo( this.labelListHeader );
        }

        if( this.prevPage ) {

            //not good ( hard coding 5 )
            this.prevPage.css( { 'left': BioSync.Common.scrollbarWidth, 'top': 5 } )
                .appendTo( this.labelListHeader );
        }
    },

    makeHoverBridge: function() {

        var descendantOptionWidth = this.descendantOption.width(); 
        var hoverBridgeWidth = ( parseInt( this.labelListWrapper.css('left') ) + ( this.config.menuShadowWidth * 2 ) ) - descendantOptionWidth;

        this.hoverBridge =
            this.make('div')
                .attr( { 'class': 'hoverBridge' } )
                .css( { top: 0, left: descendantOptionWidth } )
                .height( this.menu.outerHeight( true ) )
                .width( hoverBridgeWidth )
                .appendTo( this.descendantOption );
    },

    handleLabelMouseOver: function() {

        $(this).css( { 'background-color': 'lightGrey' } );
        document.body.style.cursor = 'pointer';
    },
    
    handleLabelMouseOut: function() {

        $(this).css( { 'background-color': 'white' } );
        document.body.style.cursor = 'default';
    },

    addLabelToList: function( p ) {

        this.labelList.append(
            this.make('div')
                .css( { 'padding': '1px 5px 1px 3px', 'text-align': 'left' } )
                .text( p.text )
                .hover( this.handleLabelMouseOver, this.handleLabelMouseOut )
                .bind( 'click', { nodeId: p.id, next: p.next, back: p.back }, $.proxy( this.handleDescendantLabelClick, this ) ) );
    },

    handleDescendantLabelClick: function( p ) {

       this.hideMenu();
       
       this.renderObj.navigateToNode( p.data );
    },
            
    addDescendantLabelOption: function() {

        this.descendantLabelsOption =
            this.make( 'div' )
                .css( { 'padding': this.config.optionPadding,
                        'background-color': 'white',
                        'z-index': this.config.menuZIndex,
                        'font-size': this.config.optionFontSize } )
                .text( 'View Descendant Labels >' )
                .hoverIntent( $.proxy( this.showDescendantLabels, this), $.proxy( this.hideDescendantLabels, this ) )
                .appendTo( this.menu );

        this.descendantOption = this.descendantLabelsOption;

        this.makeLabelList();

        for( var i = 0, ii = this.nodeInfo.collapsed.descendantLabels.length; i < ii; i++ ) {

            var info = this.nodeInfo.collapsed.descendantLabels[i];

            this.addLabelToList( { text: info.text, id: info.nodeId, next: info.next, back: info.back } );
        }
    },

    handleKeyUp: function( e ) {

        //enter
        if( e.keyCode == 13 ) {

        //down arrow
        } else if( e.keyCode == 40 ) {

        //up arrow
        } else if( e.keyCode == 38 ) {
            
        //letter 
        } else if( e.keyCode == 8 || e.keyCode == 46 || String.fromCharCode( e.keyCode ).match( /\w/ ) ) {

            if( this.userInputTimeout ) { clearTimeout( this.userInputTimeout ); }

            this.userInputTimeout = setTimeout( $.proxy( this.getMatchingLabels, this ), 500 );
        }
    },

    getMatchingLabels: function() {

        if( $.trim( this.searchInput.val() ) != '' ) {

            this.descendantLabelPage = 1;

            this.makeSearchRequest();
        
        } else {

            this.labelListWrapper.hide();
            this.labelList.empty();
        }
        
    },

    makeSearchRequest: function() {

        $.ajax( { url: BioSync.Common.makeUrl( { controller: 'plugin_treeViewer', argList: [ 'getMatchingDescendantLabels' ] } ),
                      type: "GET",
                      data: { next: this.nodeInfo.next, back: this.nodeInfo.back, value: this.searchInput.val(), page: this.descendantLabelPage },
                      success: $.proxy( this.handleMatchingLabels, this ) } );

    },

    nextPageClick: function() {

        this.descendantLabelPage++;

        this.makeSearchRequest();
    },

    prevPageClick: function() {

        this.descendantLabelPage--;

        this.makeSearchRequest();
    },

    handleMatchingLabels: function( response ) {

        this.labelList.empty();
        this.nextPage = this.prevPage = undefined;

        if( this.searchInput.is(':hidden') ) { return; }
            
        var returnValue = eval( '(' + response + ')' );

        var matchingLabels = returnValue.rows;
        var totalMatched = returnValue.total;

        if( ! matchingLabels.length ) {

            this.labelList.append(
                this.make('div')
                    .css( { 'padding': '1px 5px 1px 3px', 'text-align': 'left', 'font-weight': 'bold' } )
                    .text( 'No Matching Descendant Labels Found' ) );
        } else {

            var text;

            if( totalMatched > matchingLabels.length ) {

                var start = ( ( this.descendantLabelPage - 1 ) * this.viewer.config.collapsedCladeSearchPageLength ) + 1;
                var end = this.descendantLabelPage * this.viewer.config.collapsedCladeSearchPageLength;
                if( end > totalMatched ) { end = totalMatched; }

                text = [ start, ' - ', end ].join('');

                if( end < totalMatched ) {

                    this.nextPage = this.make('div')
                        .text( '>' )
                        .hover( this.handlePageArrowHover, this.handlePageArrowOut )
                        .css( { 'position': 'absolute','font-weight': 'bold' } )
                        .bind( 'click', { }, $.proxy( this.nextPageClick, this ) );
                }

                if( this.descendantLabelPage > 1 ) {

                    this.prevPage = this.make('div')
                        .text( '<' )
                        .hover( this.handlePageArrowHover, this.handlePageArrowOut )
                        .css( { 'position': 'absolute','font-weight': 'bold' } )
                        .bind( 'click', { }, $.proxy( this.prevPageClick, this ) );
                }

            } else {

                text = matchingLabels.length;
            }

            this.labelListHeader = 
                this.make('div').append(
                    this.make('span')
                    .css( { 'padding-top': '1px',
                            'padding-left': BioSync.Common.scrollbarWidth * 2,
                            'padding-right': BioSync.Common.scrollbarWidth * 2,
                            'padding-bottom': '3px',
                            'text-align': 'center',
                            'font-weight': 'bold' } )
                    .text( [ text, ' of ', totalMatched, ' Descendant Labels Found' ].join('') ) );

            this.labelList.append( this.labelListHeader );
        }

        for( var i = 0, ii = matchingLabels.length; i < ii; i++ ) {

            var row = matchingLabels[i];

            var id = row[0];
            var label = row[1].replace( '_', ' ' );
            var taxon = row[2];

            var text = ( taxon == label )
                ? label
                : ( ( taxon ) && ( label ) )
                    ? [ 'Taxon: ', taxon, ' Label: ', label ].join('')
                    : ( taxon )
                        ? taxon
                        : label;

            this.addLabelToList( { text: text, id: id, next: row[3], back: row[4] } );
        }

        this.labelListWrapper.show();

        this.positionLabelList();

        this.scrollForLabelList();
    },

    handlePageArrowHover: function() {

        $(this).css( { 'text-decoration': 'underline' } );
        document.body.style.cursor = 'pointer';
    },
    
    handlePageArrowOut: function() {
        
        $(this).css( { 'text-decoration': '' } );
        document.body.style.cursor = 'default';
    },

    scrollForLabelList: function() {

        var labelListOffset = this.labelListWrapper.offset();
        var viewPanelOffset = this.renderObj.viewPanel.offset();
        
        var viewPanelWidthAdjustment = ( this.renderObj.hasVerticalScrollbar() ) ? BioSync.Common.scrollbarWidth : 0;
        var labelListWidthAdjustment = ( this.labelListWrapper.outerHeight( true ) + 5 > this.menu.outerHeight( true ) ) ? BioSync.Common.scrollbarWidth : 0;

        var horiDifference = ( labelListOffset.left + this.labelListWrapper.outerWidth( true ) + ( this.config.menuShadowWidth * 2 ) + labelListWidthAdjustment ) -
                             ( viewPanelOffset.left + this.renderObj.viewPanel.outerWidth( true ) - viewPanelWidthAdjustment );
        

        if( horiDifference > 0 ) {
            this.renderObj.viewPanel.animate( { scrollLeft: '+=' + horiDifference }, 750 );
        }
    },

    addSearchOption: function() {
    
        this.searchInput =
            this.make( 'input' )
                .attr( { 'type': 'text' } )
                .width( this.config.searchInputWidth )
                .bind( 'keyup', { }, $.proxy( this.handleKeyUp, this ) )
                .val( [ 'search descendant taxa (', this.nodeInfo.collapsed.descendantLabelCount, ')' ].join('') );

        BioSync.Common.removeTextFirstFocus( { el: this.searchInput } );

        this.searchContainer =
            this.make( 'div' )
                .attr( { 'class': '' } ).append( this.searchInput )
                .css( { 'padding': this.config.optionPadding } )
                .appendTo( this.menu );

        this.descendantOption = this.searchContainer;

        this.makeLabelList();
    },

    makeLabelList: function() {
        
        var boxShadowText = [ "0 0 ", this.config.menuShadowWidth, "px ", this.config.menuShadowWidth, "px #888" ].join('');

        this.labelListWrapper =
            this.make('div')
                .attr( { 'class': 'labelListWrapper' } )
                .css( { "-moz-box-shadow":  boxShadowText, "-webkit-box-shadow": boxShadowText, "box-shadow": boxShadowText,
                        'font-weight': 'normal', 'background-color': 'white' } )
                .width( '100%' )
                .appendTo( this.descendantOption );
        
        this.labelList =
            this.make('div')
                .attr( { 'class': 'descendantList' } )
                .width( '100%' ).height( '100%' )
                .appendTo( this.labelListWrapper );
    },

    positionMenu: function() {

        this.menu.css( { top: this.menu.attr('topPos'), left: this.menu.attr('leftPos') } );
    },

    nodePreviouslyExpanded: function() {

        this.expanded = true;

        this.horizontalOption
            .unbind( 'click', $.proxy( this.expandHorizontal, this ) )
            .bind( 'click', { }, $.proxy( this.collapseHorizontal, this ) );
        
        this.horizontalOptionIcon.removeClass( 'horiExpandUI' ).addClass( 'collapseUI' );
        this.horizontalOptionText.text( 'Collapse Clade' );
        
        this.addExpandStyleToHiddenHover();
    },

    addExpandStyleToHiddenHover: function() {

        this.hiddenHover.css( { 
            'box-shadow': '0 0 5px rgba(0, 0, 255, 1)',
            '-webkit-box-shadow': '0 0 5px rgba(0, 0, 255, 1)', 
            '-moz-box-shadow': '0 0 5px rgba(0, 0, 255, 1)',
            'border': [ this.config.hiddenHoverBorder, 'px solid rgba(0,0,255, 0.8)' ].join('')
        } );
    },

    removeStyleFromHiddenHover: function() {
        
        this.hiddenHover.css( { 
                'box-shadow': '',
                '-webkit-box-shadow': '',
                '-moz-box-shadow': '',
                'border': ''
            } );
    },

    showMenu: function() {
    
        if( ( BioSync.Common.isContextMenuVisible() ) ||
            ( this.column.isNodeNotifying ) ||
            ( this.column.isShowingCollapsedNodeDialogue() ) || 
            ( this.renderObj.isViewPanelVerticallyScrolling ) ||
            ( this.renderObj.isViewPanelHorizontallyScrolling ) ) { return; }
       
        this.addExpandStyleToHiddenHover();

        this.menu.show();
        this.isMenuVisible = true;

        var menuOffset = this.menu.offset();
        var viewPanelOffset = this.renderObj.viewPanel.offset();

        var viewPanelWidthAdjustment = ( this.renderObj.hasVerticalScrollbar() ) ? BioSync.Common.scrollbarWidth : 0;
        var viewPanelHeightAdjustment = ( this.renderObj.hasHorizontalScrollbar() ) ? BioSync.Common.scrollbarWidth : 0;

        var horiDifference = ( menuOffset.left + this.menu.outerWidth( true ) + ( this.config.menuShadowWidth * 2 ) ) -
                             ( viewPanelOffset.left + this.renderObj.viewPanel.outerWidth( true ) - viewPanelWidthAdjustment );
        
        var vertDifference = ( menuOffset.top + this.menu.outerHeight( true ) + ( this.config.menuShadowWidth * 2 ) ) -
                             ( viewPanelOffset.top + this.renderObj.viewPanel.height() - viewPanelHeightAdjustment );

        if( ( horiDifference > 0 ) && ( vertDifference > 0 ) ) {
            
            this.renderObj.scrollViewPanel( {
                left: [ '+=', horiDifference ].join(''),
                top: [ '+=', vertDifference ].join(''),
                time: 750 } );

        } else if( horiDifference > 0 ) {

            this.renderObj.scrollViewPanel( { left: [ '+=', horiDifference ].join(''), time: 750 } );

        } else if( vertDifference > 0 ) {
            
            this.renderObj.scrollViewPanel( { top: [ '+=', vertDifference ].join(''), time: 750 } );
        }
    },

    hideMenuIfNotVerticallyScrolling: function() {

        if( this.renderObj.isViewPanelVerticallyScrolling ) {

            $( document ).bind( 'click', { }, $.proxy( this.checkOutOfMenuClick, this ) );

        } else {

            this.hideMenu();
        }
    },

    hideMenu: function() {

        $( document ).unbind( 'click', { }, $.proxy( this.checkOutOfMenuClick, this ) );

        if( ! this.expanded ) { this.removeStyleFromHiddenHover(); }

        this.labelListWrapper.hide();

        if( this.viewer.config.collapsedCladeSearchThreshold < this.nodeInfo.collapsed.descendantLabelCount ) {
            this.labelList.empty();
        }

        if( this.searchInput ) {

            this.searchInput.val( [ 'search descendant taxa (', this.nodeInfo.collapsed.descendantLabelCount, ')' ].join('') ).blur();

            BioSync.Common.removeTextFirstFocus( { el: this.searchInput } );
        }

        this.menu.hide();

        this.isMenuVisible = false;

        this.unbindHiddenHoverUntilMouseMove();
    },

    unbindHiddenHoverUntilMouseMove: function() {
        
        this.hiddenHover.unbind('mouseenter')
                        .unbind('mouseleave')
                        .removeProp('hoverIntent_t')
                        .removeProp('hoverIntent_s');

        $( document ).bind( 'mousemove', { }, $.proxy( this.bindHiddenHover, this ) );
    },

    bindHiddenHover: function() {
                        
        this.hiddenHover
            .hoverIntent( { interval: 200, 
                            over: $.proxy( this.showMenu, this ),
                            out: $.proxy( this.hideMenuIfNotVerticallyScrolling, this ) } );
    },

    checkOutOfMenuClick: function( e ) {

        if( this.renderObj.isViewPanelVerticallyScrolling ) { return; }

        if( ! BioSync.Common.isMouseOnElement( { x: e.pageX, y: e.pageY, el: this.menu } ) ) {

            this.hideMenu();
        }
        
    }
}
