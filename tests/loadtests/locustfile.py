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


@locust.events.quitting.add_listener
def _(environment, **kwargs):
    max_avg_response_time_ms = 10_000
    ninety_fifth_percentile_response_time_ms = 20_000
    if environment.stats.total.fail_ratio > 0.01:
        logging.error("Test failed due to failure ratio > 1%")
        environment.process_exit_code = 1
    elif environment.stats.total.avg_response_time > max_avg_response_time_ms:
        logging.error(
            f"Test failed due to average response time "
            f"ratio > {max_avg_response_time_ms} ms"
        )
        environment.process_exit_code = 1
    elif (
        environment.stats.total.get_response_time_percentile(0.95)
        > ninety_fifth_percentile_response_time_ms
    ):
        logging.error(
            f"Test failed due to 95th percentile response "
            f"time > {ninety_fifth_percentile_response_time_ms} ms"
        )
        environment.process_exit_code = 1
    else:
        environment.process_exit_code = 0
