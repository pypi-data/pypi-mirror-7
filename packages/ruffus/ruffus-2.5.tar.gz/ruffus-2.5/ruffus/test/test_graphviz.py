#!/usr/bin/env python
from __future__ import print_function
"""

    play_with_colours.py
    [--log_file PATH]
    [--verbose]

"""
import unittest

################################################################################
#
#   test
#
#
#   Copyright (c) 7/13/2010 Leo Goodstadt
#
#   Permission is hereby granted, free of charge, to any person obtaining a copy
#   of this software and associated documentation files (the "Software"), to deal
#   in the Software without restriction, including without limitation the rights
#   to use, copy, modify, merge, publish, distribute, sublicense, and/or sell
#   copies of the Software, and to permit persons to whom the Software is
#   furnished to do so, subject to the following conditions:
#
#   The above copyright notice and this permission notice shall be included in
#   all copies or substantial portions of the Software.
#
#   THE SOFTWARE IS PROVIDED "AS IS", WITHOUT WARRANTY OF ANY KIND, EXPRESS OR
#   IMPLIED, INCLUDING BUT NOT LIMITED TO THE WARRANTIES OF MERCHANTABILITY,
#   FITNESS FOR A PARTICULAR PURPOSE AND NONINFRINGEMENT. IN NO EVENT SHALL THE
#   AUTHORS OR COPYRIGHT HOLDERS BE LIABLE FOR ANY CLAIM, DAMAGES OR OTHER
#   LIABILITY, WHETHER IN AN ACTION OF CONTRACT, TORT OR OTHERWISE, ARISING FROM,
#   OUT OF OR IN CONNECTION WITH THE SOFTWARE OR THE USE OR OTHER DEALINGS IN
#   THE SOFTWARE.
#################################################################################

import sys, os

# add self to search path for testing
exe_path = os.path.split(os.path.abspath(sys.argv[0]))[0]
sys.path.insert(0,os.path.abspath(os.path.join(exe_path,"..", "..")))
if __name__ == '__main__':
    module_name = os.path.split(sys.argv[0])[1]
    module_name = os.path.splitext(module_name)[0];
else:
    module_name = __name__



#88888888888888888888888888888888888888888888888888888888888888888888888888888888888888888

#   options


#88888888888888888888888888888888888888888888888888888888888888888888888888888888888888888


from optparse import OptionParser
try:
    import StringIO as io
except:
    import io as io



#88888888888888888888888888888888888888888888888888888888888888888888888888888888888888888

#   imports


#88888888888888888888888888888888888888888888888888888888888888888888888888888888888888888

from ruffus import *
from ruffus.ruffus_exceptions import JobSignalledBreak



#88888888888888888888888888888888888888888888888888888888888888888888888888888888888888888

#   Pipeline


#88888888888888888888888888888888888888888888888888888888888888888888888888888888888888888


#
# up to date tasks
#
@check_if_uptodate (lambda : (False, ""))
def Up_to_date_task1(infile, outfile):
    pass

@graphviz(URL='"http://cnn.com"', fillcolor = '"#FFCCCC"',
                color = '"#FF0000"', pencolor='"#FF0000"', fontcolor='"#4B6000"',
                label_suffix = "???", label_prefix = "What is this?<BR/> ",
                label = "<What <FONT COLOR=\"red\">is</FONT>this>",
                shape= "component", height = 1.5, peripheries = 5,
                style="dashed")
@check_if_uptodate (lambda : (False, ""))
@follows(Up_to_date_task1)
def Up_to_date_task2(infile, outfile):
    pass

@check_if_uptodate (lambda : (False, ""))
@follows(Up_to_date_task2)
def Up_to_date_task3(infile, outfile):
    pass


@check_if_uptodate (lambda : (False, ""))
@follows(Up_to_date_task3)
def Up_to_date_final_target(infile, outfile):
    pass


#
# Explicitly specified
#
@check_if_uptodate (lambda : (False, ""))
@follows(Up_to_date_task1)
def Explicitly_specified_task(infile, outfile):
    pass



#
# Tasks to run
#
@follows(Explicitly_specified_task)
def Task_to_run1(infile, outfile):
    pass


@follows(Task_to_run1)
def Task_to_run2(infile, outfile):
    pass

@follows(Task_to_run2)
def Task_to_run3(infile, outfile):
    pass

@check_if_uptodate (lambda : (False, ""))
@follows(Task_to_run2)
def Up_to_date_task_forced_to_rerun(infile, outfile):
    pass


#
# Final target
#
@follows(Up_to_date_task_forced_to_rerun, Task_to_run3)
def Final_target(infile, outfile):
    pass

#
# Ignored downstream
#
@follows(Final_target)
def Downstream_task1_ignored(infile, outfile):
    pass

@follows(Final_target)
def Downstream_task2_ignored(infile, outfile):
    pass









try:
    from StringIO import StringIO
except:
    from io import StringIO


#88888888888888888888888888888888888888888888888888888888888888888888888888888888888888888

#   Main logic


#88888888888888888888888888888888888888888888888888888888888888888888888888888888888888888









class Test_graphviz(unittest.TestCase):
    #___________________________________________________________________________
    #
    #   test product() pipeline_printout diagnostic error messsages
    #
    #       require verbose >= 3 or an empty jobs list
    #___________________________________________________________________________
    def test_graphviz_dot(self):
        """Make sure annotations from graphviz appear in dot
        """

        s = StringIO()
        pipeline_printout_graph (
                                        s,
                                        # use flowchart file name extension to decide flowchart format
                                        #   e.g. svg, jpg etc.
                                        "dot",
                                        [Final_target, Up_to_date_final_target])
        self.assertTrue('[URL="http://cnn.com", color="#FF0000", fillcolor="#FFCCCC", fontcolor="#4B6000", height=1.5, label=<What is this?<BR/> What <FONT COLOR="red">is</FONT>this???>, pencolor="#FF0000", peripheries=5, shape=component, style=dashed]' in s.getvalue())




#
#   Necessary to protect the "entry point" of the program under windows.
#       see: http://docs.python.org/library/multiprocessing.html#multiprocessing-programming
#
if __name__ == '__main__':
    #pipeline_printout(sys.stdout, [test_product_task], verbose = 5)
    #pipeline_printout_graph( "test.png", "png", [Final_target, Up_to_date_final_target])
    #pipeline_printout_graph( "test.dot", "dot", [Final_target, Up_to_date_final_target])
    unittest.main()


