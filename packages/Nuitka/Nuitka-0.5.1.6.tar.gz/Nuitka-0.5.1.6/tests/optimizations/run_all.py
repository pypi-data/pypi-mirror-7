#!/usr/bin/env python
#     Copyright 2014, Kay Hayen, mailto:kay.hayen@gmail.com
#
#     Python test originally created or extracted from other peoples work. The
#     parts from me are licensed as below. It is at least Free Softwar where
#     it's copied from other people. In these cases, that will normally be
#     indicated.
#
#     Licensed under the Apache License, Version 2.0 (the "License");
#     you may not use this file except in compliance with the License.
#     You may obtain a copy of the License at
#
#         http://www.apache.org/licenses/LICENSE-2.0
#
#     Unless required by applicable law or agreed to in writing, software
#     distributed under the License is distributed on an "AS IS" BASIS,
#     WITHOUT WARRANTIES OR CONDITIONS OF ANY KIND, either express or implied.
#     See the License for the specific language governing permissions and
#     limitations under the License.
#

import os, sys, subprocess, tempfile, shutil

try:
    import lxml.etree
except ImportError:
    print("Warning, no 'lxml' module installed, cannot do XML based tests.")
    sys.exit(0)

# Find common code relative in file system. Not using packages for test stuff.
sys.path.insert(
    0,
    os.path.normpath(
        os.path.join(
            os.path.dirname( os.path.abspath( __file__ ) ),
            ".."
        )
    )
)
from test_common import (
    my_print,
    setup,
    convertUsing2to3,
    hasModule,
    check_output
)

python_version = setup()

if not hasModule("lxml.etree"):
    print("Warning, no 'lxml' module installed, cannot run XML based tests.")
    sys.exit(0)

search_mode = len( sys.argv ) > 1 and sys.argv[1] == "search"

start_at = sys.argv[2] if len( sys.argv ) > 2 else None

if start_at:
    active = False
else:
    active = True

def getKind( node ):
    result = node.attrib[ "kind" ]

    result = result.replace( "Statements", "" )
    result = result.replace( "Statement", "" )
    result = result.replace( "Expression", "" )

    return result

def getRole( node, role ):
    for child in node:
        if child.tag == "role" and child.attrib["name"] == role:
            return child
    else:
        return None


def checkSequence(statements):
    for statement in statements:
        kind = getKind(statement)

        # Printing is fine.
        if kind == "Print":
            print_args = getRole( statement, "values" )

            if len( print_args ) != 1:
                sys.exit( "Error, print with more than one argument." )

            print_arg = print_args[0]

            if getKind( print_arg ) != "ConstantRef":
                sys.exit( "Error, print of non-constant %s." % getKind( print_arg ) )

            continue

        # Printing in Python3 is a function call whose return value is ignored.
        if kind == "Only":
            only_expression = getRole(statement, "expression")[0]

            if getKind( only_expression ) == "Call":
                called_expression = getRole(only_expression, "called")[0]

                if getKind(called_expression) == "BuiltinRef":
                    if called_expression.attrib["builtin_name"] == "print":
                        continue

        if kind == "Frame":
            checkSequence(getRole(statement, "statements"))

            continue

        if kind == "AssignmentVariable":
            assign_source = getRole( statement, "source" )[0]

            source_kind = getKind( assign_source )

            if source_kind not in( "ConstantRef", "ImportModuleHard" ):
                sys.exit( "Error, assignment from of non-constant %s." % source_kind )
            continue

        print(lxml.etree.tostring(statement, pretty_print = True))

        sys.exit("Error, non-print statement of unknown kind '%s'." % kind)


for filename in sorted( os.listdir( "." ) ):
    if not filename.endswith( ".py" ) or filename.startswith( "run_" ):
        continue

    # Skip tests that require Python 2.7 at least.
    if filename.endswith( "27.py" ) and python_version.startswith( b"2.6" ):
        continue

    path = filename

    if not active and start_at in ( filename, path ):
        active = True


    extra_flags = [ "expect_success" ]

    if active:
        # Apply 2to3 conversion if necessary.
        assert type( python_version ) is bytes

        if python_version.startswith( b"3" ):
            path = convertUsing2to3( path )

        my_print( "Consider", path, end = " " )

        command = [
            os.environ[ "PYTHON" ],
            os.path.join( "..", "..", "bin", "nuitka" ),
            "--dump-xml",
            "--module",
            path
        ]

        result = check_output(
            command
        )

        # Parse the result into XML and check it.
        root = lxml.etree.fromstring( result )
        module_body  = root[0]
        module_statements_sequence = module_body[ 0 ]

        assert len( module_statements_sequence ) == 1
        module_statements = iter( module_statements_sequence ).next()

        checkSequence( module_statements )

        if python_version.startswith( b"3" ):
            os.unlink( path )

        my_print( "OK." )
    else:
        my_print( "Skipping", filename )
