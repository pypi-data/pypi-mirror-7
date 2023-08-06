import logging
import argh

logger = logging.getLogger('giza.operations.deploy')

from giza.command import verbose_command
from giza.app import BuildApp
from giza.deploy import Deploy
from giza.config.helper import fetch_config
from giza.serialization import ingest_yaml_list, dict_from_list

@argh.arg('--target', '-t', nargs='*', dest='push_targets')
def push(args):
    c = fetch_config(args)
    app = BuildApp(c)

    pconf = c.system.files.data.push
    pconf = dict_from_list('target', pconf)

    for target in c.runstate.push_targets:
        d = Deploy(c)

        target_pconf = pconf[target]

        if target_pconf['env'] == 'publication':
            target_pconf['env'] = 'production'

        d.load(target_pconf)

        map_task = app.add('map')
        map_task.iter = d.deploy_commands()

        map_task.job = verbose_command

    app.run()
