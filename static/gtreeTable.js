BioSync.GtreeTable = function( p ) {

    this.makeEl = BioSync.Common.makeEl;

    this.containerId = p.id;

    this.container = $( '#' + p.id ).width( $('body').width() * .95 );
    
    return this;
}

BioSync.GtreeTable.prototype = {

    config: {

        headerBackgroundColor: '#CCC'
    },

    initialize: function() {

        this.makeHeader();

        this.makeSubHeader();
        
        this.makeTable();
        
        this.makeSearchFooter();
        
        this.makeFooter();

        this.getTheInfo();
        
        this.disablePrevButton();
        this.prevButtonDisabled = true;
        
        this.enableNextButton();
        this.nextButtonDisabled = false;
    },

    getTheInfo: function() {

        $.ajax( { url: BioSync.Common.makeUrl( { controller: 'gtree', argList: [ 'getGtrees' ] } ),
                  type: "POST",
                  data: {
                      page: this.page,
                      rowsOnPage: this.rowsOnPage,
                      nameSearch: $('#nameSearch').val(),
                      descriptionSearch: $('#descriptionSearch').val(),
                      creatorSearch: $('#creatorSearch').val(),
                      nameSort: this.nameSort,
                      creatorSort: this.creatorSort,
                      dateSort: this.dateSort
                  },
                  success: $.proxy( this.handleTheInfo, this ) } );

        this.nameSort = undefined;
        this.creatorSort = undefined;
        this.dateSort = undefined;
    },

    handleTheInfo: function( response ) {

        var responseObj = eval( '(' + response + ')' );

        this.totalRecords = responseObj.totalRecords;
        this.recordsInData = responseObj.recordsInData;

        this.table.empty();

        for( var i = 0, ii = responseObj.data.length; i < ii; i++ ) {

            var backgroundColor = ( i % 2 == 0 ) ? '#E2E4FF' : 'white';
   
            var rowContainer =
                this.makeEl( 'div' ).attr( { 'id': responseObj.data[i].id } )
                    .click( function() {
                        document.location.href =
                            BioSync.Common.makeUrl( { controller: 'gtree', argList: [ 'backbone', [ $( this ).attr('id'), '?treeType=grafted' ].join('') ] } ) } )
                    .hover( BioSync.Common.setMouseToPointer, BioSync.Common.setMouseToDefault )
                    .hover( function() { $( $( this ).children() ).css( { 'background-color': '#CCC' } ); },
                            function() { $( $( this ).children() ).css( { 'background-color': $( $( this ).children()[0] ).attr('bc') } ); } );

            var nameItem =
                this.makeEl( 'div' )
                    .css( {
                        'float': 'left',
                        'padding': '3px 0px 3px 5px',
                        'text-align': 'center',
                        'background-color': backgroundColor  } )
                    .attr( { 'bc': backgroundColor } )
                    .text( ( responseObj.data[ i ].title != null ) ? responseObj.data[ i ].title : '' );

            var descriptionText = ( responseObj.data[ i ].comment != null ) ? responseObj.data[ i ].comment : '';

            var descriptionItem =
                this.makeEl( 'div' )
                    .attr( { 'title': descriptionText } )
                    .css( {
                        'float': 'left',
                        'padding': '3px 0px 3px 5px',
                        'text-align': 'center',
                        'white-space': 'nowrap',
                        'overflow': 'hidden',
                        'text-overflow': 'ellipsis',
                        'background-color': backgroundColor } )
                    .attr( { 'bc': backgroundColor } )
                    .text( descriptionText );

            var creatorItem =
                this.makeEl( 'div' )
                    .css( {
                        'float': 'left',
                        'padding': '3px 0px 3px 5px',
                        'text-align': 'center',
                        'background-color': backgroundColor } )
                    .attr( { 'bc': backgroundColor } )
                    .text( ( responseObj.data[ i ].contributor != null ) ? responseObj.data[ i ].contributor : '' );

            var dateItem =
                this.makeEl( 'div' )
                    .css( {
                        'float': 'left',
                        'padding': '3px 0px 3px 5px',
                        'text-align': 'center',
                        'background-color': backgroundColor } )
                    .attr( { 'bc': backgroundColor } )
                    .text( ( responseObj.data[ i ].date != null ) ? responseObj.data[ i ].date : '' );

            this.table.append(
                rowContainer.append( 
                    nameItem,
                    descriptionItem,
                    creatorItem,
                    dateItem,
                    this.makeEl( 'div' ).css( { 'clear': 'both' } )
                )
            );

            var tableWidth = this.table.outerWidth( true ); 

            var dateItemHeight = dateItem.height();
            var colWidth = ( tableWidth / 4 ) - 5;

            dateItem.width( colWidth );
            descriptionItem.width( colWidth ).height( dateItemHeight );
            creatorItem.width( colWidth ).height( dateItemHeight );
            nameItem.width( colWidth ).height( dateItemHeight );
        }

        var lastItemIndex = this.recordsInData;

        if( ( this.page * this.rowsOnPage ) < this.recordsInData ) {

            lastItemIndex = this.page * this.rowsOnPage;
        }

        var contextText = [
            'Showing ',
            ( ( this.page - 1  ) * this.rowsOnPage ) + 1,
            ' to ',
            lastItemIndex,
            ' of ', this.recordsInData,
            ' entries.' ].join('');


        if( this.recordsInData != this.totalRecords ) {
            
            contextText += [ '(filtered from ', this.totalRecords, ' total entries)' ].join('');
        }

        this.context.text( contextText );
    },

    makeFooter: function() {

        this.footer =
            this.makeEl( 'div' ).css( {
                'background-color': this.config.headerBackgroundColor,
                'border': '1px solid #AAA',
                'border-bottom-right-radius': '5px',
                'border-bottom-left-radius': '5px' } );

        this.context =
            this.makeEl( 'div' )
              .css( { 'float': 'left',
                      'padding-left': '5px',
                      'font-weight': 'bold' } );
        
        this.footerPagination = this.makePagination();

        this.container.append(
            this.footer.append(
                this.context,
                this.footerPagination,
                this.makeEl( 'div' ).css( { 'clear': 'both' } ) ) );

    },

    makeSearchFooter: function() {

        this.searchFooter =
            this.makeEl( 'div' ).width( '100%' ).css( { 'background-color': '#E6E6E6' } );

        this.nameSearchEl = 
            this.makeEl( 'div' ).css( {
              'padding': '3px',
              'border': '1px solid gray',
              'float': 'left' } ).append(
                this.makeEl( 'input' )
                  .attr( { 'id': 'nameSearch', 'type': 'text' } )
                  .bind( 'keydown', { }, $.proxy( this.handleSearch, this ) ) );

        this.descriptionSearchEl =
            this.makeEl( 'div' ).css( {
              'padding': '3px',
              'border': '1px solid gray',
              'float': 'left' } ).append(
                this.makeEl( 'input' )
                  .attr( { 'id': 'descriptionSearch', 'type': 'text' } )
                  .bind( 'keydown', { }, $.proxy( this.handleSearch, this ) ) );

        this.creatorSearchEl =
            this.makeEl( 'div' ).css( {
              'padding': '3px',
              'border': '1px solid gray',
              'float': 'left' } ).append(
                this.makeEl( 'input' )
                  .attr( { 'id': 'creatorSearch', 'type': 'text' } )
                  .bind( 'keydown', { }, $.proxy( this.handleSearch, this ) ) );


        this.container.append(
            this.searchFooter.append(
                this.nameSearchEl,
                this.descriptionSearchEl,
                this.creatorSearchEl,
                this.makeEl( 'div' ).css( { 'clear': 'both' } ) ) );

        BioSync.Common.storeObjPosition( this.searchFooter, this.searchFooter );

        this.nameSearchEl.width( ( this.searchFooter.myWidth / 4 ) - 9 );
        this.descriptionSearchEl.width( ( this.searchFooter.myWidth / 4 ) - 9 );
        this.creatorSearchEl.width( ( this.searchFooter.myWidth / 4 ) - 9 );

        $( this.nameSearchEl.children()[0] ).css( { 'width': ( this.searchFooter.myWidth / 4 ) - 20 } );
        $( this.descriptionSearchEl.children()[0] ).css( { 'width': ( this.searchFooter.myWidth / 4 ) - 20 } );
        $( this.creatorSearchEl.children()[0] ).css( { 'width': ( this.searchFooter.myWidth / 4 ) - 20 } );
    },

    handleSearch: function() {

        if( this.userInputTimeout ) { clearTimeout( this.userInputTimeout ); }

        this.userInputTimeout = setTimeout( $.proxy( this.getTheInfo, this ), 500 );
        
    },

    makeTable: function() {

        this.table = this.makeEl( 'div' );

        this.container.append( this.table );
    },

    sortLabelColumn: function() {

        this.labelSort =
            ( ( this.labelSort == undefined ) || ( this.labelSort == 'descending' ) )
                ? 'ascending'
                : 'descending';

        this.getTheInfo();
    },

    sortTaxonColumn: function() {
    
        this.taxonSort =
            ( ( this.taxonSort == undefined ) || ( this.taxonSort == 'descending' ) )
                ? 'ascending'
                : 'descending';

        this.getTheInfo();
    },

    makeSubHeader: function() {

        this.subHeader = this.makeEl( 'div' ).css( { 'background-color': '#E6E6E6' } ).width( '100%' );
        
        var nameSubHeader =
                this.makeEl( 'div' )
                    .css( { 'float': 'left',
                            'text-align': 'center',
                            'padding': '5px',
                            'color': '#555',
                            'font-weight': 'bold',
                            'border': '1px solid gray' } )
                    .text( 'Name' )
                    .bind( 'click', { }, $.proxy( this.sortNameColumn, this ) )
                    .hover( BioSync.Common.setMouseToPointer, BioSync.Common.setMouseToDefault );

        var descriptionSubHeader =
            this.makeEl( 'div' )
                    .css( { 'float': 'left',
                            'padding': '5px',
                            'text-align': 'center',
                            'color': '#555',
                            'font-weight': 'bold',
                            'border': '1px solid gray' } )
                    .text( 'Description' )
                    .hover( BioSync.Common.setMouseToPointer, BioSync.Common.setMouseToDefault );

        var creatorSubHeader =
            this.makeEl( 'div' )
                    .css( { 'float': 'left',
                            'padding': '5px',
                            'text-align': 'center',
                            'color': '#555',
                            'font-weight': 'bold',
                            'border': '1px solid gray' } )
                    .text( 'Created By' )
                    .bind( 'click', { }, $.proxy( this.sortCreatorColumn, this ) )
                    .hover( BioSync.Common.setMouseToPointer, BioSync.Common.setMouseToDefault );

        var dateSubHeader =
            this.makeEl( 'div' )
                    .css( { 'float': 'left',
                            'padding': '5px',
                            'text-align': 'center',
                            'color': '#555',
                            'font-weight': 'bold',
                            'border': '1px solid gray' } )
                    .text( 'Creation Date' )
                    .bind( 'click', { }, $.proxy( this.sortDateColumn, this ) )
                    .hover( BioSync.Common.setMouseToPointer, BioSync.Common.setMouseToDefault );

        var clear = this.makeEl( 'div' ).css( { 'clear': 'both' } );

        this.container.append(
            this.subHeader.append(
                nameSubHeader,
                descriptionSubHeader,
                creatorSubHeader,
                dateSubHeader,
                clear
            )
        );

        this.subHeader.children().width( ( this.subHeader.outerWidth( true ) / 4 ) - 13 );

        this.nameSort = undefined;
        this.creatorSort = undefined;
        this.dateSort = undefined;
    },

    changeRowsOnPage: function( e ) {

        this.rowsOnPage = this.rowsOnPageSelector.val();

        this.page = 1;

        this.getTheInfo();
    },

    makeHeader: function() {

        this.header =
            this.makeEl( 'div' )
                .width( '100%' )
                .css( { 'background-color': this.config.headerBackgroundColor,
                        'border': '1px solid #AAA',
                        'border-top-right-radius': '5px',
                        'border-top-left-radius': '5px' } );

        this.rowsOnPageSelector = 
            this.makeEl( 'select' )
              .width( 50 )
              .change( $.proxy( this.changeRowsOnPage, this ) )
              .append(
                this.makeEl( 'option' ).attr( { 'value': '10', 'selected': 'selected' } ).text( '10' ),
                this.makeEl( 'option' ).attr( { 'value': '25' } ).text( '25' ),
                this.makeEl( 'option' ).attr( { 'value': '50' } ).text( '50' ),
                this.makeEl( 'option' ).attr( { 'value': '100' } ).text( '100' ) );

        this.rowsOnPageContainer =
            this.makeEl( 'div' ).css( { 'float': 'left' } ).append(
                this.makeEl( 'div' )
                    .text( 'Show' )
                    .css( { 'padding': '0px 5px', 
                            'font-weight': 'bold',
                            'float': 'left' } ),
                this.makeEl( 'div' ).css( { 'float': 'left' } ).append(
                    this.rowsOnPageSelector
                ),
                this.makeEl( 'div' )
                    .text( ' entries' )
                    .css( { 'font-weight': 'bold',
                            'padding': '0px 5px',
                            'float': 'left' } ),
                 this.makeEl( 'div' ).css( { 'clear': 'both' } ) );

        this.rowsOnPage = 10;
        this.page = 1;

        this.headerPagination = this.makePagination();

        this.container.append(
            this.header.append(
                this.rowsOnPageContainer,
                this.headerPagination,
                this.makeEl( 'div' ).css( { 'clear': 'both' } ) ) );
    },

    makePagination: function() {

        return this.makeEl( 'div' ).css( { 'padding': '0px 10px', 'float': 'right' } ).append(
                    this.makeEl( 'div' ).attr( { 'class': 'prevPageLink' } )
                                        .css( { 'float': 'left' } )
                                        .text( '<' ),
                    this.makeEl( 'div' ).attr( { 'class': 'nextPageLink' } )
                                        .css( { 'padding': '0px 10px', 'float': 'left' } )
                                        .text( '>' ),
                    this.makeEl( 'div' ).css( { 'clear': 'both' } ) );
    },

    prevPageClick: function() {

        this.page -= 1;

        if( this.page == 1 ) {

            this.disablePrevButton();
        }

        if( this.nextButtonDisabled ) {

            this.enableNextButton();
        }

        this.getTheInfo();
    },
    
    nextPageClick: function() {

        this.page += 1;

        if( ( this.page * this.rowsOnPage ) >= this.recordsInData ) {

            this.disableNextButton();
        }

        if( this.prevButtonDisabled ) {

            this.enablePrevButton();
        }

        this.getTheInfo();
    },

    disablePrevButton: function() {

        $( '.prevPageLink' )
            .unbind( 'click' )
            .unbind( 'mouseenter' )
            .unbind( 'mouseleave' );

        $( '.prevPageLink' ).each( function( i, el ) {
        
            $.proxy( BioSync.Common.removeTextUnderline, el )();
            $.proxy( BioSync.Common.setMouseToDefault, el )();

        } );
            
        this.prevButtonDisabled = true;
    },

    disableNextButton: function() {

        $( '.nextPageLink' )
            .unbind( 'click' )
            .unbind( 'mouseenter' )
            .unbind( 'mouseleave' );

        $( '.nextPageLink' ).each( function( i, el ) {
        
            $.proxy( BioSync.Common.removeTextUnderline, el )();
            $.proxy( BioSync.Common.setMouseToDefault, el )();

        } );
            
        this.nextButtonDisabled = true;
    },

    enablePrevButton: function() {

        $( '.prevPageLink' )
           .bind( 'click', { }, $.proxy( this.prevPageClick, this ) )
           .hover( BioSync.Common.setMouseToPointer, BioSync.Common.setMouseToDefault )
           .hover( BioSync.Common.underlineText, BioSync.Common.removeTextUnderline );
        
        this.prevButtonDisabled = false;
    },

    enableNextButton: function() {

        $( '.nextPageLink' )
           .bind( 'click', { }, $.proxy( this.nextPageClick, this ) )
           .hover( BioSync.Common.setMouseToPointer, BioSync.Common.setMouseToDefault )
           .hover( BioSync.Common.underlineText, BioSync.Common.removeTextUnderline );

        this.nextButtonDisabled = false;
    }

}
