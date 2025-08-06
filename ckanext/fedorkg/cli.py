from logging import getLogger

import click
from ckanext.fedorkg.model import news as news_model

log = getLogger(__name__)


def get_commands():
    return [fedorkg]


@click.group('fedorkg', short_help='Perform FedORKG related actions')
def fedorkg():
    pass


@fedorkg.command()
def start():
    try:
        from ckanext.fedorkg.metadata.app import app as metadata_kg
        metadata_kg.run(port=9000, host='0.0.0.0')
        log.debug('The metadata server is now started.')
    except OSError as e:
        if e.errno == 98:
            log.warning('The metadata server could not be started since the port is already bound.')
            import requests
            response = requests.get('http://localhost:9000')
            if response.status_code == 200:
                result = response.text
                if result != 'Metadata KG':
                    raise OSError('Port 9000 bound by a different service.')
            else:
                raise OSError('Port 9000 bound by a different or unhealthy service.')
        else:
            raise e


@fedorkg.command(name='initdb')
def init_db():
    if news_model.news_table.exists():
        click.secho("FedORKG's news table already exists.", fg='green')
    else:
        news_model.news_table.create()
        click.secho("FedORKG's news table created.", fg='green')


@fedorkg.command()
def version():
    from DeTrusty import __version__ as detrusty_version
    from ckanext.fedorkg import __version__ as fedorkg_version
    click.echo(
        'FedORKG v{fedorkg_version} is powered by DeTrusty v{detrusty_version}'.format(fedorkg_version=fedorkg_version,
                                                                                       detrusty_version=detrusty_version))
