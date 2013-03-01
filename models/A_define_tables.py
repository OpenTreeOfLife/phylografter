from gluon.dal import Field

## def _sdata_rep(x):
##     w = x.citation.split(); nw = len(w)
##     n = 6
##     if nw < n:
##         s = " ".join(w)
##     else:
##         s = (" ".join(w[:n]))+"..."
##     ## n = 15
##     ## s = x.citation[:n]
##     ## if len(x.citation) > n:
##     ##     s = s+"..."
##     if x.year_published:
##         s = s+"[%s]" % x.year_published
##     if x.focal_clade:
##         s = s+". %s" % x.focal_clade.name
##     if x.label:
##         s = s+". %s" % x.label
##     return s

def _study_rep(x):
    w = x.citation.split(); nw = len(w)
    n = 6
    if nw < n:
        s = " ".join(w)
    else:
        s = (" ".join(w[:n]))+"..."
    if x.year_published:
        s = s+"[%s]" % x.year_published
    if x.focal_clade_ottol:
        s = s+". %s" % x.focal_clade_ottol.name
    if x.label:
        s = s+". %s" % x.label
    return s

def define_tables(db, migrate=False):
    # this table is obsolete and will be removed in the future
    db.define_table(
        "ncbi_taxon",
        Field("taxid", "integer", unique=True, notnull=True),
        Field("parent", "integer"),
        Field("next", "integer"),
        Field("back", "integer"),
        Field("depth", "integer"),
        Field("name", "string", notnull=True),
        Field("rank", "string"),
        format="%(name)s [ncbi:%(taxid)s]",
        migrate=migrate
        )

    # the names that map to unique nodes in the NCBI hierarchy
    db.define_table(
        "ncbi_name",
        Field("taxid", "integer", notnull=True),
        Field("name", "string"),
        Field("unique_name", "string", unique=True),
        Field("name_class"),
        migrate=migrate
        )

    # these are unique nodes in the NCBI hierarchy
    db.define_table(
        "ncbi_node",
        Field("taxid", "integer", notnull=True),
        Field("name", "string"),  # the "scientific name" as listed by NCBI
        Field("parent", "integer"),
        Field("next", "integer"),
        Field("back", "integer"),
        Field("depth", "integer"),
        Field("rank", "string"),
        Field("hidden", "boolean", notnull=True, default=False),
        Field("comments", "text"),
        migrate=migrate
        )

    db.define_table(
        "apg_taxon",
        Field("parent", "integer"),
        Field("next", "integer"),
        Field("back", "integer"),
        Field("depth", "integer"),
        Field("name", "string", required=True, unique=True, notnull=True),
        Field("rank", "string"),
        format="%(name)s",
        migrate=migrate
        )

    ## db.define_table(
    ##     "ottol_node",
    ##     Field("uid", "integer", required=True, unique=True, notnull=True),
    ##     Field("parent", "integer"),
    ##     Field("next", "integer"),
    ##     Field("back", "integer"),
    ##     Field("depth", "integer"),
    ##     Field("name", "string", required=True, notnull=True),
    ##     Field("mtime", "datetime", default=datetime.datetime.now(),
    ##           readable=False, writable=False),
    ##     format="%(name)s",
    ##     migrate=migrate
    ##     )

    db.define_table(
        "ottol_name",
        Field("opentree_uid", "string", length=32,
              required=True, notnull=True, unique=True),
        Field("opentree_parent_uid", "string", length=32),
        Field("preottol_taxid", "integer", unique=True),
        Field("preottol_parent_taxid", "integer", unique=True),
        Field("preottol_source", "string"),
        Field("preottol_source_taxid", "string"),
        Field("ncbi_taxid", "integer"),
        Field("namebank_taxid", "integer"),
        Field("treebase_taxid", "integer"),
        ## Field("node", db.ottol_node, ondelete="NO ACTION"),
        Field("name", "string", required=True, notnull=True),
        Field("unique_name", "string", unique=True,
              required=True, notnull=True),
        Field("preottol_authority", "string"),
        Field("preottol_code", "string"),
        Field("rank", "string"),
        Field("preottol_date", "string"),
        Field("comments", "string"),
        Field("preottol_homonym_flag", "boolean"),
        Field("preottol_pdb_flag", "boolean"),
        Field("mtime", "datetime", default=datetime.datetime.now(),
              readable=False, writable=False),
        format="%(name)s",
        migrate=migrate
        )

    # The taxon table is not a hierarchy.  Nodes refer to it
    # (one-to-one).  Each taxon record may or may not refer to an
    # entry into a hierarchy (ncbi or apg).  This allows for synonyms
    # in the taxon table.
    db.define_table(
        "taxon",
        ## Field("parent", "integer"), # should drop this column
        ## Field("next", "integer"),
        ## Field("back", "integer"),
        ## Field("depth", "integer"),
        Field("name", "string", required=True, notnull=True),
        Field("rank", "string"),
        ## Field("family", "string"),
        ## Field("genus", "string"),
        ## Field("species", "string"),
        ## Field("ncbi_taxon", db.ncbi_taxon, ondelete="NO ACTION"), # NOT USED
        Field("ncbi_taxid", "integer"),
        Field("namebank_id", "integer"),
        Field("tb_taxid", "integer"),
        Field("apg_taxon", db.apg_taxon, ondelete="NO ACTION"),
        format="%(name)s",
        migrate=migrate
        )

    db.define_table(
        "plantlist",
        Field("major_group"),
        Field("family"),
        Field("genus_hybrid_marker"),
        Field("genus"),
        Field("species_hybrid_marker"),
        Field("species"),
        Field("infra_rank"),
        Field("infra_epithet"),
        Field("author"),
        Field("TPL_status"),
        Field("original_status"),
        Field("confidence"),
        Field("source"),
        Field("source_id"),
        Field("IPNI_id"),
        Field("publication"),
        Field("pub_collation"),
        Field("pub_page"),
        Field("pub_date"),
        format="%(genus)s %(species)s",
        migrate=migrate
        )

    ## db.define_table(
    ##     "sdata", # study data
    ##     Field("focal_clade", db.taxon, ondelete="NO ACTION"),
    ##     Field("citation", "text", required=True, notnull=True),
    ##     Field("label", "string"),
    ##     Field("year_published", "integer",
    ##           requires=[IS_INT_IN_RANGE(1700,2050)]),
    ##     Field("contributor", "string", length=128,
    ##           required=True, notnull=True),
    ##     ## Field("datafile", "upload", uploadfield="data"),
    ##     ## Field("data", "blob"),
    ##     Field("comment", "text"),
    ##     Field("uploaded", "datetime", default=datetime.datetime.now(),
    ##           writable=False, notnull=True),
    ##     format=_sdata_rep,
    ##     migrate=migrate
    ##     )
    ## db.sdata.citation.requires = [IS_NOT_EMPTY()]

    db.define_table(
        "gene",
        Field("name", unique=True, required=True, notnull=True),
        Field("genome"),
        format="%(name)s",
        migrate=migrate
        )

    db.define_table(
        "study", # study data
        ## Field("focal_clade", db.taxon, ondelete="NO ACTION",
        ##       requires=IS_EMPTY_OR(IS_IN_DB(db, 'taxon.id', '%(name)s'))),
        Field("focal_clade_ottol", db.ottol_name, ondelete="NO ACTION",
              requires=IS_EMPTY_OR(IS_IN_DB(db, 'ottol_name.id', '%(name)s'))),
        Field("citation", "text", required=True, notnull=True),
        Field("doi", "string"),
        Field("label", "string"),
        Field("year_published", "integer",
              requires=[IS_INT_IN_RANGE(1700,2050)]),
        Field("contributor", "string", length=128, required=True, notnull=True),
        Field("comment", "text"),
        Field("uploaded", "datetime", default=datetime.datetime.now(),
              writable=False, notnull=True),
        Field("treebase_id", "integer"),
        Field("last_modified","datetime",default=datetime.datetime.now()),
        format=_study_rep,
        migrate=migrate
        )
    db.study.citation.requires = [IS_NOT_EMPTY()]

    db.define_table(
        "study_tag",
        Field("study", db.study, ondelete="NO ACTION"),
        Field("tag", "string", required=True, notnull=True),
        Field("name", "string"),
        Field("value", "string"),
        format="%(tag)s",
        migrate=migrate
        )
    db.study_tag.name.readable = False
    db.study_tag.name.writable = False
    db.study_tag.value.readable = False
    db.study_tag.value.writable = False

    db.define_table(
        "study_file",
        Field("study", db.study, ondelete="NO ACTION"),
        Field("description"),
        Field("source"),
        Field("filename"),
        Field("file", "upload", uploadfield="data"),
        Field("data", "blob"),
        Field("contributor", "string", length=128, required=True, notnull=True),
        Field("comment", "text"),
        Field("uploaded", "datetime", default=datetime.datetime.now(),
              writable=False, notnull=True),
        migrate=migrate
        )

    db.define_table(
        "otu",
        Field("study", db.study, ondelete="NO ACTION"),
        Field("label", required=True, notnull=True),
        Field("taxon", db.taxon, ondelete="NO ACTION"),
        Field("ottol_name", db.ottol_name, ondelete="NO ACTION"),
        Field("tb_nexml_id"),
        ## Field("genus", db.taxon, ondelete="NO ACTION"),
        format="%(label)s",
        migrate=migrate
        )

    db.define_table(
        "sequence",
        Field("otu", db.otu, ondelete="NO ACTION"),
        Field("gene", db.gene, ondelete="NO ACTION"),
        Field("gi", "integer"),
        Field("ac", "string"),
        Field("data", "text"),
        format="%(ac)s",
        migrate=migrate
        )

    db.define_table(
        "stree",
        ## Field("sdata", db.sdata, ondelete="NO ACTION"),
        Field("study", db.study, ondelete="NO ACTION"),
        Field("contributor", "string", length=128, required=True, notnull=True),
        Field("uploaded", "datetime", default=datetime.datetime.now(),
              writable=False, notnull=True),
        Field("newick", "text", required=True),
        Field("clade_labels_represent", "string",
              ## default="bootstrap values",
              requires=IS_NULL_OR(IS_IN_SET(["taxon names", "bootstrap values",
                                             "posterior support"]))),
        Field("clade_labels_comment", "text"),
        Field("branch_lengths_represent", "string",
              requires=IS_NULL_OR(IS_IN_SET(["substitutions per site",
                                             "character changes",
                                             "time (Myr)",
                                             "bootstrap values",
                                             "posterior support"]))),
        Field("branch_lengths_comment", "text"),
        Field("newick_idstr", "text", writable=False, readable=False),
        Field("type", "string", length=128,required=True,notnull=True),
        Field("author_contributed", "boolean", default=False),
        ## Field("tb_study_id", "string", length=128),
        ## Field("tb_analysis_id", "string", length=128),
        Field("tb_tree_id", "string", length=128),
        Field("comment", "text"),
        Field("last_modified","datetime", default=datetime.datetime.now()),
        format="%(type)s [%(id)s]",
        migrate=migrate
        )
    db.stree.contributor.requires = [IS_NOT_EMPTY()]
    db.stree.newick.requires = [IS_NOT_EMPTY()]

    db.define_table(
        "stree_tag",
        Field("stree", db.stree, ondelete="NO ACTION"),
        Field("tag", "string", required=True, notnull=True),
        Field("name", "string"),
        Field("value", "string"),
        format="%(tag)s",
        migrate=migrate
        )
    db.stree_tag.name.readable = False
    db.stree_tag.name.writable = False
    db.stree_tag.value.readable = False
    db.stree_tag.value.writable = False

    db.define_table(
        "snode",
        Field("label", "string", length=128),
        Field("otu", db.otu, ondelete="NO ACTION"),
        ## Field("taxon", db.taxon, ondelete="NO ACTION"),
        Field("ottol_name", db.ottol_name, ondelete="NO ACTION",
              requires=IS_EMPTY_OR(IS_IN_DB(db, 'ottol_name.id',
                                            '%(name)s'))),
        ## Field("exemplar", db.taxon, ondelete="NO ACTION"),
        Field("ingroup", "boolean", notnull=True, default=False),
        Field("isleaf", "boolean", notnull=True, default=False,
              readable=False, writable=False),
        Field("parent", "reference snode", readable=False, writable=False,
              ondelete="NO ACTION"),
        Field("next", "integer", readable=False, writable=False),
        Field("back", "integer", readable=False, writable=False),
        Field("depth", "integer", readable=False, writable=False),
        Field("length", "double"),
        Field("age", "double"),
        Field("age_min", "double"),
        Field("age_max", "double"),
        Field("bootstrap_support", "double", required=False,
              requires=IS_NULL_OR(IS_FLOAT_IN_RANGE(0,1.0))),
        Field("posterior_support", "double", required=False,
              requires=IS_NULL_OR(IS_FLOAT_IN_RANGE(0,1.0))),
        Field("other_support", "double", required=False),
        Field("other_support_type", "string", required=False),
        Field("tree", db.stree, required=True, readable=False, writable=False,
              ondelete="NO ACTION"),
        Field("pruned", "boolean", default=False, required=True, notnull=True,
              readable=False, writable=False),
        Field("mtime", "datetime", default=datetime.datetime.now(),
              readable=False, writable=False),
        migrate=migrate
        )

    db.define_table(
        "gtree",
        Field("contributor", "string", length=128),
        Field("mtime", "datetime", default=datetime.datetime.now()),
        Field("title", "string", length=255),
        Field("comment", "text"),
        Field("date", "datetime"),
        migrate=migrate
        )

    db.define_table(
        "gnode",
        Field("label", "string", length=128),
        Field("isleaf", "boolean", default=False),
        Field("ntips", "integer", required=False),
        Field("pruned", "boolean", default=False, required=True, notnull=True,
              readable=False, writable=False),
        Field("parent", "reference gnode", readable=False, writable=False,ondelete="NO ACTION"),
        Field("next", "integer"),
        Field("back", "integer"),
        Field("length", "double", required=False),
        Field("age", "double", required=False),
        Field("age_min", "double", required=False),
        Field("age_max", "double", required=False),
        Field("tree", db.gtree, required=True, ondelete="NO ACTION"),
        Field("snode", db.snode, required=True, ondelete="NO ACTION"),
        Field("stree", db.stree, required=False, ondelete="NO ACTION"),
        Field("viewWeight", "double", required=False),
        Field("mtime", "datetime", default=datetime.datetime.now()),
        migrate=migrate
        )

    db.define_table(
        'gtree_edit',
        Field( 'gtree', db.gtree ),
        Field( 'action', 'string',requires=IS_IN_SET(["prune","graft","replace"]), required=True ),
        Field( 'target_gnode', db.gnode ),
        Field( 'affected_clade_id', "integer" ),
        Field( 'affected_node_id', "integer" ),
        Field( 'comment', 'text' ),
        Field( 'user', db.auth_user ),
        Field( 'originalTreeType', 'string', requires=IS_IN_SET( [ "grafted", "source" ] ) ),
        Field( 'mtime', "datetime", default=datetime.datetime.now() ),
        Field( 'newNodeOriginId', 'integer' ),
        Field( 'newNodeOriginType', 'integer' ),
        migrate=migrate
        )

    db.define_table(
        'prune_detail',
        Field( 'pruned_gnode', db.gnode ),
        Field( 'gtree_edit', db.gtree_edit ),
        migrate=migrate
        )

    db.define_table(
        'unique_user',
        Field( 'first_name', 'string' ), 
        Field( 'last_name', 'string' ),
        migrate=migrate
        )


    db.define_table(
        'user_map',
        Field( 'auth_user_id', db.auth_user ),
        Field( 'unique_user_id', db.unique_user ),
        migrate=migrate
        )

    db.define_table(
        'gtree_share',
        Field( 'user', db.auth_user ),
        Field( 'gtree', db.gtree ),
        migrate=migrate
        )

    db.define_table(
        'treebase_matrix',
        Field('study', db.study,
              required=True, notnull=True, ondelete="NO ACTION"),
        Field('label', 'string'),
        Field('type', 'string'),
        Field('nchar', 'integer'),
        Field('ntax', 'integer'),
        Field('tb_matrix_id', 'integer',
              unique=True, required=True, notnull=True),
        migrate=migrate
        )

    db.define_table(
        'treebase_matrix_row',
        Field('otu', db.otu,
              required=True, notnull=True, ondelete="NO ACTION"),
        Field('data', 'text',
              required=True, notnull=True, ondelete="NO ACTION"),
        migrate=migrate
        )

    db.define_table(
        'treeMeta',
        Field('tree', 'integer' ),
        Field('treeType', 'string' ),
        Field('depth', 'integer' ),
        migrate=migrate
        )

    db.define_table(
        'treeMetaDepthDetail',
        Field('treeMeta', db.treeMeta ),
        Field('depth', 'integer' ),
        Field('nodeCount', 'double' ),
        Field('tipCount', 'double' ),
        Field('longestLabel', 'integer' ),
        migrate=migrate
        )

    db.define_table(
        'phylogramNodeMeta',
        Field('tree', 'integer' ),
        Field('treeType', 'string' ),
        Field('nodeId', 'integer' ),
        Field('text', 'string' ),
        Field('weight', 'double' ),
        Field('longestTraversal', 'double' ),
        Field('descendantTipCount', 'integer' ),
        Field('closestDescendantLabel', 'string' ),
        Field('next', 'integer' ),
        Field('back', 'integer' ),
        Field('descendantLabelCount', 'integer' ),
        migrate=migrate
        )

    db.define_table(
        'userEdit',
        Field( 'userName', 'string' ),
        Field( 'timestamp', 'datetime', default=datetime.datetime.now() ),
        Field( 'tableName', 'string' ),
        Field( 'rowId', 'int' ),
        Field( 'fieldName', 'string' ),
        Field( 'previousValue', 'string' ),
        Field( 'updatedValue', 'string' ) )


    ## db.define_table(
    ##     "gtree_edit",
    ##     Field("gtree", db.gtree, required=True, ondelete="NO ACTION"),
    ##     Field("action", "string",
    ##           requires=IS_IN_SET(["prune","graft","replace"]),
    ##           required=True),
    ##     Field("person", "string", length=128),
    ##     Field("mtime", "datetime", default=datetime.datetime.now()),
    ##     Field("target_gnode", "integer", required=True),
    ##     Field("source_node", "integer"),
    ##     Field("source_node_type", "string",
    ##           requires=IS_IN_SET(["snode","gnode"])),
    ##     Field("new_gnode", "integer"),
    ##     Field("comment", "text"),
    ##     migrate=migrate
    ##     )
