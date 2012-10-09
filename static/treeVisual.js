
var labels = [ ];

function treeVisualInit( p ) {

    $('#' + p.containerId).append(
        makeEl('div').attr( { 'id': 'raphaelWrapper', 'class': 'scrollable fullWidth fullHeight' } ).append(
            makeEl('div').attr( { 'id': 'raphaelContainer' } ) ) );

    tree = p.treeInfo.tree;
    treeId = p.treeInfo.id;

    var generationSeparation = 20;
    var nodeSeparation = 20;
    var buffer = 100;

    treeInfo = getTreeInfo( { node: tree } );

    var canvasWidth = ( ( generationSeparation * treeInfo.depth ) + ( buffer * 2 ) );
    var canvasHeight = ( ( nodeSeparation * treeInfo.tips ) + ( buffer * 2 ) );

    $('#raphaelContainer').width( canvasWidth ).height( canvasHeight );
    var r = Raphael( 'raphaelContainer', canvasWidth, canvasHeight );

    var pathString = new StringBuffer();

    buildTreePathString( { node: tree, currentTip: { x: canvasWidth - buffer, y: buffer }, generationSeparation: generationSeparation, depth: treeInfo.depth, nodeSeparation: nodeSeparation, pathString: pathString } );

    r.path( pathString ).attr( { stroke: 'black', "stroke-width": 2 } );
   
    var labelClickHandler = function() { };

    if( p.treeInfo.events && p.treeInfo.events.handleLabelClick ) {
    
        $.ajax( { url: makeUrl( { 'argList': [ p.treeInfo.events.handleLabelClick + '.js?ts=' + new Date().getTime() ], controller: 'static' } ),
                  dataType: 'script',
                  async: false } );

        labelClickHandler = window['handleLabelClick'];
    }


    renderLabels( { canvas: r, labels: labels, index: 0, onClick: labelClickHandler } );

}

function getTreeInfo( p ) {

    var myTraversal = p.node.length;
    var tips = 0;
    var myDepth = 1;
    var myTipLabel = '';

    var childLength = p.node.children.length;

    if( childLength ) {

        var returnedInfo = [];
        var longestTraversal = 0;
        var longestTipLabel = 0;
        var mostDepth = 0;

        for( var i = 0, ii = childLength; i < ii; i++ ) {

            returnedInfo.push( getTreeInfo( { 'node': p.node.children[i] } ) );

            if( returnedInfo[i].longestTipLabel.length > longestTipLabel ) {
                longestTipLabel = returnedInfo[i].longestTipLabel;
            }

            if( returnedInfo[i].traversal > longestTraversal ) {
                longestTraversal = returnedInfo[i].traversal;
            }

            if( returnedInfo[i].depth > mostDepth ) {
                mostDepth = returnedInfo[i].depth;
            }

            tips = tips + returnedInfo[i].tips;
        }

        myTraversal = myTraversal + longestTraversal;
        myDepth = myDepth + mostDepth;
        myTipLabel = longestTipLabel;

    } else {

        if( p.node.label ) { myTipLabel = p.node.label; }

        tips = tips + 1;
    }

    return { traversal: myTraversal,
             depth: myDepth,
             longestTipLabel: myTipLabel,
             tips: tips };
}

function buildTreePathString( p ) {

    for( var i = 0, ii = p.node.children.length; i < ii; i++ ) {

        buildTreePathString( { node: p.node.children[i], currentTip: p.currentTip, generationSeparation: p.generationSeparation, depth: p.depth-1, nodeSeparation: p.nodeSeparation, pathString: p.pathString  } );
    } 

    assignUnscaledNodeCoords( p );

    if( p.node.label ) { labels.push( { x: p.node.coords.unscaled.x, y: p.node.coords.y, text: p.node.label, nodeId: p.node.id } ); }

    addNodeToPathString( { node: p.node, pathString: p.pathString } );
}


function assignUnscaledNodeCoords( p ) {

    p.node.coords = { unscaled: undefined };

    var childCount = p.node.children.length;

    if( childCount ) {

        var firstChildCoords = p.node.children[0].coords;

        p.node.coords.unscaled = { x: firstChildCoords.unscaled.x + firstChildCoords.unscaled.dx,
                                  dx: -( p.generationSeparation ) };

        p.node.coords.y = ( ( p.node.children[ childCount - 1 ].coords.y + firstChildCoords.y ) / 2 );

    } else {

        p.node.coords.unscaled = { x: p.currentTip.x, dx: -( p.generationSeparation * p.depth ) };
        
        p.node.coords.y = p.currentTip.y;

        p.currentTip.y = p.currentTip.y + p.nodeSeparation;
    }
}


function addNodeToPathString( p ) {

    var childCount = p.node.children.length;

    var coords = { x: p.node.coords.unscaled.x,
                  dx: p.node.coords.unscaled.dx,
                   y: p.node.coords.y };

    p.pathString.append( "M" ).append( coords.x ).append( " " ).append( coords.y ).append( "l" ).append( coords.dx ).append( " 0" );

    if( childCount ) {

        var firstChildY = p.node.children[0].coords.y;
        var lastChildY = p.node.children[ childCount-1 ].coords.y;

        p.pathString.append( "M" ).append( coords.x ).append( " " ).append( firstChildY )
                    .append( "L" ).append( coords.x ).append( " " ).append( lastChildY );
    }
}


function renderLabels( p ) { asyncRenderLabel( p ); }


function asyncRenderLabel( p ) {

    var label = p.labels[ p.index++ ];
    var pad = 3;
    var raphaelLabel = p.canvas.text( label.x+pad, label.y, label.text )
                               .attr( { stroke: 'black',
                                        fill: 'black',
                                        "font-family": 'arial',
                                        "font-size": 12,
                                        "text-anchor": "start" } );
    
    $(raphaelLabel.node).attr( { 'nodeId': label.nodeId, 'type':'raphaelLabel', "id": 'label'+label.nodeId } )
                        .bind( 'click', p.onClick );

    if( p.index < p.labels.length ) {

        setTimeout( asyncRenderLabel, 0, { labels: p.labels, index: p.index, canvas: p.canvas, onClick: p.onClick } );

    } else {

        delete labels;
    }

}
