BioSync.EditOTU = {

    instances: { }

};


BioSync.EditOTU.editOTU = function( p ) { 

    var make = BioSync.Common.makeEl;

    this.config = { rowHeight: 30, page: 1, treeId: p.params.treeId };

    BioSync.EditOTU.instances[ p.containerId ] = this;
    
    this.container = $('#' + p.containerId).addClass('editOTUContainer');

    this.container.append( make('div').attr( { 'class': 'editOTUHeader' } ).text( 'Please use this page to contribute OTU information' ) );

    this.table = make('div').attr( { 'class': 'editOTUTable' } );

    this.tableHeader = make('div').attr( { 'class': 'editOTUTableHeader' } ).append(
                make('div').attr( { 'class': 'editOTUTableColumn' } ).text('Label'),
                make('div').attr( { 'class': 'editOTUTableColumn' } ).text('Taxon'),
                make('div').attr( { 'class': 'clear' } ) );

    this.tableFooter = make('div').attr( { 'class': 'editOTUTableFooter' } ).append( make('div').attr( { 'class': 'editOTUTablePaginator' } ) );
   
    this.tableWrapper =
        make('div').attr( { 'class': 'editOTUTableWrapper' } ).append(
            this.tableHeader, this.table, this.tableFooter );

    this.container.append( this.tableWrapper );

    var module = this;

    $( window ).load(
        function() {

            module.table.height( module.tableWrapper.outerHeight( true ) - module.tableHeader.outerHeight( true ) - module.tableFooter.outerHeight( true ) );
            module.config.tableHeight = module.table.outerHeight( true );

            module.config.rowsPerPage = Math.floor( module.config.tableHeight / module.config.rowHeight );

            module.initialize();
        } );
}

BioSync.EditOTU.editOTU.prototype = {

    initialize: function( p ) {

        this.retrievePage();
    },

    retrievePage: function( p ) {

        $.ajax( { url: BioSync.Common.makeUrl( { controller: 'plugin_editOTU', argList: [ 'getPage' ] } ),
             type: "GET",
             context: this,
             data: { treeId: this.config.treeId, page: this.config.page, rowsPerPage: this.config.rowsPerPage },
             success: this.updateTable } );
    },

    updateTable: function( response ) {

        var response = eval( [ "(", response, ")" ].join('') );
        
        console.log( response );

        for( var i = 0, ii = response.length; i < ii; i++ ) {

            this.addTableRow( { item: response[i] } );
        }
    },

    addTableRow: function( p ) {
    
        var make = BioSync.Common.makeEl;

        this.table.append( make('div').attr( { 'class': 'editOTURow' } ).append(
            make('div').attr( { 'class': 'fLeft centerText' } ).text( p.item.snode.label )
    }
}
