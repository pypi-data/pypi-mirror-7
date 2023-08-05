# -*- coding: utf-8 -*-
from __future__ import unicode_literals
from json import loads

from github3.models import GitHubCore
from github3.users import User


class Deployment(GitHubCore):
    CUSTOM_HEADERS = {
        'Accept': 'application/vnd.github.cannonball-preview+json'
        }

    def __init__(self, deployment, session=None):
        super(Deployment, self).__init__(deployment, session)
        self._api = deployment.get('url')

        #: GitHub's id of this deployment
        self.id = deployment.get('id')

        #: SHA of the branch on GitHub
        self.sha = deployment.get('sha')

        #: User object representing the creator of the deployment
        self.creator = deployment.get('creator')
        if self.creator:
            self.creator = User(self.creator, self)

        #: JSON string payload of the Deployment
        self.payload = deployment.get('payload')

        #: Date the Deployment was created
        self.created_at = self._strptime(deployment.get('created_at'))

        #: Date the Deployment was updated
        self.updated_at = self._strptime(deployment.get('updated_at'))

        #: Description of the deployment
        self.description = deployment.get('description')

        #: URL to get the statuses of this deployment
        self.statuses_url = deployment.get('statuses_url')

    def _repr(self):
        return '<Deployment [{0} @ {1}]>'.format(self.id, self.sha)

    def create_status(self, state, target_url='', description=''):
        """Create a new deployment status for this deployment.

        :param str state: (required), The state of the status. Can be one of
            ``pending``, ``success``, ``error``, or ``failure``.
        :param str target_url: The target URL to associate with this status.
            This URL should contain output to keep the user updated while the
            task is running or serve as historical information for what
            happened in the deployment. Default: ''.
        :param str description: A short description of the status. Default: ''.
        :return: partial :class:`DeploymentStatus <DeploymentStatus>`
        """
        json = None

        if state in ('pending', 'success', 'error', 'failure'):
            data = {'state': state, 'target_url': target_url,
                    'description': description}
            response = self._post(self.statuses_url, data=data,
                                  headers=Deployment.CUSTOM_HEADERS)
            json = self._json(response, 201)

        return DeploymentStatus(json, self) if json else None

    def iter_statuses(self, number=-1, etag=None):
        """Iterate over the deployment statuses for this deployment.

        :param int number: (optional), the number of statuses to return.
            Default: -1, returns all statuses.
        :param str etag: (optional), the ETag header value from the last time
            you iterated over the statuses.
        :returns: generator of :class:`DeploymentStatus`\ es
        """
        i = self._iter(int(number), self.statuses_url, DeploymentStatus,
                       etag=etag)
        i.headers = Deployment.CUSTOM_HEADERS
        return i


class DeploymentStatus(GitHubCore):
    def __init__(self, status, session=None):
        super(DeploymentStatus, self).__init__(status, session)
        self._api = status.get('url')

        #: GitHub's id for this deployment status
        self.id = status.get('id')

        #: State of the deployment status
        self.state = status.get('state')

        #: Creater of the deployment status
        self.creator = status.get('creator')
        if self.creator:
            self.creator = User(self.creator, self)

        #: JSON payload as a string
        self.payload = status.get('payload', {})

        #: Target URL of the deployment
        self.target_url = status.get('target_url')

        #: Date the deployment status was created
        self.created_at = self._strptime(status.get('created_at'))

        #: Date the deployment status was updated
        self.updated_at = self._strptime(status.get('updated_at'))

        #: Description of the deployment
        self.description = status.get('description')

    def _repr(self):
        return '<DeploymentStatus [{0}]>'.format(self.id)
