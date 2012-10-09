function updateLabel( p ) {

    var p = eval( "(" + p + ")" );

    var labels = $('svg text');
    var label = undefined;

    for( var i = 0, ii = labels.length; i < ii; i++ ) {
        if( $(labels[i]).attr('nodeId') == p.nodeId ) { label = labels[i]; break; }
    }

    $(label).children('tspan').text( p.label );   
}

function getNodeInfo( p ) {
    
    $.ajax( { url: makeUrl( { controller: "stree", argList: [ 'getNodeInfo' ] } ),
              type: "POST",
              data: { nodeId: p.data.nodeId },
              success: p.data.success } );
}

function handleLabelClick( p ) {

    var nodeId = $(this).attr('nodeId');

    getModalContent( { data: { contentUrl: makeUrl( { 'controller': 'modal', argList: [ 'editSnodeTaxon', nodeId ] } ),
                               success: { func: getNodeInfo, args: { nodeId: nodeId, success: updateLabel } } } } );
}



