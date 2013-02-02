//This contains javascript code for modal displays.  A modal window is a child window that requires the user to interact with it before the rest of the application.  In phylografter, the modal window is used in parallel with a semi-transparent, black layer just behind the modal window.  This is one of the first logical separations of javascript I did with phylografter, and, its not very elegantly coded or objectified.  Sorry.

//A place to store information
BioSync.ModalBox = {};

//Currently, in phylografter, this page is loaded through BioSync.Common.loadLibs in static/plugin_common.js.  This function is called when the document is ready ( as defined by jquery ).  See the bottom of this page for the function call.  It simply creates the DOM elements needed for the framework of the modal dialogue.
BioSync.ModalBox.initialize = function( p ) {

    var make = BioSync.Common.makeEl;

    $('body').append(
        make('div').attr( { 'id': 'modalBoxContainer' } ).append(
            make('div').attr( { 'class': 'modalBoxOverlay' } ),
            make('div').attr( { 'id': 'modalBoxContent' } ).append(
                make('div').attr( { 'id': 'modalBoxTitle' } ),
                make('div').attr( { 'id': 'modalBoxForm' } ) ) ) );
    
    BioSync.ModalBox.contentContainer = $('#modalBoxForm');
};


//This function checks for 'Esc' and 'Enter' keypresses.  When someone hits Escape, the modal dialogue disappears.  When the enter button is pressed, and there is a DOM element with a class of 'modalBoxSubmit', the element is programmatically clicked.
BioSync.ModalBox.handleKeyPress = function( p ) {

    if( p.keyCode == 27 ) {
        var cancelButton =  $('#modalBoxForm .modalBoxCancel');

        if( cancelButton.length ) { cancelButton.click(); }
        else { BioSync.ModalBox.closeBox(); }
    }

    if( p.keyCode == 13 ) { 
        $('#modalBoxForm .modalBoxSubmit').click();
    }
}


//This function accepts a title and a url and makes an ajax request to that url.  The response is handled by ModalBox.acceptForm and displayed in a modal dialogue box.  'successTrigger' and 'successData' are parameters used to trigger an event upon successful submission of the received form.  'successTrigger' is the string triggered while successData is the data passed to the event.  I now view this as a hack and would suggest not using these two.
BioSync.ModalBox.getUrlForm = function( p ) {

    $('#modalBoxTitle').text( p.title );

    $.ajax( { url: p.url,
              type: "GET",
              async: false,
              success: new Array( BioSync.ModalBox.acceptForm ) } );

    BioSync.ModalBox.successTrigger = p.successTrigger;
    BioSync.ModalBox.successTriggerData = p.successData;
}


//After receiving a form via 'getUrlForm', this function is used to handle user changes ( check, unchecks ) to checkboxes in the form.  This was done because when using some canned web2py functions, SQLFORM being one, to receive forms via ajax ( instead of via a page request which works properly ), the checkbox wasn't working properly.
BioSync.ModalBox.handleCheckboxChange = function() {

    var checkbox = $(this);

    checkbox.val( ( checkbox.is( ':checked' ) ) ? 'on' : '' );
}

//This function handles the response from getUrlForm.  It places the response directly in the DOM, so the response better be html.  It fixes a checkbox issue and aligns the html in the modal box.
BioSync.ModalBox.acceptForm = function( response ) {

    $('#modalBoxForm').html( response );

    $('#modalBoxForm input[type="checkbox"]').change( BioSync.ModalBox.handleCheckboxChange );
    
    BioSync.ModalBox.sqlFormCheckboxHack();
    
    $('#modalBoxContainer').show( 'slow', BioSync.ModalBox.alignBox );
}

//Used to set the proper checkbox value on a form returned from a web2py server using SQLFORM
BioSync.ModalBox.sqlFormCheckboxHack = function() {
 
    $('#modalBoxForm input[type="checkbox"]').each(
        function( index ) {
            var checkbox = $(this);
            if( ! checkbox.is( ':checked' ) ) { checkbox.val( '' ); }
        }
    );
}

//
BioSync.ModalBox.ajaxizeForm = function() {

    $('#modalBoxForm input[type="submit"]').bind( 'click', { }, BioSync.ModalBox.submit );
}

BioSync.ModalBox.showModalBox = function( p ) {

    var make = BioSync.Common.makeEl;

    var myDocument = $(document);
    var modalBoxForm = $('#modalBoxForm');
    var modalBoxContainer = $('#modalBoxContainer');
    var modalBoxContent = $('#modalBoxContent');
    var modalBoxTitle = $('#modalBoxTitle');

    modalBoxContent.css( { 'height': '', 'width': '' } );

    if( p.title ) { modalBoxTitle.text( p.title ); } else { modalBoxTitle.text( '' ); }

    modalBoxForm.append( p.content );
    
    modalBoxContainer.show();
    var contentHeight = modalBoxContent.outerHeight( true );
    var contentWidth = modalBoxContent.outerWidth( true );
    modalBoxContainer.hide();

    if( p.height ) {
    
        modalBoxContent.height( p.height );
        contentHeight = p.height;
        modalBoxForm.height( contentHeight - modalBoxTitle.outerHeight( true ) ); 
    }

    if( p.width ) { modalBoxContent.width( p.width ); contentWidth = p.width;  }

    modalBoxContent.css( { top: ( ( myDocument.height() - ( contentHeight ) ) / 2 ),
                           left: ( ( myDocument.width() - ( contentWidth ) ) / 2 ) } );

    
    modalBoxContainer.show( 'slow', BioSync.ModalBox.afterSlowShow );

    if( p.onClose ) { BioSync.ModalBox.onClose = p.onClose; }
};

BioSync.ModalBox.afterSlowShow = function() {
    
    $( $( '#modalBoxContainer' ).find('input')[0] ).focus();

    $(document).bind('keydown', BioSync.ModalBox.handleKeyPress );
    $(document).bind( 'click', BioSync.ModalBox.checkForOutSideMouseClick );
}

BioSync.ModalBox.checkForOutSideMouseClick = function( e ) {

    if( ( ! BioSync.Common.isMouseOnElement( { x: e.pageX, y: e.pageY, el: $( '#modalBoxContent' ) } ) ) ) {

        var cancelButton =  $('#modalBoxForm .modalBoxCancel');

        if( cancelButton.length ) {
        
            cancelButton.click();
        
        } else {
            
            BioSync.ModalBox.closeBox();
        }
    }

}

BioSync.ModalBox.alignBox = function( p ) {

    var content = $('#modalBoxContent');
    var form = $('#modalBoxForm');

    if( p && ( p.height || p.width ) ) {

        form.height( '100%' ).width( '100%' );
        
        if( p.height ) { content.height( p.height ); }
        if( p.width ) { content.width( p.width ); }
    }

    var myDocument = $( document );

    content.css( { top: ( ( myDocument.height() - content.outerHeight( true ) ) / 2 ),
                  left: ( ( myDocument.width() - content.outerWidth( true ) ) / 2 ) } );
    
    $( $('#modalBoxContainer input')[0] ).focus();

    $(document).bind('keydown', BioSync.ModalBox.handleKeyPress );
    $(document).bind( 'click', BioSync.ModalBox.checkForOutSideMouseClick );

    BioSync.ModalBox.ajaxizeForm();
}

BioSync.ModalBox.successTriggerHandler = function() {
    
    if( BioSync.ModalBox.successTrigger ) {
        
        $( document ).trigger( BioSync.ModalBox.successTrigger, [ BioSync.ModalBox.successTriggerData ] );
    }
}


BioSync.ModalBox.submit = function( p ) {

    var data = BioSync.ModalBox.getModalBoxInputs();
    
    $.ajax( { url: $('#modalBoxForm form').attr('action'),
              type: "POST",
              data: data,
              success: BioSync.ModalBox.successTriggerHandler } );

    BioSync.ModalBox.closeBox();

    p.preventDefault();
}

BioSync.ModalBox.triggerSuccess = function() {

    $( document ).trigger( BioSync.ModalBox.successTrigger );
}

BioSync.ModalBox.submitBox = function( p ) {

    var data = BioSync.ModalBox.getModalBoxInputs();
    
    var successHandlers = new Array( BioSync.ModalBox.successHandler );

    if( p.data.trigger ) {
        BioSync.ModalBox.successTrigger = p.data.trigger;
        successHandlers.push( BioSync.ModalBox.triggerSuccess );
    }
    
    if( p.data.onSuccess ) {
        
        successHandlers.push( p.data.onSuccess );
    }

    $.ajax( { url: p.data.submitUrl,
              type: "GET",
              success: successHandlers,
              data: data } );

    BioSync.ModalBox.closeBox();
}

BioSync.ModalBox.successHandler = function( response ) {

    if( response == 'None' ) { return; }

    var response = eval( "(" + response + ")" );
    
    if( response.result == 'error' ) {
        BioSync.ModalBox.showModalBox( { title: 'Error', content: BioSync.Common.makeEl('div').attr( { 'class': 'centerText' } ).text( response.message ) } );
        $(document).bind('click', BioSync.ModalBox.closeBox );
    }
}

BioSync.ModalBox.closeBox = function() {
    $('#modalBoxTitle').text();   
    $('#modalBoxForm').empty();
    $('#modalBoxContainer').hide();
    $(document).unbind('click', BioSync.ModalBox.closeBox);

    if( BioSync.ModalBox.onClose ) {
        
        for( var i = 0, ii = BioSync.ModalBox.onClose.length; i < ii; i++ ) {

            BioSync.ModalBox.onClose[i]();
        }
    }
    
    $(document).unbind('keydown', BioSync.ModalBox.handleKeyPress );
    $(document).unbind( 'click', BioSync.ModalBox.checkForOutSideMouseClick );
}

BioSync.ModalBox.getModalBoxInputs = function() {

    var data = { };

    var inputs = $('#modalBoxForm input');

    for( var i = 0, ii = inputs.length; i < ii; i++ ) {
        var el = $(inputs[i]);

        var val = el.val();

        if( el.attr('type') == 'radio' ) { val = $('#modalBoxForm input[type=radio]:checked').val(); }
        
        data[ el.attr('name') ] = val;
    }

    return data;
}

BioSync.ModalBox.makeBasicTextRow = function( p ) {
    
    var make = BioSync.Common.makeEl;

    return make('div').attr( { 'class': 'modalText' } ).text( p.text );
}

BioSync.ModalBox.makeBasicTextInput = function( p ) {
    
    var make = BioSync.Common.makeEl;

    var input = make('input').attr( { 'type': 'text', name: p.name } ).val( p.value );

    BioSync.Common.removeTextFirstFocus( { el: input } );

    return make('div').attr( { 'class': 'formRow' } ).append(
       make('div').attr( { 'class': 'dialogueLabel' } ).text( p.text ),
       make('div').attr( { 'class': 'dialogueTextInput' } ).append( input ),
       make('div').attr( { 'class': 'clear' } ) );
}

BioSync.ModalBox.makeBasicLongTextInput = function( p ) {
    
    var make = BioSync.Common.makeEl;

    return make('div').attr( { 'class': 'formRow' } ).append(
       make('div').attr( { 'class': 'dialogueLabel' } ).text( p.text ),
       make('div').attr( { 'class': 'dialogueTextInput' } ).append( make('textarea').attr( { 'rows': 3, 'cols': 20 } ).val( p.value ) ),
       make('div').attr( { 'class': 'clear' } ) );
}

BioSync.ModalBox.makeHiddenInput = function( p ) {

    return BioSync.Common.makeEl('input').attr( { 'type': 'hidden', 'name': p.name, 'value': p.value } )
}

BioSync.ModalBox.makeBasicActionRow = function( p ) {

    var make = BioSync.Common.makeEl;

    var cancelElement = make('div').attr( { 'class': 'dialogueButton twoOpt modalBoxCancel' } ).text('Cancel').click( BioSync.ModalBox.closeBox );

    if( p.onCancel ) { cancelElement.click( p.onCancel ); }

    return make('div').attr( { 'class': 'actionRow' } ).append(
        make('div').attr( { 'class': 'dialogueButton twoOpt modalBoxSubmit' } ).text( p.submitText )
            .bind( 'click', p.submitArgs, BioSync.ModalBox.submitBox )
            .bind( 'click', { }, ( p.onClick ) ? p.onClick : function() { } ),
        cancelElement,
        make('div').attr( { 'class': 'clear' } ) );
}

BioSync.ModalBox.makeRadioButtonRow = function( p ) {

    var make = BioSync.Common.makeEl;

    var containerRow = make('div').attr( { 'class': 'centerText' } );

    for( var i = 0, ii = p.options.length; i < ii; i++ ) {

        var inputDom = make('input').attr( { type: 'radio', name: p.name, value: p.options[i].value } ).click( p.options[ i ].func );

        if( p.options[i].default ) { inputDom.attr( { 'checked': '1' } ); }

        containerRow.append(
            make('span').attr( { 'class': 'radioContainer' } ).append(
                make('span').text( p.options[ i ].text ), inputDom ) );
    }

    return containerRow;
}

$(document).ready( BioSync.ModalBox.initialize );
