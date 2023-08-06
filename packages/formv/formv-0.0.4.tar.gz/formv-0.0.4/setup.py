#!/usr/bin/python
# -*- coding: utf-8 -*-

# This module is part of formv and is released under the MIT License: 
# http://www.opensource.org/licenses/mit-license.php 

import sys
from setuptools import setup, find_packages

version = '0.0.4'

PY2 = sys.version_info[0] == 2
PY3 = sys.version_info[0] >= 3

def install_requires():
    if PY2:
        return ['pyyaml>=3.10', 'pycrypto>=2.6', 
                'PIL>=1.1.7', 'dnspython>=1.11.0']
    if PY3:
        return ['pyyaml>=3.10', 'pycrypto>=2.6', 
                'Pillow>=2.1.0', 'dnspython3>=1.11.0']

setup(name='formv',
      version=version,
      description="HTML forms data validation, conversion & transformation",
      long_description="""\
*formv* is a configurable Python library that can be used to validate, 
convert & transform HTML forms data.
 
Tested under Python 2.7 and 3.2.

Includes validators for::

  - basic types 
      boolean, strings, numbers, dates, time, ranges, lists, sets
  - chained types 
      pairs, multiple fields, post-codes, states, currencies, 
      languages, phone numbers, credit cards
  - compound types 
      any validator, piped validators
  - signers & encoders 
      cost-based PBKDF2 encoding used to sign strings (e.g. cookies), 
      encode strings (e.g. user, password) and sign serialized objects 
      (e.g. serialized sessions stored on disk)  
  - documents (.pdf, .txt, .csv, .doc, etc.)
      can be validated (size, mime-type), stored, backed-up, compressed, reused
  - images (.jpg, .png, .gif, etc.)
      can be validated (size, mime-type), stored, backed-up, resized, watermarked, 
      imprinted, reused
  - geographic data 
      based on extendable YAML configuration files or user-defined callables: 
      countries, country-codes, states, various naming styles, currencies, 
      languages, post-codes, latitude, longitude, geo-distance calculation
  - network related 
      IPv4, IPv6, CIDR, MAC
  - web-forms (schema validation)
      simple fields, chained fields, key-based dependency
        
Example:: 

    # schema validation including file upload, file transformation and file recovery 
    #---------------------------------------------------------------------------------
    
    import os, formv
    from formv.configuration import build
    from formv.validators import *
    from formv.exception import Invalid
    
    from formv.utils import dict_object
    from formv.utils.compat import PY2
    from formv.utils.fileinfo import BaseFileInfo, ReusedFileInfo 
    
    from tests import multipart
    from examples import to_str, setup_mime_types, make_environ as env
    
    from datetime import datetime
    from mimetypes import guess_type
    from webob import Request, Response
    
    app_root = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
    
    # configuration is required only if you use validators based on 
    # geographic data: countries, currencies, languages, post-codes, 
    # latitude, longitude, geo-distance calculation,...
    
    formv.config = build(config_root=os.path.join(app_root, 'tests'))
    mime_types = setup_mime_types()
    
    session = dict_object(files=dict_object())
     
    class WebForm(VSchema):     
        fields = {         
            'first_name': VString(min_len=3, max_len=50), 
            'last_name': VString(min_len=3, max_len=50), 
            'postcode': VString(), 
            'state': VString(),
            'country': VCountry(required=True, mode='by-name'), 
            'email': VEmail(required=True), 
            'password': VPassword(special_chars=3),
            'file_upload': VPipe(VUploadFile(mime_types=mime_types,
                                             temp_dir='/tmp/formv/test/tmp',), 
                                 VWatermarkImage(type='image', 
                                                 file=os.path.join(app_root, 'tests/watermarks/copyright.jpg'), 
                                                 opacity=.04, angle=45), 
                                 VWatermarkImage(text='formv text watermark', angle=25, 
                                                 color=(0,0,0,128), opacity=1), 
                                 VImprintImage(text='Note the image watermark in the background',  
                                               color=(0,128,128,255)), 
                                 VImprintImage(text=datetime.strftime(datetime.utcnow(),  
                                                                      'Uploaded on %Y/%m/%d - %H:%M:%S GMT'), 
                                               color=(255,128,128,255), 
                                               margin=(25,10)), 
                           ) 
        } 
    
        chains = { 
            'coordinates': VCountryPostcode(country_field='country',     # extracts (latitude, longitude) pair
                                            postcode_field='postcode'),         
            'password': VEncodedPair(required_field='password',          # encodes (password, email) pair
                                     required_label='Password', 
                                     available_field='email'),
            'state': VState(country_field='country',                     # validates state against country
                            state_field='state', mode='by-name'),
        } 
         
    class Application(object):
        def __call__(self, environ, start_response):
            self.request = Request(make_environ())  
            response = self.request.get_response(self.response())
            return response(self.request.environ, start_response)
        
        def response(self):
            try:
                form = self.validate(self.request.POST) # - form validation
                body = to_str(form)
            except Invalid as e:
                # - recover successfully uploaded files 
                if isinstance(e.value.get('file_upload'), BaseFileInfo): 
                    session.files['file_upload'] = ReusedFileInfo(e.value['file_upload']) 
                                    
                body = e.message
                body += '<br/>errors'
                body += to_str(e.errors)
                body += '<br/>values'
                body += to_str(e.value)
    
            response = Response()                        
            response.text = unicode(body) if PY2 else body
            return response
            
        def validate(self, request): 
            form = WebForm(allow_missing_keys=True, 
                           allow_extra_keys=True, 
                           replace_empty_value=True, 
                           empty_values={ 
                               # inject recovered file back into form if no new file has been uploaded 
                               'file_upload': session.files.get('file_upload'), 
                           }) 
            return form.validate(request) 
                
    application = Application()  
         
    def make_environ():
        ''' simulates a POST request (multipart/form-data) '''
        
        app_root = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
        test_files_dir = os.path.join(app_root, 'tests/files')    
        form = []
    
        # - plain fields
        form.append(multipart.field('first_name', 'John'))
        form.append(multipart.field('last_name', 'Smith'))
        form.append(multipart.field('email', 'dummy@dummy.com'))
        form.append(multipart.field('postcode', '99501'))
        form.append(multipart.field('state', 'Alaska'))
        form.append(multipart.field('country', 'U.S.A.'))
        form.append(multipart.field('password', 'dummy-secret-password-1'))
        
        # - file upload
        f = os.path.join(test_files_dir, 'test.jpg')
        form.append(multipart.file('file_upload', filename=f, 
                                   content_type=guess_type(f, False)[0]))            
        return env(*form)
    
    
    if __name__ == '__main__':
        from wsgiref.simple_server import make_server   
        httpd = make_server('127.0.0.1', 9000, application)
        sn = httpd.socket.getsockname()
        print("Serving HTTP on", sn[0], "port", sn[1], "...")            
        httpd.serve_forever()
     
Output::

    +----------------------------------------------------------------------------------------------------------+
    | Field Name  | Field Value                                                                                |
    +==========================================================================================================+
    | coordinates | (61.216799, -149.87828)                                                                    |
    +----------------------------------------------------------------------------------------------------------+
    | country     | 'USA'                                                                                      |
    +----------------------------------------------------------------------------------------------------------+
    | email       | 'dummy@dummy.com'                                                                          |
    +----------------------------------------------------------------------------------------------------------+
    | file_upload | dir_path = '/tmp/formv/test/public'                                                        |
    |             | file_date = datetime.datetime(2014, 4, 4, 1, 33, 39, 453000)                               |
    |             | file_ext ='.jpg'                                                                           |
    |             | file_name = '16c2493562644b15b4093a02973097b1.jpg'                                         |
    |             | file_object = None                                                                         |
    |             | file_path = '/tmp/formv/test/public/16c2493562644b15b4093a02973097b1.jpg'                  |
    |             | file_size = 5129                                                                           |
    |             | guid_name ='16c2493562644b15b4093a02973097b1'                                              |
    |             | html_field = 'file_upload'                                                                 |
    |             | mime_type = 'image/pjpeg'                                                                  |
    |             | orig_name = 'test.jpg'                                                                     |
    |             | thumb_name = '16c2493562644b15b4093a02973097b1_th.jpg'                                     |
    |             | thumb_path = '/tmp/formv/test/public/16c2493562644b15b4093a02973097b1_th.jpg'              |
    |             | zip_name = None                                                                            |
    |             | zip_path = None                                                                            |
    |             | zip_size = None                                                                            |
    +----------------------------------------------------------------------------------------------------------+
    | first_name  | 'John'                                                                                     |
    +----------------------------------------------------------------------------------------------------------+
    | last_name   | 'Smith'                                                                                    |
    +----------------------------------------------------------------------------------------------------------+
    | password    | '$x-pbkdf2$20$1000$rmQEpiAjI7/FaNpFECFb2w==$l5AfchT7rWwPVxofHhhpSZPu4SJPiU4QTtD/cqmE6og='  |
    +----------------------------------------------------------------------------------------------------------+
    | postcode    | '99501'                                                                                    |
    +----------------------------------------------------------------------------------------------------------+
    | state       | 'AK'                                                                                       |
    +----------------------------------------------------------------------------------------------------------+

Geographic configuration::

    As of now the configuration available includes only USA. If you have to
    validates other countries, you have build similar configuration files and 
    place them in the corresponding folders.
        
Postcodes validation warning:: 

    If you plan to do USA postcodes validation based on the included YAML 
    file, expect a high memory usage as the file contains ~44000 postcodes.
    A better alternative would be to dump the file in a database, build 
    necessary callables to read the data and instruct formv to use these 
    callables. See formv/configuration.py for an example.

USA postcodes data source::
    
    http://www.boutell.com/zipcodes/
    http://www.boutell.com/zipcodes/zipcode.zip
 
Source:: 

    https://pypi.python.org/pypi/formv

For usage and more examples, see examples & tests.
        """,
      classifiers=[
      'Development Status :: 4 - Beta',
      'Environment :: Web Environment',
      'Environment :: Other Environment',
      'Intended Audience :: Developers',
      'License :: OSI Approved :: MIT License',      
      'Operating System :: OS Independent',
      'Programming Language :: Python',
      'Programming Language :: Python :: 2',     
      'Programming Language :: Python :: 3',
      'Topic :: Internet :: WWW/HTTP :: Dynamic Content :: CGI Tools/Libraries',
      'Topic :: Software Development :: Libraries :: Python Modules',      
      'Topic :: Utilities',            
      ],
      keywords='HTML form validation conversion transformation schema',
      author='Adrian Cristea',
      author_email='adrian.cristea@gmail.com ',
      license='MIT',
      packages=find_packages('.', exclude=[]),
      include_package_data=True,
      install_requires=install_requires(),
      zip_safe=False,
)