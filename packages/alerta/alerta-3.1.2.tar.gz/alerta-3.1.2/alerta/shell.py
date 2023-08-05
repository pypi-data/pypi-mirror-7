#!/usr/bin/env python
"""
    Alerta unified command-line tool
"""

__version__ = '3.1.2'
__license__ = 'MIT'

import os
import sys
import argparse
import time
import datetime
import json
import requests
import ConfigParser
import logging

from alerta.api import ApiClient
from alerta.alert import Alert, AlertDocument
from alerta.heartbeat import Heartbeat

prog = os.path.basename(sys.argv[0])

LOG = logging.getLogger(__name__)
root = logging.getLogger()

DEFAULT_CONF_FILE = '~/.alerta.conf'
DEFAULT_ENDPOINT_URL = 'http://localhost:8080'
DEFAULT_TIMEZONE = 'Europe/London'
DEFAULT_OUTPUT = 'text'
DEFAULT_COLOR = True
DEFAULT_DEBUG = False

DEFAULT_SEVERITY = "normal"  # "normal", "ok" or "clear"
DEFAULT_TIMEOUT = 86400

_COLOR_MAP = {
    "critical": '\033[91m',
    "major": '\033[95m',
    "minor": '\033[93m',
    "warning": '\033[96m',
    "indeterminate": '\033[92m',
    "clear": '\033[92m',
    "normal": '\033[92m',
    "informational": '\033[92m',
    "debug": '\033[90m',
    "auth": '\033[90m',
    "unknown": '\033[90m',
}
_ENDC = '\033[0m'


class AlertCommand(object):

    def __init__(self):

        self.api = None

    def set_api(self, url):

        self.api = ApiClient(endpoint=url)

    def config(self, args):

        print
        print 'Name             Value                             Location'
        print '----             -----                             --------'
        print 'config_file      %-30s    %s' % (args.config_file, sources['config_file'])
        print 'profile          %-30s    %s' % (args.profile, sources['profile'])
        print 'endpoint         %-30s    %s' % (args.endpoint, sources['endpoint'])
        print 'timezone         %-30s    %s' % (args.timezone, sources['timezone'])
        print 'output           %-30s    %s' % (args.output, sources['output'])
        print 'color            %-30s    %s' % (args.color, sources['color'])
        print 'debug            %-30s    %s' % (args.debug, sources['debug'])
        print

    def send(self, args):

        try:
            alert = Alert(
                resource=args.resource,
                event=args.event,
                environment=args.environment,
                severity=args.severity,
                correlate=args.correlate,
                status=args.status,
                service=args.service,
                group=args.group,
                value=args.value,
                text=args.text,
                tags=args.tags,
                attributes=dict([attrib.split('=') for attrib in args.attributes]),
                origin=args.origin,
                event_type=args.event_type,
                timeout=args.timeout,
                raw_data=args.raw_data
            )
        except Exception as e:
            LOG.error(e)
            sys.exit(1)

        try:
            response = self.api.send(alert)
        except Exception as e:
            LOG.error(e)
            sys.exit(1)

        if response['status'] == 'ok':
            print response['id']
        else:
            LOG.error(response['message'])
            sys.exit(1)

    def heartbeat(self, args):

        try:
            heartbeat = Heartbeat(
                origin=args.origin,
                tags=args.tags,
                timeout=args.timeout
            )
        except Exception as e:
            LOG.error(e)
            sys.exit(1)

        try:
            response = self.api.send(heartbeat)
        except Exception as e:
            LOG.error(e)
            sys.exit(1)

        if response['status'] == 'ok':
            print response['id']
        else:
            LOG.error(response['message'])
            sys.exit(1)

    def query(self, args, from_date=None):

        response = self._alerts(args.filter, from_date)
        alerts = response['alerts']

        if args.output == "json":
            print json.dumps(alerts, indent=4)
            sys.exit(0)

        # tz = pytz.timezone(args.timezone)

        for alert in reversed(alerts):

            a = AlertDocument.parse_alert(alert)

            line_color = ''
            end_color = _ENDC

            if args.color:
                line_color = _COLOR_MAP.get(a.severity, _COLOR_MAP['unknown'])

            print(line_color + '%s|%s|%s|%5d|%-5s|%-10s|%-18s|%12s|%16s|%12s' % (
                a.id[0:8],
                a.get_date('last_receive_time', 'local'),
                a.severity,
                a.duplicate_count,
                a.environment,
                ','.join(a.service),
                a.resource,
                a.group,
                a.event,
                a.value) + end_color)
            print(line_color + '   |%s' % (a.text.encode('utf-8')) + end_color)

            if args.details:
                print(line_color + '    severity   | %s -> %s' % (a.previous_severity, a.severity) + end_color)
                print(line_color + '    trend      | %s' % a.trend_indication + end_color)
                print(line_color + '    status     | %s' % a.status + end_color)
                print(line_color + '    resource   | %s' % a.resource + end_color)
                print(line_color + '    group      | %s' % a.group + end_color)
                print(line_color + '    event      | %s' % a.event + end_color)
                print(line_color + '    value      | %s' % a.value + end_color)
                print(line_color + '    tags       | %s' % ' '.join(a.tags) + end_color)

                for key, value in a.attributes.items():
                    print(line_color + '    %s | %s' % (key.ljust(10), value) + end_color)

                latency = a.receive_time - a.create_time

                print(line_color + '        time created  | %s' % a.get_date('create_time', 'iso') + end_color)
                print(line_color + '        time received | %s' % a.get_date('receive_time', 'iso') + end_color)
                print(line_color + '        last received | %s' % a.get_date('last_receive_time', 'iso') + end_color)
                print(line_color + '        latency       | %sms' % (latency.microseconds / 1000) + end_color)
                print(line_color + '        timeout       | %ss' % a.timeout + end_color)

                print(line_color + '            alert id     | %s' % a.id + end_color)
                print(line_color + '            last recv id | %s' % a.last_receive_id + end_color)
                print(line_color + '            environment  | %s' % a.environment + end_color)
                print(line_color + '            service      | %s' % ','.join(a.service) + end_color)
                print(line_color + '            resource     | %s' % a.resource + end_color)
                print(line_color + '            type         | %s' % a.event_type + end_color)
                print(line_color + '            repeat       | %s' % a.repeat + end_color)
                print(line_color + '            origin       | %s' % a.origin + end_color)
                print(line_color + '            correlate    | %s' % ','.join(a.correlate) + end_color)

        return response.get('lastTime', '')

    def watch(self, args):

        from_date = None
        while True:
            from_date = self.query(args, from_date)
            try:
                time.sleep(2)
            except (KeyboardInterrupt, SystemExit):
                sys.exit(0)

    def raw(self, args):

        response = self._alerts(args.filter)
        alerts = response['alerts']

        if args.output == "json":
            print json.dumps(alerts, indent=4)
            sys.exit(0)

        for alert in reversed(alerts):
            line_color = ''
            end_color = _ENDC

            print(line_color + '%s' % alert['rawData'] + end_color)

    def history(self, args):

        response = self._history(args.filter)
        history = response['history']

        if args.output == "json":
            print json.dumps(history, indent=4)
            sys.exit(0)

        # tz = pytz.timezone(args.timezone)

        for hist in history:

            line_color = ''
            end_color = _ENDC

            update_time = datetime.datetime.strptime(hist.get('updateTime', None), '%Y-%m-%dT%H:%M:%S.%fZ')

            if 'severity' in hist:
                if args.color:
                    line_color = _COLOR_MAP.get(hist['severity'], _COLOR_MAP['unknown'])
                print(line_color + '%s|%s|%s|%-5s|%-10s|%-18s|%s|%s|%s|%s' % (
                    hist['id'][0:8],
                    update_time.strftime('%Y/%m/%d %H:%M:%S'),
                    hist['severity'],
                    hist['environment'],
                    ','.join(hist['service']),
                    hist['resource'],
                    hist['group'],
                    hist['event'],
                    hist['value'],
                    hist['text']
                ) + end_color)

            if 'status' in hist:
                print(line_color + '%s|%s|%s|%-5s|%-10s|%-18s|%s|%s|%s|%s' % (
                    hist['id'][0:8],
                    update_time.strftime('%Y/%m/%d %H:%M:%S'),
                    hist['status'],
                    hist['environment'],
                    ','.join(hist['service']),
                    hist['resource'],
                    hist['group'],
                    hist['event'],
                    'n/a',
                    hist['text']
                ) + end_color)

    def tag(self, args):

        sys.stdout.write("Counting alerts: ")
        response = self._alerts(args.filter)
        alerts = response['alerts']
        total = response['total']
        sys.stdout.write("%s, done.\n" % total)

        sys.stdout.write("Tagging alerts: ")
        for i, alert in enumerate(alerts):
            pct = int(100.0 * i / total)
            sys.stdout.write("%3d%% (%d/%d)" % (pct, i, total))
            sys.stdout.flush()
            sys.stdout.write("\b" * (8 + len(str(i)) + len(str(total))))
            self.api.tag_alert(alert['id'], args.tags)

        sys.stdout.write("100%% (%d/%d), done.\n" % (total, total))

    def untag(self, args):

        sys.stdout.write("Counting alerts: ")
        response = self._alerts(args.filter)
        alerts = response['alerts']
        total = response['total']
        sys.stdout.write("%s, done.\n" % total)

        sys.stdout.write("Un-tagging alerts: ")
        for i, alert in enumerate(alerts):
            pct = int(100.0 * i / total)
            sys.stdout.write("%3d%% (%d/%d)" % (pct, i, total))
            sys.stdout.flush()
            sys.stdout.write("\b" * (8 + len(str(i)) + len(str(total))))
            self.api.untag_alert(alert['id'], args.tags)

        sys.stdout.write("100%% (%d/%d), done.\n" % (total, total))

    def ack(self, args):

        sys.stdout.write("Counting alerts: ")
        response = self._counts(args.filter)
        total = response['total']
        sys.stdout.write("%s, done.\n" % total)

        sys.stdout.write("Acking alerts: ")
        response = self._alerts(args.filter)
        alerts = response['alerts']
        for i, alert in enumerate(alerts):
            pct = int(100.0 * i / total)
            sys.stdout.write("%3d%% (%d/%d)" % (pct, i, total))
            sys.stdout.flush()
            sys.stdout.write("\b" * (8 + len(str(i)) + len(str(total))))
            self.api.ack_alert(alert['id'])

        sys.stdout.write("100%% (%d/%d), done.\n" % (total, total))

    def unack(self, args):

        sys.stdout.write("Counting alerts: ")
        response = self._counts(args.filter)
        total = response['total']
        sys.stdout.write("%s, done.\n" % total)

        sys.stdout.write("un-Acking alerts: ")
        response = self._alerts(args.filter)
        alerts = response['alerts']
        for i, alert in enumerate(alerts):
            pct = int(100.0 * i / total)
            sys.stdout.write("%3d%% (%d/%d)" % (pct, i, total))
            sys.stdout.flush()
            sys.stdout.write("\b" * (8 + len(str(i)) + len(str(total))))
            self.api.unack_alert(alert['id'])

        sys.stdout.write("100%% (%d/%d), done.\n" % (total, total))

    def close(self, args):

        sys.stdout.write("Counting alerts: ")
        response = self._counts(args.filter)
        total = response['total']
        sys.stdout.write("%s, done.\n" % total)

        sys.stdout.write("Closing alerts: ")
        response = self._alerts(args.filter)
        alerts = response['alerts']
        for i, alert in enumerate(alerts):
            pct = int(100.0 * i / total)
            sys.stdout.write("%3d%% (%d/%d)" % (pct, i, total))
            sys.stdout.flush()
            sys.stdout.write("\b" * (8 + len(str(i)) + len(str(total))))
            self.api.close_alert(alert['id'])

        sys.stdout.write("100%% (%d/%d), done.\n" % (total, total))

    def delete(self, args):

        sys.stdout.write("Counting alerts: ")
        response = self._counts(args.filter)
        total = response['total']
        sys.stdout.write("%s, done.\n" % total)

        sys.stdout.write("Deleting alerts: ")
        response = self._alerts(args.filter)
        alerts = response['alerts']
        for i, alert in enumerate(alerts):
            pct = int(100.0 * i / total)
            sys.stdout.write("%3d%% (%d/%d)" % (pct, i, total))
            sys.stdout.flush()
            sys.stdout.write("\b" * (8 + len(str(i)) + len(str(total))))
            self.api.delete_alert(alert['id'])

        sys.stdout.write("100%% (%d/%d), done.\n" % (total, total))

    def _alerts(self, filter, from_date=None):

        query = dict([x.split('=', 1) for x in filter if '=' in x])

        if from_date:
            query['from-date'] = from_date

        if 'sort-by' not in query:
            query['sort-by'] = 'lastReceiveTime'

        try:
            response = self.api.get_alerts(**query)
        except Exception as e:
            LOG.error(e)
            sys.exit(1)

        if response['status'] == "error":
            LOG.error(response['message'])
            sys.exit(1)

        return response

    def _counts(self, filter, from_date=None):

        query = dict([x.split('=', 1) for x in filter if '=' in x])

        if from_date:
            query['from-date'] = from_date

        if 'sort-by' not in query:
            query['sort-by'] = 'lastReceiveTime'

        try:
            response = self.api.get_counts(**query)
        except Exception as e:
            LOG.error(e)
            sys.exit(1)

        if response['status'] == "error":
            LOG.error(response['message'])
            sys.exit(1)

        return response

    def _history(self, filter, from_date=None):

        query = dict([x.split('=', 1) for x in filter if '=' in x])

        if from_date:
            query['from-date'] = from_date

        try:
            response = self.api.get_history(**query)
        except Exception as e:
            LOG.error(e)
            sys.exit(1)

        if response['status'] == "error":
            LOG.error(response['message'])
            sys.exit(1)

        return response

    def help(self, args):

        pass

    def version(self, args):

        print 'alerta client %s' % __version__
        print 'requests %s' % requests.__version__


class AlertaShell(object):

    def main(self):

        global sources

        cli = AlertCommand()

        defaults = {
            'config_file': os.environ.get('ALERTA_CONF_FILE') or DEFAULT_CONF_FILE,
            'profile': os.environ.get('ALERTA_DEFAULT_PROFILE'),
        }

        sources = {
            'config_file': 'ALERTA_CONF_FILE' if os.environ.get('ALERTA_CONF_FILE') else '[system]',
            'profile': 'ALERTA_DEFAULT_PROFILE' if os.environ.get('ALERTA_DEFAULT_PROFILE') else '[none]',
        }

        config_file = defaults['config_file']
        config = ConfigParser.RawConfigParser(defaults=defaults)
        config.read(os.path.expanduser(config_file))

        default_section = dict(config.defaults())
        if 'endpoint' in default_section:
            sources['endpoint'] = '[DEFAULT]'
        if 'timezone' in default_section:
            sources['timezone'] = '[DEFAULT]'
        if 'output' in default_section:
            sources['output'] = '[DEFAULT]'
        if 'color' in default_section:
            sources['color'] = '[DEFAULT]'
        if 'debug' in default_section:
            sources['debug'] = '[DEFAULT]'

        profile_parser = argparse.ArgumentParser(
            add_help=False
        )
        profile_parser.add_argument(
            '--profile',
            default=defaults['profile'],
            help='Select profile to apply from %s' % defaults['config_file']
        )
        args, left = profile_parser.parse_known_args()

        if args.profile != defaults['profile']:
            defaults['profile'] = args.profile
            sources['profile'] = '--profile'

        if args.profile:
            for section in config.sections():
                if section.startswith('profile '):
                    if args.profile == section.replace('profile ', ''):
                        if config.has_option(section, 'endpoint'):
                            defaults['endpoint'] = config.get(section, 'endpoint')
                            sources['endpoint'] = '[profile %s]' % args.profile
                        else:
                            defaults['endpoint'] = DEFAULT_ENDPOINT_URL
                            sources['endpoint'] = '[system]'
                        if config.has_option(section, 'timezone'):
                            defaults['timezone'] = config.get(section, 'timezone')
                            sources['timezone'] = '[profile %s]' % args.profile
                        else:
                            defaults['timezone'] = DEFAULT_TIMEZONE
                            sources['timezone'] = '[system]'
                        if config.has_option(section, 'output'):
                            defaults['output'] = config.get(section, 'output')
                            sources['output'] = '[profile %s]' % args.profile
                        else:
                            defaults['output'] = DEFAULT_OUTPUT
                            sources['output'] = '[system]'
                        if config.has_option(section, 'color'):
                            defaults['color'] = bool(config.get(section, 'color'))
                            sources['color'] = '[profile %s]' % args.profile
                        else:
                            defaults['color'] = DEFAULT_COLOR
                            sources['color'] = '[system]'
                        if config.has_option(section, 'debug'):
                            defaults['debug'] = bool(config.get(section, 'debug'))
                            sources['debug'] = '[profile %s]' % args.profile
                        else:
                            defaults['debug'] = DEFAULT_DEBUG
                            sources['debug'] = '[system]'

        if os.environ.get('ALERTA_DEFAULT_ENDPOINT'):
            defaults['endpoint'] = os.environ.get('ALERTA_DEFAULT_ENDPOINT')
            sources['endpoint'] = 'ALERTA_DEFAULT_ENDPOINT'
        elif 'endpoint' not in defaults:
            defaults['endpoint'] = DEFAULT_ENDPOINT_URL
            sources['endpoint'] = '[system]'

        if 'timezone' not in defaults:
            defaults['timezone'] = DEFAULT_TIMEZONE
            sources['timezone'] = '[system]'

        if 'output' not in defaults:
            defaults['output'] = DEFAULT_OUTPUT
            sources['output'] = '[system]'

        if os.environ.get('CLICOLOR'):
            defaults['color'] = True
            sources['color'] = 'CLICOLOR'
        elif 'color' not in defaults:
            defaults['color'] = DEFAULT_COLOR
            sources['color'] = '[system]'

        if 'debug' not in defaults:
            defaults['debug'] = DEFAULT_DEBUG
            sources['debug'] = '[system]'

        parser = argparse.ArgumentParser(
            prog='alerta',
            usage='alerta [OPTIONS] COMMAND [FILTERS]',
            description="Alerta client unified command-line tool",
            epilog='Filters:\n'
                   '    Query parameters can be used to filter alerts by any valid alert attribute\n\n'
                   '    resource=web01     Show alerts with resource equal to "web01"\n'
                   '    resource!=web01    Show all alerts except those with resource of "web01"\n'
                   '    event=~down        Show alerts that include "down" in event name\n'
                   '    event!=~down       Show all alerts that don\'t have "down" in event name\n\n'
                   '    Special query parameters include "limit", "sort-by", "from-date" and "q" (a\n'
                   '    json-compliant mongo query).\n',
            formatter_class=argparse.RawTextHelpFormatter,
            parents=[profile_parser]
        )
        parser.set_defaults(**defaults)
        parser.add_argument(
            '--endpoint-url',
            default=defaults['endpoint'],
            dest='endpoint',
            metavar='URL',
            help='API endpoint URL'
        )
        parser.add_argument(
            '--output',
            default=defaults['output'],
            help='Output format of "text" or "json"'
        )
        parser.add_argument(
            '--json',
            '-j',
            action='store_true',
            help='Output in JSON format. Shortcut for "--output json"'
        )
        parser.add_argument(
            '--color',
            '--colour',
            action='store_true',
            default=defaults['color'],
            help='Color-coded output based on severity'
        )
        parser.add_argument(
            '--no-color',
            '--no-colour',
            action='store_false',
            default=defaults['color'],
            dest='color',
            help=argparse.SUPPRESS
        )
        parser.add_argument(
            '--debug',
            action='store_true',
            help='Print debug output'
        )
        subparsers = parser.add_subparsers(
            title='Commands',
        )

        parser_send = subparsers.add_parser(
            'send',
            help='Send alert to server',
            usage='alerta [OPTIONS] send [-h] [-r RESOURCE] [-e EVENT] [-E ENVIRONMENT]\n'
                '                             [-s SEVERITY] [-C CORRELATE] [--status STATUS]\n'
                '                             [-S SERVICE] [-g GROUP] [-v VALUE] [-t TEXT]\n'
                '                             [-T TAG] [-A ATTRIBUTES] [-O ORIGIN]\n'
                '                             [--type EVENT_TYPE] [--timeout TIMEOUT]\n'
                '                             [--raw-data RAW_DATA]\n'
        )
        parser_send.add_argument(
            '-r',
            '--resource',
            help='resource under alarm'
        )
        parser_send.add_argument(
            '-e',
            '--event',
            help='event'
        )
        parser_send.add_argument(
            '-E',
            '--environment',
            help='environment eg. "production", "development", "testing"'
        )
        parser_send.add_argument(
            '-s',
            '--severity',
            help='severity'
        )
        parser_send.add_argument(
            '-C',
            '--correlate',
            action='append',
            help='correlate'
        )
        parser_send.add_argument(
            '--status',
            help='status should not normally be defined as it is server-assigned eg. "open", "closed"'
        )
        parser_send.add_argument(
            '-S',
            '--service',
            action='append',
            help='service affected eg. the application name, "Web", "Network", "Storage", "Database", "Security"'
        )
        parser_send.add_argument(
            '-g',
            '--group',
            help='group'
        )
        parser_send.add_argument(
            '-v',
            '--value',
            help='value'
        )
        parser_send.add_argument(
            '-t',
            '--text',
            help='Freeform alert text eg. "Host not responding to ping."'
        )
        parser_send.add_argument(
            '-T',
            '--tag',
            metavar='TAG',
            action='append',
            dest='tags',
            default=list(),
            help='List of tags eg. "London", "os:linux", "AWS/EC2".'
        )
        parser_send.add_argument(
            '-A',
            '--attribute',
            action='append',
            dest='attributes',
            default=list(),
            help='List of Key=Value attribute pairs eg. "priority=high", "moreInfo=..."'
        )
        parser_send.add_argument(
            '-O',
            '--origin',
            default=None,
            help='Origin of alert. Usually in form of "app/host"'
        )
        parser_send.add_argument(
            '--type',
            dest='event_type',
            default='exceptionAlert',
            help='event type eg. "exceptionAlert", "serviceAlert"'
        )
        parser_send.add_argument(
            '--timeout',
            default=None,
            help='Timeout in seconds before an "open" alert will be automatically "expired" or "deleted"'
        )
        parser_send.add_argument(
            '--raw-data',
            default=None,
            help='raw data'
        )
        parser_send.set_defaults(func=cli.send)

        parser_query = subparsers.add_parser(
            'query',
            help='List alerts based on query filter',
            usage='alerta [OPTIONS] query [-h] [FILTERS]'
        )
        parser_query.add_argument(
            '--details',
            action='store_true',
            help='Show alert details'
        )
        parser_query.add_argument(
            'filter',
            nargs='*',
            help='KEY=VALUE eg. id=5108bc20'
        )
        parser_query.set_defaults(func=cli.query)

        parser_watch = subparsers.add_parser(
            'watch',
            help='Watch alerts based on query filter',
            usage='alerta [OPTIONS] watch [-h] [FILTERS]'
        )
        parser_watch.add_argument(
            '--details',
            action='store_true',
            help='Show alert details'
        )
        parser_watch.add_argument(
            'filter',
            nargs='*',
            help='KEY=VALUE eg. id=5108bc20'
        )
        parser_watch.set_defaults(func=cli.watch)

        parser_raw = subparsers.add_parser(
            'raw',
            help='Show alert raw data',
            usage='alerta [OPTIONS] raw [-h] [FILTERS]'
        )
        parser_raw.add_argument(
            'filter',
            nargs='*',
            help='KEY=VALUE eg. id=5108bc20'
        )
        parser_raw.set_defaults(func=cli.raw)

        parser_history = subparsers.add_parser(
            'history',
            help='Show alert history',
            usage='alerta [OPTIONS] history [-h] [FILTERS]'
        )
        parser_history.add_argument(
            'filter',
            nargs='*',
            help='KEY=VALUE eg. id=5108bc20'
        )
        parser_history.set_defaults(func=cli.history)

        parser_tag = subparsers.add_parser(
            'tag',
            help='Tag alerts',
            usage='alerta [OPTIONS] tag [-h] [FILTERS]'
        )
        parser_tag.add_argument(
            '-T',
            '--tag',
            metavar='TAG',
            action='append',
            dest='tags',
            default=list(),
            help='List of tags eg. "London", "os:linux", "AWS/EC2".'
        )
        parser_tag.add_argument(
            'filter',
            nargs='*',
            help='KEY=VALUE eg. id=5108bc20'
        )
        parser_tag.set_defaults(func=cli.tag)

        parser_untag = subparsers.add_parser(
            'untag',
            help='Remove tags from alerts',
            usage='alerta [OPTIONS] untag [-h] [FILTERS]'
        )
        parser_untag.add_argument(
            '-T',
            '--tag',
            metavar='TAG',
            action='append',
            dest='tags',
            default=list(),
            help='List of tags eg. "London", "os:linux", "AWS/EC2".'
        )
        parser_untag.add_argument(
            'filter',
            nargs='*',
            help='KEY=VALUE eg. id=5108bc20'
        )
        parser_untag.set_defaults(func=cli.untag)

        parser_ack = subparsers.add_parser(
            'ack',
            help='Acknowledge alerts',
            usage='alerta [OPTIONS] ack [-h] [FILTERS]'
        )
        parser_ack.add_argument(
            'filter',
            nargs='*',
            help='KEY=VALUE eg. id=5108bc20'
        )
        parser_ack.set_defaults(func=cli.ack)

        parser_unack = subparsers.add_parser(
            'unack',
            help='Unacknowledge alerts',
            usage='alerta [OPTIONS] unack [-h] [FILTERS]'
        )
        parser_unack.add_argument(
            'filter',
            nargs='*',
            help='KEY=VALUE eg. id=5108bc20'
        )
        parser_unack.set_defaults(func=cli.unack)

        parser_close = subparsers.add_parser(
            'close',
            help='Close alerts',
            usage='alerta [OPTIONS] close [-h] [FILTERS]'
        )
        parser_close.add_argument(
            'filter',
            nargs='*',
            help='KEY=VALUE eg. id=5108bc20'
        )
        parser_close.set_defaults(func=cli.close)

        parser_delete = subparsers.add_parser(
            'delete',
            help='Delete alerts',
            usage='alerta [OPTIONS] delete [-h] [FILTERS]'
        )
        parser_delete.add_argument(
            'filter',
            nargs='*',
            help='KEY=VALUE eg. id=5108bc20'
        )
        parser_delete.set_defaults(func=cli.delete)

        parser_heartbeat = subparsers.add_parser(
            'heartbeat',
            help='Send heartbeat to server',
            usage='alerta [OPTIONS] heartbeat [-h] [-T TAG] [-O ORIGIN] [--timeout TIMEOUT]'
        )
        parser_heartbeat.add_argument(
            '-T',
            '--tag',
            metavar='TAG',
            action='append',
            dest='tags',
            default=list(),
            help='List of tags eg. "London", "os:linux", "AWS/EC2".'
        )
        parser_heartbeat.add_argument(
            '-O',
            '--origin',
            default=None,
            help='Origin of heartbeat. Usually in form of "app/host"'
        )
        parser_heartbeat.add_argument(
            '--timeout',
            default=None,
            help='Timeout in seconds before a heartbeat will be considered stale'
        )
        parser_heartbeat.set_defaults(func=cli.heartbeat)

        parser_config = subparsers.add_parser(
            'config',
            help='Show config',
            add_help=False
        )
        parser_config.set_defaults(func=cli.config)

        parser_help = subparsers.add_parser(
            'help',
            help='Show help',
            add_help=False
        )
        parser_help.set_defaults(func=cli.help)

        parser_version = subparsers.add_parser(
            'version',
            help='Show alerta version info',
            add_help=False
        )
        parser_version.set_defaults(func=cli.version)

        args = parser.parse_args(left)

        args.output = 'json' if args.json else args.output

        if args.func == cli.help:
            parser.print_help()
            sys.exit(0)

        if args.debug:
            root.setLevel(logging.DEBUG)
            LOG.setLevel(logging.DEBUG)
            LOG.debug("Alerta cli version: %s", __version__)
        else:
            root.setLevel(logging.ERROR)
            LOG.setLevel(logging.ERROR)

        if args.endpoint != defaults['endpoint']:
            sources['endpoint'] = '--endpoint'
        if args.output != defaults['output']:
            sources['output'] = '--output'
        if args.color != defaults['color']:
            sources['color'] = '--color'
        if args.debug != defaults['debug']:
            sources['debug'] = '--debug'

        cli.set_api(url=args.endpoint)

        args.func(args)


def main():

    logging.basicConfig(format="%(asctime)s - %(name)s - %(levelname)s - %(message)s")

    try:
        AlertaShell().main()
    except Exception as e:
        LOG.error(e, exc_info=1)
        sys.exit(1)
    except KeyboardInterrupt as e:
        LOG.warning("Exiting alerta client.")
        sys.exit(1)

if __name__ == "__main__":
    main()
