#!/usr/bin/env python3
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

## @file solhsm-mgmt.py
## @author JUNGO Joel
## @date April 2015
## @package solhsm-mgmt
## Basic tool to manage key on HSM.
## IMPORTANT: You MUST a path like /data/db/key.db
import argparse
import sys
import datetime

from Crypto.PublicKey import RSA
from Crypto import Random

from pysql.core import PySql

# TODO errors handling: check return values when pysql is used


__author__ = 'Joel Jungo'
__version__ = '0.2'

MAX_KEY_SIZE = 4096
MIN_KEY_SIZE = 1024
# in order to be coherent with the solHSM-network. ID type field is uint16_t
MAX_ALLOWED_ENTRIES = 65535

def reset():
    print('***WARNING***')
    print('This action will be erase your database, you should make a backup.')
    erase = input("Are you sure? (YES/NO): ")
    if erase == 'YES':
        obj = PySql()
        try:
            obj.drop_table()
        except Exception as e:
            print(" Error in access to database ({0})".format(e))
            exit(0)
        print('Your database has been deleted.')
    else:
        print('Your database has not been deleted.')


def genkey(args):
    size = args.size
    while size not in range(MIN_KEY_SIZE, MAX_KEY_SIZE+1) or (size & 0xff):
        print("Size incorrect")
        print("{0} >= size <= {1} "
              "and RSA modulus length must be a multiple of 256."
              .format(MIN_KEY_SIZE, MAX_KEY_SIZE))
        try:
            size = int(input("Please enter a valid size [default: 1024]: ")
                       or str(MIN_KEY_SIZE))
        except:
            pass


    rng = Random.new().read
    rng2 = Random.new().read
    rsa_key = RSA.generate(size, rng)
    rsa_priv = rsa_key.exportKey("PEM")
    rsa_pub = rsa_key.publickey().exportKey("PEM")

    # RSA modulus (n).
    # Public exponent (e).
    n = rsa_key.__getattr__('n')
    e = rsa_key.__getattr__('e')
    # Theses values are hard coded in order to forge dummy key
    d = 16873206504033245860732446270244916934944274309025349939762572041033210369164510704255050298319803575206577135107748120681002549417317864926512541469708655243504073084615417147302168437901664095346980780044139279192318127374868544368650348281360985242626772322378610758209477416562115187587446802831578288780149204713881088873159128233014358188530860351212979673331577936729556029608129567014178066385885200605208557909850617840631662723143468007762007527663432193069397821199342164933504851762211259256888459249431920214427044886393802688631365983226896368035098966072497004159273730211422842021552858660662534938593
    p = 152178823376282876067011649670054488149451430666731159375352264261708870501326356704315164767662481458582206422364585516501040185330033928724637969608738720957510535047214168939361080003763417182123452343285605028384423479581243445677520737901928430644038944245214189037796037198411855862030467913837403574307
    q = 138767846717421833302397659391284074156068546778624367389745643767014480855677499791034503909998389722093236333103006295781572805453936272676929969246294181893996900426429785650090347117642266385037130573213383143892066691227159620304071497331287443013578624321086516818049135798366925974810528401498233856177

    dummy_key = RSA.construct((n, e, d, p, q, 0))
    rsa_priv_dum = dummy_key.exportKey("PEM")

    rsa_pub_dum = dummy_key.publickey().exportKey("PEM")

    sql_o = PySql()
    label = args.label
    label = valid_label(label)
    type = 'RSA'

    # In solHSM-Protocol, ID is define on a uint16_t, so our database must have
    # at maximum (2^16)-1 elements.
    # So if the maximum ID is (2^16)-1 we have to find "holes" in ID column and
    # feed them. If they are full we have to abort the user request.
    list_id = sql_o.get_list_pub_key_label()

    i = 0
    found_hole = False
    hole_id = 0
    if len(list_id) == MAX_ALLOWED_ENTRIES:
        print('ERROR: The number of maximum id has been reached')
    try:
        if len(list_id) == 0:
            sql_o.add_key(label, size, type, rsa_priv, rsa_pub, rsa_priv_dum,
                              rsa_pub_dum)
        else:
            if list_id[0][0] != 0:
                sql_o.add_key_id(0, label, size, type, rsa_priv, rsa_pub, rsa_priv_dum,
                                 rsa_pub_dum)
                found_hole = True
            while i < len(list_id) and found_hole is False:
                if i < len(list_id)-1:
                    if (list_id[i+1][0] - list_id[i][0]) > 1:
                        hole_id = i+1
                        sql_o.add_key_id(hole_id, label, size, type, rsa_priv,
                                 rsa_pub, rsa_priv_dum, rsa_pub_dum)
                        found_hole = True
                i += 1
            if found_hole is False:
                sql_o.add_key(label, size, type, rsa_priv, rsa_pub, rsa_priv_dum,
                              rsa_pub_dum)
    except Exception as e:
        print(" Error in access to database ({0})".format(e))
        exit(0)

    print('\nKey was successful generated:')
    print('LABEL: {0}\n TYPE: {1} '.format(label, type))
    if found_hole:
        print(' ID: {0}\n SIZE: {1}'.format(hole_id, size))
    else:
        print(' ID: {0}\n SIZE: {1}'.format(sql_o.get_id_from_label(label),
                                            size))


def key(args):
    sql_o = PySql()
    id = args.id
    if args.view:
        id = valid_id(id)
        key_t = sql_o.get_pub_key_from_id(id)
        label = sql_o.get_label_from_id(id)
        key_type = sql_o.get_key_type_from_id(id)
        key_size = sql_o.get_key_size_from_id(id)

        if None in (key_t, label, key_size, key_type):
            print('ERROR: ID not found!')
            sys.exit(0)

        print('\nLabel : {0}'.format(label))
        print('Type of key : {0}'.format(key_type))
        print('Key size : {0}'.format(key_size))
        print('\nPublic key is: ')
        print(key_t[0].decode('utf-8'))

    if args.list:
        for val in sql_o.get_list_pub_key_label():
            print('ID: {id}, LABEL: {l}'.format(id=val[0], l=val[1]))
        
    if args.delete:
        id = valid_id(id)
        try:
            print('ID: {0} will be deleted.'.format(id))
            erase = str(input("Are you sure? (YES/NO): "))
            if erase == 'YES':
                sql_o.delete_key_from_id(id)
                print('Your entry (ID: {0}) has been deleted.'.format(id))
            else:
                print('Action canceled.')
        except Exception as e:
            print(" Error in access to database ({0})".format(e))
            exit(0)

    if args.export:
        id = valid_id(id)
        out = args.out
        td = str(datetime.datetime.now())

        key = sql_o.get_pub_key_from_id(id)
        label = sql_o.get_label_from_id(id)
        if None in (key, label):
            print('ERROR: ID not found!')
            sys.exit(0)

        if args.out is None:
            out = str(label) + '_' + td
        try:
            with open(out, 'w') as fd:
                fd.write(key[0].decode('utf-8'))
            fd.close()
            print('Key exported as {0}'.format(out))
        except:
            print('Directory not found!')


def valid_id(id):
    while id is None:
        try:
            id = int(input('Enter ID: '))
        except:
            pass
    return id


def valid_label(label):
    while label is None or label is '':
        try:
            label = input('Enter label: ')
        except:
            pass
    return label


def main():
    parser = argparse.ArgumentParser(__file__,
                                     formatter_class=
                                     argparse.RawDescriptionHelpFormatter,
                                     description=
                                     '''
This program provide tools in order to initialize the HSM and manage keys.
You can reset your system, create some priv/pub key and view public keys.
All actions are logged on syslog. The size of key must be between 1024 and 8192.
IMPORTANT : You MUST have a path like /data/db/key.db

Tool kit:
reset_base: HARD database reset. Make backup before use it.
genkey:     Key generation tool kit.
key:        Key management tool kit.
                                    ''',
                                     epilog=
'''Examples:
    $ python3 SolHSM-MGMT.py -v
    $ python3 SolHSM-MGMT.py reset_base
    $ python3 SolHSM-MGMT.py genkey --rsa --size 2048 --label apachekey
    $ python3 SolHSM-MGMT.py key --view --id 123
    $ python3 SolHSM-MGMT.py key --list
    $ python3 SolHSM-MGMT.py key --delete  --id 123
    $ python3 SolHSM-MGMT.py key --export --id 123 --out /home/user/key.pem

    ''')

    parser.add_argument('type', choices=['reset_base', 'genkey', 'key', ' '])
    parser.add_argument("--rsa", "-r", help="RSA keys",
                        action="store_true", default=False)
    parser.add_argument("--view", "-w", help="View key from id",
                        action="store_true", default=False)                        
    parser.add_argument("--delete", "-d",  help="Delete key from id",
                        action="store_true", default=False)                        
    parser.add_argument("--export", "-p", help="export key in PEM format",
                        action="store_true", default=False)
    parser.add_argument("--out", "-o", help="export key in PEM format",
                        action="store")
    parser.add_argument("--id", "-i", type=int, help="Give id",
                        action="store") 
    parser.add_argument("--size", "-s", type=int, help="Set size of key",
                        action="store")
    parser.add_argument("--label", "-b",  help="Set label of key",
                        action="store")
    parser.add_argument("--list", "-l",  help="List all public keys",
                        action="store_true")


    args = parser.parse_args()

    if args.type == 'reset_base':
        reset()
    elif args.type == 'genkey' and args.rsa:
        genkey(args)
    elif args.type == 'key':
        key(args)
    else:
        print('Error argument')
        parser.print_help()


if __name__ == '__main__':
    main()
