"""
 <@LICENSE>
 * Licensed to the Apache Software Foundation (ASF) under one or more
 * contributor license agreements.  See the NOTICE file distributed with
 * this work for additional information regarding copyright ownership.
 * The ASF licenses this file to you under the Apache License, Version 2.0
 * (the "License"); you may not use this file except in compliance with
 * the License.  You may obtain a copy of the License at:
 * 
 *     http://www.apache.org/licenses/LICENSE-2.0
 * 
 * Unless required by applicable law or agreed to in writing, software
 * distributed under the License is distributed on an "AS IS" BASIS,
 * WITHOUT WARRANTIES OR CONDITIONS OF ANY KIND, either express or implied.
 * See the License for the specific language governing permissions and
 * limitations under the License.
 * </@LICENSE>
 */
"""
## @file pysql.py
## @author JUNGO Joel
## @date April 2015
## @package pysql
## Very Simple API to access to hsm's database.
import sqlite3 as sql
import sys

import logging
import syslog

## This class allows user to access to key.db sqlite3 database. This
# class provide accesser and getter method in order to interact with db. The 
# database is located at /data/db/key.db

class PySql:
    db = None
    dbpath = '/data/db/key.db'
    cursor = None
    ## The Constructor
    # Connect to database and create the table if it doesn't exist.
    #  @param self The object pointer.
    def __init__(self):
        syslog.openlog(logoption=syslog.LOG_PID, facility=syslog.LOG_LOCAL0)
        
        self.db = sql.connect(self.dbpath)
        self.cursor = self.db.cursor()

        # key dumm priv are used to initialize stunnel. There are very dummy keys
        # and should never be used for real cryptographic opertions.
        stm = '''
                CREATE TABLE if not exists  PRIVKEY (
                    ID INTEGER PRIMARY KEY      autoincrement unique,
                    LABEL           TEXT         NOT NULL,
                    LEN             INTEGER      NOT NULL,
                    TYPE            CHAR(10)     NOT NULL,
                    timestamp datetime default current_timestamp,
                    KEY_priv        BLOB         NOT NULL,
                    KEY_pub         BLOB         ,
                    KEY_dumm_priv   BLOB         ,
                    KEY_dumm_pub    BLOB         )
              '''

        self.cursor.execute(stm)
        self.db.commit()
        self.db.close()

    ## drop key.db table
    #  @param self The object pointer.
    def drop_table(self):
        try:
            dbname = self.dbpath
            self.db = sql.connect(dbname)
            self.cursor = self.db.cursor()
            self.cursor.execute('DROP TABLE IF EXISTS PRIVKEY')
            self.db.commit()

        except Exception as e:
            self.db.rollback()
            raise e
        finally:
            self.db.close()

    ## add key
    # @param self The object pointer.
    # @param label: Identifies the key by a name.
    # @param len: Size of key in bytes.
    # @param type: Type of key (RSA, 3DES, AES) Only RSA is implemented.
    # @param key_priv: Private key in pem format.
    # @param key_pub: Public key in pem format.
    # @param key_dumm_priv: Dummy private key in pem format.
    # @param key_dumm_pub: Dummy public key in pem format.
    def add_key(self, label, len, type, key_priv, key_pub, 
                key_dumm_priv, key_dumm_pub):
        try:
            self.db = sql.connect(self.dbpath)
            self.cursor = self.db.cursor()
            self.cursor.execute('insert into PRIVKEY(label, len, type, \
                                key_priv, key_pub, key_dumm_priv, key_dumm_pub)\
                                values (?,?,?,?,?,?,?)',
                                (label, len, type, key_priv, key_pub,
                                    key_dumm_priv, key_dumm_pub))
            self.db.commit()
            msg = 'Key created: '+str(self.get_id_from_key_priv(key_priv))+', label: '+label
            syslog.syslog(syslog.LOG_WARNING, msg)
        except Exception as e:
            self.db.rollback()
            msg = 'ERROR: invalid sql request'
            syslog.syslog(syslog.LOG_ERR, msg)
            print(msg)
            raise e
        finally:
            self.db.close()
            syslog.closelog()


    ## add key and force ID
    # @param self The object pointer.
    # @id: indicate an id
    # @param label: Identifies the key by a name.
    # @param len: Size of key in bytes.
    # @param type: Type of key (RSA, 3DES, AES) Only RSA is implemented.
    # @param key_priv: Private key in pem format.
    # @param key_pub: Public key in pem format.
    # @param key_dumm_priv: Dummy private key in pem format.
    # @param key_dumm_pub: Dummy public key in pem format.
    def add_key_id(self, id, label, len, type, key_priv, key_pub,
                key_dumm_priv, key_dumm_pub):
        try:
            self.db = sql.connect(self.dbpath)
            self.cursor = self.db.cursor()
            self.cursor.execute('insert into PRIVKEY(id, label, len, type, \
                                key_priv, key_pub, key_dumm_priv, key_dumm_pub)\
                                values (?,?,?,?,?,?,?,?)',
                                (id, label, len, type, key_priv, key_pub,
                                    key_dumm_priv, key_dumm_pub))
            self.db.commit()
            msg = 'Key created: '+str(self.get_id_from_key_priv(key_priv))+', label: '+label
            syslog.syslog(syslog.LOG_WARNING, msg)
        except Exception as e:
            self.db.rollback()
            msg = 'ERROR: invalid sql request'
            syslog.syslog(syslog.LOG_ERR, msg)
            print(msg)
            raise e
        finally:
            self.db.close()
            syslog.closelog()

    ## Get id from label
    # @param self The object pointer.
    # @param label: Identifies the key by a name.
    # @return id as integer
    def get_id_from_label(self, label):
        self.db = sql.connect(self.dbpath)
        self.cursor = self.db.cursor()
        self.cursor.execute('select id from PRIVKEY '
                            '   where label=:label'
                            '   order by id DESC', {'label':label})
        val = self.cursor.fetchone()
        self.db.close()
        if val is None:
            return None
        return val[0]

    ## Get id from label
    # @param self The object pointer.
    # @param key_priv: key_value.
    # @return id as integer
    def get_id_from_key_priv(self, key_priv):
        self.db = sql.connect(self.dbpath)
        self.cursor = self.db.cursor()
        self.cursor.execute('select id from PRIVKEY '
                            '   where key_priv=:key_priv'
                            '   order by id DESC', {'key_priv':key_priv})
        val = self.cursor.fetchone()
        self.db.close()
        if val is None:
            return None
        return val[0]

    ## Get pub key from id
    # @param id: ID of key.
    # @return (key_pub, key_dumm_pub) as tuple
    def get_pub_key_from_id(self, id):
        self.db = sql.connect(self.dbpath)
        self.cursor = self.db.cursor()
        self.cursor.execute('select key_pub, key_dumm_pub from PRIVKEY '
                            'where id=:id', {'id':id})
        val = self.cursor.fetchone()
        self.db.close()
        if val is None:
            return None
        return val

    ## Get all pub key id and label
    # @return (id, label) as tuple
    def get_list_pub_key_label(self):
        self.db = sql.connect(self.dbpath)
        self.cursor = self.db.cursor()
        self.cursor.execute('select id, label from PRIVKEY')
        val = self.cursor.fetchall()
        self.db.close()
        if val is None:
            return None
        return val

    ## Get priv key from id
    # @param id: ID of key.
    # @return (key_priv, key_pub, key_dumm_priv, key_dumm_pub) as tuple
    def get_priv_key_from_id(self, id):
        self.db = sql.connect(self.dbpath)
        self.cursor = self.db.cursor()
        self.cursor.execute('select key_priv,  key_dumm_priv from PRIVKEY '
                            'where id=:id', {'id':id})
        val = self.cursor.fetchone()
        self.db.close()
        if val is None:
            return None
        return val

    ## Get label from id
    # @param id: ID of key.
    # @return label
    def get_label_from_id(self, id):
        self.db = sql.connect(self.dbpath)
        self.cursor = self.db.cursor()
        self.cursor.execute('select label from PRIVKEY '
                            'where id=:id', {'id':id})
        val = self.cursor.fetchone()
        self.db.close()
        if val is None:
            return None
        return val[0]

    ## Get size of key from id
    # @param id: ID of key.
    # @return size of key
    def get_key_size_from_id(self, id):
        self.db = sql.connect(self.dbpath)
        self.cursor = self.db.cursor()
        self.cursor.execute('select len from PRIVKEY '
                            'where id=:id', {'id':id})
        val = self.cursor.fetchone()
        self.db.close()
        if val is None:
            return None
        return val[0]

    ## Get type of the key from id
    # @param id: ID of key.
    # @return type of key
    def get_key_type_from_id(self, id):
        self.db = sql.connect(self.dbpath)
        self.cursor = self.db.cursor()
        self.cursor.execute('select type from PRIVKEY '
                            'where id=:id', {'id':id})
        val = self.cursor.fetchone()
        self.db.close()
        if val is None:
            return None
        return val[0]

    ## Delete entry from ID
    # @param self The object pointer.
    # @param id: ID of key.
    def delete_key_from_id(self, id):
        try:
            self.db = sql.connect(self.dbpath)
            self.cursor = self.db.cursor()
            self.cursor.execute('delete from PRIVKEY where id=:id', {'id':id})
            self.db.commit()
            msg = 'Key deleted: '+str(id)
            syslog.syslog(syslog.LOG_WARNING, msg)
        except Exception as e:
            self.db.rollback()
            msg = 'ERROR: invalid sql request'
            syslog.syslog(syslog.LOG_ERR, msg)
            print(msg)
            raise e

        finally:
            self.db.close()
            syslog.closelog()
