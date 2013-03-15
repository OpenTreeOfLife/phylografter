# Fetch study metadata from treebase and see if there's a DOI therein

function treebase {
  study=$1
  tb=$2
  doi=`wget -q -O - "http://treebase.org/treebase-web/search/study/anyObjectAsRDF.rdf?namespacedGUID=TB2:S$tb"  | grep -o "10\\.[0-9]*/[^<]*"`
  if [ "x$doi" != "x" ]; then
    echo found $study "$doi"
  else
    echo missing $study $tb
  fi
  sleep 1
}
