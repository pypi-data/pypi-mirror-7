#!/usr/bin/env python
# -*- coding: utf-8 -*-

# Copyright (c) 2014 clowwindy
#
# Permission is hereby granted, free of charge, to any person obtaining a copy
# of this software and associated documentation files (the "Software"), to deal
# in the Software without restriction, including without limitation the rights
# to use, copy, modify, merge, publish, distribute, sublicense, and/or sell
# copies of the Software, and to permit persons to whom the Software is
# furnished to do so, subject to the following conditions:
#
# The above copyright notice and this permission notice shall be included in
# all copies or substantial portions of the Software.
#
# THE SOFTWARE IS PROVIDED "AS IS", WITHOUT WARRANTY OF ANY KIND, EXPRESS OR
# IMPLIED, INCLUDING BUT NOT LIMITED TO THE WARRANTIES OF MERCHANTABILITY,
# FITNESS FOR A PARTICULAR PURPOSE AND NONINFRINGEMENT. IN NO EVENT SHALL THE
# AUTHORS OR COPYRIGHT HOLDERS BE LIABLE FOR ANY CLAIM, DAMAGES OR OTHER
# LIABILITY, WHETHER IN AN ACTION OF CONTRACT, TORT OR OTHERWISE, ARISING FROM,
# OUT OF OR IN CONNECTION WITH THE SOFTWARE OR THE USE OR OTHER DEALINGS IN THE
# SOFTWARE.

from __future__ import with_statement
import sys
if sys.version_info < (2, 6):
    import simplejson as json
else:
    import json


# TODO remove gevent
try:
    import gevent
    import gevent.monkey
    gevent.monkey.patch_all(dns=gevent.version_info[0] >= 1)
except ImportError:
    gevent = None
    print >>sys.stderr, 'warning: gevent not found, using threading instead'


import socket
import select
import threading
import SocketServer
import struct
import logging
import getopt
import encrypt
import os
import utils
import udprelay


def send_all(sock, data):
    bytes_sent = 0
    while True:
        r = sock.send(data[bytes_sent:])
        if r < 0:
            return r
        bytes_sent += r
        if bytes_sent == len(data):
            return bytes_sent


class ThreadingTCPServer(SocketServer.ThreadingMixIn, SocketServer.TCPServer):
    allow_reuse_address = True

    def server_activate(self):
        if config_fast_open:
            try:
                self.socket.setsockopt(socket.SOL_TCP, 23, 5)
            except socket.error:
                logging.error('warning: fast open is not available')
        self.socket.listen(self.request_queue_size)


class Socks5Server(SocketServer.StreamRequestHandler):
    def handle_tcp(self, sock, remote):
        try:
            fdset = [sock, remote]
            while True:
                should_break = False
                r, w, e = select.select(fdset, [], [])
                if sock in r:
                    data = self.decrypt(sock.recv(4096))
                    if len(data) <= 0:
                        should_break = True
                    else:
                        result = send_all(remote, data)
                        if result < len(data):
                            raise Exception('failed to send all data')
                if remote in r:
                    data = self.encrypt(remote.recv(4096))
                    if len(data) <= 0:
                        should_break = True
                    else:
                        result = send_all(sock, data)
                        if result < len(data):
                            raise Exception('failed to send all data')
                if should_break:
                    # make sure all data are read before we close the sockets
                    # TODO: we haven't read ALL the data, actually
                    # http://cs.ecs.baylor.edu/~donahoo/practical/CSockets/TCPRST.pdf
                    break

        finally:
            sock.close()
            remote.close()

    def encrypt(self, data):
        return self.encryptor.encrypt(data)

    def decrypt(self, data):
        return self.encryptor.decrypt(data)

    def handle(self):
        try:
            self.encryptor = encrypt.Encryptor(self.server.key,
                                               self.server.method)
            sock = self.connection
            sock.setsockopt(socket.IPPROTO_TCP, socket.TCP_NODELAY, 1)
            iv_len = self.encryptor.iv_len()
            data = sock.recv(iv_len)
            if iv_len > 0 and not data:
                sock.close()
                return
            if iv_len:
                self.decrypt(data)
            data = sock.recv(1)
            if not data:
                sock.close()
                return
            addrtype = ord(self.decrypt(data))
            if addrtype == 1:
                addr = socket.inet_ntoa(self.decrypt(self.rfile.read(4)))
            elif addrtype == 3:
                addr = self.decrypt(
                    self.rfile.read(ord(self.decrypt(sock.recv(1)))))
            elif addrtype == 4:
                addr = socket.inet_ntop(socket.AF_INET6,
                                        self.decrypt(self.rfile.read(16)))
            else:
                # not supported
                logging.warn('addr_type not supported, maybe wrong password')
                return
            port = struct.unpack('>H', self.decrypt(self.rfile.read(2)))
            try:
                logging.info('connecting %s:%d' % (addr, port[0]))
                remote = socket.create_connection((addr, port[0]))
                remote.setsockopt(socket.IPPROTO_TCP, socket.TCP_NODELAY, 1)
            except socket.error, e:
                # Connection refused
                logging.warn(e)
                return
            self.handle_tcp(sock, remote)
        except socket.error, e:
            logging.warn(e)


def main():
    global config_server, config_server_port, config_method, config_fast_open

    logging.basicConfig(level=logging.DEBUG,
                        format='%(asctime)s %(levelname)-8s %(message)s',
                        datefmt='%Y-%m-%d %H:%M:%S', filemode='a+')


    version = ''
    try:
        import pkg_resources
        version = pkg_resources.get_distribution('shadowsocks').version
    except:
        pass
    print 'shadowsocks %s' % version

    config_path = utils.find_config()
    try:
        optlist, args = getopt.getopt(sys.argv[1:], 's:p:k:m:c:',
                                      ['fast-open', 'workers:'])
        for key, value in optlist:
            if key == '-c':
                config_path = value

        if config_path:
            logging.info('loading config from %s' % config_path)
            with open(config_path, 'rb') as f:
                try:
                    config = json.load(f)
                except ValueError as e:
                    logging.error('found an error in config.json: %s',
                                  e.message)
                    sys.exit(1)
        else:
            config = {}

        optlist, args = getopt.getopt(sys.argv[1:], 's:p:k:m:c:',
                                      ['fast-open', 'workers='])
        for key, value in optlist:
            if key == '-p':
                config['server_port'] = int(value)
            elif key == '-k':
                config['password'] = value
            elif key == '-s':
                config['server'] = value
            elif key == '-m':
                config['method'] = value
            elif key == '--fast-open':
                config['fast_open'] = True
            elif key == '--workers':
                config['workers'] = value
    except getopt.GetoptError:
        utils.print_server_help()
        sys.exit(2)

    config_server = config['server']
    config_server_port = config['server_port']
    config_key = config['password']
    config_method = config.get('method', None)
    config_port_password = config.get('port_password', None)
    config_timeout = config.get('timeout', 600)
    config_fast_open = config.get('fast_open', False)
    config_workers = config.get('workers', 1)

    if not config_key and not config_path:
        sys.exit('config not specified, please read '
                 'https://github.com/clowwindy/shadowsocks')

    utils.check_config(config)

    if config_port_password:
        if config_server_port or config_key:
            logging.warn('warning: port_password should not be used with '
                         'server_port and password. server_port and password '
                         'will be ignored')
    else:
        config_port_password = {}
        config_port_password[str(config_server_port)] = config_key

    encrypt.init_table(config_key, config_method)
    addrs = socket.getaddrinfo(config_server, int(8387))
    if not addrs:
        logging.error('cant resolve listen address')
        sys.exit(1)
    ThreadingTCPServer.address_family = addrs[0][0]
    tcp_servers = []
    udp_servers = []
    for port, key in config_port_password.items():
        tcp_server = ThreadingTCPServer((config_server, int(port)),
                                        Socks5Server)
        tcp_server.key = key
        tcp_server.method = config_method
        tcp_server.timeout = int(config_timeout)
        logging.info("starting server at %s:%d" %
                     tuple(tcp_server.server_address[:2]))
        tcp_servers.append(tcp_server)
        udp_server = udprelay.UDPRelay(config_server, int(port), None, None,
                                       key, config_method, int(config_timeout),
                                       False)
        udp_servers.append(udp_server)

    def run_server():
        for tcp_server in tcp_servers:
            threading.Thread(target=tcp_server.serve_forever).start()
        for udp_server in udp_servers:
            udp_server.start()

    if int(config_workers) > 1:
        if os.name == 'posix':
            children = []
            is_child = False
            for i in xrange(0, int(config_workers)):
                r = os.fork()
                if r == 0:
                    logging.info('worker started')
                    is_child = True
                    run_server()
                    break
                else:
                    children.append(r)
            if not is_child:
                def handler(signum, frame):
                    for pid in children:
                        os.kill(pid, signum)
                        os.waitpid(pid, 0)
                    sys.exit()
                import signal
                signal.signal(signal.SIGTERM, handler)
                # master
                for child in children:
                    os.waitpid(child, 0)
        else:
            logging.warn('worker is only available on Unix/Linux')
            run_server()
    else:
        run_server()


if __name__ == '__main__':
    try:
        main()
    except socket.error, e:
        logging.error(e)
