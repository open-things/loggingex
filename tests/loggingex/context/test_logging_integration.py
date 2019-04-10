import logging
import queue
import threading
import time

from pytest import fixture

from loggingex.context import LoggingContextFilter, context
from .helpers import InitializedContextBase


class SimpleLoggingTests(InitializedContextBase):
    @fixture(autouse=True)
    def logging_context_of_the_test(self, request, initialized_context):
        with context(test=request.node.name):
            yield

    @fixture()
    def logging_context_filter(self, initialized_context):
        return LoggingContextFilter()

    @fixture()
    def logger_name(self, request):
        return "test.%s" % request.node.name

    @fixture(autouse=True)
    def logger(self, caplog, logging_context_filter, logger_name):
        logger = logging.getLogger(logger_name)
        logger.addFilter(logging_context_filter)
        with caplog.at_level(logging.DEBUG, logger_name):
            yield logger
        logger.removeFilter(logging_context_filter)

    def log_some_messages(self, logger_name):
        logger = logging.getLogger(logger_name)
        logger.info("outside message #%d", 1)
        with context(scope="outer"):
            logger.info("message in outer scope #%d", 1)
            for i in range(1, 3):
                with context(scope="inner", num=i):
                    logger.info("message in inner scope #%d", i)
            logger.info("message in outer scope #%d", 2)
        logger.info("outside message #%d", 2)

        expected_output = [
            ("outside message #1", {}),
            ("message in outer scope #1", {"scope": "outer"}),
            ("message in inner scope #1", {"scope": "inner", "num": 1}),
            ("message in inner scope #2", {"scope": "inner", "num": 2}),
            ("message in outer scope #2", {"scope": "outer"}),
            ("outside message #2", {}),
        ]
        return expected_output

    def test_correct_context_is_added_to_log_records(self, caplog, logger_name):
        expected = self.log_some_messages(logger_name)
        records = caplog.records
        assert len(records) == len(expected)
        for record, (message, extras) in zip(records, expected):
            assert record.name == logger_name
            assert record.message == message
            for k, v in extras.items():
                assert getattr(record, k, "undefined") == v


class MultiThreadedLoggingTests(InitializedContextBase):
    @fixture(autouse=True)
    def logging_context_of_the_test(self, request, initialized_context):
        with context(test=request.node.name):
            yield

    @fixture()
    def logging_context_filter(self, initialized_context):
        return LoggingContextFilter()

    @fixture()
    def logger_name(self, request):
        return "test.%s" % request.node.name

    @fixture(autouse=True)
    def logger(self, caplog, logging_context_filter, logger_name):
        logger = logging.getLogger(logger_name)
        logger.addFilter(logging_context_filter)
        with caplog.at_level(logging.DEBUG, logger_name):
            yield logger
        logger.removeFilter(logging_context_filter)

    def log_some_messages(self, logger_name, q):
        thread = threading.get_ident()
        logger = logging.getLogger(logger_name)
        with context(thread=thread):
            logger.info("[thread=%r] outside message #%d", thread, 1)
            q.put(
                ("[thread=%r] outside message #1" % thread, {"thread": thread})
            )
            time.sleep(0.1)
            for i in range(1, 3):
                with context(scope="inner", num=i):
                    logger.info(
                        "[thread=%r] message in inner scope #%d", thread, i
                    )
                    q.put(
                        (
                            "[thread=%r] message in inner scope #%d"
                            % (thread, i),
                            {"thread": thread, "scope": "inner", "num": i},
                        )
                    )
                    time.sleep(0.1)
            logger.info("[thread=%r] outside message #%d", thread, 2)
            q.put(
                ("[thread=%r] outside message #2" % thread, {"thread": thread})
            )

    def create_threads(self, logger_name, q, num=2):
        threads = []
        for i in range(num):
            thread = threading.Thread(
                target=self.log_some_messages,
                args=(logger_name, q),
                name="t_%d" % (i + 1),
            )
            threads.append(thread)
        return threads

    def run_threads_to_completion(self, threads):
        # start all threads
        for t in threads:
            t.start()

        # wait for all threads to complete
        for t in threads:
            t.join()

    def get_expected_messages(self, q):
        # put a dummy end mark in the queue
        q.put(None)

        # retrieve expected messages from queue
        expected_messages = []
        msg = q.get()
        while msg is not None:
            expected_messages.append(msg)
            msg = q.get()

        return expected_messages

    def test_threads_do_not_mix_their_contexts(self, caplog, logger_name):
        q = queue.Queue(maxsize=1000)
        threads = self.create_threads(logger_name, q)
        self.run_threads_to_completion(threads)

        expected = self.get_expected_messages(q)
        records = caplog.records
        assert len(records) == len(expected)

        # note: we can not reliably guess the message order, but we know that
        # thread id is part of the message, so this should be good enough
        expected = sorted(expected, key=lambda o: o[0])
        records = sorted(records, key=lambda o: o.message)
        for record, (message, extras) in zip(records, expected):
            assert record.name == logger_name
            assert record.message == message
            for k, v in extras.items():
                assert getattr(record, k, "undefined") == v
