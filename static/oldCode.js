    updateConnection: function( p ) {
        
        var columnConnection = p.columnConnection;
        var ancestorColumn = p.ancestorColumn;
        var descendantColumn = p.descendantColumn;

        var expandedNodeDOM = $( ancestorColumn.container.find('div.expanded')[0] );

        var ancestorConnection = new Object();
        BioSync.Common.storeObjPosition( expandedNodeDOM, ancestorConnection );

        var ancestorColumnCoords = { x1: ancestorConnection.myPosition.left + ancestorConnection.myWidth,
                                     y1: ancestorConnection.myPosition.top + ( ancestorConnection.myHeight / 2 ) }
                        
        columnConnection[ 0 ] =
            ancestorColumn.canvas.path( [ "M", ancestorColumnCoords.x1, " ", ancestorColumnCoords.y1, "L" ].join('') )
                                     .attr( { stroke: this.config.columnConnectionColor, "stroke-width": this.config.columnConnectionWidth } );


        var descendantRootNode = descendantColumn.nodeInfo[ descendantColumn.rootId ];

        columnConnection[ 1 ] = descendantColumn.canvas.path( [ "M", descendantRootNode.x, " ", descendantRootNode.y, "L" ].join("") )
                                     .attr( { stroke: this.config.columnConnectionColor, "stroke-width": this.config.columnConnectionWidth } );

        ancestorColumnCoords.x2 = ancestorColumn.myWidth + descendantRootNode.x;
        ancestorColumnCoords.y2 = descendantRootNode.y + ( descendantColumn.centerOffset - ancestorColumn.centerOffset );

        if( ancestorColumnCoords.y2 > ancestorColumn.myHeight ) {
            ancestorColumn.canvas.setSize( ancestorColumn.svgDiv.width(), ancestorColumnCoords.y2 );
            ancestorColumn.svgDiv.height( ancestorColumnCoords.y2 );
        }

        var descendantColumnCoords = { x2: ancestorColumnCoords.x1 - ancestorColumn.myWidth,
                                       y2: ancestorColumnCoords.y1 - ( descendantColumn.centerOffset - ancestorColumn.centerOffset ) };
        
        if( descendantColumnCoords.y2 > descendantColumn.myHeight ) {
            descendantColumn.canvas.setSize( descendantColumn.svgDiv.width(), descendantColumnCoords.y2 );
            descendantColumn.svgDiv.height( descendantColumnCoords.y2 );
        }

        if( p.animate ) {
            
            columnConnection[ 0 ].animate( { path: [ "M", ancestorColumnCoords.x1, " ", ancestorColumnCoords.y1,
                                                     "L", ancestorColumnCoords.x2, " ", ancestorColumnCoords.y2 ].join("") }, this.config.animateColumnConnectionTime );
            
            columnConnection[ 1 ].animate( { path: [ "M", descendantRootNode.x, " ", descendantRootNode.y,
                                                     "L", descendantColumnCoords.x2, " ", descendantColumnCoords.y2 ].join("") }, this.config.animateColumnConnectionTime );

            var renderObj = this;

            setTimeout( function() { columnConnection[0].animate( { opacity: 0.1 }, 200 ); }, renderObj.config.animateColumnConnectionTime );
            setTimeout( function() { columnConnection[1].animate( { opacity: 0.1 }, 200 ); }, renderObj.config.animateColumnConnectionTime );

        } else {

            columnConnection[ 0 ].attr( { path: [ "M", ancestorColumnCoords.x1, " ", ancestorColumnCoords.y1,
                                                  "L", ancestorColumnCoords.x2, " ", ancestorColumnCoords.y2 ].join(""),
                                          opacity: 0.1 } );
            
            columnConnection[ 1 ].attr( { path: [ "M", descendantRootNode.x, " ", descendantRootNode.y,
                                                  "L", descendantColumnCoords.x2, " ", descendantColumnCoords.y2 ].join(""),
                                          opacity: 0.1 } );
        }
} 

/*

BioSync.TreeViewer.RenderUtil = {

    Common: {

        clearContainer: function( p ) { p.viewer.container.empty(); },

        getCladePathString: function( p ) {

            var pathString = new BioSync.Common.StringBuffer();

            pathString.append( this.getNodePathString( p ) );

            for( var i = 0, ii = p.node.children.length; i < ii; i++ ) {
                pathString.append( this.getCladePathString( { node: p.nodeInfo[ p.node.children[i] ], nodeInfo: p.nodeInfo } ) );    
            }

            return pathString.toString();
        },

        getNodePathString: function( p ) {

            if( p.node.isCollapsed ) { return ''; }

            var pathString = new BioSync.Common.StringBuffer();

            var childCount = p.node.children.length;

            pathString.append( [ "M", p.node.x, " ", p.node.y, "l", p.node.dx, " 0" ].join("") );

            if( childCount ) {

                if( childCount == 1 ) {

                    var tipSep = this.config.verticalTipBuffer;

                    var childY = p.nodeInfo[ p.node.children[0] ].y;
                    var lastChildY = p.nodeInfo[ p.node.children[ childCount-1 ] ].y;

                    pathString.append( [ "M", p.node.x, " ", childY - ( tipSep / 4 ) , "l0 ", ( tipSep / 2 ) ].join("") );

                } else {
                    
                    var firstChildY = p.nodeInfo[ p.node.children[0] ].y;
                    var lastChildY = p.nodeInfo[ p.node.children[ childCount-1 ] ].y;

                    pathString.append( [ "M", p.node.x, " ", firstChildY, "L", p.node.x, " ", lastChildY ].join("") );
                }
            }

            return pathString.toString();
        },

        renderLabels: function( p ) {

            var viewer = p.viewer;
            
            for( var nodeId in p.data ) {

                var node = p.data[ nodeId ];

                if( node.label ) {

                    var label = 
                        p.canvas.text( node.x + viewer.config.tipLabelBuffer , node.y, node.label )
                                    .attr( { stroke: 'none',
                                             fill: viewer.config.treeColor,
                                             "font-family": viewer.config.fontFamily,
                                             "font-size": viewer.config.fontSize,
                                             "text-anchor": "start" } );

                    var eventObj = viewer.events;

                    if( eventObj.labelClick || eventObj.labelRightClick ) {

                        var info = { left: { func: function() { }, params: { } }, right: { func: function() { }, params: { } } }

                        if( eventObj.labelClick ) {

                            if( eventObj.labelClick.type == 'getUrlForm' ) {
                               
                               info.left = { func: BioSync.ModalBox.getUrlForm,
                                             params: { url: [ eventObj.labelClick.url, nodeId ].join('/') } };

                            }
                        }

                        $( label.node ).bind( 'click', info, BioSync.Common.handleBothClicks );
                        
                        $( label.node )
                            .bind( 'mouseover', { el: $(viewer.container) }, BioSync.Common.addHoverPointer )
                            .bind( 'mouseout', { el: $(viewer.container) }, BioSync.Common.removeHoverPointer );
                    }

                    if( node.isInternal ) {

                        var boundingBox = label.getBBox();

                        var top = node.y - ( boundingBox.height / 2 );
                        var left = node.x - boundingBox.width;
                         
                        label.attr( { x: left + p.viewer.config.nonTipLabelBuffer, y: top } );
                    }

                    node.raphaelLabel = label;
                }
            }
        },

        addNodeSelector: function( p ) {

            var viewer = p.viewer;

            var column = ( 'column' in p ) ? p.column : viewer.columns[ viewer.currentColumnIndex ];

            var nodeSelector =
                p.canvas.circle( 0, 0, viewer.config.nodeSelectorRadius )
                                .attr( { fill: viewer.config.nodeSelectorColor,
                                         stroke: viewer.config.nodeSelectorColor,
                                         "fill-opacity": .7,
                                         "stroke-width": viewer.config.pathWidth } ).hide();

            if( viewer.events.nodeClick || viewer.events.nodeRightClick ) {
                $( nodeSelector.node ).bind( 'mousedown',
                                             { viewer: viewer, column: column, nodeSelector: nodeSelector },
                                             viewer.handleNodeClick );
            }

            p.container.bind( 'mousemove',
                              { viewer: viewer, column: column, nodeSelector: nodeSelector },
                              viewer.renderUtil.updateNodeSelector );

            return nodeSelector;
        },

        getLabelWidth: function( p ) {

            var label = p.canvas.text( 10, 10, p.label )
                                    .attr( { stroke: p.viewer.config.treeColor,
                                             fill: p.viewer.config.treeColor,
                                             "font-family": p.viewer.config.fontFamily,
                                             "font-size": p.viewer.config.fontSize } );
            var box = label.getBBox();
            label.remove();
            return box.width;
        }

    },

    phylogram: {

        browse: {
            
            initialize: function( p ) {

                var viewer = p.viewer;
                
                var make = BioSync.Common.makeEl;

                viewer.svgWrapper = make('div').attr( { 'class': 'svgWrapper' } ).height('100%').width('100%').appendTo( viewer.container );
                viewer.svgDiv = make('div').attr( { 'class': 'browseSvgDiv' } ).appendTo( viewer.svgWrapper );
                viewer.canvas = Raphael( viewer.svgDiv.get(0), 300, 100 );

                BioSync.TreeViewer.RenderUtil.Common.labelWidthMetric = 
                    ( BioSync.TreeViewer.RenderUtil.Common.getLabelWidth( {
                        label: 'aaaaa',
                        viewer: viewer,
                        canvas: viewer.canvas } ) ) / 5;
            },

            renderReceivedTree: function( p ) {

                var viewer = p.viewer;

                viewer.svgDiv.width( p.canvas.x ).height( p.canvas.y );
                viewer.canvas.setSize( p.canvas.x, p.canvas.y );

                viewer.rootId = p.rootId;
                viewer.nodeInfo = p.nodeInfo;

                viewer.canvas.path( p.pathString )
                                     .attr( { stroke: viewer.config.treeColor,
                                              "stroke-width": viewer.config.pathWidth,
					      "stroke-linejoin": "round" } );
                
                BioSync.TreeViewer.RenderUtil.Common.renderLabels( {
                    data: viewer.nodeInfo,
                    viewer: viewer,
                    canvas: viewer.canvas } )
               
                if( viewer.hasNodeSelector ) {

                    viewer.nodeSelector =
                        BioSync.TreeViewer.RenderUtil.Common.addNodeSelector( {
                            viewer: viewer,
                            container: viewer.container,
                            canvas: viewer.canvas } );
                }
            }
        },

        navigate: {

            initialize: function( p ) {

                var viewer = p.viewer;

                var make = BioSync.Common.makeEl;

                viewer.viewPanel = make('div').attr( { 'class': 'viewPanel' } )
                                              .height( '100%' )
                                              .width( viewer.container.width() );

                viewer.columnWrapper = make('div').attr( { 'class': 'columnWrapper' } ).height( viewer.container.height() - BioSync.Common.scrollbarWidth );

                viewer.columns = [ this.makeInitialColumnObjects( ) ];
                
                viewer.currentColumnIndex = 0;
                var currentColumn = viewer.columns[0];
                currentColumn.index = 0;
                
                viewer.container.append(
                    viewer.viewPanel.append(
                        viewer.columnWrapper.append( 
                            currentColumn.container.append(
                                currentColumn.svgWrapper.append( currentColumn.svgDiv ) ) ) ) );
                
                currentColumn.canvas = Raphael( currentColumn.svgDiv.get(0), 300, 100 );

                BioSync.TreeViewer.RenderUtil.Common.labelWidthMetric = 
                    ( BioSync.TreeViewer.RenderUtil.Common.getLabelWidth( {
                        label: 'aaaaa',
                        viewer: viewer,
                        canvas: currentColumn.canvas } ) ) / 5;
            },

            handleCollapseCladeExternalColumnResponse: function( response ) {

                var response = eval( "(" + response + ")" );

                var viewer = this;

                response.viewer = viewer;

                viewer.renderUtil.renderReceivedTree( response )
                
                viewer.viewPanel.scrollTop( 0 );

                if( viewer.currentColumnIndex > 0 ) {
                
                    var prevCol = viewer.columns[ viewer.currentColumnIndex - 1 ];
                    var nextCol = viewer.columns[ viewer.currentColumnIndex ];

                    viewer.renderUtil.initializePathBetweenColumns( {
                        viewer: viewer,
                        prevColumn: prevCol,
                        curColumn: nextCol } );

                    viewer.renderUtil.animatePathBetweenColumns( {
                        viewer: viewer,
                        prevColumn: prevCol,
                        curColumn: nextCol } );
                }
            },

            handleCollapseCladeInternalColumnResponse: function( response ) {

                var response = eval( "(" + response + ")" );

                var viewer = this;

                response.viewer = viewer;

                viewer.columns.splice( viewer.currentColumnIndex, 0, viewer.renderUtil.makeInitialColumnObjects( ) );
                
                var clickedCol = viewer.columns[ viewer.currentColumnIndex ];
                clickedCol.index = viewer.currentColumnIndex;

                clickedCol.canvas = Raphael( clickedCol.svgDiv.get(0), 300, 100 );

                clickedCol.container.append(
                    clickedCol.svgWrapper.append( clickedCol.svgDiv ) ).insertBefore( viewer.columns[ viewer.currentColumnIndex + 1 ].container );

                viewer.renderUtil.renderReceivedTree( response )
                
                viewer.viewPanel.scrollTop( 0 );

                var nextCol = viewer.columns[ viewer.currentColumnIndex + 1 ];

                $( clickedCol.container.find( [ 'div.hiddenHover[nodeId="', nextCol.rootId, '"]' ].join('') )[0] ).addClass('expanded'); 
                
                if( viewer.currentColumnIndex > 0 ) {

                    viewer.renderUtil.initializePathBetweenColumns( {
                        viewer: viewer,
                        prevColumn: clickedCol,
                        curColumn: nextCol } );

                    viewer.renderUtil.animatePathBetweenColumns( {
                        viewer: viewer,
                        prevColumn: clickedCol,
                        curColumn: nextCol } );
                }
                
                viewer.currentColumnIndex = viewer.columns.length - 1;
            },

            handleVerticalExpandResponse: function( response ) {

                var response = eval( "(" + response + ")" );

                var viewer = this;

                response.viewer = viewer;

                viewer.renderUtil.renderReceivedTree( response )

                var prevCol = viewer.columns[ viewer.currentColumnIndex - 1 ];
                var nextCol = viewer.columns[ viewer.currentColumnIndex ];

                if( viewer.currentColumnIndex > 0 ) {
                
                    viewer.renderUtil.initializePathBetweenColumns( {
                        viewer: viewer,
                        prevColumn: prevCol,
                        curColumn: nextCol } );

                    viewer.renderUtil.animatePathBetweenColumns( {
                        viewer: viewer,
                        prevColumn: prevCol,
                        curColumn: nextCol } );
                }
                
                this.viewPanel.scrollTop( 0 );
            },

            initializePathBetweenColumns: function( p ) {

                var viewer = p.viewer;
                var prevColumn = p.prevColumn;
                var curColumn = p.curColumn;

                if( prevColumn.expandNodePaths ) {
                        
                    for( var i = 0, ii = prevColumn.expandNodePaths.length; i < ii; i++ ) {
                        prevColumn.expandNodePaths[ i ].hide().remove();
                    }
                }
               
                var expandedHover = $( prevColumn.container.find('div.expanded')[0] );
                var expandedHoverPosition = expandedHover.position();
                        
                prevColumn.expandNodePaths =
                    [ prevColumn.canvas.path( [ "M", expandedHoverPosition.left + expandedHover.width(), " ",
                                                     expandedHoverPosition.top + ( expandedHover.height() / 2 ),
                                                "L" ].join("") ).attr( { stroke: 'blue', "stroke-width": 2 } ) ];

                prevColumn.expandNodePaths.push( curColumn.canvas.path( [ "M", curColumn.rootLocation.x, " ",
                                                                               curColumn.rootLocation.y,
                                                                          "L" ].join("") ).attr( { stroke: 'blue', "stroke-width": 2 } ) );
            },

            animatePathBetweenColumns: function( p ) {

                var viewer = p.viewer;
                var prevColumn = p.prevColumn;
                var curColumn = p.curColumn;

                var expandedHover = $( prevColumn.container.find('div.expanded')[0] );
                var expandedHoverPosition = expandedHover.position();

                var prevColumnX1 = ( expandedHoverPosition.left + expandedHover.width() );
                var prevColumnY1 = ( expandedHoverPosition.top + ( expandedHover.height() / 2 ) );

                var prevColumnX2 = prevColumn.myWidth + curColumn.rootLocation.x;
                var prevColumnY2 = curColumn.rootLocation.y + ( curColumn.centerOffset - prevColumn.centerOffset );

                var curColumnX1 = curColumn.rootLocation.x;
                var curColumnY1 = curColumn.rootLocation.y;

                var curColumnX2 = prevColumnX1 - prevColumn.myWidth;
                var curColumnY2 = prevColumnY1 - ( curColumn.centerOffset - prevColumn.centerOffset );

                if( prevColumnY2 > prevColumn.myHeight ) {
                    var newHeight = prevColumnY2 - prevColumn.centerOffset;
                    prevColumn.svgDiv.height( newHeight );
                    prevColumn.canvas.setSize( prevColumn.myWidth, newHeight );
                    prevColumn.myHeight = newHeight;
                }

                prevColumn.expandNodePaths[0].animate( { path: [ "M", prevColumnX1, " ", prevColumnY1,                                                                      
                                                                 "L", prevColumnX2, " ", prevColumnY2 ].join("") }, 200 );
 
                prevColumn.expandNodePaths[1].animate( { path: [ "M", curColumnX1, " ", curColumnY1,
                                                                 "L", curColumnX2, " ", curColumnY2 ].join("") }, 200 );
            },


            showDescendantLabels: function( p ) {
                $(this).children('div.labelListWrapper').show();
            },
            
            hideDescendantLabels: function( p ) {
                $(this).children('div.labelListWrapper').hide();
            },

            handleExpandNodeDialog: function( p ) {

                var container = $(this);
                var list = container.children('div.labelListWrapper'); 
                var bridge = container.children('div.hoverBridge');

                if( BioSync.Common.isMouseOnElement( { el: container, x: p.pageX, y: p.pageY } ) &&
                    list.is(':hidden') ) {

                    list.show();

                } else if( ( ( ! BioSync.Common.isMouseOnElement( { el: container, x: p.pageX, y: p.pageY } ) ) &&
                             ( ! BioSync.Common.isMouseOnElement( { el: list, x: p.pageX, y: p.pageY } ) ) &&
                             ( ! BioSync.Common.isMouseOnElement( { el: bridge, x: p.pageX, y: p.pageY } ) ) )
                            && list.is(':visible') ) {

                    list.hide();

                }
            },

            receiveTree: function( p ) {

                var viewer = p.viewer;

                var currentColumn = viewer.columns[0];

                currentColumn.tree = viewer.tree;

            },

            makeInitialColumnObjects: function() {

                var make = BioSync.Common.makeEl;

                return { svgDiv: make('div').attr( { 'class': 'navigateSvgDiv' } ),
                         svgWrapper: make('div').attr( { 'class': 'svgWrapper' } ).height( '100%' ),
                         container: make('div').attr( { 'class': 'columnContainer' } ).height( '100%' ) };
            },

            DOMToCanvasCoords: function( p ) {

                var curColumn = p.currentColumn;

                return { x: p.x - curColumn.myOffset.left + p.viewer.viewPanel.scrollLeft(),
                         y: p.y - curColumn.myOffset.top - curColumn.centerOffset + p.viewer.viewPanel.scrollTop() }

            },

            updateNodeSelector: function( p ) {

                var nodeSelector = p.data.nodeSelector;

                if( $('#contextMenu').length || $('.expandOptionBox:visible').length ) { nodeSelector.hide(); return; }

                var viewer = p.data.viewer;
                var column = p.data.column;

                if( BioSync.Common.symbolDragInfo ) { nodeSelector.hide(); return true; }
              
                var closestNodeInfo =
                    viewer.getClosestNode( {
                        coords: viewer.renderUtil.DOMToCanvasCoords( {
                            viewer: viewer,
                            currentColumn: column,
                            x: p.pageX, y: p.pageY } ),
                        node: column.nodeInfo[ column.rootId ],
                        nodeId: column.rootId,
                        nodeInfo: column.nodeInfo } );

                if( closestNodeInfo.distance < 50 &&
                    ( ! column.nodeInfo[ closestNodeInfo.id ].isCollapsed ) ) {

                    nodeSelector.attr( { cx: closestNodeInfo.node.x, cy: closestNodeInfo.node.y } ).show().toFront();
                    $( nodeSelector.node ).attr( { 'nodeId': closestNodeInfo.id } );

                } else {

                    nodeSelector.hide();
                }
            },


            finishSliderOptions: function( p ) {

                var viewer = p.viewer;
                var make = BioSync.Common.makeEl;

                var sliderOptions = viewer.config.phylogram[ viewer.viewMode ].sliderOptions;

                var container = make('div');

                for( var option in sliderOptions ) {

                    var outputContainer = $('#' + [ option, 'SVG' ].join('') ).parent().parent();
                    
                    sliderOptions[option].svg =
                        Raphael(
                            [ option, 'SVG' ].join(''),
                            outputContainer.outerWidth( true ),
                            outputContainer.outerHeight( true ) );

                    var y = outputContainer.outerHeight( true ) / 2;

                    sliderOptions[option].path = 
                        sliderOptions[option].svg.path( [ 'M0 ', y, 'L', sliderOptions[ option ].value, ' ', y ].join('') ).attr( {
                        stroke: 'black', fill: 'black', 'stroke-width': 4 } );
                }
            },

            createSliderOptions: function( p ) {
                
                var viewer = p.viewer;
                var make = BioSync.Common.makeEl;

                var sliderOptions = viewer.config.phylogram[ viewer.viewMode ].sliderOptions;

                var container = make('div');

                for( var option in sliderOptions ) {

                    container.append( 
                        make('div').attr( { 'class': 'rangeDataContainer' } ).append(
                           make('div').attr( { 'class': 'rangeDataInput' } ).append(
                               make('div').attr( { 'class': 'rangeDataLabel' } ).text( [ sliderOptions[ option ].text, ' (in pixels) : ' ].join('') ),
                               make('div').attr( { 'class': 'rangeDataLabel configCurrentSliderValue' } ).text( sliderOptions[ option ].value ),
                               make('div').attr( { 'class': 'rangeDataLabel' } ).append(
                                   make('div').width( 125 ).slider( { min: sliderOptions[option].range.min,
                                                                      max: sliderOptions[option].range.max, value: sliderOptions[ option ].value } )
                                                           .bind('slide', { viewer: viewer, option: option }, viewer.renderUtil.optionSlideChange ) ),
                               make('div').attr( { 'class': 'rangeDataLabel' } ).text( 'Save' )
                                          .bind( 'click', { viewer: viewer }, sliderOptions[ option ].update ),
                               make('div').attr( { 'class': 'clear' } ) ),
                           make('div').attr( { 'class': 'rangeDataOutput' } ).append(
                               make('div').append(
                                   make('div').attr( { 'id': [ option, 'SVG' ].join('') } ).width( sliderOptions[ option ].value ) ) ) ) );
                }

                return container;
            },

            showModalColorConfig: function( p ) {

                var viewer = p.data.viewer;
                var make = BioSync.Common.makeEl;

                if( ! $['farbtastic'] ) {
                    BioSync.Common.loadScript( { name: 'farbtastic' } );
                    BioSync.Common.loadCSS( { name: 'farbtastic' } );
                }

                BioSync.ModalBox.showModalBox( {
                    title: 'Config',
                    content:
                        make('div').attr( { 'class': 'configPanel' } ).append(
                            make('div').attr( { 'class': 'colorOptionContainer' } ).append( 
                                make('span').attr( { 'class': 'dropDownLabel' } ).text( 'Color of : ' ),
                                make('span').append(
                                    make('select').attr( { 'id': 'colorOptions', 'name': 'colorOptions' } )
                                                  .append( viewer.getConfigColorDropdownOptions() )
                                                  .bind( 'change', { viewer: viewer }, viewer.renderUtil.updateFarbtastic ) ) ),
                            make('div').attr( { 'class': 'currentColorContainer' } ).append(
                                make('span').text( 'Hex value : ' ),
                                make('span').attr( { 'id': 'configCurrentColor', 'class': 'configCurrentValue' } ) ),
                            make('div').attr( { 'id': 'colorPicker' } ),
                            make('div').attr( { 'class': 'configSaveButton' } )
                                       .text('Save')
                                       .bind( 'click', { viewer: viewer }, viewer.saveColorConfig ) ) } );

                           //make('div').attr( { 'class': 'fLeft' } ).append( viewer.renderUtil.createSliderOptions( { viewer: viewer } ) ),
                               
                viewer.farbtastic = $.farbtastic( '#colorPicker', viewer.renderUtil.updateNewColorValue )
                    .setColor( viewer.config.colorOptions[ $('#colorOptions').val() ].value );

                //viewer.renderUtil.finishSliderOptions( { viewer: viewer } ); 
            },

            updateBranchLength: function( p ) {
                
                var viewer = p.data.viewer; 

            },

            optionSlideChange: function( p ) {

                var viewer = p.data.viewer; 
                var option = p.data.option; 
                var slider = $(this);
                var value = slider.slider( 'option', 'value' );
                
                var y = slider.parent().siblings('.rangeDataOutput').outerHeight( true ) / 2;

                slider.parent().siblings('.configCurrentSliderValue').text( value );
                
                viewer.config.phylogram[ viewer.viewMode ].sliderOptions[option].path.attr( { path: [ 'M0 ', y, 'L', value, ' ', y ].join('') } );

                viewer.config.phylogram[ viewer.viewMode ].sliderOptions[option].svg.setSize( value, 24 )
                $( [ '#', option, 'SVG' ].join('') ).width( value );
                
            },

            updateFarbtastic: function( p ) {
                var viewer = p.data.viewer;
                
                viewer.farbtastic.setColor( viewer.config.colorOptions[ p.currentTarget.value ].value );
            },

            updateNewColorValue: function( color ) { $('#configCurrentColor').text( color ).css( { 'color': color } ); },

            updateNodeSelectorColor: function( p ) {

                var viewer = p.viewer;

                for( var i = 0, ii = viewer.currentColumnIndex; i <= ii; i++ ) {
                    
                    var curColumn = viewer.columns[i].nodeSelector.attr( {
                        fill: p.value, stroke: p.value } );
                }
           
                var title = $('#modalBoxTitle');
                var titleOffset = title.offset();
                 
                BioSync.Common.notify( { text: 'Changes Saved',
                                         timeout: 3000,
                                         x: titleOffset.left + ( title.outerWidth( true ) / 2 ),
                                         y: titleOffset.top - 40 } );

            },

            updateExpandableNodeColor: function( p ) {

                var viewer = p.viewer;

                for( var i = 0, ii = viewer.currentColumnIndex; i <= ii; i++ ) {
                    
                    var curColumn = viewer.columns[i];

                    for( var nodeId in curColumn.nodeInfo ) {
                        
                        if( curColumn.nodeInfo[ nodeId ].hiddenHover ) {

                            curColumn.nodeInfo[ nodeId ].hiddenHover.path.attr( {
                                stroke: p.value, fill: p.value } );
                        }
                    }
                }
            
                var title = $('#modalBoxTitle');
                var titleOffset = title.offset();
                 
                BioSync.Common.notify( { text: 'Changes Saved',
                                         timeout: 3000,
                                         x: titleOffset.left + ( title.outerWidth( true ) / 2 ),
                                         y: titleOffset.top - 40 } );
            },

            collapseClade: function( p ) {
                
                var viewer = p.viewer;
                var clickedColumn = p.column;
                
                var rootId = clickedColumn.rootId;

                var clickedRightColumn = ( clickedColumn.index == viewer.currentColumnIndex ) ? true : false;
                var expandedNode = $( clickedColumn.container.find('div.expanded')[0] );

                var clickedColumnExpandedNode = ( expandedNode.length ) ? clickedColumn.nodeInfo[ expandedNode.attr('nodeId') ] : { next: -1, back: -1 };
                var clickedColumnCollapsingNode = clickedColumn.nodeInfo[ p.nodeId ];

                var isCollapsingExpandedNode = ( ( clickedColumnExpandedNode.next > clickedColumnCollapsingNode.next ) &&
                                                 ( clickedColumnExpandedNode.back < clickedColumnCollapsingNode.back ) ) ? true : false;

                var responseFun = undefined;

                if( ( clickedRightColumn ) || ( isCollapsingExpandedNode ) ) {
                
                    viewer.renderUtil.updateColumns( { clickedIndex: clickedColumn.index - 1, viewer: viewer } );

                    responseFun = viewer.renderUtil.handleCollapseCladeExternalColumnResponse;

                } else {

                    viewer.currentColumnIndex = clickedColumn.index;
                    viewer.renderUtil.removeColumn( { viewer: viewer, column: clickedColumn } );
                    
                    responseFun = viewer.renderUtil.handleCollapseCladeInternalColumnResponse;
                }

                $.ajax( { url: BioSync.Common.makeUrl( { controller: 'plugin_treeViewer', argList: [ 'collapseClade' ] } ),
                          type: "GET",
                          context: viewer,
                          data: { nodeId: p.nodeId, rootId: rootId, collapsedNodeIds: clickedColumn.collapsedNodeIds.join(':'), treeType: viewer.treeType },
                          success: new Array(
                            responseFun,
                            function() { viewer.container.find( [ 'div[nodeId="', p.nodeId, '"]' ].join('') ).addClass('userCollapsed'); },
                            ( p.success ) ? p.success : function() { },
                            function() { $(document).trigger('cladeCollapsed', { viewer: viewer, columnIndex: clickedColumn.index } ); } ) } );
            },

            navigateToNode: function( p ) {

                var viewer = p.viewer;
                var nodeId = p.nodeId;
                var nextId = p.next;
            
                var found = false;
                    
                for( var i = 0, ii = viewer.currentColumnIndex; i <= ii; i++ ) {

                    var column = viewer.columns[i];

                    if( column.nodeInfo[ nodeId ] ) {
                       if( column.nodeInfo[ nodeId ].raphaelLabel ) {
                           column.nodeInfo[ nodeId ].raphaelLabel.attr( { 'stroke': '#CEE8F0', fill: '#CEE8F0' } );
                       }
                       found = true;
                       break;
                    }
                }

                if( ! found ) { 
                
                    for( var i = 0, ii = viewer.currentColumnIndex; ii >= i; ii-- ) {

                        var currentColumn = viewer.columns[ ii ];
                      
                        for( var id in currentColumn.nodeInfo ) { 

                            if( ( currentColumn.nodeInfo[ id ].hiddenHover ) &&
                                ( currentColumn.nodeInfo[ id ].next < nextId && currentColumn.nodeInfo[ id ].back > nextId ) ) { 

                                var fakeClickEl = currentColumn.nodeInfo[ id ].hiddenHover.el.find('div.descendantAction');
                                viewer.renderUtil.expandNode( {
                                    target: fakeClickEl, data: { viewer: viewer, columnIndex: ii, nodeId: id },
                                    success: function() { setTimeout( function() {
                                        viewer.renderUtil.navigateToNode( { viewer: viewer, nodeId: nodeId, next: nextId } ); }, 200 ); } } );
                                return;
                            }
                        }
                    }
                }
            },

            unNavigateToNode: function( p ) {

                var viewer = p.viewer;
                var nodeId = p.nodeId;
                
                for( var i = 0, ii = viewer.currentColumnIndex; i <= ii; i++ ) {

                    var column = viewer.columns[i];

                    if( column.nodeInfo[ nodeId ] ) {
                       column.nodeInfo[ nodeId ].raphaelLabel.attr( { 'stroke': viewer.config.treeColor, fill: viewer.config.treeColor } );
                    }
                }

            }
         }
    }
}
