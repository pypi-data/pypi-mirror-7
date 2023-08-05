# -*- coding: utf-8 -*-
import MySQLdb
import logging
from system.models import Configuration
from django.db import transaction
import re
from models import EnvironmentAttr, DatabaseInfraAttr

LOG = logging.getLogger(__name__)

SGBD_MYSQL = 'M'
SGBD_MONGODB = 'G'


class DBMonitorProvider(object):
    
    @classmethod
    def get_credentials(self, environment):
        LOG.info("Getting credentials...")
        from dbaas_credentials.credential import Credential
        from dbaas_credentials.models import CredentialType
        integration = CredentialType.objects.get(type= CredentialType.DBMONITOR)
        return Credential.get_credentials(environment= environment, integration= integration)

    @classmethod
    def auth(self, environment):
        try:
            LOG.info("Conecting with dbmonitor...")
            credentials = self.get_credentials(environment= environment)
            self.DECODE_KEY = credentials.secret
            endpoint, database = credentials.endpoint.split('/')
            host, port = endpoint.split(':')
            connection_timeout_in_seconds = Configuration.get_by_name_as_int('mysql_connect_timeout', default=5)
            self.client = MySQLdb.connect(host=host, port=int(port),
                                     user=credentials.user, passwd=credentials.password,
                                     db=database, connect_timeout=connection_timeout_in_seconds)
            LOG.debug('Successfully connected to mysql %s' % (credentials.endpoint))
        except Exception, e:
            LOG.error(str(e))
            raise e

    @classmethod
    @transaction.commit_on_success
    def create_dbmonitor_monitoring(self, databaseinfra):
        
        LOG.info('Creating monitoring on DBMonitor')
        environment = databaseinfra.environment
        instances = databaseinfra.instances.all()
        if len(instances) == 1:
            flag_cluster_str = 'false'
            flag_cluster = False
            machine = instances[0].hostname
        else:
            flag_cluster_str = 'true'
            flag_cluster = True
            machine = ''
        driver_name = databaseinfra.engine.engine_type.name.lower()
        if re.match(r'^mongo.*', driver_name):
            sgbd = SGBD_MONGODB
        elif re.match(r'^mysql.*', driver_name):
            sgbd = SGBD_MYSQL
        else:
            LOG.error('Not implemented engine type')
            raise NotImplementedError()
        dns, port = databaseinfra.endpoint_dns.split(':')
        self.auth(environment)
        
        tipo = EnvironmentAttr.objects.get(dbaas_environment=environment).dbmonitor_environment
        
        sql = """INSERT INTO dbmonitor_database ( nome, maquina, sgbd, tipo, dns, porta, versao, usuario, senha,
                             ativo, flag_cluster, coleta_info_sessoes, coleta_info_tablespaces, coleta_info_segmentos,
                             coleta_info_backup, coleta_info_key_buffer, testa_conexao, coleta_tamanho_database,
                             flag_autenticacao, testa_replicacao )
                 VALUES (
                 '%(nome)s', '%(maquina)s', '%(sgbd)s', '%(tipo)s', '%(dns)s', '%(porta)s', '%(versao)s', '%(usuario)s', 
                 encode('%(senha)s', '%(decodekey)s'), 
                 %(ativo)s, %(flag_cluster)s, %(coleta_info_sessoes)s, %(coleta_info_tablespaces)s, %(coleta_info_segmentos)s,
                 %(coleta_info_backup)s, %(coleta_info_key_buffer)s, %(testa_conexao)s, %(coleta_tamanho_database)s,
                 %(flag_autenticacao)s, %(testa_replicacao)s
                 )
        """ % {
        'nome': databaseinfra.name[:50],
        'maquina': machine,
        'sgbd': sgbd,
        'tipo': tipo,
        'dns': dns,
        'porta': port,
        'versao': databaseinfra.engine.version,
        'usuario': databaseinfra.user,
        'senha': databaseinfra.password,
        'decodekey': self.DECODE_KEY,
        'ativo': 'true',
        'flag_cluster': flag_cluster_str,
        'coleta_info_sessoes': 'true',
        'coleta_info_tablespaces': 'false',
        'coleta_info_segmentos': 'false',
        'coleta_info_backup': 'false',
        'coleta_info_key_buffer': 'false',
        'testa_conexao': 'true',
        'coleta_tamanho_database': 'true',
        'flag_autenticacao': 'false',
        'testa_replicacao': 'false',
        }
        
        try:
            cursor = self.client.cursor()
            cursor.execute(sql)
            dbmonitor_infraid = self.client.insert_id()

            if flag_cluster:
                cont = 0
                for instance in instances:
                    cont+=1
                    sql2 = """INSERT INTO dbmonitor_instancia (database_id, nome, maquina, dns, porta, ativo)
                              VALUES (%(database_id)s, '%(nome)s', '%(maquina)s', '%(dns)s', '%(porta)s', %(ativo)s)
                    """ % {
                    'database_id': dbmonitor_infraid,
                    'nome': databaseinfra.name[:48]+ '-' + str(cont),
                    'maquina': instance.hostname,
                    'dns': instance.dns,
                    'porta': instance.port,
                    'ativo': 'true',
                    }
                    cursor.execute(sql2)
            self.client.commit()
            dbinfraattr = DatabaseInfraAttr(dbaas_databaseinfra = databaseinfra, dbmonitor_databaseinfra = dbmonitor_infraid)
            dbinfraattr.save()
            LOG.info('Monitoring in DBMonitor successfully created')
        except Exception, e:
            LOG.error(str(e))
            raise e
        
        
    @classmethod
    @transaction.commit_on_success
    def remove_dbmonitor_monitoring(self, databaseinfra):
        
        LOG.info('Removing monitoring on DBMonitor')
        
        try:
            self.auth(databaseinfra.environment)
            infraattr = DatabaseInfraAttr.objects.get(dbaas_databaseinfra=databaseinfra)
        
            cursor = self.client.cursor()
            sql = "UPDATE dbmonitor_database SET ativo = false WHERE id = %s" % (infraattr.dbmonitor_databaseinfra)
            cursor.execute(sql)
            sql = "UPDATE dbmonitor_instancia SET ativo = false WHERE database_id = %s" % (infraattr.dbmonitor_databaseinfra)
            cursor.execute(sql)
            self.client.commit()
            
            infraattr.delete()
            LOG.info('Monitoring in DBMonitor successfully removed')
            
        except Exception, e:
            LOG.error(str(e))
            raise e
