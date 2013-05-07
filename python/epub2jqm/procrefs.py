#!/usr/bin/env python


import formatter, htmllib, locale, os, StringIO, re, readline, tempfile, zipfile
import base64, webbrowser
import json
import csv


from bs4 import BeautifulSoup

locale.setlocale(locale.LC_ALL, 'en_US.utf-8')

basedir = ''
genPath = 'gen'
tempPath = 'temp'
rawHeadingPath = "temp/refs/heading-content-raw/"
pageHeadingsPath = "page/refs/headings/"
chaps = None
headingsStore = {}          # store metadata for all headings found in EPUB

class Breadcrumb():
    def __init__(self, text, link):
        self.text = text
        self.link = link


#region Common Head for HTML files
def write_references_common_head(f, title):
    f.write('''<!DOCTYPE html>
<html>
    <head>
        <meta charset="utf-8" />
        <meta name="viewport" content="width=device-width, height=device-height, initial-scale=1.0, maximum-scale=1.0, minimum-scale=1.0, user-scalable=no" />
        <title>''')

    f.write(title)

    f.write('''</title>

        <link href="../jquery-mobile/jquery.mobile.theme-1.3.1.min.css" rel="stylesheet" type="text/css"/>
        <link href="../jquery-mobile/jquery.mobile.swatch.f.css" rel="stylesheet" type="text/css"/>
        <link href="../jquery-mobile/jquery.mobile.swatch.l.css" rel="stylesheet" type="text/css"/>
        <link href="../assets/css/custom_arrow.css" rel="stylesheet" type="text/css"/>
        <link href="../jquery-mobile/jquery.mobile.structure-1.3.1.min.css" rel="stylesheet" type="text/css"/>
        <link href="../assets/css/full.css" rel="stylesheet" type="text/css"/>
        <link href="../assets/css/recreated_tables.css" rel="stylesheet" type="text/css"/>
        <script src="../jquery-mobile/jquery-1.9.1.min.js" type="text/javascript"></script>
        <script src="../../jquery-customization.js" type="text/javascript"></script>
        <script src="../jquery-mobile/jquery.mobile-1.3.1.min.js" type="text/javascript"></script>
        <script src="../../cordova-2.7.0.js" type="text/javascript" charset="utf-8"></script>
        <script src="../assets/js/metrics.js" type="text/javascript" charset="utf-8"></script>

    </head>''')

#endregion
def write_references_breadcrumbs(html_file, headingId):

    # do not write breadcrumbs for root condition
    if headingId != 0:
        breadcrumbs = []
        currentHeadingId = headingId

        # put heading's listview into breadcrumbs
        if heading_has_children(headingId) and heading_has_text(headingId):
            text = get_heading_title(headingId)
            link = get_heading_listview_link(headingId)
            breadcrumb = Breadcrumb(text, link)
            breadcrumbs.append(breadcrumb)

        while currentHeadingId != 0:
            parentId = get_heading_parent(currentHeadingId)
            text = get_heading_title(parentId)
            link = get_heading_parent_listview_link(currentHeadingId)
            breadcrumb = Breadcrumb(text, link)
            breadcrumbs.append(breadcrumb)
            currentHeadingId = parentId

        breadcrumbs.reverse()

        html_file.write('''
            <div id=references_breadcrumbs>
            ''')
        if len(breadcrumbs):
            for index, breadcrumb in enumerate(breadcrumbs):
                assert isinstance(breadcrumb, Breadcrumb)

                html_file.write('''
                    <a href="''')
                html_file.write(breadcrumb.link)
                html_file.write('''" >''')
                html_file.write(breadcrumb.text)
                html_file.write('''</a>''')

                html_file.write('<span class="carrot"> > </span>')

        if heading_has_children(headingId) and heading_has_text(headingId):
            html_file.write("Overview")
        else:
            html_file.write(get_heading_title(headingId))

        html_file.write('''
            </div>   <!-- end of references listview breadcrumbs -->
            </br>''')


def write_references_listview_breadcrumbs(html_file, headingId):

    # do not write breadcrumbs for root condition
    if headingId != 0:
        breadcrumbs = []
        currentHeadingId = headingId

        while currentHeadingId != 0:
            parentId = get_heading_parent(currentHeadingId)
            text = get_heading_title(parentId)
            link = get_heading_parent_link(currentHeadingId)
            breadcrumb = Breadcrumb(text, link)
            breadcrumbs.append(breadcrumb)
            currentHeadingId = parentId

        breadcrumbs.reverse()

        html_file.write('''
            </br>
            <div id=references_listview_breadcrumbs>
            ''')
        if len(breadcrumbs):
            for index, breadcrumb in enumerate(breadcrumbs):
                assert isinstance(breadcrumb, Breadcrumb)

                html_file.write('''
                    <a href="''')
                html_file.write(breadcrumb.link)
                html_file.write('''" >''')
                html_file.write(breadcrumb.text)
                html_file.write('''</a>''')

                html_file.write(' > ')

        html_file.write(get_heading_title(headingId))

        html_file.write('''
            </div>   <!-- end of references listview breadcrumbs -->
            </br>''')


def write_references_page_body_start(f, headingId):
    global headingsStore
    f.write('''
    <body>

        <!-- Start of page -->
        <div data-role="page" id="''')

    pageId = "r%s" % headingId
    f.write(pageId)

    f.write('''" data-theme="d">
            <div data-role="header" data-id="references-header" data-theme="l" data-position="fixed">
                <a href="''')
    f.write(get_heading_parent_listview_link(headingId))
    f.write('''" data-role="button" data-iconshadow="false" data-corners="false" data-theme="reset" data-transition="fade" class="back_button" role="button" aria-label="back"></a>''')
    f.write('''
                <h1>References</h1>
	            <a href="../menu.html"  rel="external" data-role="button" data-theme="reset" data-transition="fade" data-iconshadow="false" data-corners="false" class="menu_button ui-btn-right" role="button" aria-label="main menu"></a>''')
    #print headingsStore[headingId]

    f.write('''
            </div>  <!-- end of header div -->

            <div data-role="content">''')

    write_references_breadcrumbs(f, headingId)


def write_references_page_body_end(f, headingId):

    f.write('''
            </div>

            <script type="text/javascript">

                $('#''')
    pageId = "r%s" % headingId

    f.write(pageId)

    f.write("""').on('pageshow', function (event, ui) {
                    document.addEventListener("deviceready", function(){
                    trackReferencesPageView(""")
    f.write("%s" % headingId)
    f.write(''');
                },true);
            });

            </script>
        </div>
    </body>
</html>

    ''')


def get_heading_parent(headingId):
    return headingsStore[headingId]['parent']

def get_heading_title(headingId):
    return headingsStore[headingId]['title']

def get_heading_level(headingId):
    return headingsStore[headingId]['level']

def heading_has_children(headingId):
    state = headingsStore[headingId]['hasChildren']

    return headingsStore[headingId]['hasChildren']

def heading_has_text(headingId):
    state = headingsStore[headingId]['hasText']
    return state

def get_heading_children(headingId):
    return headingsStore[headingId]['children']

def get_heading_parent_link(headingId):
    parentId = get_heading_parent(headingId)
    link = "lv-%d.html" % parentId
    return link

def get_heading_listview_link(headingId):
    link = "lv-%d.html" % headingId
    return link

def get_heading_parent_listview_link(headingId):
    # if heading has text then parent link is it's own listview
    if heading_has_text(headingId) and heading_has_children(headingId):
        link = "lv-%d.html" % headingId
    else:
        parentId = get_heading_parent(headingId)
        link = "lv-%d.html" % parentId
    return link

def get_heading_child_link(childId):
    if heading_has_children(childId) is True:
        link = "lv-%d.html" % childId
    else:
        link = "%d.html" % childId
    return link

def get_heading_overview_link(headingId):
    link = "%d.html" % headingId
    return link


def textify(html_snippet):
    ''' text dump of html '''
    class Parser(htmllib.HTMLParser):
        def anchor_end(self):
            self.anchor = None

    class Formatter(formatter.AbstractFormatter):
        pass

    class Writer(formatter.DumbWriter):
        def __init__(self, fl):
            formatter.DumbWriter.__init__(self, fl)
        def send_label_data(self, data):
            self.send_flowing_data(data)
            self.send_flowing_data(' ')

    o = StringIO.StringIO()
    p = Parser(Formatter(Writer(o)))
    p.feed(html_snippet)
    p.close()

    return o.getvalue()

def table_of_contents(fl):
    global basedir

    # find opf file
    soup = BeautifulSoup(fl.read('META-INF/container.xml'))
    opf = dict(soup.find('rootfile').attrs)['full-path']

    basedir = os.path.dirname(opf)
    print "Base Directory = %s" % basedir
    if basedir:
        basedir = '{0}/'.format(basedir)

    soup =  BeautifulSoup(fl.read(opf))

    # title
    yield (soup.find('dc:title').text, None)

    # all files, not in order
    print("Printing all files:")
    x, ncx = {}, None
    for item in soup.find('manifest').findAll('item'):
        d = dict(item.attrs)
        x[d['id']] = '{0}{1}'.format(basedir, d['href'])
        if d['media-type'] == 'application/x-dtbncx+xml':
            ncx = '{0}{1}'.format(basedir, d['href'])
            print ("Table of contents file = %s" % ncx)


    # reading order, not all files
    print ("Printing files in order:")
    y = []
    for item in soup.find('spine').findAll('itemref'):
        y.append(x[dict(item.attrs)['idref']])

    z = {}
    if ncx:
        # get titles from the toc
        soup =  BeautifulSoup(fl.read(ncx))

        for navpoint in soup('navpoint'):
            k = navpoint.content.get('src', None)
            # strip off any anchor text
            k = k.split('#')[0]
            if k:
                z[k] = navpoint.navlabel.text

    # output
    for section in y:
        if section in z:
            yield (z[section].encode('utf-8'), section.encode('utf-8'))
        else:
            yield (u'', section.encode('utf-8').strip())

def list_chaps(chaps):

    print "Listing chapters"
    for i, (title, src) in enumerate(chaps):
        print "Source file = %s " % src
    return i

def check_epub(fl):
    if os.path.isfile(fl) and os.path.splitext(fl)[1].lower() == '.epub':
        return True

def dump_epub(fl):
    if not check_epub(fl):
        return
    fl = zipfile.ZipFile(fl, 'r')
    chaps = [i for i in table_of_contents(fl)]
    for title, src in chaps:
        print title
        print '-' * len(title)
        if src:
            soup = BeautifulSoup(fl.read(src))
            print unicode(soup.find('body')).encode('utf-8')
        print '\n'

def parse_epub(fl):
    global chaps

    if not check_epub(fl):
        print "Bad EPUB file."
        return

    fl = zipfile.ZipFile(fl, 'r')
    chaps = [i for i in table_of_contents(fl)]

    list_chaps(chaps)


def write_heading_content(headingId):
    # write current heading, and content between current and next heading
    # to heading content file as HTML using heading ID as name
    with open(pageHeadingsPath + str(headingId) + ".html", "w") as hidf:

        try:

            write_references_common_head(hidf, "References")
            write_references_page_body_start(hidf, headingId)

            # read in raw content from temp file and write it to heading content file
            with open(rawHeadingPath + str(headingId) + ".html", "r") as thcf:
                try:
                    ## Read the first line
                    line = thcf.readline()
                    while line:
                        hidf.write(line)
                        line = thcf.readline()

                except IOError:
                    pass
                finally:
                    thcf.close()

            write_references_page_body_end(hidf, headingId)

        finally:
            hidf.close()


def write_temp_heading_content(headingId, headingTag):
    # write current heading, and content between current and next heading
    # to heading content file as HTML using heading ID as name
    with open(rawHeadingPath + str(headingId) + ".html", "w") as thcf:

        try:
            thcf.write (headingTag.prettify(formatter="html"))
            sibling = headingTag.findNextSibling(text=None)
            while sibling is not None:
                if sibling.name == 'h1' or sibling.name == 'h2' or sibling.name == 'h3' or\
                   sibling.name == 'h4' or sibling.name == 'h5' or sibling.name == 'h6':
                    break
                else:

                    thcf.write (sibling.prettify(formatter="html"))
                    sibling = sibling.findNextSibling(text=None)

        finally:
            thcf.close()

def write_children_listview_body(f, headingId):

    f.write('''
    <body>
        <!-- Start of listview page -->
        <div data-role="page" id="''')

    f.write(str(headingId))
    f.write('''" data-theme="d">

  	        <div data-role="header" data-id="references-header" data-theme="l" data-position="fixed">''')

    if get_heading_level(headingId) > 0:
        f.write('''<a href="''')
        f.write(get_heading_parent_link(headingId))
        f.write('''" data-role="button" data-theme="reset" data-iconshadow="false" data-transition="fade" data-corners="false" class="back_button" role="button" aria-label="back"></a>''')
    f.write('''
                <h1>References</h1>
	            <a href="../menu.html" rel="external" data-role="button" data-theme="reset" data-iconshadow="false" data-corners="false" data-transition="fade" class="menu_button ui-btn-right" role="button" aria-label="main menu"></a>
            </div>  <!-- end of header div -->
    ''')



    f.write('''
            <div data-role="content" data-theme="d" >''')

    write_references_listview_breadcrumbs(f, headingId)

    f.write('''
                <ul data-count-theme="b" data-role="listview" data-inset="true" data-divider-theme="a">''')

    # if heading has children and text then first
    # item in list is the Overview which is text
    # of current heading
    if heading_has_text(headingId):
        f.write('''

                    <li data-icon="thin-arrow"><a href="''')
        f.write(get_heading_overview_link(headingId))
        f.write('''">Overview</a></li>''')

    children = get_heading_children(headingId)
    for childId in children:
        print "Child ID = %s" % childId
        title = get_heading_title(childId)
        childLink = get_heading_child_link(childId)
        f.write('''
                    <li data-icon="thin-arrow"><a href="''')
        f.write(childLink)
        f.write('''" data-transition="fade" ><div style="white-space:normal;">''')
        f.write(title)
        f.write('''</div></a></li>''')


    # write link to parent list view
    f.write('''
                </ul> <!-- end of listview -->
            </div> <!-- end of content div -->
        </div> <!-- end of page div -->
    </body>
</html>

        ''')

def write_children_listview(headingId):
    # write current heading, and content between current and next heading
    # to heading content file as HTML using heading ID as name
    with open(pageHeadingsPath + "lv-" + str(headingId) + ".html", "w") as lvf:

        try:
            write_references_common_head(lvf, 'References')
            write_children_listview_body(lvf, headingId)
        finally:
            lvf.close()

def create_heading_map(fl):
    global headingsStore

    headingId = 1
    h1ListView  = []
    h2ListView  = []
    h3ListView  = []
    h4ListView  = []
    h5ListView  = []
    lastTag = None
    lastLevel = 1

    try:
        # turn file handle into zip file handle
        fl = zipfile.ZipFile(fl, 'r')

        # create a new JSON file that contains all the headings metadata
        with open("content-map-refs.txt", "w") as f:
            try:
                # write root
                headingsStore[0] = {'title':'References', 'level':0, 'parent':None, 'src':None, 'hasText':False, 'hasChildren':True}

                #for each chapter file in the EPUB
                for title, src in chaps:
                    if src:
                        # BeautifulSoup creates a nested data structure that represents
                        # the XHTML chapter file that is in the EPUB document
                        soup = BeautifulSoup(fl.read(src))

                        # get just the heading tags
                        headings = soup.find_all(["h1", "h2", "h3", "h4", "h5", "h6"])
                        for headingTag in headings:
                            if headingTag.name == "h1":
                                level = 1
                                parentId = 0
                                h1ListView.append(headingId)
                            elif headingTag.name == "h2":
                                level = 2
                                h2ListView.append(headingId)
                                # parent is last one in higher level list
                                parentId = h1ListView[-1]
                            elif headingTag.name == "h3":
                                level = 3
                                h3ListView.append(headingId)
                                parentId = h2ListView[-1]
                            elif headingTag.name == "h4":
                                level = 4
                                h4ListView.append(headingId)
                                parentId = h3ListView[-1]
                            elif headingTag.name == "h5":
                                level = 5
                                h5ListView.append(headingId)
                                parentId = h4ListView[-1]
                            elif headingTag.name == "h6":
                                level = 6
                                parentId = h5ListView[-1]
                            elif headingTag.name == "img":
                                print "Found IMG tag."

                            #print "Heading text = " + headingTag.text
                            #print "Heading tag = " + headingTag.name

                            # write out contents of original file
                            # may delete this later as unnecessary
                            htmlFile = os.path.basename(src)
                            htmlFile = os.path.splitext(htmlFile)[0]
                            htmlFile = "temp/refs/orig-file-content/" + htmlFile + ".html"
                            # print "HTML file =", htmlFile

                            # see if heading has text below it
                            sibling = headingTag.findNextSibling(text=None)
                            while sibling is None:
                                sibling = headingTag.findNextSibling(text=None)

                            if sibling.name == 'h1' or sibling.name == 'h2' or sibling.name == 'h3' or\
                               sibling.name == 'h4' or sibling.name == 'h5' or sibling.name == 'h6':
                                headingHasText = False
                            else:
                                headingHasText = True

                            hasChildren = False
                            headingsStore[headingId] = {'title':headingTag.text, 'level':level, 'parent':parentId, 'src':htmlFile, 'hasText':headingHasText, 'hasChildren':hasChildren}

                            if headingHasText:
                                write_temp_heading_content(headingId, headingTag)

                            # modify heading tag with custom attributes
                            headingTag['data-irda-section'] = 'undefined'
                            headingTag['data-irda-condition'] = 'undefined'
                            headingTag['data-irda-hid'] = headingId

                            # write individual file for each heading
                            headingId += 1
                            lastTag = headingTag


                        # done processing chapter file, write it out as HTML
                        with open(htmlFile, "w") as hf:
                            try:
                                hf.write (soup.body.prettify(formatter="html"))
                            finally:
                                hf.close()

                # now that we have post heading information
                # do some post processing
                for parentHeadingId in headingsStore.keys():
                    childHeadings = []
                    for childHeadingId in headingsStore.keys():
                        if get_heading_parent(childHeadingId) == parentHeadingId:
                            childHeadings.append(childHeadingId)
                    if len(childHeadings) != 0:
                        headingsStore[parentHeadingId]['hasChildren'] = True
                        dict = headingsStore[parentHeadingId]
                        dict['children'] = childHeadings
                        headingsStore[parentHeadingId] = dict
                        # print "Parent ID of", parentHeadingId, "has children ", childHeadings
                    else:
                        headingsStore[parentHeadingId]['hasChildren'] = False
                        # print "Parent ID of %d has no children" % (parentHeadingId)

            finally:
                json.dump(headingsStore, f, indent=4)
            f.close()
    except IOError:
        pass

    # now that we have all child heading info
    # create heading listview and heading content files
    for headingId in headingsStore.keys():
        if heading_has_text(headingId):
            write_heading_content(headingId)
        if heading_has_children(headingId):
            write_children_listview(headingId)
            # print "Parent ID of", parentHeadingId, "has children ", childHeadings


def initDirs():
    global genPath
    global rawHeadingPath
    global pageHeadingsPath

    """Builds directory structure"""
    if not os.path.exists(genPath):
        os.mkdir(genPath)
        print "Creating gen root path " + genPath + "..."
    else:
        print "Gen path " + genPath + " exists..."

    if not os.path.exists(rawHeadingPath):
        os.mkdir(rawHeadingPath)
        print "Creating raw heading path " + rawHeadingPath + "..."
    else:
        print "Raw heading path " + rawHeadingPath + " exists..."

    if not os.path.exists(pageHeadingsPath):
        os.mkdir(pageHeadingsPath)
        print "Creating page heading path " + pageHeadingsPath + "..."
    else:
        print "Page heading path " + pageHeadingsPath + " exists..."

    print "Creation of directories complete."

if __name__ == '__main__':

    import argparse

    parser = argparse.ArgumentParser(
        formatter_class=argparse.RawDescriptionHelpFormatter,
        description=__doc__,
    )
    parser.add_argument('-d', '--dump', action='store_true',
        help='dump EPUB to text')
    parser.add_argument('-r', '--refs', help='references EPUB file to parse')
    parser.add_argument('-t', '--tables', help='CSV table data file')
    args = parser.parse_args()

    initDirs()
    if args.refs:
        if args.dump:
            dump_epub(args.refs)
        else:
            try:
                parse_epub(args.refs)
                create_heading_map(args.refs)
            except KeyboardInterrupt:
                pass


