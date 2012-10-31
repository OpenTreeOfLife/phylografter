BioSync.TreeViewer.ControlPanel.prototype = {

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
        }
    },

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

    addViewOption: function( p ) {

        var viewOption;

        if( ! this.panelContent.find(".controlPanelItemLabel:contains('view >')").length ) {

            viewOption =
                this.make('div').attr( { 'class': 'controlPanelItem' } ).append(
                    this.make('span').attr( { 'class': 'controlPanelItemLabel' } ).text( 'view > ' ) )
                        .hoverIntent( $.proxy( this.showChildHoverMenu, this ), $.proxy( this.hideChildHoverMenu, this ) );

            this.panelContent.append( viewOption );

        } else {

            viewOption = $( this.panelContent.children(":contains('view')") );
        }

        viewOption.append(
            this.make( 'div' ).attr( { 'class': 'controlPanelItem', 'check': 'true' } ).append(
                this.make( 'span' ).attr( { 'class': 'controlPanelItemLabel', 'name': p.name } ).html( [ p.name, ' ', BioSync.Common.htmlCodes.check ].join(' ') ) )
            .bind( 'click', { }, this.toggleCheck )
            .bind( 'click', { }, $.proxy( this.viewer.togglePanel, this.viewer ) ) );
    },

    toggleCheck: function() {

        var that = $(this);
        var label = $( that.children()[0] );

        if( that.attr('check') == 'true' ) {

            that.attr( { 'check': 'false' } );
            label.html( label.html().substring( 0, label.html().indexOf(' ') ) );

        } else { 
            
            that.attr( { 'check': 'true' } );
            label.html( [ label.html(), BioSync.Common.htmlCodes.check ].join(' ') );
        } 
    },

    showControlPanel: function() {

        this.panelButtonLabel.css( { 'font-weight': 'bold' } );

        this.optionContainer.show();
    },
    
    hideControlPanel: function( ) {

        this.panelButtonLabel.css( { 'font-weight': 'normal' } );

        this.optionContainer.hide();
    },

    updateMaxTips: function() {

        if( this.optionObjs.treeSize ) {

            this.optionObjs.treeSize.updateMaxTips();
        }
    },

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

        this.optionContainer.hide();
    },

    //not being used (zoom)
    ratioChange: function( e, ui ) {

        var scaleRatio = ui.value / this.baseRatio;
        this.baseRatio = ui.value;

        //this.viewer.renderObj.changeTreeSize( { ratio: this.viewer.renderObj.scaleRatio } );

        var config = this.viewer.config;

        var ajaxNames = [ 'fontSize', 'scaleRatio', 'branchLength', 'horizontalPadding', 'verticalPadding', 'tipLabelBuffer', 'verticalTipBuffer' ];
        var ajaxValues = [  ];

        for( var i = 0, ii = ajaxNames.length; i < ii; i++ ) {

            var name = ajaxNames[i];
            config[ name ] = config[ name ] * scaleRatio;
            ajaxValues.push( config[ name ] );
        }

        BioSync.Common.style.fontSize = config.fontSize;
        BioSync.Common.setTextWidthMetric();

        this.viewer.updateConfig( { names: ajaxNames, values: ajaxValues, redraw: true } );
    },

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

        return [ container, label ];
    }
}


BioSync.TreeViewer.ControlPanel.prototype.options.treeSize.prototype = {

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
                    .bind( 'keyup', option, $.proxy( this.handleValueChange, this ) );

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

    handleValueChange: function( e ) {

        if( e.data.userInputTimeout ) { clearTimeout( e.data.userInputTimeout ); }

        e.data.userInputTimeout = setTimeout( $.proxy( this.updateValue, e.data ), this.config.valueChangeTimeout );
    },

    updateValue: function() { this.slider.slider( 'option', 'value', this.valueBox.val() ); },
    
    handleMouseOverOptionList: function( e ) {
    },
    
    handleMouseOutOfOptionList: function( e ) {

        if( ( ! BioSync.Common.isMouseOnElement( { x: e.pageX, y: e.pageY, el: this.container } ) ) ) {
            
            this.hideOption();
        }
    },

    updateMaxTips: function() {

        var optionObj = this.config.options.maxTips;

        optionObj.slider.unbind( 'slidechange' );

        optionObj.slider.slider( 'option', 'value', this.controlPanel.viewer.config.maxTips.value );

        optionObj.valueBox.val( this.controlPanel.viewer.config.maxTips.value );
                                       
        optionObj.slider.bind(
            'slidechange', { name: 'maxTips' }, ( optionObj.handleOnChange ) ? $.proxy( this[ optionObj.handleOnChange ], this ) : $.proxy( this.updateConfig, this ) );
    },

    updateConfig: function( e, ui ) {

        if( this.controlPanel.viewer.config[ e.data.name ].value != ui.value ) {
        
            this.controlPanel.viewer.updateConfig( { names: [ e.data.name ], values: [ ui.value ], redraw: true } );
        }
    },

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
    
    updateFontSize: function( e, ui ) {
         
        BioSync.Common.style.fontSize = ui.value;
        BioSync.Common.setTextWidthMetric();

        this.updateConfig( e, ui );        
    },

    handleSlide: function( e, ui ) { this.val( ui.value ); },

    handleMouseOutOfContainer: function( e ) {

        if( ( ! BioSync.Common.isMouseOnElement( { x: e.pageX, y: e.pageY, el: this.sizingOptionsContainer } ) ) ) {
            
            this.hideOption();
        }
    },

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

    hideOption: function() {

        this.label.css( { 'background-color': 'white' } );
        
        this.sizingOptionsContainer.hide();
       
        this.controlPanel.optionContainer.css( { 'width': '', 'height': '' } );
    }

}

BioSync.TreeViewer.ControlPanel.prototype.options.branchLength.prototype = {

    config: {

        padding: 5    
    },

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
        }

        return this;
    },

    handleMouseOutOfSelectionContainer: function( e ) {

        if( ( ! BioSync.Common.isMouseOnElement( { x: e.pageX, y: e.pageY, el: this.container } ) ) ) {
            
            this.hideOption();
        }
    },

    handleMouseOverContainer: function( e ) {

        this.label.css( { 'background-color': 'lightGrey' } );

        this.selectionContainer.show();

        this.controlPanel.optionContainer.width(
            this.label.outerWidth( true ) +
            this.selectionContainer.outerWidth( true ) + 
            this.controlPanel.config.optionContainerLeftBuffer );
    },

    handleMouseOutOfContainer: function( e ) {
        
        if( ( ! BioSync.Common.isMouseOnElement( { x: e.pageX, y: e.pageY, el: this.selectionContainer } ) ) ) {
            
            this.hideOption();
        }
    },

    hideOption: function( e ) {

        this.label.css( { 'background-color': 'white' } );
        
        this.selectionContainer.hide();
       
        this.controlPanel.optionContainer.css( { 'width': '' } );
    },

    handleSmoothClick: function() {

        if( this.branchLengthStyle == 'smooth' ) { return; }

        this.branchLengthStyle = 'smooth';

        this.smoothSpan.html( [ 'smooth', BioSync.Common.htmlCodes.check ].join( ' ' ) );
        this.scaleSpan.html('scale');
        
        this.controlPanel.viewer.renderObj.updateBranchLength( this.branchLengthStyle );
    },

    handleScaledClick: function() {

        if( this.branchLengthStyle == 'scale' ) { return; }

        this.branchLengthStyle = 'scale';

        this.scaleSpan.html( [ 'scale', BioSync.Common.htmlCodes.check ].join( ' ' ) );
        this.smoothSpan.html('smooth');
        
        this.controlPanel.viewer.renderObj.updateBranchLength( this.branchLengthStyle );
    }
}


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

    handleMouseOverContainer: function() {

       this.searchLabel.css( { 'background-color': 'lightGrey' } );

       this.searchContainer.show();

       this.controlPanel.optionContainer.width(
        this.searchLabel.outerWidth( true ) +
        this.searchContainer.outerWidth( true ) + 
        this.controlPanel.config.optionContainerLeftBuffer );
    },

    handleMouseOutOfContainer: function() {

       this.searchLabel.css( { 'background-color': 'white' } );
       
       this.searchContainer.hide();
       
       this.controlPanel.optionContainer.css( { 'width': '' } );
    },

    handleMouseOutOfSearch: function( e ) {

        if( ( ! BioSync.Common.isMouseOnElement( { x: e.pageX, y: e.pageY, el: this.container } ) ) ) {

            this.resetElements();
            this.searchInput.val('label or taxon').blur();
            BioSync.Common.removeTextFirstFocus( { el: this.searchInput } );
        }
    },

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

    setSearchHover: function() {
        
        $('.searchResult').unbind( 'mouseenter mouseleave' ).hover( $.proxy( this.searchResultHoverIn, this ), $.proxy( this.searchResultHoverOut, this ) );
    },

    searchResultHoverIn: function( e ) {

        this.unStyleCurrentlySelected();
        this.currentlySelected = $( e.target );
        this.styleCurrentlySelected();
    },

    searchResultHoverOut: function( e ) {

        this.unStyleCurrentlySelected();
    },

    handleSearchAutoScroll: function( p ) {

        //scrolling makes the mouse move
        $(document).unbind('mousemove');

        //scroll and on success function
        this.matchingLabelList.animate( { scrollTop: '+=' + p.scroll }, 250, 'linear', $.proxy( this.setSearchMouseMove, this ) );
    },

    setSearchMouseMove: function() {

        $( document ).bind( 'mousemove', { }, $.proxy( this.handleMouseMoveInSearch, this ) );
    },

    handleMouseMoveInSearch: function() {

        this.matchingLabelList.removeClass('noCursor');

        this.setSearchHover();
    },

    styleCurrentlySelected: function() {

        this.currentlySelected.css( {
            'background-color': '#EAEAEA' } );
    },

    unStyleCurrentlySelected: function( p ) {

        if( this.currentlySelected ) {
            this.currentlySelected.css( {
                'background-color': 'white' } );
        }
    },

    handleKeyUp: function( e ) {

        var that = this;
        //enter
        if( e.keyCode == 13 ) {

            this.currentlySelected.click();

        //down arrow
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
            
        //up arrow
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
           
        //letter 
        } else if( e.keyCode == 8 || e.keyCode == 46 || String.fromCharCode( e.keyCode ).match( /\w/ ) ) {

            if( this.userInputTimeout ) { clearTimeout( this.userInputTimeout ); }

            this.userInputTimeout = setTimeout( $.proxy( this.getMatchingLabels, this ), 500 );
        }
    },
   
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

    makeSearchRequest: function() {

        $.ajax( { url: BioSync.Common.makeUrl( { controller: 'plugin_treeViewer', argList: [ 'getMatchingDescendantLabels' ] } ),
                  type: "GET", data: { value: this.searchInput.val(), next: 1, page: this.labelPage }, success: $.proxy( this.handleMatchingLabels, this ) } );
    },

    labelSelected: function( e ) {

        var el = $( $( e.target ).closest( "[nodeId]" ) );

        this.controlPanel.viewer.renderObj.navigateToNode( { nodeId: el.attr('nodeId'), next: el.attr('next'), back: el.attr('back') } );
        this.controlPanel.viewer.controlPanel.hideControlPanel();
    },

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

    sizeElementsAfterSearch: function() {
        
        if( this.matchingLabelList.outerHeight( true ) > parseInt( this.config.labelListMaxHeight ) ) {
            this.matchingLabelList.width( this.matchingLabelList.outerWidth( true ) + BioSync.Common.scrollbarWidth );
        }

        this.searchContainer.width( this.matchingLabelList.outerWidth( true ) );

        this.alignSearchWithLabelList();

        this.setOptionContainerHeight();
        this.setOptionContainerWidth(); 
    },

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

    setOptionContainerWidth: function() {

        this.controlPanel.optionContainer.width(
            this.searchLabel.outerWidth( true ) +
            this.config.pixelsBetweenLabelAndSearch +
            this.searchContainer.outerWidth( true ) );
    },
        
    alignSearchWithLabelList: function() {

        var offset = ( this.config.searchInputPadding * 2 ) +
            ( this.config.searchInputBorderWidth * 2 );

        var width = this.matchingLabelList.outerWidth( true ) - offset;

        this.searchInput.width( width );
        this.hoverBridge.width( width );
    },

    alignSearchWithContainer: function() {

        var width = this.searchContainer.outerWidth( true ) - this.config.searchInputMarginRight;
        this.searchInput.width( width );
        this.hoverBridge.width( width );
    },

    resetElements: function() {

        this.currentlySelected = undefined;
        this.matchingLabelList.empty().show().css( { 'height': '', 'width': '' } );
        this.searchContainer.width( this.config.initialSearchContainerWidth );
        this.alignSearchWithContainer();
        this.controlPanel.optionContainer.css( { 'height': '', 'width': '' } );
        this.nextPageButton = this.prevPageButton = undefined;
    },

    nextPageClick: function() {

        this.labelPage++;

        this.makeSearchRequest();
    },

    prevPageClick: function() {

        this.labelPage--;

        this.makeSearchRequest();
    },
}
