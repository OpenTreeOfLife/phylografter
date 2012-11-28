BioSync = {};

BioSync.Common = {

	applicationName: '',

    scrollbarWidth: undefined,

    //libraries: [ 'optionsMenu', 'modalBox', 'raphael' ],
    libraries: [ 'modalBox', 'raphael' ],

    symbolDragInfo: undefined,

    style: { fontFamily: 'Verdana', fontSize: 12 },

    htmlCodes: { check: '&#x2713;' },

    events: {

        logout: {
            handler: function() { window.location = BioSync.Common.makeUrl( { controller: 'user', argList: [ 'logout' ] } ) },
            text: 'Logout'
        },

        addTree: {
            handler: function() { BioSync.ModalBox.showModalBox( { content: BioSync.Common.events.addTree.modalContent(), title: 'Add Tree' } ); },
            text: 'Add Tree',
            modalContent: function() {
               return BioSync.Common.makeEl('div').append(
                    BioSync.ModalBox.makeBasicTextInput( { 'name': 'treeName', 'text': 'Name : ', value: '' } ),
                    BioSync.ModalBox.makeBasicTextInput( { 'name': 'newick', 'text': 'Newick : ', value: '' } ),
                    BioSync.ModalBox.makeBasicActionRow( { 'submitText': 'Add', 'submitArgs': { trigger: 'treeAdded', 'submitUrl': BioSync.Common.makeUrl( { argList: [ 'addTree' ] } ) } } ) ); }
        }
    }
};

BioSync.Common.loadLibs = function( libraries ) {

    BioSync.Common.applicationName = applicationName;
    delete applicationName;

    for( var i = 0, ii = libraries.length; i < ii; i++ ) {
        BioSync.Common.loadScript( { name: libraries[i] } );
        BioSync.Common.loadCSS( { name: libraries[i] } );

        if( libraries[i] == 'raphael' ) {

            Raphael.fn.circlePath = function(x, y, r) {      
                var s = "M" + x + "," + (y-r) + "A"+r+","+r+",0,1,1,"+(x-0.1)+","+(y-r)+" z";   
                return s;
            }

            Raphael.fn.quarterCirclePath = function(x, y, r, id) {
                if( id == 0 ) {
                    x1 = x; y1 = y - r; x2 = x+r; y2 = y; rot = r;
                } else if( id == 1 ) {
                    x1 = x+r; y1 = y; x2 = x; y2 = y+r; rot = r;
                } else if( id == 2 ) {
                    x1 = x; y1 = y+r; x2 = x-r; y2 = y; rot = -r;
                } else if( id == 3 ) {
                    x1 = x-r; y1 = y; x2 = x; y2 = y-r; rot = -r;
                }
                    
                var s = [ 'M', x1, y1, 'A', r, r, r, 0, 1, x2, y2 ].join(' ');
                return s;
            }
        }
    }
}

BioSync.Common.loadScript = function( p ) {

    $.ajax( { url: BioSync.Common.makeUrl( { 'argList': [ p.name + '.js?ts=' + new Date().getTime() ], controller: 'static' } ),
              dataType: 'script',
              async: false } );
};

BioSync.Common.loadCSS = function( p ) {

    $.get( BioSync.Common.makeUrl( { 'argList': [ p.name + '.css?ts=' + new Date().getTime() ], controller: 'static' } ), BioSync.Common.loadCSSHelper );
};

BioSync.Common.loadCSSHelper = function( css ) {
    
    $('<style type="text/css"></style>').html( css ).appendTo( 'head' ); 
};

BioSync.Common.preventDefault = function( e ) { e.preventDefault(); }

BioSync.Common.makeEl = function( elementName ) { return $(document.createElement(elementName)); };

BioSync.Common.makeUrl = function( p ) {

    var url = new BioSync.Common.StringBuffer();

    var controller = ( p.controller ) ? p.controller : 'default';
    
    url.append('/').append( BioSync.Common.applicationName ).append('/').append( controller );
    
    for( var i = 0, ii = p.argList.length; i < ii; i++ ) { url.append('/').append( p.argList[i] ); }

    return url.toString();
}

BioSync.Common.isMouseOnElement = function( p ) {

    var elementOffset = p.el.offset();

    if( p.x < elementOffset.left || p.y < elementOffset.top ||
        p.x > ( elementOffset.left + p.el.outerWidth( true ) ) ||
        p.y > ( elementOffset.top + p.el.outerHeight( true ) ) ) { 

            return false;

    } else { return true; }
}

BioSync.Common.removeDragHighlight = function( p ) {

    if( p.el.hasClass('dragHighlight') ) { p.el.removeClass('dragHighlight'); }
}

BioSync.Common.StringBuffer = function() {

    return function() { this.buffer = []; }

}();

BioSync.Common.StringBuffer.prototype = {

    append: function( string ) {
                this.buffer.push( string ); return this;
            },

    toString: function() { return this.buffer.join(""); }
};

BioSync.Common.getFakeUID = function() {
    
    var S4 = function() { return (((1+Math.random())*0x10000)|0).toString(16).substring(1); }
           
    return (S4()+S4()+"-"+S4()+"-"+S4()+"-"+S4()+"-"+S4()+S4()+S4());
}

BioSync.Common.returnFalse = function() { return false; }

//don't like these
BioSync.Common.addHoverPointer = function( p ) { if( p.data.el ) { p.data.el.addClass('pointer'); } else { $(this).addClass('pointer'); } }
BioSync.Common.removeHoverPointer = function( p ) { if( p.data.el ) { p.data.el.removeClass('pointer'); } else { $(this).removeClass('pointer'); } }
//

BioSync.Common.applySymbolDrag = function( p ) { p.el.bind( 'mousedown', p, BioSync.Common.setSymbolDragInfo ); }

BioSync.Common.setSymbolDragInfo = function( p ) { BioSync.Common.symbolDragInfo = p.data; }

BioSync.Common.checkForSymbolDrag = function( p ) {

    var info = BioSync.Common.symbolDragInfo;

    if( ! info ) { return; }

    $('body').css( { cursor: 'pointer' } );

    info.img.css( { top: p.pageY - 30, left: p.pageX - 30 } ).show();

    $(document).trigger( info.moveFunc, [ { x: p.pageX - 15, y: p.pageY - 15 } ] );
}

BioSync.Common.checkForSymbolDrop = function( p ) {

    var info = BioSync.Common.symbolDragInfo;
    
    if( ! info ) { return; }
    
    $('body').css( { cursor: 'auto' } );

    info.dropParams.dropCoords = { x: p.pageX - 15, y: p.pageY - 15 };

    $(document).trigger( info.dropFunc, [ info.dropParams ] );

    info.img.hide();

    BioSync.Common.symbolDragInfo = undefined;
}

BioSync.Common.handleBothClicks = function( p ) {

    if( p.which == 1 ) { p.data.left.func( p.data.left.params ); }
    else if( p.which == 3 ) { p.data.right.func( p.data.right.params ); }
}

BioSync.Common.showItem = function( p ) { $( this ).find( p.data.selector ).show(); }
BioSync.Common.hideItem = function( p ) { $( this ).find( p.data.selector ).hide(); }

BioSync.Common.getScrollbarWidth = function() {
    var $div = $('<div />')
        .css({ width: 100, height: 100, overflow: 'auto', position: 'absolute', top: -1000, left: -1000 })
        .prependTo('body').append('<div />').find('div')
        .css({ width: '100%', height: 200 });
    BioSync.Common.scrollbarWidth = ( 100 - $div.width() );
    $div.parent().remove();
}

BioSync.Common.setScrollbarWidth = function() {
    
    $.ajax( { url: BioSync.Common.makeUrl( { 'argList': [ 'setScrollbarWidth' ], controller: 'plugin_common' } ),
              data: { width: BioSync.Common.scrollbarWidth } } );
}

BioSync.Common.setSessionWindowDimensions = function() {

    $.ajax( { url: BioSync.Common.makeUrl( { 'argList': [ 'setSessionWindowDimensions' ], controller: 'plugin_common' } ),
              data: { width: $(window).width(), height: $(window).height() } } );
}

BioSync.Common.notify = function( p ) {

    var make = BioSync.Common.makeEl;
    var id = BioSync.Common.getFakeUID();

    if( ! BioSync.Common.notifyInfo ) { BioSync.Common.notifyInfo = { }; }

    BioSync.Common.notifyInfo[ id  ] = { };

    var appendToElement = $('body');

    if( p.appendTo ) { appendToElement = p.appendTo; }

    var notifyContainer = make('div').attr( { class: 'notifyBox' } ).appendTo( appendToElement ).hide();

    var notifyContent =  undefined;
    
    if( p.content ) {

        notifyContent = make('div').attr( { 'class': 'notifyContent' } ).append( p.content ).appendTo( notifyContainer);

    } else {

        notifyContent = make('div').attr( { 'class': 'notifyContent' } )
                            .text( p.text ).appendTo( notifyContainer );
    }

    BioSync.Common.notifyInfo[id].container = notifyContainer;
    BioSync.Common.notifyInfo[id].content = notifyContent;

    notifyContainer.css( { 'top': p.y, 'left': p.x - ( notifyContainer.width() / 2 ) } );

    notifyContainer.fadeIn( 1000 );

    if( p.dotdotdot ) {
        BioSync.Common.notifyInfo[ id ].curDotDotDot = '';
        BioSync.Common.notifyInfo[ id ].originalText = p.text;

        BioSync.Common.notifyInfo[ id ].dotDotDotTimeout = setTimeout( $.proxy( BioSync.Common.DoDotDotDot, BioSync.Common.notifyInfo[id] ), 1000 );
    }

    if( p.timeoutTrigger ) {

        $( document ).bind( p.timeoutTrigger, { }, $.proxy( this.closeNotifyBox, BioSync.Common.notifyInfo[id] ) );
        BioSync.Common.notifyInfo[id].trigger = p.timeoutTrigger;

    } else {

        setTimeout( $.proxy( BioSync.Common.closeNotifyBox, BioSync.Common.notifyInfo[id] ), ( p.timeout ) ? p.timeout : 5000 );
    }
}

BioSync.Common.DoDotDotDot = function() {

    this.curDotDotDot = ( this.curDotDotDot == '' )
        ? '.'
        : ( this.curDotDotDot == '.' )
            ? '. .'
            : ( this.curDotDotDot == '. .' )
                ? '. . .'
                : '';

    this.content.text( [ this.originalText, this.curDotDotDot ].join('') );

    this.dotDotDotTimeout = setTimeout( $.proxy( BioSync.Common.DoDotDotDot, this ), 250 );
}

BioSync.Common.dotDotDotText = function( p ) {

    var dotEl = this.makeEl('div').attr( { 'class': 'dotContainer' } ).appendTo( $('body') );

    BioSync.Common.dotInfo = {
        curDot: '',
        dotContainer: dotEl,
        originalText: p.content.text(),
        stopText: p.stopText,
        content: p.content,
        textCoords: { },
        stopFunction: p.stopFunction,
        minimumTime: p.minimumTime,
        startTime: new Date().getTime() };
        
    var textCoords = BioSync.Common.dotInfo.textCoords;

    this.storeObjPosition( $( p.content.children()[0]), textCoords );

    dotEl.css( { 'left': textCoords.myOffset.left + textCoords.myWidth,
                 'top': textCoords.myOffset.top + ( textCoords.myHeight / 4 ) } ).height( textCoords.myHeight );


    if( p.content.css('font-size') ) { dotEl.css( { 'font-size': p.content.css( 'font-size' ) } ); }

    BioSync.Common.dotInfo.timeout = setTimeout( $.proxy( BioSync.Common.doDotDotDotText, BioSync.Common.dotInfo ), 250 );

    $( document ).bind( p.stopTrigger, { }, $.proxy( BioSync.Common.stopDotDotDotText, BioSync.Common.dotInfo ) );
}

BioSync.Common.doDotDotDotText = function() {

    this.curDot = ( this.curDot == '' )
        ? '.'
        : ( this.curDot == '.' )
            ? '. .'
            : ( this.curDot == '. .' )
                ? '. . .'
                : '';

    this.dotContainer.text( this.curDot );

    this.timeout = setTimeout( $.proxy( BioSync.Common.doDotDotDotText, this ), 250 );
}

BioSync.Common.stopDotDotDotText = function() {

    if( this.minimumTime ) {
        
        var time = new Date().getTime();
        
        var difference = this.minimumTime - ( time - this.startTime );
      
        if( difference > 100 ) {
            
            setTimeout( $.proxy( BioSync.Common.actuallyStopDotDotDotText, BioSync.Common.dotInfo ), difference );

            return;
        }
    }

    $.proxy( BioSync.Common.actuallyStopDotDotDotText, BioSync.Common.dotInfo )();
}

BioSync.Common.actuallyStopDotDotDotText = function() {
    
    clearTimeout( this.timeout );
    this.dotContainer.remove();

    if( this.stopFunction ) {
       
        for( var i = 0, ii = this.stopFunction.length; i < ii; i++ ) {

            this.stopFunction[i]();
        }
    } 

    if( this.stopText ) {

        this.content.text( this.stopText );
    }
}

BioSync.Common.closeNotifyBox = function() {

    this.container.empty().remove();

    if( this.dotDotDotTimeout ) { clearTimeout( this.dotDotDotTimeout ); }

    if( this.trigger ) {    
      
        $( document ).unbind( this.trigger );
    }

    delete this;
}

BioSync.Common.showSubMenu = function( p ) { $( $(this).find('.menu')[0] ).show(); return true; }
BioSync.Common.hideSubMenu = function( p ) { $( $(this).find('.menu')[0] ).hide(); return true; }

BioSync.Common.makeButtonOptionMenu = function( p ) {

    var make = this.makeEl;

    var menu = make('div').attr( { 'class': 'menu' } ).appendTo( p.button );

    for( var i = 0, ii = p.options.length; i < ii; i++ ) {
        p.options[i].container = menu;
        menu.append(
            ( p.options[i].hoverMenu )
                ? this.makeHoverOptionMenu( p.options[i] )
                : this.makeOptionItem( p.options[i] ) );
    }

    var mostWidth = 0;

    $.each( menu.children(), function() { if( $(this).outerWidth(true) > mostWidth ) { mostWidth = $(this).outerWidth(true); } } );

    menu.children().width( mostWidth );

    return menu;
}

BioSync.Common.makeHoverOptionMenu = function( p ) {

    var make = this.makeEl;

    var menuWrapper =
        make('div').attr( { 'class': 'menuOptionItem' } )
                   .css( { margin: 4, padding: 4 } )
                   .hover( BioSync.Common.showSubMenu, BioSync.Common.hideSubMenu )
                   .text( p.text )
                   .appendTo( p.container );

    var menu = make('div').attr( { 'class': 'menu' } ).appendTo( menuWrapper );

    for( var i = 0, ii = p.options.length; i < ii; i++ ) {
        p.options[i].container = menu;
        menu.append(
            ( p.options[i].hoverMenu )
                ? this.makeHoverOptionMenu( p.options[i] )
                : this.makeOptionItem( p.options[i] ) );
    }

    var mostWidth = 0;

    $.each( menu.children(), function() { if( $(this).outerWidth(true) > mostWidth ) { mostWidth = $(this).outerWidth(true); } } );

    menu.children().width( mostWidth );

    menuWrapper.append( menu );
    setTimeout( function() { menu.css( { top: 0, left: menuWrapper.outerWidth( true ) } ); }, 1000 );

    menu.hide();

    return menuWrapper
}

BioSync.Common.makeOptionItem = function( p ) {

    var item = this.makeEl('div').attr( { 'class': 'menuOptionItem' } )
                                 .css( { margin: 4, padding: 4 } ).html( p.text );

    for( var i = 0, ii = p.func.length; i < ii; i++ ) {

        item.bind( 'click', p.funcParams, p.func[i] );
    }

    return item;
}

BioSync.Common.capitalizeFirstLetter = function( p ) { return p.charAt(0).toUpperCase() + p.slice(1); }

BioSync.Common.hexToRGB = function( p ) {

    var hex = p.hex.substring( 1, 7 );

    return [ 'rgba(',
             [ parseInt( hex.substring( 0, 2 ), 16 ),
               parseInt( hex.substring( 2, 4 ), 16 ),
               parseInt( hex.substring( 4, 6 ), 16 ),
               p.opacity ].join(','),
             ')' ].join('');
}

BioSync.Common.removeFlashyBorder = function( p ) {

    return { 'box-shadow': '',
             '-webkit-box-shadow': '',
             '-moz-box-shadow': '',
             'border': '' };
}

BioSync.Common.createFlashyBorder = function( p ) {

    return { 'box-shadow': [ '0 0 5px ', this.hexToRGB( { hex: p.color, opacity: 1 } ) ].join(''),
             '-webkit-box-shadow': [ '0 0 5px ', this.hexToRGB( { hex: p.color, opacity: 1 } ) ].join(''),
             '-moz-box-shadow': [ '0 0 5px ', this.hexToRGB( { hex: p.color, opacity: 1 } ) ].join(''),
             'border': [ '2px solid ', this.hexToRGB( { hex: p.color, opacity: .8 } ) ].join('') };
}

BioSync.Common.jsEventUnWrapper = function( p ) { p.data.func( p.data.params ); }

jQuery.fn.expandable = function() {

    var el = $( this[0] ).addClass('relative');
    var p = arguments[0];

    var make = BioSync.Common.makeEl;

    var elHeight = el.height();
    var elWidth = el.width();

    var imgLength = elHeight - 5;

    var downUrl = BioSync.Common.makeUrl( { controller: 'static', argList: [ 'images', 'downArrowUI.png' ] } );
    var downHoverUrl = BioSync.Common.makeUrl( { controller: 'static', argList: [ 'images', 'downArrowHoverUI.png' ] } );
    var upUrl = BioSync.Common.makeUrl( { controller: 'static', argList: [ 'images', 'upArrowUI.png' ] } );
    var upHoverUrl = BioSync.Common.makeUrl( { controller: 'static', argList: [ 'images', 'upArrowHoverUI.png' ] } );

    el.append(
        make('img').attr( { 'class': 'absolute hoverPointer', 'src': downUrl } )
                   .height( imgLength ).width( imgLength )
                   .css( { left: elWidth - imgLength - 5, top: 5 } )
                   .hover( function() { $(this).attr( 'src', ( $(this).attr('src').search('down') > 0 ) ? downHoverUrl : upHoverUrl ); },
                           function() { $(this).attr( 'src', ( $(this).attr('src').search('down') > 0 ) ? downUrl : upUrl ); } )
                   .click( function( e ) { el.find( p.selector ).toggle('slow');
                                           $(this).attr( 'src', ( $(this).attr('src').search('down') > 0 ) ? upUrl : downUrl ); e.stopPropagation(); } ) ); 
    
    return el;
};

jQuery.fn.draggable = function() {

    var el = $( this[0] );
    var p = arguments[0];

    if( el.hasClass('draggable') ) { el.removeClass('draggable').unbind('mousedown'); }

    el.addClass('draggable').bind( 'mousedown', { },
        function() { BioSync.Common.domDragInfo = {
            el: el, receptacle: p.receptacle, receptacleFun: p.receptacleFun, receptacleFunParams: p.receptacleFunParams,
            yOff: el.outerHeight( true ) / 2, xOff: el.outerWidth( true ) / 2 }; } )

    return el;
};

BioSync.Common.checkForDomDrag = function( e ) {

    var info = BioSync.Common.domDragInfo;

    if( !info ) { return; }
    
    $('body').css( { cursor: 'pointer' } );

    if( ! info.dragEl ) {

        info.dragEl = info.el.clone().css( { 'z-index': '5000' } ).addClass('absolute').appendTo( $('body') );
        info.el.hide();
        $('body').css( { '-moz-user-select': 'none',
                         '-webkit-user-select': 'none',
                         '-khtml-user-select': 'none' } );
    }

    info.dragEl.css( { top: e.pageY - info.yOff, left: e.pageX - info.xOff } );

    if( BioSync.Common.isMouseOnElement( { el: info.receptacle, x: e.pageX, y: e.pageY } ) ) {
        info.receptacle.css( BioSync.Common.createFlashyBorder( { color: '#00BFFF' } ) );
    } else {
        info.receptacle.css( BioSync.Common.removeFlashyBorder( { color: '#00BFFF' } ) );
    }
}

BioSync.Common.checkForDomDrop = function( e ) {

    var info = BioSync.Common.domDragInfo;
    
    if( ! info ) { return; }
    
    info.dragEl.empty().remove();
    
    $('body').css( { cursor: 'auto' } );

    if( BioSync.Common.isMouseOnElement( { el: info.receptacle, x: e.pageX, y: e.pageY } ) ) {
        info.receptacleFun( info.receptacleFunParams );
    } else {
        info.el.show('slow');
    }

    info.receptacle.css( BioSync.Common.removeFlashyBorder( { color: '#00BFFF' } ) );

    delete BioSync.Common.domDragInfo;
}

BioSync.Common.setTextWidthMetric = function() {

    var canvas = Raphael( $('body').get(0), 300, 100 );

    var label = canvas.text( 10, 10, 'aaaaa' )
                      .attr( { stroke: 'black',
                               "font-family": BioSync.Common.style.fontFamily,
                               "font-size": BioSync.Common.style.fontSize } );

    var box = label.getBBox();
    label.remove();

    $.ajax( { url: BioSync.Common.makeUrl( { 'argList': [ 'setTextWidthMetric' ], controller: 'plugin_common' } ),
              data: { width: ( box.width / 5 ) } } );

    //canvas.canvas.parentElement.removeChild( canvas.canvas );
    canvas.remove();
}

BioSync.Common.setPageHeight = function() {

    if( $('#page').height() ) {

        $.ajax( { url: BioSync.Common.makeUrl( { 'argList': [ 'setPageHeight' ], controller: 'plugin_common' } ),
                  data: { pageHeight: $('#page').height() } } );
    }
}

BioSync.Common.storeObjPosition = function( obj, location ) {
    
    location.myWidth = obj.outerWidth( true );
    location.myHeight = obj.outerHeight( true );
    location.myOffset = obj.offset();
    location.myPosition = obj.position();
    location.myBottom = location.myOffset.top + location.myHeight;
    location.myRight = location.myOffset.left + location.myWidth;

}

BioSync.Common.isContextMenuVisible = function() {

    if( $('#contextMenu:visible').length ) { return true; }
    
    if( $('.contextMenu:visible').length ) { return true; }
}

BioSync.Common.disableSelection = function( el ) {

    el.attr( 'unselectable', 'on')
      .css( { '-moz-user-select':'none',
              '-webkit-user-select':'none',
              'user-select':'none' } ).onselectstart = function() { return false; }
}

BioSync.Common.getDistance = function( p ) {

    return Math.sqrt( Math.pow( p.point1.x - p.point2.x, 2) + Math.pow( p.point1.y - p.point2.y, 2) );
}

BioSync.Common.removeTextFirstFocus = function( p ) {

    p.el.addClass('initialLabelInput').bind( 'focus', { }, $.proxy( this.unbindFirstFocus, p.el ) );
}

BioSync.Common.unbindFirstFocus = function() {

    this.val('').removeClass('initialLabelInput').unbind( 'focus', { }, $.proxy( BioSync.Common.unbindFirstFocus, this ) );
}

BioSync.Common.setMouseToPointer = function() { document.body.style.cursor = 'pointer'; }
BioSync.Common.setMouseToDefault = function() { document.body.style.cursor = 'default'; }

BioSync.Common.underlineText = function() { $( this ).css( { 'text-decoration': 'underline' } ); }
BioSync.Common.removeTextUnderline = function() { $( this ).css( { 'text-decoration': 'none' } ); }

BioSync.Common.isModalBoxVisible = function() { return $('#modalBoxContainer').is(':visible'); }

$(document).mousemove( BioSync.Common.checkForSymbolDrag );
$(document).mousemove( BioSync.Common.checkForDomDrag );

$(document).mouseup( BioSync.Common.checkForSymbolDrop );
$(document).mouseup( BioSync.Common.checkForDomDrop );

BioSync.Common.loadLibs( BioSync.Common.libraries );
$( BioSync.Common.getScrollbarWidth );
$( BioSync.Common.setScrollbarWidth );
$( BioSync.Common.setSessionWindowDimensions );
$( BioSync.Common.setTextWidthMetric );
//$( BioSync.Common.setPageHeight );

