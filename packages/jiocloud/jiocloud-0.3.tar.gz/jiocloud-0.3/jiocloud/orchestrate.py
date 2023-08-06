#    Copyright Reliance Jio Infocomm, Ltd.
#    Author: Soren Hansen <Soren.Hansen@ril.com>
#
#    Licensed under the Apache License, Version 2.0 (the "License"); you may
#    not use this file except in compliance with the License. You may obtain
#    a copy of the License at
#
#         http://www.apache.org/licenses/LICENSE-2.0
#
#    Unless required by applicable law or agreed to in writing, software
#    distributed under the License is distributed on an "AS IS" BASIS, WITHOUT
#    WARRANTIES OR CONDITIONS OF ANY KIND, either express or implied. See the
#    License for the specific language governing permissions and limitations
#    under the License.
#
import argparse
import etcd
import errno
import socket
import sys
import time
import urllib3
from urllib3.exceptions import HTTPError

class DeploymentOrchestrator(object):
    def __init__(self, host='127.0.0.1', port=4001):
        self.etcd = etcd.Client(host=host, port=port)

    def trigger_update(self, new_version):
        self.etcd.write('/current_version', new_version)

    def pending_update(self):
        return not (self.current_version() == self.local_version())

    def current_version(self):
        return self.etcd.read('/current_version').value.strip()

    def ping(self):
        try:
            return bool(self.etcd.machines)
        except etcd.EtcdError, HTTPError:
            return False

    def update_own_info(self, hostname, interval=60, version=None):
        version = version or self.local_version()
        version_dir = '/running_version/%s' % version
        self.etcd.write('%s/%s' % (version_dir, hostname), str(time.time()))
        self.etcd.write(version_dir, None, dir=True, prevExist=True, ttl=(interval*2+10))

    def running_versions(self):
        res = self.etcd.read('/running_version')
        return filter(lambda x: x != 'running_version',
                      [x.key.split('/')[-1] for x in res.children])

    def check_single_version(self, version, verbose=False):
        desired_version_seen = False
        running_versions = self.running_versions()
        unwanted_versions = filter(lambda x:x != version,
                                   running_versions)
        wanted_version_found = version in running_versions
        if verbose:
            print 'Wanted version found:', wanted_version_found
            print 'Unwanted versions found:', ', '.join(unwanted_versions)
        return wanted_version_found and not unwanted_versions

    def new_discovery_token(self, discovery_endpoint):
        http = urllib3.PoolManager()
        r = http.request('GET', '%snew' % (discovery_endpoint,))
        return r.data.split('/')[-1]

    def local_version(self, new_value=None):
        mode = new_value is None and 'r' or 'w'

        try:
            with open('/etc/current_version', mode) as fp:
                if new_value is None:
                    return fp.read().strip()
                else:
                    fp.write(new_value)
                    return new_value
        except IOError, e:
            if e.errno == errno.ENOENT:
                return ''
            raise

if __name__ == '__main__':
    parser = argparse.ArgumentParser(description='Utility for orchestrating updates')
    parser.add_argument('--host', type=str, default='127.0.0.1', help="etcd host")
    parser.add_argument('--port', type=int, default=4001, help="etcd port")
    subparsers = parser.add_subparsers(dest='subcmd')

    trigger_parser = subparsers.add_parser('trigger_update', help='Trigger an update')
    trigger_parser.add_argument('version', type=str, help='Version to deploy')

    current_version_parser = subparsers.add_parser('current_version', help='Get available version')

    ping_parser = subparsers.add_parser('ping', help='Ping etcd')

    pending_update = subparsers.add_parser('pending_update', help='Check for pending update')

    local_version_parser = subparsers.add_parser('local_version', help='Get or set local version')
    local_version_parser.add_argument('version', nargs='?', help="If given, set this as the local version")

    update_own_info_parser = subparsers.add_parser('update_own_info', help="Update host's own info")
    update_own_info_parser.add_argument('--interval', type=int, default=60, help="Update interval")
    update_own_info_parser.add_argument('--hostname', type=str, default=socket.gethostname(),
                                        help="This system's hostname")
    update_own_info_parser.add_argument('--version', type=str,
                                        help="Override version to report into etcd")
    running_versions_parser = subparsers.add_parser('running_versions', help="List currently running versions")

    new_discovery_token_parser = subparsers.add_parser('new_discovery_token', help="Get new discovery token")
    new_discovery_token_parser.add_argument('--endpoint', default='https://discovery.etcd.io/', help='Discovery token endpoint')

    check_single_version_parser = subparsers.add_parser('check_single_version', help="Check if the given version is the only one currently running")
    check_single_version_parser.add_argument('version', help='The version to check for')
    check_single_version_parser.add_argument('--verbose', '-v', action='store_true', help='Be verbose')
    args = parser.parse_args()

    do = DeploymentOrchestrator(args.host, args.port)
    if args.subcmd == 'trigger_update':
        do.trigger_update(args.version)
    elif args.subcmd == 'current_version':
        print do.current_version()
    elif args.subcmd == 'check_single_version':
        sys.exit(not do.check_single_version(args.version, args.verbose))
    elif args.subcmd == 'update_own_info':
        do.update_own_info(args.hostname, version=args.version)
    elif args.subcmd == 'ping':
        did_it_work = do.ping()
        if did_it_work:
            print 'Connection succesful'
            sys.exit(0)
        else:
            print 'Connection failed'
            sys.exit(1)
    elif args.subcmd == 'local_version':
        print do.local_version(args.version)
    elif args.subcmd == 'running_versions':
        print '\n'.join(do.running_versions())
    elif args.subcmd == 'new_discovery_token':
        print do.new_discovery_token(args.endpoint)
    elif args.subcmd == 'pending_update':
        pending_update = do.pending_update()
        if pending_update:
            print 'Yes, there is an update pending'
        else:
            print 'No updates pending'
        sys.exit(not pending_update)
