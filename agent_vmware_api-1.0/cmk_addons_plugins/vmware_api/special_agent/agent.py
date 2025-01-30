#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Check validity of VCSA certificates (STS/TLS), tags and DRS/HA (enabled/disabled)
"""

#
# Author: muehling.stefan[at]googlemail[dot]com
# Date  : 2024-12-18
#
# CheckMK special agent for VMware API
#  - certificates
#  - tags
#  - drs/ha setup
# Requires:
#
#

# Example: agent_vmware-api.py --vcenter 172.16.1.1 --username Administrator@vsphere.local --password My_Secret --verify-ssl

import sys
import argparse
import logging
from typing import Optional, Sequence
import requests
import json

from urllib3.exceptions import InsecureRequestWarning
requests.packages.urllib3.disable_warnings(category=InsecureRequestWarning)

from cmk.special_agents.v0_unstable.agent_common import (
    SectionWriter,
    special_agent_main,
)
from cmk.special_agents.v0_unstable.argument_parsing import (
    Args,
    create_default_argument_parser,
)

from pathlib import Path

from cmk.utils import password_store, paths, store

from OpenSSL import crypto

import time


signing_endpoint = 'api/vcenter/certificate-management/vcenter/signing-certificate'
tls_endpoint = 'api/vcenter/certificate-management/vcenter/tls'
trusted_root_chains_endpoint = 'api/vcenter/certificate-management/vcenter/trusted-root-chains'
tags_endpoint = 'api/vcenter/tagging/associations'
vms_endpoint = 'api/vcenter/vm'
drsha_endpoint = 'api/vcenter/cluster'

#https://{api_host}/api/vcenter/vm

sep = '|'

class VMWareTag:
    def __init__(self, vm, category_id, name, description, id, used_by):
        self.vm = vm
        self.category_id = category_id
        self.name = name
        self.description = description
        self.id = id
        self.used_by = used_by
    def __str__(self):
        return f'{self.name}'
    def __repr__(self):
        return f'{self.name}'

def parse_arguments(argv: Sequence[str]) -> argparse.Namespace:
    """'
    Parse arguments needed to construct an URL and for connection conditions
    """

    parser = create_default_argument_parser(description=__doc__)
    # required
    parser.add_argument(
        "-u", "--username", default=None, help="Username for API Login", required=True
    )
    group = parser.add_mutually_exclusive_group()
    group.add_argument(
        "-s",
        "--password",
        default=None,
        help="""Password for API Login. Preferred over --password-id""",
    )
    group.add_argument(
        "--password-id",
        default=None,
        help="""Password store reference to the password for API login""",
    )
    parser.add_argument(
        "-p",
        "--port",
        default=443,
        type=int,
        help="Use alternative port (default: 443)",
    )
    parser.add_argument(
        "--verify-ssl",
        action="store_true",
        default=False,
    )

    # required
    parser.add_argument(
        "host",
        metavar="HOSTNAME",
        help="""IP address or hostname of your VMware API""",
    )

    return parser.parse_args(argv)

def main(argv: Optional[Sequence[str]] = None) -> None:
    agent_version = 'v0.1'
    agent_build = '2023-02-21'
    agent_os = 'Linux'
    certificates = []

    def check_vmware_certificates(certs, usage):
        try:
            # Assuming the certificates are in PEM format in a trusted_certs list
            for _cert in certs:
                client_certificate = crypto.load_certificate(crypto.FILETYPE_PEM, _cert)
                subject = client_certificate.get_subject()
                CN = subject.CN
                subject = "".join("/{:s}={:s}".format(name.decode(), value.decode()) for name, value in subject.get_components())
                expires = time.mktime(time.strptime(str(client_certificate.get_notAfter()), "b'%Y%m%d%H%M%SZ'"))
                result = f'{usage}{sep}{CN}{sep}{expires}{sep}{subject}'
                if not result in certificates:
                    certificates.append(result)

        except Exception as e:
            print(e)

    if argv is None:
        argv = sys.argv[1:]

    args = parse_arguments(argv)

    pw_id, pw_path = args.password_id.split(":")
    password=args.password if args.password is not None else password_store.lookup(Path(pw_path), pw_id)
    verify = args.verify_ssl


    # Collect everything
    try:
        print(f'<<<vmware_api_certificates:sep({ord(sep)})>>>')

        # Get session ID
        response = requests.post(f'https://{args.host}/api/session', auth=(args.username, password), verify=verify)
        if response.ok:
            session_id = response.json()
        else:
            raise SystemExit("Unable to retrieve a session ID.")

        # SSL / HTTPS certificate
        response = requests.get(f'https://{args.host}/{tls_endpoint}', headers={"vmware-api-session-id": session_id}, verify=verify)
        if response.ok:
            try:
                tls = response.json()
                check_vmware_certificates([tls['cert']], 'UI')
            except:
                pass
        else:
            ...
            #raise SystemExit(f'Unable to retrieve tls endpoint.')

        # Signing certificate chain
        response = requests.get(f'https://{args.host}/{signing_endpoint}', headers={"vmware-api-session-id": session_id}, verify=verify)
        if response.ok:
            try:
                for value in response.json().values():
                    # active cert chain
                    if isinstance(value, dict):
                        check_vmware_certificates(value['cert_chain'], 'Signing')
            except:
                pass
        else:
            ...
            #raise SystemExit(f'Unable to retrieve signing endpoint.')

        # Trusted root chains
        response = requests.get(f'https://{args.host}/{trusted_root_chains_endpoint}', headers={"vmware-api-session-id": session_id}, verify=verify)
        trusted_root_chains = ''
        if response.ok:
            trusted_root_chains = response.json()
        else:
            ...
            #raise SystemExit(f'Unable to retrieve trusted_root_chain endpoint.')

        for trusted_root_chain in trusted_root_chains:
            response = requests.get(f'https://{args.host}/{trusted_root_chains_endpoint}/{trusted_root_chain["chain"]}', headers={"vmware-api-session-id": session_id}, verify=verify)
            if response.ok:
                try:
                    for key, value in response.json().items():
                        check_vmware_certificates(value['cert_chain'], 'Trust chain')
                except:
                    pass
            else:
                ...
                #raise SystemExit(f'Unable to retrieve trusted_root_chain endpoint.')

        print('\n'.join(certificates))

    except:
        raise

    try:

        print(f'<<<vmware_api_vm_ips:sep({ord(sep)})>>>')
        vms_response = requests.get(f'https://{args.host}/{vms_endpoint}', headers={"vmware-api-session-id": session_id}, verify=verify)
        vms = { vm['vm']: {'name': vm['name']} for vm in vms_response.json() }
        try:
            for vm in vms:
                vm_response = requests.get(f'https://{args.host}/{vms_endpoint}/{vm}', headers={"vmware-api-session-id": session_id}, verify=verify)
#                print(vm_response.json())
                uuid = vm_response.json()['identity']['bios_uuid']
                ip_response = requests.get(f'https://{args.host}/{vms_endpoint}/{vm}/guest/identity', headers={"vmware-api-session-id": session_id}, verify=verify)
                ip_object = ip_response.json()
                ip = ip_object.get('ip_address', '')
                print(f"{uuid}{sep}{vms[vm]['name']}{sep}{ip}")
        except:
            raise

    except:
        raise

    try:
        print(f'<<<vmware_api_tags:sep({ord(sep)})>>>')


        VMWareTags = {}
        response = requests.get(f'https://{args.host}/{tags_endpoint}', headers={"vmware-api-session-id": session_id}, verify=verify)
        if response.ok:
            vms_response = requests.get(f'https://{args.host}/{vms_endpoint}', headers={"vmware-api-session-id": session_id}, verify=verify)
            vms = { vm['name']: None for vm in vms_response.json() }
#            print(response.json())
            try:
                for value in response.json()['associations']:

                    vmware_tag = value['tag']
                    vmware_object = value['object']['id']
                    tag_response = requests.get(f'https://{args.host}/api/cis/tagging/tag/{vmware_tag}', headers={"vmware-api-session-id": session_id}, verify=verify)
                    tag_object = tag_response.json()
                    try:
                        vm_response = requests.get(f'https://{args.host}/{vms_endpoint}/{vmware_object}', headers={"vmware-api-session-id": session_id}, verify=verify)
                        vm_object = vm_response.json()['identity']['name']
                        vms[vm_object] = VMWareTag(vm_object, **tag_object)
                    except:
                        continue
            except:
                raise
            else:
                for vm, tags in vms.items():
                    if tags == None and not vm.startswith('vCLS'):
                        print(vm,)

    except:
        raise

    try:
        with SectionWriter(f"vmware_api_ha") as w:
            drsha_response = requests.get(f'https://{args.host}/{drsha_endpoint}', headers={"vmware-api-session-id": session_id}, verify=verify).json()
            if isinstance(drsha_response, list):
                w.append_json(drsha_response)

    except:
        raise

    print('<<<check_mk>>>')
    print(f'Version: {agent_version}')
    print(f'AgentOS: {agent_os}')
    print(f'BuildDate: {agent_build}')


if __name__ == '__main__':
    main()


