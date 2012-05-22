import os
import sys
import traceback
import StringIO
import warnings
import re

warnings.simplefilter("error")

from support import get_data_files
from support import TestData, convert, convertExpected, treeTypes
import html5lib
from html5lib import html5parser, treebuilders, constants

#Run the parse error checks
checkParseErrors = False

#XXX - There should just be one function here but for some reason the testcase
#format differs from the treedump format by a single space character
def convertTreeDump(data):
    return u"\n".join(convert(3)(data).split(u"\n")[1:])

namespaceExpected = re.compile(ur"^(\s*)<(\S+)>", re.M).sub


def runParserTest(innerHTML, input, expected, errors, treeClass,
                  namespaceHTMLElements):
    #XXX - move this out into the setup function
    #concatenate all consecutive character tokens into a single token
    try:
        p = html5parser.HTMLParser(tree = treeClass,
                                   namespaceHTMLElements=namespaceHTMLElements)
    except constants.DataLossWarning:
        return

    try:
        if innerHTML:
            document = p.parseFragment(input, innerHTML)
        else:
            try:
                document = p.parse(input)
            except constants.DataLossWarning:
                return 
    except:
        errorMsg = u"\n".join([u"\n\nInput:", input, u"\nExpected:", expected,
                               u"\nTraceback:", traceback.format_exc().decode('utf8')])
        assert False, errorMsg

    output = convertTreeDump(p.tree.testSerializer(document))

    expected = convertExpected(expected)
    if namespaceHTMLElements:
        expected = namespaceExpected(ur"\1<html \2>", expected)

    errorMsg = u"\n".join([u"\n\nInput:", input, u"\nExpected:", expected,
                           u"\nReceived:", output])
    assert expected == output, errorMsg
    errStr = [u"Line: %i Col: %i %s"%(line, col, 
                                      constants.E[errorcode] % datavars if isinstance(datavars, dict) else (datavars,)) for
              ((line,col), errorcode, datavars) in p.errors]

    errorMsg2 = u"\n".join([u"\n\nInput:", input,
                            u"\nExpected errors (" + unicode(len(errors)) + u"):\n" + u"\n".join(errors),
                            u"\nActual errors (" + unicode(len(p.errors)) + u"):\n" + u"\n".join(errStr)])
    if checkParseErrors:
            assert len(p.errors) == len(errors), errorMsg2

def test_parser():
    sys.stderr.write('Testing tree builders '+ " ".join(treeTypes.keys()) + "\n")
    files = get_data_files('tree-construction')
    
    for filename in files:
        testName = os.path.basename(filename).replace(".dat","")

        tests = TestData(filename, u"data")
        
        for index, test in enumerate(tests):
            input, errors, innerHTML, expected = [test[key] for key in
                                                      u'data', u'errors',
                                                      u'document-fragment',
                                                      u'document']
            if errors:
                errors = errors.split(u"\n")

            for treeName, treeCls in treeTypes.iteritems():
                for namespaceHTMLElements in (True, False):
                    print input
                    yield (runParserTest, innerHTML, input, expected, errors, treeCls,
                           namespaceHTMLElements)
