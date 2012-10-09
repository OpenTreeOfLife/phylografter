def setSessionWindowDimensions():
    session.windowWidth = int( request.vars.width )
    session.windowHeight = int( request.vars.height )

def setTextWidthMetric():
    session.textWidthMetric = float( request.vars.width ) * 1.25

def setPageHeight():
    session.pageHeight = int( request.vars.pageHeight )

def setScrollbarWidth():
    session.scrollbarWidth = int( request.vars.width )
