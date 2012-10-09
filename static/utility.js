function makeEl( el ) { return $(document.createElement(el)); }

function makeUrl( p ) {

    var url = new StringBuffer();

    var controller = ( p.controller ) ? p.controller : 'default';
    
    url.append('/').append(globals.applicationName).append('/').append(controller);
    
    for( var i = 0, ii = p.argList.length; i < ii; i++ ) { url.append('/').append( p.argList[i] ); }

    return url.toString();
}

function StringBuffer() { 
   this.buffer = []; 
} 

StringBuffer.prototype.append = function append(string) { 
    this.buffer.push(string); 
    return this; 
}; 

StringBuffer.prototype.toString = function toString() { 
    return this.buffer.join(""); 
}
