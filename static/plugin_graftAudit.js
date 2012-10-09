BioSync.GraftAudit = {

    instances: { }

};
                
BioSync.GraftAudit.graftAudit = function( p ) { 

    BioSync.GraftAudit.instances[ p.containerId ] = this;
    
    this.containerId = p.containerId;    

    this.container = $('#' + p.containerId);
    
    var make = BioSync.Common.makeEl;

    this.rollbackButton =
        make('button').attr( { 'type': 'button', 'class': 'auditActionButton disabledButton' } ).text('Rollback');
    
    this.saveButton =
        make('button').attr( { 'type': 'button', 'class': 'auditActionButton' } ).text('Save Changes').hide()
                      .bind( 'click', { auditModule: this }, this.showSaveDialogue );

    this.header = make('div').attr( { 'class': 'graftAuditHeader' } ).append(
        make('div').attr( { 'class': 'graftAuditOptions' } ).append( this.rollbackButton, this.saveButton ),
        make('div').attr( { 'class': 'clear' } ) );

    this.graftListContainer = make('div').attr( { 'class': 'extend' } );
    
    this.container.append( this.header, this.graftListContainer );

    this.graftListContainer.height( this.container.outerHeight( true ) - this.header.outerHeight( true ) );

    var treeViewer = $( this.container.closest('.treeViewerContainer') );
    if( treeViewer ) {
        this.treeViewer = BioSync.TreeViewer.instances[ treeViewer.attr('id') ];
        this.treeViewer.graftAuditModule = this;
        this.treeViewer.container.bind( 'graftSuccess', { auditModule: this }, this.handleGraftSuccess );
        this.treeViewer.container.bind( 'expandNodeSuccess', { auditModule: this }, this.handleExpandNodeSuccess );
        $( document ).bind( 'verticallyExpandNodeSuccess', { auditModule: this }, this.handleVerticallyExpandNodeSuccess );
        $( document ).bind( 'cladeCollapsed', { auditModule: this }, this.handleCladeCollapse );
        if( this.treeViewer.treeType == 'grafted' ) {
            this.initialize( { treeViewer: this.treeViewer } );
        } else {
            //this.addNoLabelIndicator();
        }
    }
    
};


BioSync.GraftAudit.graftAudit.prototype = {

    initialize: function( p ) { this.createGraftAudit(); },

    createGraftAudit: function( p ) {

        $.ajax( { url: BioSync.Common.makeUrl( { controller: 'plugin_graftAudit', argList: [ 'getGraftedTreeAudit' ] } ),
                 type: "GET",
                 context: this,
                 async: false,
                 data: { treeId: this.treeViewer.treeId },
                 success: this.handleGraftAuditResponse } );
    },

    createColorContainer: function( p ) {

        var make = BioSync.Common.makeEl;

        var borderString = Math.floor( p.treeViewer.style.pathWidth * 2 ) + 'px solid ' + p.graftObj.color;

        return make('div').width( 15 ).attr( { 'class': 'colorContainer' } ).append(
            make('div').attr( { 'class': 'colorIndicator' } )
                       .css( { 'border-top': borderString, 'border-bottom': borderString } ) );
    },

    showStudyDetail: function( p ) {

       $('#modalBoxForm').load( [ BioSync.Common.makeUrl( { controller: 'study', argList: [ 'view', p.data.studyId ] } ), '#content' ].join(' '),
                                function() { $('#modalBoxForm').append( BioSync.Common.makeEl('div').attr( { 'class': 'clear' } ) );
                                             BioSync.ModalBox.showModalBox( { title: 'Study', content: undefined } ); } );

    },

    rootCreateInfoContainer: function( p ) {
        
        var graftObj = p.graftObj;
        var make = BioSync.Common.makeEl;

        var study = ( graftObj.studyCitation.length > 40 )
         ? [ graftObj.studyCitation.substr( 0, 40 ), '...' ].join('')
         : graftObj.studyCitation;

        return rootContainer = make('div').attr( { 'class': 'rootContainer' } ).append(
            make('div').attr( { 'class': 'textInfo centerText bold' } ).text( 'Backbone Tree' ),
            make('div').attr( { 'class': 'detail' } ).append(
                make('div').attr( { 'class': 'textInfo leftText' } ).text( [ 'Focal Clade : ', graftObj.focalClade ].join('') ),
                make('div').attr( { 'class': 'textInfo leftText' } ).text( [ 'OTUs : ', graftObj.otuCount ].join('') ),
                make('div').attr( { 'class': 'textInfo leftText' } ).text( [ 'Nodes In Tree : ', graftObj.sourceCount ].join('') ),
                make('div').attr( { 'class': 'textInfo leftText hoverUnderline' } ).text( [ 'Study : ', study ].join('') )
                           .bind( 'click', { studyId: graftObj.studyId }, this.showStudyDetail ) ).hide() );
    },

    replaceCreateInfoContainer: function( p ) {
      
        var auditModule = this;

        var graftObj = p.graftObj;
        var make = BioSync.Common.makeEl;
        
        var headerText = [ 'Replace : ', ( graftObj.clade ) ? [ graftObj.clade, ' ' ].join('') : '', graftObj.nodeCount, ( graftObj.nodeCount == 1 ) ? ' node' : ' nodes' ].join('');
        
        var replaceDetailText = [ 'Replaced Clade : ', ( graftObj.replaced ) ? [ graftObj.replaced, ', ' ].join('') : '', graftObj.replacedCount, ( graftObj.replacedCount == 1 ) ? ' node' : ' nodes' ].join('');

        var study = ( graftObj.studyCitation.length > 40 )
             ? [ graftObj.studyCitation.substr( 0, 40 ), '...' ].join('')
             : graftObj.studyCitation;
        
        return make('div').attr( { 'class': 'infoContainer' } ).append(
            make('div').attr( { 'class': 'textInfo centerText bold' } ).text( headerText ),
            make('div').attr( { 'class': 'detail' } ).append(
                make('div').attr( { 'class': 'textInfo leftText' } ).text( replaceDetailText ),
                make('div').attr( { 'class': 'textInfo leftText' } ).text( [ 'Date : ', graftObj.datetime ].join('') ),
                make('div').attr( { 'class': 'textInfo leftText' } ).text( [ 'Actor : ', graftObj.user ].join('') ),
                make('div').attr( { 'class': 'textInfo leftText hoverUnderline' } ).text( [ 'Study : ', study ].join('') )
                           .click( function( e ) { auditModule.showStudyDetail( { data: { studyId: graftObj.studyId } } ); e.stopPropagation(); } ),
                make('div').attr( { 'class': 'textInfo centerText bold hoverUnderline' } ).text('View Pre Replace')
                           .click( function( e ) { auditModule.viewReplacement( { auditModule: auditModule, editId: graftObj.editId } ); e.stopPropagation(); } ),
                make('div').attr( { 'class': 'textInfo centerText bold hoverUnderline' } ).text('View Replace Undo')
                           .click( function( e ) { auditModule.viewReplaceUndo( { auditModule: auditModule, editId: graftObj.editId } ); e.stopPropagation(); } ) ).hide() );

    },

    graftCreateInfoContainer: function( p ) {
      
        var auditModule = this;

        var graftObj = p.graftObj;
        var make = BioSync.Common.makeEl;
        
        var headerText = [ 'Graft : ', ( graftObj.clade ) ? [ graftObj.clade, ' ' ].join('') : '', graftObj.nodeCount, ( graftObj.nodeCount == 1 ) ? ' node' : ' nodes' ].join('');

        var study = ( graftObj.studyCitation.length > 40 )
             ? [ graftObj.studyCitation.substr( 0, 40 ), '...' ].join('')
             : graftObj.studyCitation;
        

        graftObj.navigateToNodeOption =
            make('span').attr( { 'class': 'navigateToNodeButton auditAction' } )
                       .bind('click', { params: { viewer: p.treeViewer,
                                                  nodeId: graftObj.nodeId,
                                                  next: graftObj.next },
                                        func: p.treeViewer.renderUtil.navigateToNode }, BioSync.Common.jsEventUnWrapper )
                       .text('Navigate To');
        
        return make('div').attr( { 'class': 'infoContainer' } ).append(
            make('div').attr( { 'class': 'textInfo centerText bold' } ).text( headerText ),
            make('div').attr( { 'class': 'detail' } ).append(
                make('div').attr( { 'class': 'textInfo leftText' } ).text( [ 'Date : ', graftObj.datetime ].join('') ),
                make('div').attr( { 'class': 'textInfo leftText' } ).text( [ 'Actor : ', graftObj.user ].join('') ),
                make('div').attr( { 'class': 'textInfo leftText hoverUnderline' } ).text( [ 'Study : ', study ].join('') )
                           .click( function( e ) { auditModule.showStudyDetail( { data: { studyId: graftObj.studyId } } ); e.stopPropagation(); } ),
               make('div').attr( { 'class': 'textInfo centerText bold hoverUnderline' } ).text('View Pre Graft')
                           .click( function( e ) { auditModule.viewGraft( { auditModule: auditModule, editId: graftObj.editId } ); e.stopPropagation(); } ),
               make('div').attr( { 'class': 'textInfo centerText bold hoverUnderline' } ).text('View Graft Undo')
                           .click( function( e ) { auditModule.viewGraftUndo( { auditModule: auditModule, editId: graftObj.editId } ); e.stopPropagation(); } ) ).hide() );
    },

    pruneCreateInfoContainer: function( p ) {

        var auditModule = this;

        var graftObj = p.graftObj;
        var make = BioSync.Common.makeEl;

        var headerText = [ 'Prune : ', ( graftObj.clade ) ? [ graftObj.clade, ', ' ].join('') : '', graftObj.nodeCount, ( graftObj.nodeCount == 1 ) ? ' node' : ' nodes' ].join('');

        var study = ( graftObj.studyCitation.length > 40 )
         ? [ graftObj.studyCitation.substr( 0, 40 ), '...' ].join('')
         : graftObj.studyCitation;

        return make('div').attr( { 'class': 'infoContainer' } ).append(
            make('div').attr( { 'class': 'textInfo centerText bold' } ).text( headerText ),
            make('div').attr( { 'class': 'detail' } ).append(
                make('div').attr( { 'class': 'textInfo leftText' } ).text( [ 'Date : ', graftObj.datetime ].join('') ),
                make('div').attr( { 'class': 'textInfo leftText' } ).text( [ 'Actor : ', graftObj.user ].join('') ),
                make('div').attr( { 'class': 'textInfo leftText hoverUnderline' } ).text( [ 'Study : ', study ].join('') )
                           .click( function( e ) { auditModule.showStudyDetail( { data: { studyId: graftObj.studyId } } ); e.stopPropagation(); } ),
                make('div').attr( { 'class': 'textInfo centerText bold hoverUnderline' } ).text('View Pre Prune')
                           .click( function( e ) { auditModule.viewPrune( { auditModule: auditModule, editId: graftObj.editId } ); e.stopPropagation(); } ),
                make('div').attr( { 'class': 'textInfo centerText bold hoverUnderline' } ).text('View Prune Undo')
                           .click( function( e ) { auditModule.viewPruneUndo( { auditModule: auditModule, editId: graftObj.editId } ); e.stopPropagation(); } ) ).hide() );
    },

    viewReplace: function( p ) {

        $.ajax( { url: BioSync.Common.makeUrl( { controller: 'plugin_graftAudit', argList: [ 'viewReplace', p.editId ] } ),
                 type: "GET",
                 context: p.auditModule,
                 success: new Array( p.auditModule.handleViewEditResponse ) } );
    },

    viewReplaceUndo: function( p ) {

        $.ajax( { url: BioSync.Common.makeUrl( { controller: 'plugin_graftAudit', argList: [ 'viewReplaceUndo', p.editId ] } ),
                 type: "GET",
                 context: p.auditModule,
                 success: new Array( p.auditModule.handleViewEditResponse ) } );
    },

    viewGraft: function( p ) {

        $.ajax( { url: BioSync.Common.makeUrl( { controller: 'plugin_graftAudit', argList: [ 'viewGraft', p.editId ] } ),
                 type: "GET",
                 context: p.auditModule,
                 success: new Array( p.auditModule.handleViewEditResponse ) } );
    },

    viewGraftUndo: function( p ) {

        $.ajax( { url: BioSync.Common.makeUrl( { controller: 'plugin_graftAudit', argList: [ 'viewGraftUndo', p.editId ] } ),
                 type: "GET",
                 context: p.auditModule,
                 success: new Array( p.auditModule.handleViewEditResponse ) } );
    },

    viewPrune: function( p ) {

        $.ajax( { url: BioSync.Common.makeUrl( { controller: 'plugin_graftAudit', argList: [ 'viewPrune', p.editId ] } ),
                 type: "GET",
                 context: p.auditModule,
                 success: new Array( p.auditModule.handleViewEditResponse ) } );
    },

    viewPruneUndo: function( p ) {

        $.ajax( { url: BioSync.Common.makeUrl( { controller: 'plugin_graftAudit', argList: [ 'viewPruneUndo', p.editId ] } ),
                 type: "GET",
                 context: p.auditModule,
                 success: new Array( p.auditModule.handleViewEditResponse ) } );
    },

    handleViewEditResponse: function( response ) {

        var auditModule = this;
        var viewer = auditModule.treeViewer;

        var response = eval( "(" + response + ")" ); 

        var affectedClade = response.affectedClade;
        
        if( affectedClade.id ) {
            
            viewer.renderUtil.navigateToNode( { viewer: viewer, nodeId: affectedClade.id, next: affectedClade.next } );
            
            var currentColumn = viewer.columns[ viewer.currentColumnIndex ];

            var affectedCladePath =
                BioSync.TreeViewer.RenderUtil.Common.getCladePathString( {
                    node: currentColumn.nodeInfo[ affectedClade.id ],
                    nodeInfo: currentColumn.nodeInfo } );
        
            auditModule.affectedCladePath = currentColumn.canvas.path( affectedCladePath ).attr( { stroke: 'orange', "stroke-width": viewer.style.pathWidth } );
            
            viewer.renderUtil.updateColumns( { clickedIndex: viewer.currentColumnIndex, viewer: viewer } );
            
            currentColumn = viewer.columns[ viewer.currentColumnIndex ];
            
            response.render.viewer = viewer; 
            viewer.renderUtil.renderReceivedTree( response.render );
                
            currentColumn.container.hide();
            
            auditModule.undoPrunePath = currentColumn.canvas.path( currentColumn.path.attr('path') ).attr( { stroke: 'orange', "stroke-width": viewer.style.pathWidth } );

            if( response.affectedNodeId ) {

                var prunedCladePath =
                    BioSync.TreeViewer.RenderUtil.Common.getCladePathString( {
                        node: currentColumn.nodeInfo[ response.affectedNodeId ],
                        nodeInfo: currentColumn.nodeInfo } )
                
                auditModule.prunedCladePath =
                    currentColumn.canvas.path( prunedCladePath ).attr( { stroke: auditModule.graftHistory[ response.targetNodeId ].color,
                                                                         "stroke-width": viewer.style.pathWidth } );
            }

            currentColumn.container.show('slow');
        }
    },

    handleCladeCollapse: function( p, q ) {
        
        var auditModule = p.data.auditModule;
        var viewer = auditModule.treeViewer;
        var graftHistory = auditModule.graftHistory;

        var curColumn = viewer.columns[ q.columnIndex ];
        var prevColumn = viewer.columns[ q.columnIndex - 1 ];

        for( var nodeId in graftHistory ) {

            var graftObj = graftHistory[ nodeId ];

            if( prevColumn && viewer.isAncestor( { currentNodeId: curColumn.rootId,
                                                   nodeInfo: prevColumn.nodeInfo,
                                                   ancestorNodeId: nodeId } ) ) {

                if( graftHistory[ nodeId ].paths[ q.columnIndex ] ) {
                    graftHistory[ nodeId ].paths[ q.columnIndex ].remove();
                }

                graftHistory[ nodeId ].paths[ q.columnIndex ] = 
                    curColumn.canvas.path(
                        BioSync.TreeViewer.RenderUtil.Common.getCladePathString( { node: curColumn.nodeInfo[ curColumn.rootId ],
                                                                                   nodeInfo: curColumn.nodeInfo } ) )
                                .attr( { 'stroke': graftHistory[ nodeId ].color,
                                         'stroke-width': viewer.style.pathWidth } );

                curColumn.rootAncestor = nodeId;

                foundAncestor = true;
            }
                
            if( curColumn.nodeInfo[ nodeId ] ) {

                auditModule.addGraftIndication( { viewer: viewer, columnIndex: q.columnIndex, nodeId: nodeId,
                                                  graftObj: graftHistory[ nodeId ], alreadyExists: true } );
            }
        }
    },

    handleVerticallyExpandNodeSuccess: function( p, q ) {

        var auditModule = p.data.auditModule;
        var viewer = auditModule.treeViewer;
        var graftHistory = auditModule.graftHistory;

        var curColumn = viewer.columns[ viewer.currentColumnIndex ];
        var prevColumn = viewer.columns[ viewer.currentColumnIndex - 1 ];

        for( var nodeId in graftHistory ) {

            var graftObj = graftHistory[ nodeId ];

            if( prevColumn && viewer.isAncestor( { currentNodeId: curColumn.rootId,
                                                   nodeInfo: prevColumn.nodeInfo,
                                                   ancestorNodeId: nodeId } ) ) {

                if( graftHistory[ nodeId ].paths[ viewer.currentColumnIndex ] ) {
                    graftHistory[ nodeId ].paths[ viewer.currentColumnIndex ].remove();
                }

                graftHistory[ nodeId ].paths[ viewer.currentColumnIndex ] = 
                    curColumn.canvas.path(
                        BioSync.TreeViewer.RenderUtil.Common.getCladePathString( { node: curColumn.nodeInfo[ curColumn.rootId ],
                                                                                   nodeInfo: curColumn.nodeInfo } ) )
                                .attr( { 'stroke': graftHistory[ nodeId ].color,
                                         'stroke-width': viewer.style.pathWidth } );

                curColumn.rootAncestor = nodeId;

                foundAncestor = true;
            }
                
            if( curColumn.nodeInfo[ nodeId ] ) {

                auditModule.addGraftIndication( { viewer: viewer, nodeId: nodeId, graftObj: graftHistory[ nodeId ], alreadyExists: true } );
            }
        }
    },

    handleExpandNodeSuccess: function( p, q ) {

        var auditModule = p.data.auditModule;
        var viewer = auditModule.treeViewer;
        var graftHistory = auditModule.graftHistory;

        var curColumn = viewer.columns[ viewer.currentColumnIndex ];
        var prevColumn = viewer.columns[ viewer.currentColumnIndex - 1 ];

        if( viewer.graftInfo && ( viewer.graftColumnIndex != viewer.currentColumnIndex - 1 ) ) {

            if( viewer.isAncestor( { currentNodeId: curColumn.rootId,
                                     nodeInfo: prevColumn.nodeInfo,
                                     ancestorNodeId: viewer.graftInfo.clipboardNodeId } ) ) {
            } else {
                curColumn.canvas.path( curColumn.path.attr('path') ).attr( { stroke: '#63D1F4', "stroke-width": viewer.style.pathWidth } );
            }
        
        } else {
        
            var foundAncestor = false;

            for( var nodeId in graftHistory ) {

                var graftObj = graftHistory[ nodeId ];

                if( viewer.isAncestor( { currentNodeId: curColumn.rootId,
                                         nodeInfo: prevColumn.nodeInfo,
                                         ancestorNodeId: nodeId } ) ) {
                    graftHistory[ nodeId ].paths[ viewer.currentColumnIndex ] = 
                        curColumn.canvas.path(
                            BioSync.TreeViewer.RenderUtil.Common.getCladePathString( { node: curColumn.nodeInfo[ curColumn.rootId ],
                                                                                       nodeInfo: curColumn.nodeInfo } ) )
                                    .attr( { 'stroke': graftHistory[ nodeId ].color,
                                             'stroke-width': viewer.style.pathWidth } );

                    curColumn.rootAncestor = nodeId;

                    foundAncestor = true;
                }
                    
                if( curColumn.nodeInfo[ nodeId ] ) {
                  
                   auditModule.addGraftIndication( { viewer: viewer, nodeId: nodeId, graftObj: graftHistory[ nodeId ] } );
                }

            }

            if( !foundAncestor ) {
                    
                curColumn.rootAncestor = prevColumn.rootAncestor;

                graftHistory[ curColumn.rootAncestor ].paths[ viewer.currentColumnIndex ] =
                        curColumn.canvas.path(
                            BioSync.TreeViewer.RenderUtil.Common.getCladePathString( { node: curColumn.nodeInfo[ curColumn.rootId ],
                                                                                       nodeInfo: curColumn.nodeInfo } ) )
                                    .attr( { 'stroke': graftHistory[ curColumn.rootAncestor ].color,
                                             'stroke-width': viewer.style.pathWidth } );
            }
        }

        auditModule.updateNavigateTo();
    },

    reInitializeModule: function( p ) {

        var auditModule = this;

        auditModule.graftListContainer.empty();
        auditModule.saveButton.hide();

        var isHidden = false;

        if( auditModule.container.is(':hidden') ) { isHidden = true; auditModule.container.show(); }

        auditModule.createGraftAudit();
        
        if( isHidden ) { auditModule.container.hide(); }
    },

    handleGraftSuccess: function( p, q ) { p.data.auditModule.reInitializeModule(); },

    handleItemClick: function( p ) {

        var domItem = $(this);
        var auditModule = p.data.auditModule;

        if( ! domItem.attr('editId') ) { return; }

        if( domItem.hasClass('selectedItem') ) {
            domItem.removeClass('selectedItem');
            auditModule.rollbackButton.addClass('disabledButton').unbind('click');
        } else {

            var buttonAction = ( domItem.hasClass('disabledItem') )
                ? { text: 'Undo Rollback', func: auditModule.undoRollback }
                : { text: 'Rollback', func: auditModule.rollbackGraft };

            domItem.siblings().removeClass('selectedItem');
            domItem.addClass('selectedItem');
            auditModule.rollbackButton.removeClass('disabledButton').bind( 'click', { auditModule: auditModule }, buttonAction.func ).text( buttonAction.text );
        }
    },

    handleGraftAuditResponse: function( response ) {
        
        var response = eval( "(" + response + ")" );

        var auditModule = this;
        var treeViewer = auditModule.treeViewer;
        var make = BioSync.Common.makeEl;

        var colors = [ '#c60c30', '#00a1de', '#62361b', '#009b3a', '#f9461c', '#522398', '#e27ea6', '#f9e300' ];
        var colorIndex = 0;

        var graftHistory = auditModule.graftHistory = { };

        for( var i = 0, ii = response.graftHistory.length; i < ii; i++ ) {

            var responseItem = response.graftHistory[ i ];
            var nodeId = responseItem.nodeId;

            var graftObj = responseItem;

            graftObj.color = colors[colorIndex]; graftObj.paths = { };
            
            graftObj.itemContainer =
                make('div').attr( { 'class': 'graftAuditContainer', 'editId': graftObj.editId } )
                           .css( { 'background-color': graftObj.color } )
                           .appendTo( auditModule.graftListContainer )
                           .bind( 'click', { auditModule: auditModule }, auditModule.handleItemClick );
            
            var infoContainer =
                auditModule[ [ graftObj.action, 'CreateInfoContainer'].join('') ]( {
                    treeViewer: treeViewer,
                    graftObj: graftObj } );

            graftObj.itemContainer.append( infoContainer ).expandable( { selector: '.detail' } );
            
            for( var j = 0, jj = treeViewer.columns.length; j < jj; j++ ) {

                var currentColumn = treeViewer.columns[j];

                if( currentColumn.nodeInfo[ nodeId ] ) {

                    if( graftObj.navigateToNodeOption ) {
                        graftObj.navigateToNodeOption.hide();
                    }

                    auditModule.addGraftIndication( { viewer: treeViewer, nodeId: nodeId, graftObj: graftObj } );
                }
                
            }

            colorIndex++;

            auditModule.graftHistory[ nodeId ] = graftObj;
        }
    },

   updateNavigateTo: function( p ) {

        var auditModule = this;
        var treeViewer = auditModule.treeViewer;
        var graftHistory = auditModule.graftHistory;

        for( var nodeId in graftHistory ) {

            var historyObj = graftHistory[ nodeId ];

            if( historyObj.navigateToNodeOption ) {

                var found = false;

                for( var i = 0, ii = treeViewer.currentColumnIndex; i <= ii; i++ ) { 

                    if( treeViewer.columns[i].nodeInfo[ nodeId ] ) {

                        if( historyObj.navigateToNodeOption.css('display') != 'none' ) {
                            historyObj.navigateToNodeOption.hide();
                        }
                        found = true;
                        break;
                    } 
                }

                if( (!found) && historyObj.navigateToNodeOption.css('display') == 'none' ) {
                    historyObj.navigateToNodeOption.show();
                }
            }
        }
   },

   addGraftIndication: function( p ) {

       var viewer = p.viewer;
       var curColumn = viewer.columns[ ( 'columnIndex' in p ) ? p.columnIndex : viewer.currentColumnIndex ];

       var nodeId = p.nodeId;
       var graftObj = p.graftObj;


       if( p.alreadyExists && graftObj.paths[ viewer.currentColumnIndex ] ) {        

           graftObj.paths[ viewer.currentColumnIndex ].remove();
       }

       if( curColumn.nodeInfo[ nodeId ].isCollapsed ) {
       
            curColumn.nodeInfo[ nodeId ].hiddenHover.el.css( BioSync.Common.createFlashyBorder( { color: graftObj.color } ) );

        } else {
                
            graftObj.paths[ viewer.currentColumnIndex ] =
                curColumn.canvas.path(
                    BioSync.TreeViewer.RenderUtil.Common.getCladePathString( {
                        node: curColumn.nodeInfo[ nodeId ],
                        nodeInfo: curColumn.nodeInfo } ) ).attr( { 'stroke': graftObj.color,
                                                                   'stroke-width': viewer.style.pathWidth } );
        }
   },

   resetModule: function( ) {

       var auditModule = this;

       var treeViewer = auditModule.treeViewer;

       auditModule.container.find('.disabledItem').removeClass('disabledItem').find('.colorIndicator').show();

       auditModule.container.find('.selectedItem').removeClass('selectedItem');

       auditModule.rollbackButton.addClass('disabledButton').unbind('click').text('Rollback');
       auditModule.saveButton.hide( 'slow' );

       var currentColumn = treeViewer.columns[0];

       for( var nodeId in auditModule.graftHistory ) {

           if( currentColumn.nodeInfo[ nodeId ] ) {

                auditModule.addGraftIndication( { viewer: treeViewer, nodeId: nodeId, graftObj: auditModule.graftHistory[ nodeId ] } );
            }
        }
   },
   
   undoRollback: function( p ) {
       
       var auditModule = p.data.auditModule;

       var domItem = auditModule.container.find('.selectedItem');
       var editId = domItem.attr('editId');

       if( domItem.next().length ) {

            $.ajax( { url: BioSync.Common.makeUrl( { controller: 'plugin_graftAudit', argList: [ 'rollbackGraft', domItem.next().attr('editId') ] } ),
                 type: "GET",
                 context: auditModule,
                 success: new Array( p.data.auditModule.handleRollbackResponse,
                                     function() { auditModule.rollbackSuccess( { editId: domItem.next().attr('editId') } ); } ) } );
       } else {

           $.ajax( { url: BioSync.Common.makeUrl( { controller: 'plugin_graftAudit', argList: [ 'undoRollback', auditModule.treeViewer.treeId ] } ),
                     type: "GET",
                     context: auditModule,
                     success: new Array( auditModule.handleRollbackResponse, auditModule.resetModule ) } );
       }
   },

   rollbackGraft: function( p ) {

       var auditModule = p.data.auditModule;

       var editId = auditModule.container.find('.selectedItem').attr('editId');

       var collapsedNodeIds = [ ];
       
       $('.columnWrapper').find('div.userCollapsed').each( function() { collapsedNodeIds.push( $(this).attr('nodeId') ); } );

       $.ajax( { url: BioSync.Common.makeUrl( { controller: 'plugin_graftAudit', argList: [ 'rollbackGraft', editId ] } ),
                 type: "GET",
                 context: auditModule,
                 data: { collapsedNodeIds: collapsedNodeIds.join(':') },
                 success: new Array( p.data.auditModule.handleRollbackResponse,
                                     function() { auditModule.rollbackSuccess( { editId: editId } ); } ) } );
   },

   rollbackSuccess: function( p ) {

       var auditModule = this;
       var editId = p.editId;
       
       var selector = [ '.graftAuditContainer[editId="', editId, '"]' ].join('');
       var domItem = auditModule.container.find( selector );

       auditModule.resetModule();

       domItem.addClass('disabledItem').find('.colorIndicator').hide();
       domItem.nextAll().addClass('disabledItem').find('.colorIndicator').hide();

       auditModule.saveButton.show( 'slow' );
   },

   handleRollbackResponse: function( response ) {

        var response = eval( "(" + response + ")" );

        var auditModule = this;
        var viewer = auditModule.treeViewer;

        response.viewer = viewer;
    
        viewer.renderUtil.updateColumns( { clickedIndex: -1, viewer: viewer } );
        auditModule.treeViewer.renderUtil.renderReceivedTree( response );
   },

   showSaveDialogue: function( p ) {

       var auditModule = p.data.auditModule;

       var make = BioSync.Common.makeEl;
       var form = BioSync.ModalBox;

       var content =
           make('div').append(
               form.makeBasicTextRow( { text: "Would you like to revert the current grafted tree to a former state ('edit'), \
                                               or would you prefer to create a new tree ('fork')" } ),
               form.makeRadioButtonRow( { name: 'saveType', options: [ { value: 'edit', text: 'Edit : ', func: function() { $('#forkContent').hide() }, default: true },
                                                                       { value: 'fork', text: 'Fork : ', func: function() { $('#forkContent').show() } } ] } ),
               form.makeHiddenInput( { name: 'editId', value: $( auditModule.container.find('.disabledItem')[0] ).attr('editId') } ),
               make('div').attr( { 'id': 'forkContent' } ).append(
                   form.makeBasicTextInput( { name: 'treeTitle', text: 'Tree Name : ', value: 'Untitled Grafted Tree' } ),
                   form.makeBasicLongTextInput( { name: 'treeComment', text: 'Tree Description : ', value: '' } )
               ).hide(),
               form.makeBasicActionRow( { submitText: 'Make Changes',
                                          submitArgs: { context: auditModule, onSuccess: auditModule.handleSaveAudit,
                                                        submitUrl: BioSync.Common.makeUrl( { controller: 'plugin_graftAudit', argList: [ 'saveChanges' ] } ) } } ) );

       BioSync.ModalBox.showModalBox( { title: 'Edit or Fork ?', content: content } );
   },

   handleSaveAudit: function( response ) {

        var response = eval( "(" + response + ")" );

        var auditModule = this;
        var viewer = auditModule.treeViewer;

        response.render.viewer = viewer;
    
        viewer.renderUtil.updateColumns( { clickedIndex: -1, viewer: viewer } );
        auditModule.treeViewer.renderUtil.renderReceivedTree( response.render );

        if( response.treeId != viewer.treeId ) {

            viewer.treeId = window.location.hash = response.treeId;
            
            auditModule.graftHistory = { };
            
            auditModule.reInitializeModule();
            
        } else {
       
            var deletedGraftItems = $('.graftAuditContainer.disabledItem');
            
            for( var i = 0, ii = deletedGraftItems.length; i < ii; i++ ) {
            
                var item = $( deletedGraftItems[ i ] );

                var editId = item.attr('editId');
                
                for( var nodeId in auditModule.graftHistory ) {
                
                    if( auditModule.graftHistory[ nodeId ].editId == editId ) {

                        delete auditModule.graftHistory[ nodeId ];
                        break;
                    }
                }
                
                item.empty().remove();
            }
        }
            
        auditModule.resetModule();
   }
}


BioSync.TreeViewer.RenderUtil.phylogram.navigate.expandNode = function( p ) {

    var viewer = p.data.viewer;
    
    viewer.renderUtil.updateColumns( { clickedIndex: p.data.columnIndex, viewer: viewer } );

    var revertInfo = $('.graftAuditContainer.disabledItem');

    var requestData = ( viewer.treeType == 'grafted' )
        ? ( revertInfo.length ) ? { controller: 'plugin_graftAudit', editId: $( revertInfo[0] ).attr('editid') }
                                : { controller: 'plugin_treeGrafter' }
        : { controller: 'plugin_treeViewer' };

    requestData.nodeId = p.data.nodeId;
    
    $.ajax( { url: BioSync.Common.makeUrl( { controller: requestData.controller, argList: [ 'navigateExpandNode' ] } ),
              type: "GET",
              context: viewer,
              data: requestData,
              success: new Array( viewer.handleReceivedTree,
                                  function() { viewer.renderUtil.addAnimations( { viewer: viewer, clickedHover: $(p.target).closest('div.hiddenHover') } );
                                               viewer.container.trigger('expandNodeSuccess', { } ); },
                                  ( p.success ) ? p.success : function() { },
                                  viewer.renderUtil.checkForCollapsedGraftClade ) } );
                
    $('body').find('div.expandOptionContainer:visible').hide();
}
