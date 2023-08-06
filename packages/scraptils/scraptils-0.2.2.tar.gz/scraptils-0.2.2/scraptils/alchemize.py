#!/usr/bin/env python

# -*- coding: utf-8 -*-
#    This file is part of liberit.

#    liberit is free software: you can redistribute it and/or modify
#    it under the terms of the GNU Affero General Public License as published by
#    the Free Software Foundation, either version 3 of the License, or
#    (at your option) any later version.

#    liberit is distributed in the hope that it will be useful,
#    but WITHOUT ANY WARRANTY; without even the implied warranty of
#    MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the
#    GNU Affero General Public License for more details.

#    You should have received a copy of the GNU Affero General Public License
#    along with liberit.  If not, see <http://www.gnu.org/licenses/>.

# (C) 2012 Adam Tauber <asciimoo@faszkorbacs.hu>


import sys
import re
from sys import stderr
from scraptils.io import parse_json, parse_csv, readlines

pytypes  = (bool, int, float, unicode)
sqltypes = ('Boolean', 'Integer', 'Float', 'String')

disallowed_chars = re.compile('[^a-zA-Z_]', re.U)

def clean(field, maxwidth=40):
    global disallowed_chars
    return disallowed_chars.sub('_', field).lower()[:maxwidth]

def _mkstruct(): return {'_conns': []}

def discover(table, data, schema=None):
    if not schema:
        schema = {table: _mkstruct()}
    elif not schema.has_key(table):
        schema[table] = _mkstruct()

    for key, value in data.items():
        if key == '_name':
            continue
        key = clean(key)
        if isinstance(value, dict):
            sub = discover(key, value, schema)
            if len(sub):
                schema[table]['_conns'].append(key)
        elif isinstance(value, list):
            for i in value:
                # TODO
                pass
        elif type(value) in pytypes:
            if schema[table].has_key(key):
                if sqltypes.index(schema[table][key]) < pytypes.index(type(value)):
                    schema[table][key] = sqltypes[pytypes.index(type(value))]
            else:
                schema[table][key] = sqltypes[pytypes.index(type(value))]
        else:
            print >> stderr, '[!] Error - cannot handle value "%r" - %r' % (value, type(value))
    return schema

def defcolumn(name, field_type, *args):
    attrs = ', '.join(args)
    field = '    %s = Column(%s' % (name, field_type)
    if attrs:
        field += ', ' + attrs
    field += ')'
    return field

def assoc_table(t1, t2):
    return ['%s_%s = Table(\'%s_%s\', Base.metadata' % (t1, t2, t1, t2)
           ,'  ,Column(\'%s_id\', Integer, ForeignKey(\'%s.id\'))' % (t1, t1)
           ,'  ,Column(\'%s_id\', Integer, ForeignKey(\'%s.id\')))' % (t2, t2)
           ,''
           ]

def createschema(schema, connection_string):
    ret = ['from sqlalchemy import create_engine, Column, Integer, String, Float, Boolean, ForeignKey, Table'
          ,'from sqlalchemy.orm import relationship, scoped_session, sessionmaker, backref'
          ,'from sqlalchemy.ext.declarative import declarative_base'
          ,''
          ,'engine = create_engine(\'%s\')' % connection_string
          ,'session = scoped_session(sessionmaker(autocommit=False, autoflush=False, bind=engine))'
          ,''
          ,'Base = declarative_base()'
          ,'Base.metadata.bind = engine'
          ,'Base.query = session.query_property()'
          ,''
          ]
    relations = set()
    for table_name, attrs in schema.items():
        if attrs.get('_conns') != None:
            for rel_table in attrs['_conns']:
                relations.add(tuple(sorted((table_name, rel_table))))
            schema[table_name].pop('_conns')
        elif attrs.get('_name'):
            schema[table_name].pop('_name')

    for t1, t2 in relations:
        ret.extend(assoc_table(t1, t2))
    for table_name, attrs in schema.items():
        ret.extend(('class %s(Base):' % table_name.capitalize()
                   ,'    __tablename__ = \'%s\'' % table_name
                   ,'    id = Column(Integer, primary_key=True)'
                   ))
        for field_name, field_type in set(attrs.items()):
            ret.append(defcolumn(field_name, field_type))
        for t1, t2 in relations:
            if t1 == table_name:
                ret.append('    %ss = relationship(\'%s\', secondary=%s_%s)' % (t2, t2.capitalize(), t1, t2))
            elif t2 == table_name:
                ret.append('    %ss = relationship(\'%s\', secondary=%s_%s)' % (t1, t1.capitalize(), t1, t2))
        ret.append('')
        ret.append('    def __init__(self, %s):' % ', '.join('%s=None' % x for x in attrs.keys()))
        ret.extend('        self.%s = %s' % (x, x) for x in attrs.keys())
        ret.append('')

    ret.append('')
    ret.append('if __name__ == \'__main__\':')
    ret.append('    Base.metadata.create_all(bind=engine)')
    ret.append('')
    return '\n'.join(ret)

def argparser():
    import argparse
    argp = argparse.ArgumentParser(description='Scraptils JSON SQLizer')
    argp.add_argument('-i', '--input'
                     ,help      = 'Input file - default is STDIN'
                     ,metavar   = 'FILE'
                     ,default   = sys.stdin
                     ,type      = argparse.FileType('r')
                     )
    argp.add_argument('-t', '--input-type'
                     ,help      = 'Input file type'
                     ,choices   = ('json', 'csv')
                     ,default   = 'json'
                     )
    argp.add_argument('-d', '--db'
                     ,help      = 'Database connection string - default is \'sqlite:///data.sqlite\''
                     ,default   = 'sqlite:///data.sqlite'
                     )
    return vars(argp.parse_args())


if __name__ == '__main__':
    #r = parse_json(json.dumps({'_name': 'data_table', 'test_int': 6, 'test_float': 4.4, 'test_str': 'asdf', 'conn_table': {'test_bool': True}}))
    #print parse_json(json.dumps({'_name': 'data_table', 'test_int': 6, 'test_float': 4.4, 'test_str': 'asdf', 'conn_table': {'test_bool': True}}), r)
    args = argparser()
    schema = {}
    if args['input_type'] == 'json':
        for line in readlines(args['input']):
            schema = discover(*parse_json(line), schema=schema)
    elif args['input_type'] == 'csv':
        schema = discover(*parse_csv(args['input']), schema=schema)
    print createschema(schema, args['db'])
