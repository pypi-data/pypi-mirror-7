#!/usr/bin/env python
# encoding: utf-8

"""This module provides functions to generate an ec2stack configuration file.
"""

import os

from alembic import command
from alembic.config import Config as AlembicConfig


def main():
    """
    Entry point into the configuration application.

    """
    config_folder = _create_config_folder()
    _create_config_file(config_folder)
    _create_database()


def _create_config_folder():
    """
    Creates a folder to hold the user's configuration files.

    @return: Path of the configuration folder.
    """
    config_folder = os.path.join(os.path.expanduser('~'), '.ec2stack')
    if not os.path.exists(config_folder):
        os.makedirs(config_folder)
    os.chmod(config_folder, 0700)
    return config_folder


def _create_config_file(config_folder):
    """
    Reads in configuration items and writes them out to the configuration file.

    @param config_folder: Path of the configuration folder.
    """
    config_file = open(config_folder + '/ec2stack.conf', 'w+')

    ec2stack_address = raw_input('EC2Stack bind address [0.0.0.0]: ')
    if ec2stack_address == '':
        ec2stack_address = '0.0.0.0'
    config_file.write('EC2STACK_BIND_ADDRESS = \'%s\'\n' % ec2stack_address)

    ec2stack_port = raw_input('EC2Stack bind port [5000]: ')
    if ec2stack_port == '':
        ec2stack_port = '5000'
    config_file.write('EC2STACK_PORT = \'%s\'\n' % ec2stack_port)

    cloudstack_host = raw_input('Cloudstack host [localhost]: ')
    if cloudstack_host == '':
        cloudstack_host = 'localhost'
    config_file.write('CLOUDSTACK_HOST = \'%s\'\n' % cloudstack_host)

    cloudstack_port = raw_input('Cloudstack port [8080]: ')
    if cloudstack_port == '':
        cloudstack_port = '8080'
    config_file.write('CLOUDSTACK_PORT = \'%s\'\n' % cloudstack_port)

    cloudstack_protocol = raw_input('Cloudstack protocol [http]: ')
    if cloudstack_protocol == '':
        cloudstack_protocol = 'http'
    config_file.write('CLOUDSTACK_PROTOCOL = \'%s\'\n' % cloudstack_protocol)

    cloudstack_path = raw_input('Cloudstack path [/client/api]: ')
    if cloudstack_path == '':
        cloudstack_path = '/client/api'
    config_file.write('CLOUDSTACK_PATH = \'%s\'\n' % cloudstack_path)

    cloudstack_custom_disk_offering = raw_input(
        'Cloudstack custom disk offering name [Custom]: '
    )
    if cloudstack_custom_disk_offering == '':
        cloudstack_custom_disk_offering = 'Custom'

    config_file.write(
        'CLOUDSTACK_CUSTOM_DISK_OFFERING = \'%s\'\n' % cloudstack_custom_disk_offering
    )

    while True:
        cloudstack_default_zone = raw_input(
            'Cloudstack default zone name: '
        )
        if cloudstack_default_zone != '':
            config_file.write(
                'CLOUDSTACK_DEFAULT_ZONE = \'%s\'\n' %
                cloudstack_default_zone)
            break

    configure_instance_type_mapings = raw_input(
        'Do you wish to input instance type mappings? (Yes/No): '
    )

    if configure_instance_type_mapings.lower() in ['yes', 'y']:
        config_file = _read_user_instance_mappings(config_file)

    configure_resource_type_mapings = raw_input(
        'Do you wish to input resource type to resource id mappings'
        + ' for tag support? (Yes/No): '
    )

    if configure_resource_type_mapings.lower() in ['yes', 'y']:
        config_file = _read_user_resource_type_mappings(config_file)

    config_file.close()


def _read_user_instance_mappings(config_file):
    instance_type_map = {}
    while True:
        key = raw_input(
            'Insert the AWS EC2 instance type you wish to map: '
        )

        value = raw_input(
            'Insert the name of the instance type you wish to map this to: '
        )

        instance_type_map[key] = value

        add_more = raw_input(
            'Do you wish to add more mappings? (Yes/No): ')
        if add_more.lower() in ['no', 'n']:
            break

    config_file.write(
        'INSTANCE_TYPE_MAP = %s\n' % instance_type_map
    )

    return config_file


def _read_user_resource_type_mappings(config_file):
    resource_type_map = {}
    while True:
        key = raw_input(
            'Insert the cloudstack resource id you wish to map: '
        )

        value = raw_input(
            'Insert the cloudstack resource type you wish to map this to: '
        )

        resource_type_map[key] = value

        add_more = raw_input(
            'Do you wish to add more mappings? (Yes/No): ')
        if add_more.lower() in ['no', 'n']:
            break

    config_file.write(
        'RESOURCE_TYPE_MAP = %s\n' % resource_type_map
    )

    return config_file


def _create_database():
    """
    Creates/Updates the database.
    """
    directory = os.path.join(os.path.dirname(__file__), '../migrations')
    config = AlembicConfig(os.path.join(
        directory,
        'alembic.ini'
    ))
    config.set_main_option('script_location', directory)
    command.upgrade(config, 'head', sql=False, tag=None)
