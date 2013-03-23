# This is a quick and dirty script to assist the process of obtaining DOIs for studies.
#
# 1. Get the list of studies from phylografter's database:
#
#     use phylografter;
#     select id, doi, treebase_id, citation from study into outfile "/tmp/dois-tmp.txt";
#
#    (we put it in /tmp because the 'mysql' command is setuid so can't
#    write the file in our directory)
#
# 2. Create an empty tb.results file and shuffle query results
# 
#     touch tb.results cr.results
#     cp /tmp/dois-tmp.txt ./
#
# 3. Obtain as many DOIs from treebase as possible
#
#     python classify.py dois-tmp.txt | grep "treebase " | cat functions.sh - | bash >>tb.results
#
# 4. Process study list
#
#     python classify.py dois-tmp.txt >tmp.out
#
# 5. The file tmp.out has two parts.
#    The references have to be processed manually or sent to Crossref using this form
#
#     http://www.crossref.org/stqUpload/
#
#    This service requires registration and is limited to 1000 DOIs per month.
#    Must be used on chunks of fewer than 15000 characters (100 or so references).
#    Copy results returned by the service from browser into cr.results.
#
# 6. Generate mysql update commands
#
#     python classify.py dois-tmp.txt >tmp.out
#
# 7. Run the update commands on phylografter's database

import re, sys

# Some dois may have already been looked for in treebase
treebase_no_doi = {}
treebase_found_doi = {}
tbfile = open("tb.results", 'r')
for line in tbfile:
  cols = line.strip().split(' ')
  # missing 32 1852
  # found 33 10.1111/j.1095-8339.2010.01041.x
  if cols[0] == "missing":
    treebase_no_doi[cols[1]] = True
  elif cols[0] == "found":
    treebase_found_doi[cols[1]] = cols[2]
  else:
    print >>sys.stderr, "Not understood: %s" % line
tbfile.close()

# Some dois may have already been looked for via Crossref (or manually)
# The file consists of 2-, 3-, or 4-line blocks,
#   123. Reference
#   http://dx.doi.org/...
crossref_no_doi = {}
crossref_found_doi = {}
id_re = re.compile("(^[0-9]*). ")
crfile = open("cr.results", 'r')
id = "missing"
doi = "missing"
for line in crfile:
  line = line.strip()
  if line == "":
    if doi != "missing":
      crossref_found_doi[id] = doi
    elif id != "missing":
      crossref_no_doi[id] = True
    id = "missing"
    doi = "missing"
  else:
    m = id_re.search(line)
    if m:
      id = m.group(1)
    elif line.startswith("http://dx.doi.org/"):
      doi = line[18:]
crfile.close()

def for_crossref(study_id, reference):
  if reference.endswith(", null"):
    reference = reference[:-6]
  print '%s. %s.' % (study_id, reference)
  print

total = 0
already = 0
from_reference = 0
treebase_wins = 0
treebase_lookup = 0
crossref_wins = 0
crossref_loses = 0
crossref_lookup = 0
crossref_lookup_tb = 0

ready_to_insert = {}
look_up_in_treebase = {}
doi_field = {}

num_re = re.compile("^[0-9]*$")
doi_re = re.compile("10\\.[0-9]+/.+")

# Deal with mysql continuation lines
previous = ""

infile = open(sys.argv[1], 'r')

for line in infile:
  line = line.strip()

  if line.endswith("\r\\"):
    previous = previous + line[0:-2] + " "
  else:
    line = previous + line
    previous = ""
    cells = line.split("\t")
    # Columns: study id, doi, treebase, reference
    if len(cells) == 4:
      total += 1
      study_id = cells[0]
      doi = cells[1]
      doi_field[study_id] = doi
      treebase_id = cells[2]
      reference = cells[3]

      # Flush trailing . so it doesn't become part of DOI
      if reference.endswith("."):
        reference = reference[0:-1]

      if doi.startswith("10.") or doi.startswith("doi:") or doi.startswith("http:"):
        already += 1
      elif study_id == "222":   # Fake citation
        already += 1
      elif study_id == "1019":   # Fake citation
        already += 1
      elif study_id in treebase_found_doi:
        ready_to_insert[study_id] = treebase_found_doi[study_id]
        treebase_wins += 1
      elif study_id in crossref_found_doi:
        ready_to_insert[study_id] = crossref_found_doi[study_id]
        crossref_wins += 1
      else:
        m = doi_re.search(reference)
        if m:
          ready_to_insert[study_id] = m.group()
          from_reference += 1
        elif study_id in crossref_no_doi:
          crossref_loses += 1
        elif study_id in treebase_no_doi:
          # TBD: CLEAN ', null' OFF OF THE END
          for_crossref(study_id, reference)
          crossref_lookup_tb += 1
        elif num_re.match(treebase_id):
          look_up_in_treebase[study_id] = treebase_id
          treebase_lookup += 1
        else:
          for_crossref(study_id, reference)
          crossref_lookup += 1
    else:
      print >>sys.stderr, "Bad line:"
      print >>sys.stderr, line

infile.close()

print

for study_id in sorted(ready_to_insert.keys(), key=int):
  doi = doi_field[study_id]
  if doi == "\\N":
    print "update study set doi='%s' where id=%s and doi is null;" % (ready_to_insert[study_id], study_id)
  else:
    print "update study set doi='%s' where id=%s and doi='%s';" % (ready_to_insert[study_id], study_id, doi)
  
print


for study_id in look_up_in_treebase:
  print "treebase %s %s" % (study_id, look_up_in_treebase[study_id])


print >>sys.stderr, "Studies:            %d" % total
print >>sys.stderr, "Already have:       %d" % already
print >>sys.stderr, "Got from reference: %d" % from_reference
print >>sys.stderr, "Treebase succeeded: %d" % treebase_wins
print >>sys.stderr, "Treebase failed:    %d" % crossref_lookup_tb
print >>sys.stderr, "Try treebase:       %d" % treebase_lookup
print >>sys.stderr, "Got from crossref:  %d" % crossref_wins
print >>sys.stderr, "Crossref failed:    %d" % crossref_loses
print >>sys.stderr, "Try crossref:       %d" % crossref_lookup
