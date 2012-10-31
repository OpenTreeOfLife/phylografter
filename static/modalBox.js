BioSync.ModalBox = {};

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

BioSync.ModalBox.getUrlForm = function( p ) {

    $('#modalBoxTitle').text( p.title );

    $.ajax( { url: p.url,
              type: "GET",
              async: false,
              success: new Array( BioSync.ModalBox.acceptForm ) } );

    BioSync.ModalBox.successTrigger = p.successTrigger;
    BioSync.ModalBox.successTriggerData = p.successData;
}

BioSync.ModalBox.handleCheckboxChange = function() {

    var checkbox = $(this);

    checkbox.val( ( checkbox.is( ':checked' ) ) ? 'on' : '' );
}

BioSync.ModalBox.acceptForm = function( response ) {

    $('#modalBoxForm').html( response );

    $('#modalBoxForm input[type="checkbox"]').change( BioSync.ModalBox.handleCheckboxChange );
    
    BioSync.ModalBox.sqlFormCheckboxHack();
    
    $('#modalBoxContainer').show( 'slow', BioSync.ModalBox.alignBox );
}

BioSync.ModalBox.sqlFormCheckboxHack = function() {
 
    $('#modalBoxForm input[type="checkbox"]').each(
        function( index ) {
            var checkbox = $(this);
            if( ! checkbox.is( ':checked' ) ) { checkbox.val( '' ); }
        }
    );
}

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

    if( p.height ) { modalBoxContent.height( p.height ); contentHeight = p.height; }
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
