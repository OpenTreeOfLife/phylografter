BioSync.TreeViewer.Sidebar.phylogram.navigate.prototype = {

    config: { verticalSpacing: 5,
              borderOffset: 2,
              headerWidth: 200,
              hideTimeout: 1000 },

    initialize: function() {

        this.panels = { };
        this.panelArray = [ ];

        this.scrollbarOffset = ( this.viewer.renderObj.hasVerticalScrollbar() ) ? BioSync.Common.scrollbarWidth : 0;
             
        return this;
    },

    addPanel: function( p ) {
        
        this.panels[ p.id ] = { };

        var header = this.make('div').attr( { 'class': 'panelHeader' } )
            .hoverIntent( this.showCloseButton, this.hideCloseButton );

        var name =  this.make('div').attr( { 'class': 'panelName' } ).text( p.name );

        var closeButton = this.make('div').attr( { 'class': 'panelClose' } )
                    .text('x')
                    .bind( 'click', { }, $.proxy( this.viewer.controlPanel.toggleCheck, $( [ '.controlPanelItemLabel[name="', p.name, '"]' ].join('') ).parent() ) );

        var content = this.make( 'div' ).attr( { 'class': 'panelContent' } ).append( p.content ).hide();

        var container =
            this.make('div').attr( { 'id': p.id, 'class': 'panelContainer' } ).append(
                header.append( name, closeButton, this.make('div').attr( { 'class': 'clear' } ) ),
                content );

        this.viewer.container.append( container );

        var top = this.determineTopPosition( this.panelArray.length );

        var viewPanelWidth = this.viewer.renderObj.viewPanel.width();
        if( this.hidingPanelContent ) { viewPanelWidth = this.viewPanelWidth; }
        var left =  viewPanelWidth - container.outerWidth( true ) - this.config.borderOffset - this.scrollbarOffset;

        container.css( { 'top': top, 'left': left } );
        
        this.viewer.controlPanel.addViewOption( { name: p.name } );

        this.panels[ p.id ] = { header: header, name: name, closeButton: closeButton, container: container, content: content, id: p.id, sidebarObj: this };
        this.panelArray.push( this.panels[ p.id ] );
                    
        name.bind( 'click', { }, $.proxy( this.showPanel, this.panels[ p.id ] ) );
        closeButton.bind( 'click', { }, $.proxy( this.removePanel, this.panels[ p.id ] ) );

        return this;
    },

    determineTopPosition: function( index ) {

        if( index > 0 ) {
            
            return parseInt( $( $('.panelContainer')[ index - 1 ] ).css('top') ) + $( $('.panelHeader')[ index - 1 ] ).outerHeight( true ) + this.config.verticalSpacing;

        } else { 

            return this.config.verticalSpacing;
        }

    },

    showCloseButton: function() { $( this ).children('.panelClose').css( { 'color': 'blue' } ); },
    
    hideCloseButton: function() { $( this ).children('.panelClose').css( { 'color': 'white' } ); },

    removePanel: function() {

        if( this.content.is(':visible') ) {

            $.proxy( this.sidebarObj.hidePanelContent, this )();
            setTimeout( $.proxy( this.sidebarObj.hidePanel, this ), this.sidebarObj.config.hideTimeout );

        } else {

           $.proxy( this.sidebarObj.hidePanel, this )();
        }
    },

    hideAnyPanelContent: function() {

        var that = this;
            
        for( var i = 0, ii = this.panelArray.length; i < ii; i++ ) {

            if( this.panelArray[i].content.is(':visible') ) {
                that.hidingPanelContent = true;
                that.viewPanelWidth = this.viewer.renderObj.viewPanel.width() + 200;
                $.proxy( this.hidePanelContent, this.panelArray[i] )();
            }
        }

        setTimeout( function() { that.hidingPanelContent = false; }, this.config.hideTimeout );
    },

    hidePanel: function() { this.container.hide( 'slide', { direction: 'right' }, this.sidebarObj.config.hideTimeout ); },
        

    hidePanelContent: function() {

        var that = this;

        var viewPanelWidth = this.sidebarObj.viewer.renderObj.viewPanel.outerWidth( true );

        this.sidebarObj.viewer.renderObj.viewPanel.animate( { width: viewPanelWidth + that.sidebarObj.config.headerWidth }, that.sidebarObj.config.hideTimeout );
       
        this.name.css( { 'text-align': '', width: '', 'padding-left': '5px', 'padding-right': '5px' } );

        this.content.hide( 'slide', { direction: 'up' }, that.sidebarObj.config.hideTimeout, function() { 
            that.container.css( { 'width': '' } );
            that.container.animate( { left: viewPanelWidth + ( that.sidebarObj.config.headerWidth - that.sidebarObj.config.borderOffset ) - that.container.outerWidth( true ) - that.sidebarObj.scrollbarOffset }, that.sidebarObj.config.hideTimeout ); } );

        this.name.unbind( 'click' ).bind( 'click', { }, $.proxy( this.sidebarObj.showPanel, this ) ); 
       
        $( this.container.siblings( '.panelContainer[autoHide="true"]' ) ).each( function( i, el ) {

            $(this).attr( { 'autoHide': 'false' } );
            
            $.proxy( that.sidebarObj.showHeader, that.sidebarObj.panels[ $(this).attr('id') ] )();
        } );
    },

    showPanel: function() {

        var that = this;

        var viewPanel = this.sidebarObj.viewer.renderObj.viewPanel;

        var viewPanelWidth = viewPanel.width();

        viewPanel.animate( { width: viewPanelWidth - that.sidebarObj.config.headerWidth }, that.sidebarObj.config.hideTimeout );

        this.container.animate( { width: ( this.sidebarObj.config.headerWidth - this.sidebarObj.config.borderOffset ), left: viewPanelWidth - this.sidebarObj.config.headerWidth }, that.sidebarObj.config.hideTimeout, function() {

            that.content.show();
            
            var difference = ( that.content.offset().top + that.content.outerHeight( true ) ) -
                             ( viewPanel.offset().top + viewPanel.outerHeight( true ) );

            if( difference > 0 ) { that.content.height( that.content.height() - difference ); }
                
            that.name.css( { 'text-align': 'center',
                             'padding-left': '0px',
                             'padding-right': '0px' } ).width( that.header.outerWidth( true ) - that.closeButton.outerWidth( true ) );
        } );

        this.name.unbind( 'click' ).bind( 'click', { }, $.proxy( this.sidebarObj.hidePanelContent, this ) ); 

        $( $( this.container.siblings('.panelContainer').filter(':visible') ).attr( { 'autoHide': 'true' } ) ).each( function( i, el ) {

            $.proxy( that.sidebarObj.removePanel, that.sidebarObj.panels[ $(this).attr('id') ] )();

        } );
    },

    showHeader: function( ) {

        var that = this;
            
        this.container.show( 'slide', { direction: 'right' }, that.sidebarObj.config.hideTimeout, function() {
            $(this).css( { 'left': that.sidebarObj.viewer.renderObj.viewPanel.width() - $(this).outerWidth( true ) - that.sidebarObj.config.borderOffset - that.sidebarObj.scrollbarOffset } ); } );
    },

    updateHeaderCoords: function() {

        if( ( ! this.scrollbarOffset ) && this.viewer.renderObj.hasVerticalScrollbar() ) {
        
            this.scrollbarOffset = BioSync.Common.scrollbarWidth;

            for( var i = 0, ii = this.panelArray.length; i < ii; i++ ) {
               
                var panel = this.panelArray[i];

                if( panel.content.is(':hidden') ) {

                    var top = this.determineTopPosition( i );

                    panel.container.css( { 'top': top, 'left': this.viewer.myWidth - panel.container.outerWidth( true ) - this.scrollbarOffset } );
                }

            }
        }
    }
}
