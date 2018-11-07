#coding=utf8
import gevent.monkey
gevent.monkey.patch_socket()

import os, sys
sys.path.insert(0, "/home/btt/pysproto/build/lib.linux-x86_64-2.7")
import unittest
import argparse
from lib import env
from lib import proto
#import GreenletProfiler

def init_sproto(cfg_file):
    env.read(cfg_file)
    sproto_path = env.get('sproto', 'sproto_path')
    spb_file = env.get('sproto', 'spb_file')
    base_package = env.get('sproto', 'base_package')
    ret = proto.init_proto(sproto_path, spb_file, base_package, False)

    return ret

def main():
    # args
    parser = argparse.ArgumentParser()
    parser.add_argument(
        '-s', '--server', dest='host', help='game server ip address')
    parser.add_argument(
        '-p', '--port', dest='port', help='game server tcp port')
    parser.add_argument(
        '-d', '--case', dest='case', default='case', help='test case folder')
    parser.add_argument('-l', '--log', dest='log_file', help='set log file')
    parser.add_argument(
        '-v',
        '--verbose',
        action="count",
        dest='verbosity',
        help='show more info')
    parser.add_argument("-f", '--file', dest='test_file', help='set test file')
    parser.add_argument(
        '-c',
        '--cfg',
        dest='cfg_file',
        default='config.ini',
        help='set config file')
    args = parser.parse_args()

    print("init proto ...")
    cfg_file = args.cfg_file
    if not init_sproto(cfg_file):
        exit(1)

    if args.host:
        env.set('login', 'host', args.host)
    if args.port:
        env.set('login', 'port', str(args.port))

    print("server address %s:%s" % (env.get('login', 'host'),
                                env.get('login', 'port')))

    # create test class
    suites = []
    if args.test_file:
        p, f = os.path.split(args.test_file)
        sys.path.append(p)
        suite = unittest.TestLoader().loadTestsFromName(
            os.path.splitext(f)[0] if f.endswith(".py") else f)
        suites.append(suite)
    else:
        suite = unittest.TestLoader().discover(args.case)
        suites.append(suite)

    alltests = unittest.TestSuite(suites)
    stream = sys.stderr
    if args.log_file:
        stream = open(args.log_file, 'w')
    result = unittest.TextTestRunner(verbosity=3, stream=stream).run(alltests)
    stream.close()

    if len(result.errors) or len(result.failures):
        exit(1)
    else:
        exit(0)


if __name__ == "__main__":
    main()
