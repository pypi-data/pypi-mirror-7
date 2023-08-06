# Copyright 2014 MongoDB, Inc.
#
# Licensed under the Apache License, Version 2.0 (the "License");
# you may not use this file except in compliance with the License.
# You may obtain a copy of the License at
#
# http://www.apache.org/licenses/LICENSE-2.0
#
# Unless required by applicable law or agreed to in writing, software
# distributed under the License is distributed on an "AS IS" BASIS,
# WITHOUT WARRANTIES OR CONDITIONS OF ANY KIND, either express or implied.
# See the License for the specific language governing permissions and
# limitations under the License.

import logging

logger = logging.getLogger('giza.content.examples.views')

from rstcloth.rstcloth import RstCloth

def full_example(collection, examples):
    r = RstCloth()

    if len(examples) == 1:
        ex_str = 'Example'
    else:
        ex_str = 'Examples'

    r.h2(ex_str)
    r.newline()

    if collection is not None:
        if 'pre' in collection:
            r.content(collection.pre)
            r.newline()

        if 'content' in collection:
            r.content(collection.content)
            r.newline()

        if 'documents' in collection:
            r.codeblock(content=collection.documents,
                        language='javascript')
            r.newline()

        if 'post' in collection:
            r.content(collection.post)
            r.newline()

    for idx, example in enumerate(examples):
        if idx != 0 :
            r.newline(2)

        if len(examples) > 1:
            r.h3(example.title)
            r.newline()

        r.content(example.pre)
        r.newline()

        for op in example.operation:
            if 'pre' in op:
                r.content(op.pre)
                r.newline()

            r.codeblock(content=op.code,
                        language=op.language)
            r.newline()

            if 'post' in op:
                r.content(op.post)
                r.newline()

        r.content(example.post)
        r.newline()
        r.codeblock(content=example.results,
                    language='javascript')

    return r
