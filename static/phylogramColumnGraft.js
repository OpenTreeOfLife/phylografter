BioSync.TreeGrafter.RenderUtil.Column = function( renderObj ) {

    this.renderObj = renderObj;
    this.make = renderObj.make;
    return this;
}

BioSync.TreeGrafter.RenderUtil.Column.prototype = new BioSync.TreeViewer.RenderUtil.Column();
BioSync.TreeGrafter.RenderUtil.Column.constructor = BioSync.TreeGrafter.RenderUtil.Column;
BioSync.TreeGrafter.RenderUtil.Column.prototype.super = BioSync.TreeViewer.RenderUtil.Column.prototype;

BioSync.TreeGrafter.RenderUtil.Column.prototype.handlePruneCladeOptionClick = function() {

    this.nodeIdToPrune = this.closestNodeToMouse.id;

    this.renderObj.pruneClade( { column: this, nodeId: this.nodeIdToPrune } );
}

BioSync.TreeGrafter.RenderUtil.Column.prototype.handleReplaceCladeOptionClick = function() {

    this.nodeIdToReplace = this.closestNodeToMouse.id;

    this.renderObj.getClipboardForCladeReplace( { column: this, nodeId: this.nodeIdToReplace } );
}

BioSync.TreeGrafter.RenderUtil.Column.prototype.handleGraftCladeOptionClick = function() {

    this.nodeIdToGraftOnto = this.closestNodeToMouse.id;

    this.renderObj.getClipboardForCladeGraft( { column: this, nodeId: this.nodeIdToGraftOnto } );
}
