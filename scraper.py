
import httplib
import csv
import mechanize 
import lxml.html
import scraperwiki

annDonorsurl = "http://periodicdisclosures.aec.gov.au/AnalysisDonor.aspx"

annReportingPeriods={
"1998-1999":"1",
"1999-2000":"2",
"2000-2001":"3",
"2001-2002":"4",
"2002-2003":"5",
"2003-2004":"6",
"2004-2005":"7",
"2005-2006":"8",
"2006-2007":"9",
"2007-2008":"10",
"2008-2009":"23",
"2009-2010":"24",
"2010-2011":"48",
"2011-12":"49",
"2012-13":"51",
"2013-14":"55",
}


def patch_http_response_read(func):
    def inner(*args):
        try:
            return func(*args)
        except httplib.IncompleteRead, e:
            return e.partial

    return inner
httplib.HTTPResponse.read = patch_http_response_read(httplib.HTTPResponse.read)

uniqueRowIndex = 0
for reportingPeriod, periodid in annReportingPeriods.items():
    br = mechanize.Browser()
    response = br.open(annDonorsurl)
    print "Loading data for "+reportingPeriod

    br.select_form(predicate=lambda f: f.attrs.get('id', None) == 'formMaster')

    br['ctl00$dropDownListPeriod']=[periodid]
    response = br.submit("ctl00$buttonGo")
    response = br.open(annDonorsurl)

    br.select_form(predicate=lambda f: f.attrs.get('id', None) == 'formMaster')
    response = br.submit("ctl00$ContentPlaceHolderBody$analysisControl$buttonExport")

    br.select_form(predicate=lambda f: f.attrs.get('id', None) == 'formMaster')
    br['ctl00$ContentPlaceHolderBody$exportControl$dropDownListOptions']=['csv']
    response = br.submit("ctl00$ContentPlaceHolderBody$exportControl$buttonExport")

    lines = response.read().split("\n")
    clist = list(csv.reader(lines))
    
    title = clist.pop(0)
    dateupdated = clist.pop(0)
    headers = clist.pop(0)
    if "" in headers:
        headers.remove("")
    headers.append("ReportingPeriod")
    headers.append("Unique")
    print "Period "+reportingPeriod+" %d columns and %d rows" %  (len(headers), len(clist))
    rows = []
    for row in clist:
        if len(row) == 9: 
            row[8] = reportingPeriod
            
            row.append(uniqueRowIndex)
            rows.append(dict(zip(headers, row)))
            uniqueRowIndex = uniqueRowIndex+1
        else:
            print "Invalid row in "+reportingPeriod+". Ignored and continuing."

    unique_keys =  ['Unique']
    scraperwiki.sqlite.save(unique_keys, rows)
