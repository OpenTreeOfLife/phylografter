BioSync.OptionsMenu = {};

BioSync.OptionsMenu.makeOptionsMenu = function( p ) {

    var make = BioSync.Common.makeEl;

    var button = make('span').attr( { 'class': 'menuLabel' } ).text( p.label );

    if( p.type == 'hover' ) {
        button.hover( BioSync.OptionsMenu.showMenu, BioSync.OptionsMenu.hideMenu );
    } else if( p.type == 'click' ) {
        button.click( BioSync.OptionsMenu.toggleMenu );
    }

    $( '#' + p.containerId ).append( button );
    
    var buttonOffset = button.offset();

    var menu = make( 'ul' ).attr( { 'class': 'contextMenu' } )
                           .hide()
                           .css( { top: buttonOffset.top + button.height(), left: buttonOffset.left } );


   for( var i = 0, ii = p.eventInfo.length; i < ii; i++ ) {

       menu.append( BioSync.OptionsMenu.makeMenuItem( { event: p.eventInfo[i] } ) );
   }

   return button.append( menu );

};

BioSync.OptionsMenu.makeContextMenu = function( p ) {

    var make = BioSync.Common.makeEl;
   
    var menu = make( 'div' ).attr( { 'id': 'contextMenu', 'class': 'contextMenu' } )
                            .css( { top: p.coords.y, left: p.coords.x } );

    var list = make( 'ul' ).attr( { 'class': 'contextMenuList' } ).appendTo( menu );
   
   for( var i = 0, ii = p.options.length; i < ii; i++ ) {

       list.append( BioSync.OptionsMenu.makeMenuItem( { event: p.options[i] } ).bind( 'click', { }, BioSync.OptionsMenu.closeContextMenu ) );
   }

   $('body').append( menu );

   $(document).bind( 'click', { clickAway: p.clickAway }, BioSync.OptionsMenu.checkForContextMenuClick );
}

BioSync.OptionsMenu.checkForContextMenuClick = function( p ) {

    if( ! BioSync.Common.isMouseOnElement( { el: $('#contextMenu'), x: p.pageX, y: p.pageY } ) ) {

        BioSync.OptionsMenu.closeContextMenu();

        if( p.data.clickAway ) { p.data.clickAway(); }
    }
}

BioSync.OptionsMenu.closeContextMenu = function() {

    $('#contextMenu').empty().remove();
    $(document).trigger('contextMenuClosed');
    $(document).unbind( 'click', BioSync.OptionsMenu.checkForContextMenuClick );
}

BioSync.OptionsMenu.toggleMenu = function() {
    $(this).children('ul').toggle();
}

BioSync.OptionsMenu.showMenu = function() {
    $(this).children('ul').show();
}

BioSync.OptionsMenu.hideMenu = function() {
    $(this).children('ul').hide();
}

BioSync.OptionsMenu.highlightItem = function() {
    $(this).addClass('highlight');
}

BioSync.OptionsMenu.removeHighlight = function() {
    $(this).removeClass('highlight');
}

BioSync.OptionsMenu.makeMenuItem = function( p ) {

    var text = ( p.event.text ) ? p.event.text : BioSync.Common.events[p.event].text;
    var handler = ( p.event.action ) ? p.event.action : BioSync.Common.events[p.event].handler;
    var params = ( p.event.params ) ? p.event.params : { };

    return BioSync.Common.makeEl( 'li' ).attr( { 'class': 'contextMenuItem' } )
                                        .mouseover( BioSync.OptionsMenu.highlightItem )
                                        .mouseout( BioSync.OptionsMenu.removeHighlight )
                                        .text( text )
                                        .bind( 'click', params, handler );
}

BioSync.OptionsMenu.hideContextMenu = function() { $('.contextMenu').hide(); $('#contextMenu').hide(); }
