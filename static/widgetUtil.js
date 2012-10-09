function widgetResponseHandler( widgetName, data ) { 

    $.ajax( { url: makeUrl( { 'argList': [ widgetName + '.js?ts=' + new Date().getTime() ], controller: 'static' } ),
              dataType: 'script',
              async: false } );


    var func = widgetName + 'Init';

    window[ func ]( data );
}
