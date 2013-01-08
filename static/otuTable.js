BioSync.OtuTable = function( p ) {

    this.makeEl = BioSync.Common.makeEl;

    this.containerId = p.id;

    this.container = $( '#' + p.id ).width( $('body').width() * .95 );

    this.studyId = p.studyId;

    return this;
}

BioSync.OtuTable.prototype = {

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

        $.ajax( { url: BioSync.Common.makeUrl( { controller: 'otu', argList: [ 'getStudyOTUs' ] } ),
                  type: "POST",
                  data: {
                      studyId: this.studyId,
                      page: this.page,
                      rowsOnPage: this.rowsOnPage,
                      labelSearch: $('#labelSearch').val(),
                      taxonSearch: $('#taxonSearch').val(),
                      taxonSort: this.taxonSort,
                      labelSort: this.labelSort
                  },
                  success: $.proxy( this.handleTheInfo, this ) } );
    },

    handleTheInfo: function( response ) {

        var responseObj = eval( '(' + response + ')' );

        this.totalRecords = responseObj.totalRecords;
        this.recordsInData = responseObj.recordsInData;

        this.table.empty();

        for( var i = 0, ii = responseObj.data.length; i < ii; i++ ) {

            var backgroundColor = ( i % 2 == 0 ) ? '#E2E4FF' : 'white';
    
            var leftItem =
                this.makeEl( 'div' ).css( {
                    'float': 'left',
                    'padding': '3px 0px 3px 5px',
                    'background-color': backgroundColor  } ).text( responseObj.data[ i ][0] );

            var rightItem =
                this.makeEl( 'div' ).css( {
                    'float': 'left',
                    'padding': '3px 0px 3px 5px',
                    'background-color': backgroundColor } )
                        .width( '50%' ).append( responseObj.data[ i ][1] )

            this.table.append( leftItem, rightItem, this.makeEl( 'div' ).css( { 'clear': 'both' } ) );

            var tableWidth = this.table.outerWidth( true ); 

            leftItem.width( ( tableWidth / 2 ) - 5 );
            rightItem.width( ( tableWidth / 2 ) - 5 ).height( leftItem.height() );
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

        this.labelSearchEl = 
            this.makeEl( 'div' ).css( {
              'padding': '3px',
              'border': '1px solid gray',
              'float': 'left' } ).append(
                this.makeEl( 'input' )
                  .attr( { 'id': 'labelSearch', 'type': 'text' } )
                  .bind( 'keydown', { }, $.proxy( this.handleSearch, this ) ) );

        this.taxonSearchEl =
            this.makeEl( 'div' ).css( {
              'padding': '3px',
              'border': '1px solid gray',
              'float': 'left' } ).append(
                this.makeEl( 'input' )
                  .attr( { 'id': 'taxonSearch', 'type': 'text' } )
                  .bind( 'keydown', { }, $.proxy( this.handleSearch, this ) ) );

        this.container.append(
            this.searchFooter.append(
                this.labelSearchEl,
                this.taxonSearchEl,
                this.makeEl( 'div' ).css( { 'clear': 'both' } ) ) );

        BioSync.Common.storeObjPosition( this.searchFooter, this.searchFooter );

        this.labelSearchEl.width( ( this.searchFooter.myWidth / 2 ) - 9 );
        this.taxonSearchEl.width( ( this.searchFooter.myWidth / 2 ) - 9 );

        $( this.labelSearchEl.children()[0] ).css( { 'width': ( this.searchFooter.myWidth / 2 ) - 20 } );
        $( this.taxonSearchEl.children()[0] ).css( { 'width': ( this.searchFooter.myWidth / 2 ) - 20 } );
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
        
        var leftSubHeader =
                this.makeEl( 'div' )
                    .css( { 'float': 'left',
                            'text-align': 'center',
                            'padding': '5px',
                            'color': '#555',
                            'font-weight': 'bold',
                            'border': '1px solid gray' } )
                    .text( 'Label' )
                    .bind( 'click', { }, $.proxy( this.sortLabelColumn, this ) )
                    .hover( BioSync.Common.setMouseToPointer, BioSync.Common.setMouseToDefault );

        var rightSubHeader =
            this.makeEl( 'div' )
                    .css( { 'float': 'left',
                            'padding': '5px',
                            'text-align': 'center',
                            'color': '#555',
                            'font-weight': 'bold',
                            'border': '1px solid gray' } )
                    .text( 'Taxon' )
                    .bind( 'click', { }, $.proxy( this.sortTaxonColumn, this ) )
                    .hover( BioSync.Common.setMouseToPointer, BioSync.Common.setMouseToDefault );

        var clear = this.makeEl( 'div' ).css( { 'clear': 'both' } );

        this.container.append( this.subHeader.append( leftSubHeader, rightSubHeader, clear ) );

        this.subHeader.children().width( ( this.subHeader.outerWidth( true ) / 2 ) - 13 );

        this.labelSort = undefined;
        this.taxonSort = 'ascending';
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

