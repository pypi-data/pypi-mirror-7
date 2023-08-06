# -*- coding: utf-8 -*-
from __future__ import unicode_literals
from .base import BaseYarnAPI
from .constants import YarnApplicationState, FinalApplicationStatus
from .errors import IllegalArgumentError
from .hadoop_conf import get_resource_manager_host_port


class ResourceManager(BaseYarnAPI):
    """
    The ResourceManager REST API's allow the user to get information about the
    cluster - status on the cluster, metrics on the cluster,
    scheduler information, information about nodes in the cluster,
    and information about applications on the cluster.
    """
    def __init__(self, address=None, port=8088, timeout=30):
        self.address, self.port, self.timeout = address, port, timeout
        if address is None:
            self.logger.debug('Get configuration from hadoop conf dir')
            address, port = get_resource_manager_host_port()
            self.address, self.port = address, port

    def cluster_information(self):
        """
        The cluster information resource provides overall information about
        the cluster.
        """
        path = '/ws/v1/cluster/info'
        return self.request(path)

    def cluster_metrics(self):
        """
        The cluster metrics resource provides some overall metrics about the
        cluster. More detailed metrics should be retrieved from the jmx
        interface.
        """
        path = '/ws/v1/cluster/metrics'
        return self.request(path)

    def cluster_scheduler(self):
        """
        A scheduler resource contains information about the current scheduler
        configured in a cluster. It currently supports both the Fifo and
        Capacity Scheduler. You will get different information depending on
        which scheduler is configured so be sure to look at the type
        information.
        """
        path = '/ws/v1/cluster/scheduler'
        return self.request(path)

    def cluster_applications(self, state=None, final_status=None,
                             user=None, queue=None, limit=None,
                             started_time_begin=None, started_time_end=None,
                             finished_time_begin=None, finished_time_end=None):
        """
        With the Applications API, you can obtain a collection of resources,
        each of which represents an application.
        """
        path = '/ws/v1/cluster/apps'

        legal_states = set([s for s, _ in YarnApplicationState])
        if state is not None and state not in legal_states:
            msg = 'Yarn Application State %s is illegal' % (state,)
            raise IllegalArgumentError(msg)

        legal_final_statuses = set([s for s, _ in FinalApplicationStatus])
        if final_status is not None and final_status not in legal_final_statuses:
            msg = 'Final Application Status %s is illegal' % (final_status,)
            raise IllegalArgumentError(msg)

        loc_args = (
            ('state', state),
            ('finalStatus', final_status),
            ('user', user),
            ('queue', queue),
            ('limit', limit),
            ('startedTimeBegin', started_time_begin),
            ('startedTimeEnd', started_time_end),
            ('finishedTimeBegin', finished_time_begin),
            ('finishedTimeEnd', finished_time_end))

        params = self.construct_parameters(loc_args)

        return self.request(path, **params)

    def cluster_application_statistics(self, state_list=None,
                                       application_type_list=None):
        """
        With the Application Statistics API, you can obtain a collection of
        triples, each of which contains the application type, the application
        state and the number of applications of this type and this state in
        ResourceManager context.

        This method work in Hadoop > 2.0.0
        """
        path = '/ws/v1/cluster/appstatistics'

        # TODO: validate state argument
        states = ','.join(state_list) if state_list is not None else None
        if application_type_list is not None:
            applicationTypes = ','.join(application_type_list)
        else:
            applicationTypes = None

        loc_args = (
            ('states', states),
            ('applicationTypes', applicationTypes))
        params = self.construct_parameters(loc_args)

        return self.request(path, **params)

    def cluster_application(self, application_id):
        """
        An application resource contains information about a particular
        application that was submitted to a cluster.
        """
        path = '/ws/v1/cluster/apps/{appid}'.format(appid=application_id)

        return self.request(path)

    def cluster_application_attempts(self, application_id):
        """
        With the application attempts API, you can obtain a collection of
        resources that represent an application attempt.
        """
        path = '/ws/v1/cluster/apps/{appid}/appattempts'.format(
            appid=application_id)

        return self.request(path)

    def cluster_nodes(self, state=None, healthy=None):
        """
        With the Nodes API, you can obtain a collection of resources, each of
        which represents a node.
        """
        path = '/ws/v1/cluster/nodes'
        # TODO: validate state argument

        legal_healthy = ['true', 'false']
        if healthy is not None and healthy not in legal_healthy:
            msg = 'Valid Healthy arguments are true, false'
            raise IllegalArgumentError(msg)

        loc_args = (
            ('state', state),
            ('healthy', healthy),
        )
        params = self.construct_parameters(loc_args)

        return self.request(path, **params)

    def cluster_node(self, node_id):
        """
        A node resource contains information about a node in the cluster.
        """
        path = '/ws/v1/cluster/nodes/{nodeid}'.format(nodeid=node_id)

        return self.request(path)
