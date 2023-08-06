"""Cheshire3 Licensing.

With the exception of marc_utils module, Cheshire3 is provided under the
conditions of the BSD 3-clause license.

Copyright &copy; 2005-2012, the University of Liverpool.
All rights reserved.

Redistribution and use in source and binary forms, with or without
modification, are permitted provided that the following conditions are met:

 * Redistributions of source code must retain the above copyright notice,
   this list of conditions and the following disclaimer.
 * Redistributions in binary form must reproduce the above copyright notice,
   this list of conditions and the following disclaimer in the documentation
   and/or other materials provided with the distribution.
 * Neither the name of the University of Liverpool nor the names of its
   contributors may be used to endorse or promote products derived from this
   software without specific prior written permission.

THIS SOFTWARE IS PROVIDED BY THE COPYRIGHT HOLDERS AND CONTRIBUTORS "AS IS"
AND ANY EXPRESS OR IMPLIED WARRANTIES, INCLUDING, BUT NOT LIMITED TO, THE
IMPLIED WARRANTIES OF MERCHANTABILITY AND FITNESS FOR A PARTICULAR PURPOSE ARE
DISCLAIMED. IN NO EVENT SHALL THE COPYRIGHT HOLDER OR CONTRIBUTORS BE LIABLE
FOR ANY DIRECT, INDIRECT, INCIDENTAL, SPECIAL, EXEMPLARY, OR CONSEQUENTIAL
DAMAGES (INCLUDING, BUT NOT LIMITED TO, PROCUREMENT OF SUBSTITUTE GOODS OR
SERVICES; LOSS OF USE, DATA, OR PROFITS; OR BUSINESS INTERRUPTION) HOWEVER
CAUSED AND ON ANY THEORY OF LIABILITY, WHETHER IN CONTRACT, STRICT LIABILITY,
OR TORT (INCLUDING NEGLIGENCE OR OTHERWISE) ARISING IN ANY WAY OUT OF THE USE
OF THIS SOFTWARE, EVEN IF ADVISED OF THE POSSIBILITY OF SUCH DAMAGE.


MARC Utilities Module
---------------------

The following licensing conditions apply to the marc_utils module included in
the Cheshire3 package. In the following statements, "This file" and "the
Software" should be understood to mean marc_utils.py.

> This file should be available from
> http://www.pobox.com/~asl2/software/PyZ3950/
> and is licensed under the X Consortium license:
> Copyright (c) 2001, Aaron S. Lav, asl2@pobox.com
> All rights reserved.

> Permission is hereby granted, free of charge, to any person obtaining a
> copy of this software and associated documentation files (the
> "Software"), to deal in the Software without restriction, including
> without limitation the rights to use, copy, modify, merge, publish,
> distribute, and/or sell copies of the Software, and to permit persons
> to whom the Software is furnished to do so, provided that the above
> copyright notice(s) and this permission notice appear in all copies of
> the Software and that both the above copyright notice(s) and this
> permission notice appear in supporting documentation.

> THE SOFTWARE IS PROVIDED "AS IS", WITHOUT WARRANTY OF ANY KIND, EXPRESS
> OR IMPLIED, INCLUDING BUT NOT LIMITED TO THE WARRANTIES OF
> MERCHANTABILITY, FITNESS FOR A PARTICULAR PURPOSE AND NONINFRINGEMENT
> OF THIRD PARTY RIGHTS. IN NO EVENT SHALL THE COPYRIGHT HOLDER OR
> HOLDERS INCLUDED IN THIS NOTICE BE LIABLE FOR ANY CLAIM, OR ANY SPECIAL
> INDIRECT OR CONSEQUENTIAL DAMAGES, OR ANY DAMAGES WHATSOEVER RESULTING
> FROM LOSS OF USE, DATA OR PROFITS, WHETHER IN AN ACTION OF CONTRACT,
> NEGLIGENCE OR OTHER TORTIOUS ACTION, ARISING OUT OF OR IN CONNECTION
> WITH THE USE OR PERFORMANCE OF THIS SOFTWARE.

> Except as contained in this notice, the name of a copyright holder
> shall not be used in advertising or otherwise to promote the sale, use
> or other dealings in this Software without prior written authorization
> of the copyright holder.
"""


def license_text():
    return __doc__


def cheshire3_license():
    return __doc__.split('\n\n')[1]


def cheshire3_license_text():
    return '\n\n'.join(__doc__.split('\n\n')[:5]) + '\n'


def marc_utils_license():
    return '\n\n'.join(__doc__.split('\n\n')[7:]) + '\n'
