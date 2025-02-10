import logging

import locust


class ArpavPpcvUser(locust.FastHttpUser):
    wait_time = locust.between(1, 5)

    @locust.task
    def coverage_configurations(self):
        self.client.get("/api/v2/coverages/coverage-configurations")

    @locust.task
    def configuration_parameters(self):
        self.client.get("/api/v2/coverages/configuration-parameters")

    @locust.task
    def coverage_identifiers(self):
        self.client.get("/api/v2/coverages/coverage-identifiers")

    @locust.task
    def stations(self):
        self.client.get("/api/v2/observations/stations")

    @locust.task
    def variables(self):
        self.client.get("/api/v2/observations/variables")


@locust.events.quitting.add_listener
def _(environment, **kwargs):
    if environment.stats.total.fail_ratio > 0.01:
        logging.error("Test failed due to failure ratio > 1%")
        environment.process_exit_code = 1
    elif environment.stats.total.avg_response_time > 1000:
        logging.error("Test failed due to average response time ratio > 1000 ms")
        environment.process_exit_code = 1
    elif environment.stats.total.get_response_time_percentile(0.95) > 5000:
        logging.error("Test failed due to 95th percentile response time > 5000 ms")
        environment.process_exit_code = 1
    else:
        environment.process_exit_code = 0
