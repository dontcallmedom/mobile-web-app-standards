import sys
import json
from urllib import urlopen
from lxml import etree

trs_rdf = urlopen("http://www.w3.org/2002/01/tr-automation/tr.rdf")
trs = etree.parse(trs_rdf)
wgs_rdf = urlopen("http://www.w3.org/2000/04/mem-news/public-groups.rdf")
wgs = etree.parse(wgs_rdf)

ns = {"c":"http://www.w3.org/2000/10/swap/pim/contact#", "o":"http://www.w3.org/2001/04/roadmap/org#", "d":"http://www.w3.org/2000/10/swap/pim/doc#", "rdf":"http://www.w3.org/1999/02/22-rdf-syntax-ns#", "rec":"http://www.w3.org/2001/02pd/rec54#", "dc":"http://purl.org/dc/elements/1.1/"}

data = {}

maturities = ["LastCall", "WD", "CR", "PR", "Rec", "Note"]

for filename in sys.argv[1:]:
    id = filename.split("/")[-1].split(".")[0]
    f = open(filename)
    feature_data = json.loads(f.read())
    tr_latest = "/".join(feature_data["TR"].split("/")[:5])
    if tr_latest == "":
        continue
    tr = trs.xpath("/rdf:RDF/*[d:versionOf/@rdf:resource='%s' or d:versionOf/@rdf:resource='%s/']" % (tr_latest, tr_latest),namespaces=ns)
    if len(tr) == 0:
        sys.stderr.write("%s: %s not found in tr.rdf\n" % (id, tr_latest))
        continue
    tr = tr[0]
    title = tr.xpath("dc:title/text()", namespaces=ns)[0]
    maturity_url = tr.xpath("rdf:type/@rdf:resource",namespaces=ns)
    maturity_type = tr.tag.split("}")[1:][0]
    maturity = ""
    maturity_types = []
    if len(maturity_url) > 0:
        def getType(x): return x.split('#')[1]
        maturity_types = map(getType , maturity_url)
    maturity_types.append(maturity_type)
    pickMaturity = (lambda x, y: x if not y in maturities or (x in maturities and maturities.index(x) < maturities.index(y)) else y)
    maturity = reduce(pickMaturity, maturity_types)
    wg_urls = tr.xpath("o:deliveredBy/c:homePage/@rdf:resource", namespaces=ns)
    data[id]={"wgs":[], "maturity":maturity, "title":title}
    for url in wg_urls:
        wg = {"url":url}
        wg["label"] =wgs.xpath("/rdf:RDF/*[c:homePage/@rdf:resource='%s']/o:name/text()" % url, namespaces=ns)
        data[id]["wgs"].append(wg)

print json.dumps(data)
