#! /usr/bin/env python
"""Generats an HTML document from an OData metadata document"""


import sys
import string
import logging
from optparse import OptionParser
import getpass

import pyslet.iso8601 as iso
import pyslet.rfc2396 as uri
import pyslet.rfc2617 as auth
import pyslet.rfc2616 as http
import pyslet.odata2.csdl as edm
import pyslet.odata2.metadata as edmx
import pyslet.xml20081126.structures as xml


def fetch_url(url, username=None, password=None):
    mgr = http.Client()
    url = uri.URIFactory.URI(url)
    # does url end with $metadata?
    if url.GetFileName() != "$metadata":
        url = uri.URIFactory.Resolve(url, "$metadata")
    if username:
        cred = auth.BasicCredentials()
        cred.userid = username
        cred.password = password
        cred.protectionSpace = url.GetCanonicalRoot()
        mgr.add_credentials(cred)
    doc = edmx.Document(baseURI=url, reqManager=mgr)
    doc.Read()
    mgr.close()
    if not doc.root.GetBase():
        doc.root.SetBase(url)
    return doc


def load_file(filename):
    doc = edmx.Document()
    with open(filename, 'rb') as f:
        doc.Read(f)
    return doc


def write_doc(doc, template, out):
    if not isinstance(doc.root, edmx.Edmx):
        return "Source was not a DataServices document"
    with open(template, 'rb') as f:
        data = f.read()
    params = {
        'namespace': "",
        'summary': "Schema Documentation",
        'description': '',
        'entity_list': "<p>Not supported in this version</p>",
        'tables': "<p>Not supported in this version</p>",
        'index': "<p>Not supported in this version</p>",
        'date': str(iso.TimePoint.FromNow())
    }
    ds = doc.root.DataServices
    if len(ds.Schema) != 1:
        logging.warn("Documenting the first Schema tag only")
    params['namespace'] = xml.EscapeCharData7(ds.Schema[0].name)
    sdoc = ds.Schema[0].Documentation
    if sdoc is not None:
        if sdoc.Summary is not None:
            params['summary'] = "%s" % xml.EscapeCharData7(
                sdoc.Summary.GetValue())
        if sdoc.LongDescription is not None:
            params['description'] = "%s" % xml.EscapeCharData7(
                sdoc.LongDescription.GetValue())
    tables = []
    dl_items = []
    index_items = []
    for ec in ds.Schema[0].EntityContainer:
        if not ec.IsDefaultEntityContainer():
            logging.warn("Ignoring non-default EntityContainer: %s", ec.name)
            continue
        es_list = []
        for es in ec.EntitySet:
            es_list.append(es.name)
        es_list.sort()
        for esn in es_list:
            es = ec[esn]
            dl_items.append('<dt><a href=%s>%s</a></dt>' %
                            (xml.EscapeCharData7("#" + es.name, True),
                             xml.EscapeCharData7(es.name)))
            index_items.append((es.name, es.name, "entity set"))
            if es.Documentation is not None:
                if es.Documentation.Summary is not None:
                    dl_items.append('<dd>%s</dd>' % xml.EscapeCharData7(
                        es.Documentation.Summary.GetValue()))
            tables.append(es_table(es, index_items))
    params['entity_list'] = string.join(dl_items, '\n')
    params['tables'] = string.join(tables, "\n\n")
    index_items.sort()
    index_dl = []
    cname = ''
    for name, link, note in index_items:
        if name != cname:
            index_dl.append('<dt>%s</dt>' % xml.EscapeCharData7(name))
            cname = name
        index_dl.append('<dd><a href=%s>%s</a></dd>' %
                        (xml.EscapeCharData7("#" + link, True),
                         xml.EscapeCharData7(note)))
    params['index'] = string.join(index_dl, '\n')
    out.write(data % params)
    return 0


def es_table(es, index_items):
    result = """<h3><a id=%(anchor)s>%(title)s</a></h3>
%(summary)s
%(description)s
<table class="typedef">
    <thead>
        <th>Name</th>
        <th>Type</th>
        <th>Multiplicity</th>
        <th>Description</th>
        <th>Notes</th>
    </thead>
    <tbody>%(body)s</tbody>
</table>"""
    params = {
        'anchor': xml.EscapeCharData7(es.name, True),
        'title': '',
        'summary': '',
        'description': '',
        'body': ''}
    tb = []
    type = es.entityType
    if type.HasStream():
        params['title'] = (xml.EscapeCharData7(es.name) +
                           " <em>(Media Resource)</em>")
    else:
        params['title'] = xml.EscapeCharData7(es.name)
    typedoc = type.Documentation
    if typedoc is not None:
        if typedoc.Summary is not None:
            params['summary'] = (
                '<p class="summary">%s</p>' %
                xml.EscapeCharData7(typedoc.Summary.GetValue()))
        if typedoc.LongDescription is not None:
            params['description'] = (
                '<p class="description">%s</p>' %
                xml.EscapeCharData7(typedoc.LongDescription.GetValue()))
    for p in type.Property:
        if p.name in es.keys:
            tr = ['<tr class="key">']
        else:
            tr = ["<tr>"]
        link = '%s.%s' % (es.name, p.name)
        tr.append("<td><a id=%s>%s</a></td>" % (
            xml.EscapeCharData(link, True),
            xml.EscapeCharData7(p.name)))
        index_items.append((p.name, link, "property of %s" % es.name))
        tr.append("<td>%s</td>" % xml.EscapeCharData7(p.type))
        tr.append("<td>%s</td>" % ("Optional" if p.nullable else "Required"))
        summary = description = ""
        if p.Documentation is not None:
            if p.Documentation.Summary:
                summary = p.Documentation.Summary.GetValue()
            if p.Documentation.LongDescription:
                description = p.Documentation.LongDescription.GetValue()
        tr.append("<td>%s</td>" % xml.EscapeCharData7(summary))
        tr.append("<td>%s</td>" % xml.EscapeCharData7(description))
        tr.append("</tr>")
        tb.append(string.join(tr, ''))
    for np in type.NavigationProperty:
        tr = ['<tr class="navigation">']
        link = '%s.%s' % (es.name, np.name)
        tr.append("<td><a id=%s>%s</a></td>" % (
            xml.EscapeCharData(link, True),
            xml.EscapeCharData7(np.name)))
        index_items.append((np.name, link, "navigation property of %s" %
                            es.name))
        tr.append("<td><em>%s</em></td>" %
                  xml.EscapeCharData7(es.NavigationTarget(np.name).name))
        tr.append("<td>%s</td>" %
                  edm.EncodeMultiplicity(np.toEnd.multiplicity))
        summary = description = ""
        if np.Documentation is not None:
            if np.Documentation.Summary:
                summary = np.Documentation.Summary.GetValue()
            if np.Documentation.LongDescription:
                description = np.Documentation.LongDescription.GetValue()
        tr.append("<td>%s</td>" % xml.EscapeCharData7(summary))
        tr.append("<td>%s</td>" % xml.EscapeCharData7(description))
        tr.append("</tr>")
        tb.append(string.join(tr, ''))

    params['body'] = string.join(tb, '\n')
    return result % params


if __name__ == '__main__':
    parser = OptionParser()
    parser.add_option("-s", "--service", dest="url",
                      help="fetch metadata from URL for diff")
    parser.add_option("-u", "--user", dest="user",
                      help="user name for basic auth credentials")
    parser.add_option("--password", dest="password",
                      help="password for basic auth credentials")
    parser.add_option("-t", "--template", dest="template",
                      default="odatadoc.tmpl",
                      help="path to the template file")
    parser.add_option("-v", action="count", dest="logging",
                      default=0, help="increase verbosity of output")
    (options, args) = parser.parse_args()
    if options.logging > 3:
        level = 3
    else:
        level = options.logging
    logging.basicConfig(
        level=[logging.ERROR, logging.WARN, logging.INFO,
               logging.DEBUG][level])
    if len(args) != 1 and options.url is None:
        sys.exit("Usage: odatadoc.py [-s URL] | [metadata]")
    if options.user is not None:
        username = options.user
        if options.password is not None:
            password = options.password
        else:
            password = getpass.getpass()
    else:
        username = password = None
    if not args:
        # load metadata from the URL
        doc = fetch_url(options.url, username, password)
    else:
        doc = load_file(args[0])
    sys.exit(write_doc(doc, options.template, sys.stdout))
