"""
The `petl` module.

"""


__version__ = VERSION = '0.24.1'


from petl.util import header, fieldnames, data, records, rowcount, look, see, \
    itervalues, values, iterdata, valuecounter, valuecounts, \
    valueset, isunique, lookup, lookupone, recordlookup, recordlookupone, \
    typecounter, typecounts, typeset, parsecounter, parsecounts, \
    stats, rowlengths, DuplicateKeyError, datetimeparser, dateparser, \
    timeparser, boolparser, \
    expr, limits, strjoin, valuecount, lookall, dataslice, parsenumber, \
    stringpatterns, stringpatterncounter, randomtable, dummytable, \
    diffheaders, diffvalues, columns, facetcolumns, heapqmergesorted, \
    shortlistmergesorted, progress, clock, isordered, rowgroupby, nrows, \
    nthword, lookstr, listoflists, tupleoftuples, listoftuples, tupleoflists, \
    lol, tot, tol, lot, iternamedtuples, namedtuples, iterrecords, dicts, \
    iterdicts, dictlookup, dictlookupone, cache, empty, numparser, coalesce

from petl.io import fromcsv, frompickle, fromsqlite3, tocsv, topickle, \
    tosqlite3, fromdb, \
    appendcsv, appendpickle, appendsqlite3, todb, appenddb, fromtext, \
    totext, appendtext, fromxml, fromjson, fromdicts, tojson, \
    fromtsv, totsv, appendtsv, tojsonarrays, tohtml, fromucsv, toucsv, \
    appenducsv, fromutsv, toutsv, appendutsv, \
    FileSource, GzipSource, BZ2Source, URLSource, StdinSource, StdoutSource, \
    StringSource, PopenSource, ZipSource, \
    fromutext, toutext, appendutext, touhtml

from petl.transform import rename, cut, cat, convert, fieldconvert, addfield, \
    rowslice, \
    head, tail, sort, melt, recast, duplicates, conflicts, \
    mergereduce, select, complement, diff, capture, \
    split, fieldmap, facet, selecteq, rowreduce, merge, aggregate, \
    recordreduce, \
    rowmap, recordmap, rowmapmany, recordmapmany, setheader, pushheader, skip, \
    extendheader, unpack, join, leftjoin, rightjoin, outerjoin, crossjoin, \
    antijoin, rangeaggregate, rangecounts, selectop, selectne, selectgt, \
    selectge, selectlt, selectle, rangefacet, selectrangeopenleft, \
    selectrangeopenright, selectrangeopen, selectrangeclosed, rangerowreduce, \
    rangerecordreduce, selectin, selectnotin, selectre, rowselect, \
    recordselect, \
    fieldselect, rowlenselect, selectis, selectisnot, selectisinstance, \
    transpose, \
    intersection, pivot, recordcomplement, recorddiff, cutout, skipcomments, \
    convertall, convertnumbers, hashjoin, hashleftjoin, hashrightjoin, \
    hashantijoin, hashcomplement, hashintersection, replace, replaceall, \
    resub, flatten, unflatten, mergesort, annex, unpackdict, unique, \
    fold, mergeduplicates, addrownumbers, selectcontains, search, sub, \
    addcolumn, lookupjoin, hashlookupjoin, filldown, fillright, fillleft, \
    multirangeaggregate, unjoin, rowgroupmap, distinct, \
    groupcountdistinctvalues, \
    groupselectfirst, groupselectmax, groupselectmin, selecttrue, \
    selectfalse, \
    selectnone, selectnotnone, update, selectusingcontext, \
    addfieldusingcontext, \
    prefixheader, suffixheader, movefield


def lenstats(table, field):
    """
    Convenience function to report statistics on value lengths under the given
    field. E.g.::

        >>> from petl import lenstats    
        >>> table1 = [['foo', 'bar'],
        ...           [1, 'a'],
        ...           [2, 'aaa'],
        ...           [3, 'aa'],
        ...           [4, 'aaa'],
        ...           [5, 'aaaaaaaaaaa']]
        >>> lenstats(table1, 'bar')
        {'count': 5, 'errors': 0, 'min': 1.0, 'max': 11.0, 'sum': 20.0, 'mean': 4.0}

    """

    return stats(convert(table, field, lambda v: len(v)), field)


# convenience aliases
eq = selecteq
ne = selectne
lt = selectlt
gt = selectgt
le = selectle
ge = selectge
true = selecttrue
false = selectfalse
none = selectnone
notnone = selectnotnone
counts = valuecounts
move = movefield
