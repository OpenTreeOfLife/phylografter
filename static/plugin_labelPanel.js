BioSync.LabelPanel = {

    instances: { },

    handleExpandNode: function( p, q ) {

        var instances = BioSync.LabelPanel.instances;

        for( var containerId in instances ) {

            instances[ containerId ].handleExpandNode( { viewer: q.viewer } );
            
        }
    },

    recentTextInput: function( p ) {
        p.instance.setRecentTextInput();
    },

    events: {
    }

            

};
                
$(document).bind( 'expandNode', { }, BioSync.LabelPanel.handleExpandNode ); 

BioSync.LabelPanel.labelPanel = function( p ) { 

    BioSync.LabelPanel.instances[ p.containerId ] = this;
    
    this.containerId = p.containerId;    
    this.labelDivs = { };

    this.container =
        $('#' + p.containerId).addClass('labelPanelContainer')
                              .bind( 'keyup', { labelPanel: this }, this.handleKeyUp );
    
    this.events = p.eventInfo;

    var make = BioSync.Common.makeEl;

    this.input =
        make('input').attr( { 'id': p.containerId + 'input',
                              'type': 'text',
                              'value': 'search for a label',
                              'class': 'labelSearchInput initialLabelInput' } )
                     .bind( 'focus', { labelPanel: this }, this.firstInputFocus );

   
    this.header = make('div').attr( { 'class': 'labelPanelHeader' } ).append(
        make('div').attr( { 'class': 'labelOptionsContainer' } ),
        make('div').attr( { 'class': 'labelSearchContainer' } ).append( this.input ),
        make('div').attr( { 'class': 'clear' } ) );

    this.labelListContainer = make('div').attr( { 'class': 'labelListContainer extend' } );
    
    this.container.append( this.header, this.labelListContainer );

    this.optionMenu =
        BioSync.Common.makeHoverOptionMenu( {
            container: $( this.header.find('div.labelOptionsContainer')[0] ),
            text: '>',
            options: [ { text: 'Sort Alphabetically',
                         funcParams: { labelPanel: this },
                         func: this.sortAlphabetically } ] } );

    this.textInput = $( this.container.find('input.labelSearchInput') );
    this.labelSearchContainer = $( this.container.find( 'div.labelSearchContainer' ) );

    this.labelListContainer.height( this.container.outerHeight( true ) - this.labelSearchContainer.outerHeight( true ) );

    if( this.container.closest('treeViewerContainer') ) {
        this.treeViewer = BioSync.TreeViewer.instances[ $( this.container.closest('.treeViewerContainer') ).attr('id') ];
        this.initialize( { treeViewer: this.treeViewer } );
    } else {
        this.addNoLabelIndicator();
    }
};


BioSync.LabelPanel.labelPanel.prototype = {

    initialize: function( p ) {
        this.removeLabels();
        this.labelDivs = { }; this.labels = [ ];
        this.createLabels( { labelPanel: this, treeViewer: p.treeViewer } );
    },

    sortAlphabetically: function( p ) {
      
        var labelPanel = p.data.labelPanel;

        var newOrder =
            labelPanel.labelListContainer.find('.labelPanelListItem').sort( labelPanel.alphabetizeLabels );

        labelPanel.removeLabels();

        labelPanel.labelListContainer.append( newOrder );
        
        $.each( newOrder, function() { $(this).bind( 'mouseover', { thisPanel: labelPanel }, labelPanel.addHoverClass )
                                              .mouseout( labelPanel.removeHoverClass ); } )
                                              .bind( 'click', { labelPanel: labelPanel }, labelPanel.handleLabelClick );

        labelPanel.updateSortOptionToTopo();
    },

    alphabetizeLabels: function( a, b ) { return ( $(a).text() > $(b).text() ) ? 1 : -1; },
    topologicalizeLabels: function( a, b ) { return ( parseInt( $(a).attr('next') ) > parseInt( $(b).attr('next') ) ) ? 1 : -1; },

    removeLabels: function() {
        this.labelListContainer.empty();
    },

    updateSortOptionToTopo: function() {

        var labelPanel = this;

        labelPanel.optionMenu.find('.menuOptionItem:contains("Sort Alphabetically")')
            .text('Sort Topologically')
            .unbind('click')
            .bind('click', { labelPanel: labelPanel }, labelPanel.sortTopologically );
    },

    updateSortOptionToAlpha: function() {

        var labelPanel = this;

        labelPanel.optionMenu.find('.menuOptionItem:contains("Sort Topologically")')
            .text('Sort Alphabetically')
            .unbind('click')
            .bind('click', { labelPanel: labelPanel }, labelPanel.sortAlphabetically );
    },

    sortTopologically: function( p ) {

        var labelPanel = p.data.labelPanel;

        var newOrder =
            labelPanel.labelListContainer.find('.labelPanelListItem').sort( labelPanel.topologicalizeLabels );

        labelPanel.removeLabels();

        labelPanel.labelListContainer.append( newOrder );
        
        $.each( newOrder, function() { $(this).bind( 'mouseover', { thisPanel: labelPanel }, labelPanel.addHoverClass )
                                              .mouseout( labelPanel.removeHoverClass ); } )
                                              .bind( 'click', { labelPanel: labelPanel }, labelPanel.handleLabelClick );

        labelPanel.updateSortOptionToAlpha();
    },
    
    addNoLabelIndicator: function() {

        this.labelListContainer.append( BioSync.Common.makeEl('div').attr( { 'class': 'noLabels centerText' } ).text('No Labels') );
    },

    removeNoLabelIndicator: function() {
        this.container.find('div.noLabels').empty().remove();
    },

    firstInputFocus: function( p ) {
       
        p.data.labelPanel.textInput.val('').removeClass('initialLabelInput').unbind('focus'); 
    },

    addHoverClass: function( p ) {
        if( p.data.thisPanel.recentTextInput ) { return; }
        $( p.target ).siblings('.labelPanelListItemHighlighted').removeClass('labelPanelListItemHighlighted');
        $( p.target ).addClass('labelPanelListItemHighlighted');
    },
    
    removeHoverClass: function( p ) {
        $( p.target ).removeClass('labelPanelListItemHighlighted');
    },

    handleExpandNode: function( p ) {

        var labelPanel = this;
        var treeViewer = p.viewer;

        var selectedLabel = labelPanel.container.find('.labelPanelListItemSelected');

        if( selectedLabel.length ) {
            
            var nodeId = $(selectedLabel[0]).attr('nodeId');
            var found = false;

            for( var i = 0, ii = treeViewer.columns.length; i < ii; i++ ) {
               
                var curColumn = treeViewer.columns[i];

                if( curColumn.nodeInfo[ nodeId ] ) { found = true; break; }
            }

            if( !found ) { selectedLabel.removeClass('labelPanelListItemSelected'); }
        }
    },

    handleLabelClick: function( p ) {

        var clickedDiv = $( p.target );
        var labelPanel = p.data.labelPanel;

        if( clickedDiv.hasClass('labelPanelListItemSelected') ) {

            clickedDiv.removeClass('labelPanelListItemSelected');
            labelPanel.treeViewer.renderUtil.unNavigateToNode( { viewer: labelPanel.treeViewer, nodeId: clickedDiv.attr('nodeId') } );

        } else {

            var currentlySelected = $( labelPanel.container.find('.labelPanelListItemSelected') );

            if( currentlySelected.length ) {

                currentlySelected.removeClass('labelPanelListItemSelected');

                labelPanel.treeViewer.renderUtil.unNavigateToNode( { viewer: labelPanel.treeViewer, nodeId: currentlySelected.attr('nodeId') } );

            }
           
            clickedDiv.addClass('labelPanelListItemSelected');
        
            labelPanel.treeViewer.renderUtil.navigateToNode( {
                viewer: labelPanel.treeViewer,
                nodeId: clickedDiv.attr('nodeId'),
                next: clickedDiv.attr('next') } );
        }

    },

    handleCreateLabelsResponse: function( response ) {

        var labelPanel = this;
        labelPanel.labelInfo = eval( "(" + response + ")" );
        var labelInfo = labelPanel.labelInfo;

        var make = BioSync.Common.makeEl;

        for( var nodeId in labelPanel.labelInfo ) {

            var labelText = labelInfo[ nodeId ].label;

            var labelDiv = make('div').attr( { 'class': 'labelPanelListItem', 'nodeId': nodeId, 'next': labelInfo[ nodeId ].next } )
                                      .text( labelText )
                                      .bind( 'mouseover', { thisPanel: labelPanel }, labelPanel.addHoverClass )
                                      .mouseout( this.removeHoverClass );
                
            labelDiv.bind( 'click', { labelPanel: this }, this.handleLabelClick );

            this.labelDivs[ nodeId ] = labelDiv;

            this.labels.push( labelText );

            this.labelListContainer.append( labelDiv );
        }
    },

    createLabels: function( p ) {

        $.ajax( { url: BioSync.Common.makeUrl( { controller: 'plugin_labelPanel', argList: [ 'getTreeLabels' ] } ),
                 type: "GET",
                 context: p.labelPanel,
                 data: { treeId: p.treeViewer.treeId,
                         treeType: p.treeViewer.treeType },
                 success: p.labelPanel.handleCreateLabelsResponse } );
    },

    setRecentTextInput: function() {
        this.recentTextInput = false;
    },

    handleKeyUp: function( p ) {

        var thisPanel = p.data.labelPanel;
        
        var listItems = thisPanel.labelListContainer.children('div');
        
        var visibleListItems = listItems.filter(':visible');

        var selectedListItem = $( listItems.filter('.labelPanelListItemHighlighted') );

        if( p.keyCode == 13 && selectedListItem.length ) {

            thisPanel.handleLabelClick( { target: selectedListItem.get(0), data: { labelPanel: thisPanel } } );

        } else if( p.keyCode == 40 ) {

            var elToHighlight;

            if( selectedListItem.length ) {
            
                if( selectedListItem.get(0) == visibleListItems[ visibleListItems.length - 1 ] ) { return; }

                selectedListItem.removeClass('labelPanelListItemHighlighted');

                elToHighlight = selectedListItem.next();

                while( elToHighlight.is(':hidden') ) {
                    elToHighlight = elToHighlight.next();
                }
            } else if( document.activeElement.id == thisPanel.textInput.attr('id') ) {

                 elToHighlight = $( visibleListItems[0] );
            }

            elToHighlight.addClass('labelPanelListItemHighlighted');
            thisPanel.textInput.val( elToHighlight.text() );

            var difference = ( elToHighlight.offset().top + elToHighlight.height() ) -
                                ( thisPanel.labelListContainer.offset().top + thisPanel.labelListContainer.height() );

            if( difference > 0 )  {
            
                thisPanel.labelListContainer.scrollTop( thisPanel.labelListContainer.scrollTop() + difference + elToHighlight.height() );
                thisPanel.recentTextInput = true;
                setTimeout( BioSync.LabelPanel.recentTextInput, 800, { instance: thisPanel } );
            }

        } else if( p.keyCode == 38 && selectedListItem.length ) {
            
            selectedListItem.removeClass('labelPanelListItemHighlighted');

            if( selectedListItem.get(0) == visibleListItems[0] ) { thisPanel.textInput.focus(); return; }

            var elToHighlight = selectedListItem.prev();
            while( elToHighlight.is(':hidden') ) {
                elToHighlight = elToHighlight.prev();
            }

            elToHighlight.addClass('labelPanelListItemHighlighted');
            thisPanel.textInput.val( elToHighlight.text() );
        
            var difference = ( elToHighlight.offset().top - thisPanel.labelListContainer.offset().top );

            if( difference < 0 ) {
                thisPanel.labelListContainer.scrollTop( thisPanel.labelListContainer.scrollTop() + difference - elToHighlight.height() );
                thisPanel.recentTextInput = true;
                setTimeout( BioSync.LabelPanel.recentTextInput, 800, { instance: thisPanel } );
            }

        } else if( p.keyCode == 8 || p.keyCode == 46 || String.fromCharCode( p.keyCode ).match( /\w/ ) ) {

            listItems.show();

            var regExp = new RegExp( thisPanel.textInput.val(), 'gi' );

            for( var labelId in thisPanel.labelDivs ) {

                var labelDiv = thisPanel.labelDivs[labelId];

                if( ! labelDiv.text().match( regExp ) ) {

                    labelDiv.hide();
                }
            }

            if( ! listItems.filter(':visible').length ) {
                thisPanel.addNoLabelIndicator();
            } else if( listItems.filter('.noLabels').length && listItems.filter('.labelPanelListItem:visible').length ) {
                thisPanel.removeNoLabelIndicator();
            }
        
            $( listItems.filter('.labelPanelListItemHighlighted') ).removeClass('labelPanelListItemHighlighted');

            thisPanel.recentTextInput = true;
            setTimeout( BioSync.LabelPanel.recentTextInput, 800, { instance: thisPanel } );
        }
    }
}
