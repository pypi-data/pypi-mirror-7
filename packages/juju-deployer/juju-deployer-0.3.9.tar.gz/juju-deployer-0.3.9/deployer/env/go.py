import errno
import os
import socket
import time

from .base import BaseEnvironment
from ..utils import ErrorExit, _get_juju_home, yaml_load

from jujuclient import (
    EnvError,
    Environment as EnvironmentClient,
    UnitErrors,
)

from .watchers import (
    raise_on_errors,
    WaitForMachineTermination,
    WaitForUnits,
)


class GoEnvironment(BaseEnvironment):

    def __init__(self, name, options=None, endpoint=None):
        self.name = name
        self.options = options
        self.api_endpoint = endpoint
        self.client = None

    def _get_token(self):
        home = _get_juju_home()
        jenv = os.path.join(
            home, 'environments', '%s.jenv' % self.name)
        if not os.path.exists(jenv):
            with open(os.path.join(home, 'environments.yaml')) as fh:
                data = yaml_load(fh.read())
                token = data.get('environments', {}).get(self.name, {}).get(
                    'admin-secret')
                if token is None:
                    raise EnvError(
                        {'Error': "Environment config not found %s" % self.name
                         })
                return token
        with open(jenv) as fh:
            data = yaml_load(fh.read())
            token = data.get('bootstrap-config', {}).get(
                'admin-secret')
            if token is None:
                raise EnvError("Could not find admin-secret for environment")
        return token

    def add_unit(self, service_name, machine_spec):
        return self.client.add_unit(service_name, machine_spec)

    def add_units(self, service_name, num_units):
        return self.client.add_units(service_name, num_units)

    def add_relation(self, endpoint_a, endpoint_b):
        return self.client.add_relation(endpoint_a, endpoint_b)

    def close(self):
        if self.client:
            self.client.close()

    def connect(self):
        if not self.api_endpoint:
            # Should really have a cheaper/faster way of getting the endpoint
            # ala juju status 0 for a get_endpoint method.
            self.get_cli_status()
        while True:
            try:
                self.client = EnvironmentClient(self.api_endpoint)
            except socket.error as err:
                if not err.errno in (
                        errno.ETIMEDOUT, errno.ECONNREFUSED, errno.ECONNRESET):
                    raise
                time.sleep(1)
                continue
            else:
                break
        self.client.login(self._get_token())
        self.log.debug("Connected to environment")

    def get_config(self, svc_name):
        return self.client.get_config(svc_name)

    def get_constraints(self, svc_name):
        try:
            return self.client.get_constraints(svc_name)
        except EnvError as err:
            if 'constraints do not apply to subordinate services' in str(err):
                return {}
            raise

    def get_cli_status(self):
        status = super(GoEnvironment, self).get_cli_status()
        # Opportunistic, see connect method comment.
        if not self.api_endpoint:
            self.api_endpoint = "wss://%s:17070/" % (
                status["machines"]["0"]["dns-name"])
        return status

    def expose(self, name):
        return self.client.expose(name)

    def reset(self,
              terminate_machines=False,
              terminate_delay=0,
              timeout=360, watch=False):
        """Destroy/reset the environment."""
        status = self.status()
        destroyed = False
        for s in status.get('services', {}).keys():
            self.log.debug(" Destroying service %s", s)
            self.client.destroy_service(s)
            destroyed = True

        if destroyed:
            # Mark any errors as resolved so destruction can proceed.
            self.resolve_errors()

            # Wait for units
            self.wait_for_units(timeout, goal_state='removed', watch=watch)

        # The only value to not terminating is keeping the data on the
        # machines around.
        if not terminate_machines:
            self.log.info(
                " warning: juju-core machines are not reusable for units")
            return
        self._terminate_machines(status, watch, terminate_delay)

    def _terminate_machines(self, status, watch, terminate_wait):
        """Terminate all machines, optionally wait for termination.
        """
        # Terminate machines
        self.log.debug(" Terminating machines")

        # Don't bother if there are no service unit machines
        if len(status['machines']) == 1:
            return

        # containers before machines, container hosts post wait.
        machines = status['machines'].keys()

        container_hosts = set()
        containers = set()

        def machine_sort(x, y):
            for ctype in ('lxc', 'kvm'):
                for m in (x, y):
                    if ctype in m:
                        container_hosts.add(m.split('/', 1)[0])
                        containers.add(m)
                        if m == x:
                            return -1
                        if m == y:
                            return 1
            return cmp(x, y)

        machines.sort(machine_sort)

        for mid in machines:
            self._terminate_machine(mid, container_hosts)

        if containers:
            watch = self.client.get_watch(120)
            WaitForMachineTermination(
                watch, containers).run(self._delta_event_log)

        for mid in container_hosts:
            self._terminate_machine(mid)

        if terminate_wait:
            self.log.info("  Waiting for machine termination")
            callback = watch and self._delta_event_log or None
            self.client.wait_for_no_machines(None, callback)

    def _terminate_machine(self, mid, container_hosts=()):
        if mid == "0":
            return
        if mid in container_hosts:
            return
        self.log.debug("  Terminating machine %s", mid)
        self.terminate_machine(mid)

    def _check_timeout(self, etime):
        w_timeout = etime - time.time()
        if w_timeout < 0:
            self.log.error("Timeout reached while resolving errors")
            raise ErrorExit()
        return w_timeout

    def resolve_errors(self, retry_count=0, timeout=600, watch=False, delay=5):
        """Resolve any unit errors in the environment.

        If retry_count is given then the hook execution is reattempted. The
        system will do up to retry_count passes through the system resolving
        errors.

        If retry count is not given, the error is marked resolved permanently.
        """
        etime = time.time() + timeout
        count = 0
        while True:
            error_units = self._get_units_in_error()
            for e_uid in error_units:
                try:
                    self.client.resolved(e_uid, retry=bool(retry_count))
                    self.log.debug("  Resolving error on %s", e_uid)
                except EnvError as err:
                    if 'already resolved' in err:
                        continue

            if not error_units:
                if not count:
                    self.log.debug("  No unit errors found.")
                else:
                    self.log.debug("  No more unit errors found.")
                return

            w_timeout = self._check_timeout(etime)
            if retry_count:
                time.sleep(delay)

            count += 1
            try:
                self.wait_for_units(
                    timeout=int(w_timeout), watch=True,
                    on_errors=raise_on_errors(UnitErrors))
            except UnitErrors as err:
                if retry_count == count:
                    self.log.info(
                        " Retry count %d exhausted, but units in error (%s)",
                        retry_count, " ".join(u['Name'] for u in err.errors))
                    return
            else:
                return

    def set_annotation(self, svc_name, annotation):
        return self.client.set_annotation(svc_name, 'service', annotation)

    def status(self):
        return self.client.get_stat()

    def log_errors(self, errors):
        """Log the given unit errors.

        This can be used in the WaitForUnits error handling machinery, e.g.
        see deployer.watchers.log_on_errors.
        """
        messages = [
            'unit: {Name}: machine: {MachineId} agent-state: {Status} '
            'details: {StatusInfo}'.format(**error) for error in errors
        ]
        self.log.error(
            'The following units had errors:\n   {}'.format(
                '   \n'.join(messages)))

    def wait_for_units(
            self, timeout, goal_state="started", watch=False, services=None,
            on_errors=None):
        """Wait for units to reach a given condition."""
        callback = self._delta_event_log if watch else None
        watcher = self.client.get_watch(timeout)
        WaitForUnits(
            watcher, goal_state=goal_state,
            services=services, on_errors=on_errors).run(callback)

    def _delta_event_log(self, et, ct, d):
        # event type, change type, data
        name = d.get('Name', d.get('Id', 'unknown'))
        state = d.get('Status', d.get('Life', 'unknown'))
        if et == "relation":
            name = self._format_endpoints(d['Endpoints'])
            state = "created"
            if ct == "remove":
                state = "removed"
        self.log.debug(
            " Delta %s: %s %s:%s", et, name, ct, state)

    def _format_endpoints(self, eps):
        if len(eps) == 1:
            ep = eps.pop()
            return "[%s:%s:%s]" % (
                ep['ServiceName'],
                ep['Relation']['Name'],
                ep['Relation']['Role'])

        return "[%s:%s <-> %s:%s]" % (
            eps[0]['ServiceName'],
            eps[0]['Relation']['Name'],
            eps[1]['ServiceName'],
            eps[1]['Relation']['Name'])
