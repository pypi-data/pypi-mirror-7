#!/usr/bin/python
# -*- coding: utf-8 -*-

# This module is part of formv and is released under the MIT License: 
# http://www.opensource.org/licenses/mit-license.php 

import time
from formv.validators.base import VBase
from formv.validators.strings import VString
from formv.exception import Invalid
from formv.utils import extract_text as _
from datetime import date, datetime

__all__ = ('VDate','VTime','VToDate',)

class VDate(VBase):
    def __init__(self, earliest_date=None, latest_date=None, 
                 after_now=False, today_or_after=False, 
                 date_format='%d/%m/%Y', return_timestamp=False, **kw):
        VBase.__init__(self, **kw)
        
        if earliest_date: 
            if not isinstance(earliest_date, (date, datetime)):
                msg = _('Invalid earliest date type: %s')
                raise ValueError(msg % type(earliest_date))
        if latest_date: 
            if not isinstance(latest_date, (date, datetime)):
                msg = _('Invalid latest date type: %s')
                raise ValueError(msg % type(latest_date))
        
        self.earliest_date = earliest_date
        if isinstance(earliest_date, datetime):
            self.earliest_date = date(earliest_date.year, 
                                      earliest_date.month, 
                                      earliest_date.day)  
              
        self.latest_date = latest_date
        if isinstance(latest_date, datetime):
            self.latest_date = date(latest_date.year, 
                                    latest_date.month, 
                                    latest_date.day)   
                     
        self.after_now = after_now
        self.today_or_after = today_or_after
        self.date_format = date_format
        self.return_timestamp = return_timestamp

    def _validate(self, value):
        self.messages.update({
            'invalid': _('Invalid date'),
            'after': _('Date must be after %(date)s'),
            'before': _('Date must be before %(date)s'),
            'future': _('The date must be sometime in the future'),
            'invalid_format': _('A valid date format is required')
        })
        
        date_value = value
        if isinstance(value, datetime):
            date_value = date(value.year, value.month, value.day)            
            
        if self.earliest_date and date_value < self.earliest_date: 
            fmt = self.earliest_date.strftime(self.date_format)
            raise Invalid(self.message('after', date=fmt), value)
        
        if self.latest_date and self.latest_date < date_value: 
            fmt = self.latest_date.strftime(self.date_format)
            raise Invalid(self.message('before', date=fmt), value)
        
        if self.after_now and date_value < date.today(): 
            raise Invalid(self.message('future'), value)

        if self.today_or_after:
            utc_today = datetime.utcnow()
            if date_value < date(utc_today.year, utc_today.month, utc_today.day):            
                raise Invalid(self.message('future'), value)
        
        if self.return_timestamp:   # - UNIX time-stamp (1970, 2038) interval
            return int(time.mktime(value.timetuple())) 
        
        return value


class VTime(VString):
    def _validate(self, value):
        value = VString._validate(self, value)
        self.messages.update({'invalid': _('Invalid time')})        
        t = value.replace(':','').replace('-','').replace('.','').replace(' ','').strip()
        if len(t) == 4 or len(t) == 6:
            try:
                int(t)
                if len(t) == 6:
                    hrs, mnt, sec = int(t[:2]), int(t[2:4]), int(t[4:])
                    if not (0 <= hrs <= 23 and 0 <= mnt <= 60 and 0 <= sec <= 60):
                        raise Invalid(self.message('invalid'), value)
                    return '%s:%s:%s' % (t[:2], t[2:4], t[4:])
                if len(t) == 4:
                    hrs, mnt = int(t[:2]), int(t[2:])
                    if not (0 <= hrs <= 23 and 0 <= mnt <= 60):
                        raise Invalid(self.message('invalid'), value)
                    return '%s:%s' % (t[:2], t[2:])
            except ValueError:
                raise Invalid(self.message('invalid'), value)
        else:
            raise Invalid(self.message('invalid'), value)


class VToDate(VString):
    """ converts string to date """
    def __init__(self, date_format='%d/%m/%Y', **kw):
        VString.__init__(self, **kw)        
        self.date_format = date_format        
                         
    def _validate(self, value):
        value = VString._validate(self, value)
        self.messages.update({'invalid': _('Invalid date string or date format')})

        try:
            if value:
                return datetime.strptime(value, self.date_format)
            return value
        except:
            raise Invalid(self.message('invalid'), value)    