# test_sampling.py
# -*- coding: utf8 -*-
# vim:fileencoding=utf8 ai ts=4 sts=4 et sw=4
# Copyright 2009 SKA South Africa (http://ska.ac.za/)
# BSD license - see COPYING for details

"""Tests for the katcp.sampling module.
   """

import unittest2 as unittest
import threading
import time
import logging
import katcp
import mock
import Queue

from katcp.testutils import (
    TestLogHandler, DeviceTestSensor, start_thread_with_cleanup)
from katcp import sampling, Sensor

log_handler = TestLogHandler()
logging.getLogger("katcp").addHandler(log_handler)


class TestSampling(unittest.TestCase):

    def setUp(self):
        """Set up for test."""
        # test sensor
        self.sensor = DeviceTestSensor(
                Sensor.INTEGER, "an.int", "An integer.", "count",
                [-4, 3],
                timestamp=12345, status=Sensor.NOMINAL, value=3)

        # test callback
        def inform(sensor_name, timestamp, status, value):
            self.calls.append(sampling.format_inform_v5(
                sensor_name, timestamp, status, value) )

        self.calls = []
        self.inform = inform

    def test_sampling(self):
        """Test getting and setting the sampling."""
        s = self.sensor

        sampling.SampleNone(None, s)
        sampling.SampleAuto(None, s)
        sampling.SamplePeriod(None, s, 10)
        sampling.SampleEvent(None, s)
        sampling.SampleDifferential(None, s, 2)
        self.assertRaises(ValueError, sampling.SampleNone, None, s, "foo")
        self.assertRaises(ValueError, sampling.SampleAuto, None, s, "bar")
        self.assertRaises(ValueError, sampling.SamplePeriod, None, s)
        self.assertRaises(ValueError, sampling.SamplePeriod, None, s, "0")
        self.assertRaises(ValueError, sampling.SamplePeriod, None, s, "-1")
        self.assertRaises(ValueError, sampling.SampleEvent, None, s, "foo")
        self.assertRaises(ValueError, sampling.SampleDifferential, None, s)
        self.assertRaises(ValueError, sampling.SampleDifferential,
                          None, s, "-1")
        self.assertRaises(ValueError, sampling.SampleDifferential,
                          None, s, "1.5")

        sampling.SampleStrategy.get_strategy("none", None, s)
        sampling.SampleStrategy.get_strategy("auto", None, s)
        sampling.SampleStrategy.get_strategy("period", None, s, "15")
        sampling.SampleStrategy.get_strategy("event", None, s)
        sampling.SampleStrategy.get_strategy("differential", None, s, "2")
        self.assertRaises(ValueError, sampling.SampleStrategy.get_strategy,
                          "random", None, s)
        self.assertRaises(ValueError, sampling.SampleStrategy.get_strategy,
                          "period", None, s, "foo")
        self.assertRaises(ValueError, sampling.SampleStrategy.get_strategy,
                          "differential", None, s, "bar")

    def test_event(self):
        """Test SampleEvent strategy."""
        event = sampling.SampleEvent(self.inform, self.sensor)
        self.assertEqual(event.get_sampling_formatted(),
                         ('event', []) )

        self.assertEqual(self.calls, [])

        event.attach()
        self.assertEqual(len(self.calls), 1)

        self.sensor.set_value(2, status=Sensor.NOMINAL)
        self.assertEqual(len(self.calls), 2)

        # Test that an update is suppressed if the sensor value is unchanged
        self.sensor.set_value(2, status=Sensor.NOMINAL)
        self.assertEqual(len(self.calls), 2)

        # Test that an update happens if the status changes even if the value is
        # unchanged
        self.sensor.set_value(2, status=Sensor.WARN)
        self.assertEqual(len(self.calls), 3)


    def test_differential(self):
        """Test SampleDifferential strategy."""
        diff = sampling.SampleDifferential(self.inform, self.sensor, 5)
        self.assertEqual(self.calls, [])

        diff.attach()
        self.assertEqual(len(self.calls), 1)

    def test_differential_timestamp(self):
        # Test that the timetamp differential is stored correctly as
        # seconds. This is mainly to check the conversion of the katcp spec from
        # milliseconds to seconds for katcp v5 spec.
        time_diff = 4.12                  # Time differential in seconds
        ts_sensor = Sensor(Sensor.TIMESTAMP, 'ts', 'ts sensor', '')
        diff = sampling.SampleDifferential(self.inform, ts_sensor, time_diff)
        self.assertEqual(diff._threshold, time_diff)

    def test_periodic(self):
        """Test SamplePeriod strategy."""
        sample_p = 10                            # sample period in seconds
        period = sampling.SamplePeriod(self.inform, self.sensor, sample_p)
        self.assertEqual(self.calls, [])

        period.attach()
        self.assertEqual(self.calls, [])

        next_p = period.periodic(1)
        self.assertEqual(next_p, 1 + sample_p)
        self.assertEqual(len(self.calls), 1)

        next_p = period.periodic(11)
        self.assertEqual(len(self.calls), 2)
        self.assertEqual(next_p, 11 + sample_p)

        next_p = period.periodic(12)
        self.assertEqual(next_p, 12 + sample_p)
        self.assertEqual(len(self.calls), 3)

    def test_event_rate(self):
        """Test SampleEventRate strategy."""
        shortest = 10
        longest = 20
        patcher = mock.patch('katcp.sampling.time')
        mtime = patcher.start()
        self.addCleanup(patcher.stop)
        time_ = mtime.time
        time_.return_value = 1
        evrate = sampling.SampleEventRate(
            self.inform, self.sensor, shortest, longest)
        new_period = mock.Mock()
        evrate.set_new_period_callback(new_period)

        time_.return_value = 1

        self.assertEqual(self.calls, [])

        evrate.attach()
        # Check initial update
        self.assertEqual(len(self.calls), 1)

        # Too soon, should not send update
        self.sensor.set_value(1)
        self.assertEqual(len(self.calls), 1)
        # but should have requested a future update at now + shortest-time
        new_period.assert_called_once_with(evrate, 11)
        new_period.reset_mock()

        time_.return_value = 11
        next_p = evrate.periodic(11)
        self.assertEqual(len(self.calls), 2)
        self.assertEqual(new_period.called, False)

        evrate.periodic(12)
        self.assertEqual(len(self.calls), 2)
        self.assertEqual(new_period.called, False)
        evrate.periodic(13)
        self.assertEqual(len(self.calls), 2)
        self.assertEqual(new_period.called, False)

        evrate.periodic(31)
        self.assertEqual(len(self.calls), 3)

        time_.return_value = 32
        self.assertEqual(len(self.calls), 3)

        time_.return_value = 41
        self.sensor.set_value(2)
        self.assertEqual(len(self.calls), 4)

    def test_differential_rate(self):
        difference = 2
        shortest = 10
        longest = 20
        patcher = mock.patch('katcp.sampling.time')
        mtime = patcher.start()
        self.addCleanup(patcher.stop)
        time_ = mtime.time
        time_.return_value = 0
        drate = sampling.SampleDifferentialRate(
            self.inform, self.sensor, difference, shortest, longest)
        self.assertEqual(
            drate.get_sampling(), sampling.SampleStrategy.DIFFERENTIAL_RATE)

        new_period = mock.Mock()
        drate.set_new_period_callback(new_period)

        self.assertEqual(len(self.calls), 0)
        drate.attach()
        self.assertEqual(len(self.calls), 1)
        # Bigger than `difference`, but too soon
        self.sensor.set_value(0)
        # Should not have added a call
        self.assertEqual(len(self.calls), 1)
        # Should have requested a future update at shortest-time
        new_period.assert_called_once_with(drate, 10)
        new_period.reset_mock()

        # call before shortest update period
        drate.periodic(7)
        # Should not have added a call
        self.assertEqual(len(self.calls), 1)
        # Call at next period, should call, and schedule a periodic update
        # `longest` later
        next_p = drate.periodic(10)
        self.assertEqual(len(self.calls), 2)
        self.assertEqual(next_p, 30)
        next_p = drate.periodic(30)
        self.assertEqual(len(self.calls), 3)
        self.assertEqual(next_p, 50)

        # Update with a too-small difference in value, should not send an
        # update, nor should it schedule a shortest-time future-update
        self.sensor.set_value(-1)
        self.assertEqual(len(self.calls), 3)
        self.assertEqual(new_period.called, False)

        next_p = drate.periodic(50)
        self.assertEqual(len(self.calls), 4)
        self.assertEqual(next_p, 70)


    def test_event_rate_fractions(self):
        # Test SampleEventRate strategy in the presence of fractional seconds --
        # mainly to catch bugs when it was converted to taking seconds instead of
        # milliseconds, since the previous implementation used an integer number
        # of milliseconds
        shortest = 3./8
        longest = 6./8
        evrate = sampling.SampleEventRate(self.inform, self.sensor, shortest,
                                          longest)
        evrate.set_new_period_callback(mock.Mock())

        now = [0]
        evrate._time = lambda: now[0]

        evrate.attach()
        self.assertEqual(len(self.calls), 1)

        now[0] = 0.999*shortest
        self.sensor.set_value(1)
        self.assertEqual(len(self.calls), 1)

        now[0] = shortest
        self.sensor.set_value(1)
        self.assertEqual(len(self.calls), 2)

        next_time = evrate.periodic(now[0] + 0.99*shortest)
        self.assertEqual(len(self.calls), 2)
        self.assertEqual(next_time, now[0] + longest)

class FakeEvent(object):
    def __init__(self, time_source, wait_called_callback=None, waited_callback=None):
        self._event = threading.Event()
        self._set = False
        self._set_lock = threading.Lock()
        self.wait_called_callback = wait_called_callback
        self.waited_callback = waited_callback
        self._time_source = time_source

    def set(self):
        with self._set_lock:
            self._set = True
            self.break_wait()

    def clear(self):
        with self._set_lock:
            self._set = False
            self._event.clear()

    def isSet(self):
        return self._set

    is_set = isSet

    def wait(self, timeout=None):
        if self.wait_called_callback:
            self.wait_called_callback(timeout)
        start_time = self._time_source()
        if not self._set and (timeout is None or timeout >= 0):
            self._event.wait()
        with self._set_lock:
            if not self._set:
                self._event.clear()
            isset = self._set
        now = self._time_source()

        if self.waited_callback:
            self.waited_callback(start_time, now, timeout)
        return isset

    def break_wait(self):
        self._event.set()

class TestReactorIntegration(unittest.TestCase):
    def setUp(self):
        """Set up for test."""
        # test sensor
        # self._print_lock = threading.Lock()
        self._time_lock = threading.Lock()
        self._next_wakeup = 1e99
        self.wake_waits = Queue.Queue()
        self.sensor = DeviceTestSensor(
                Sensor.INTEGER, "an.int", "An integer.", "count",
        [-4, 3],
                timestamp=12345, status=Sensor.NOMINAL, value=3)


        # test callback
        self.inform_called = threading.Event()
        def inform(sensor_name, timestamp, status, value):
            self.inform_called.set()
            self.calls.append((self.time(),
                               (sensor_name, float(timestamp), status, value)) )

        def next_wakeup_callback(timeout):
            with self._time_lock:
                if timeout is not None:
                    next_wake = self.time() + timeout
                    self._next_wakeup = min(self._next_wakeup, next_wake)
                else:
                    self._next_wakeup = 1e99
            self.wake_waits.put(timeout)

        def waited_callback(start, end, timeout):
            # A callback that updates 'simulated time' whenever wake.wait() is
            # called
            with self._time_lock:
                self._next_wakeup = 1e99

        # test reactor
        self.reactor = sampling.SampleReactor()

        # Patch time.time so that we can lie about time.
        self.time_patcher = mock.patch('katcp.sampling.time')
        mtime = self.time_patcher.start()
        self.addCleanup(self.time_patcher.stop)
        self.time = mtime.time
        self.start_time = self.time.return_value = 0

        # Replace the reactor wake Event with a time-warping mock Event
        self.reactor._wakeEvent = self.wake = wake = FakeEvent(
            self.time, next_wakeup_callback, waited_callback)

        start_thread_with_cleanup(self, self.reactor)
        # Wait for the event loop to reach its first wake.wait()
        self.wake_waits.get(timeout=1)

        self.calls = []
        self.inform = inform

    def _add_strategy(self, strat, wait_initial=True):
        # Add strategy to test reactor while taking care to mock time.time as
        # needed, and waits for the initial update (all strategies except None
        # should send an initial update)

        self.reactor.add_strategy(strat)

        if wait_initial:
            self.inform_called.wait(1)
            self.inform_called.clear()
            self.wake_waits.get(timeout=1)

    def timewarp(self, jump, wait_for_waitstate=True, event_to_await=None):
        """
        Timewarp simulation time by `jump` seconds

        Arguments
        ---------

        jump: float
            Number of seconds to time-warp by
        wait_for_waitstate: bool, default True
            Wait until the simulated loop again enters a wait state that times
            out beyond the current time-warp end-time. Will wake up the simulated
            loop as many times as necessary.
        event_to_await: Event or None, default None
            If an Event object is passed, wait for it to be set after
            time-warping, and then clear it.
        """

        start_time = self.time.return_value
        end_time = start_time + jump
        while end_time >= self._next_wakeup:
            with self._time_lock:
                self.time.return_value = self._next_wakeup
            self.wake.break_wait()
            if wait_for_waitstate:
                wait_timeout = self.wake_waits.get(timeout=1)
            else:
                break

        if event_to_await:
            event_to_await.wait(1)
            event_to_await.clear()
        with self._time_lock:
            self.time.return_value = end_time


    def test_periodic(self):
        """Test reactor with periodic sampling."""
        period = 10.
        no_periods = 5
        period_strat = sampling.SamplePeriod(self.inform, self.sensor, period)
        self._add_strategy(period_strat)

        for i in range(no_periods):
            self.timewarp(period, event_to_await=self.inform_called)

        self.reactor.remove_strategy(period_strat)

        call_times = [t for t, vals in self.calls]
        self.assertEqual(len(self.calls), no_periods + 1)
        self.assertEqual(call_times,
                         [self.start_time + i*period
                          for i in range(no_periods + 1)])


    def test_event_rate(self):
        max_period = 10.
        min_period = 1.
        event_rate_strat = sampling.SampleEventRate(
            self.inform, self.sensor, min_period, max_period)
        self._add_strategy(event_rate_strat)

        no_max_periods = 3

        # Do some 'max period' updates where the sensor has not changed
        for i in range(no_max_periods):
            self.timewarp(max_period, event_to_await=self.inform_called)

        call_times = [t for t, vals in self.calls]
        self.assertEqual(len(self.calls), no_max_periods + 1)
        self.assertEqual(call_times,
                         [self.start_time + i*max_period
                          for i in range(no_max_periods + 1)])

        del self.calls[:]

        # Now do a sensor update without moving time along, should not result in
        # any additional updates
        update_time = self.time()
        expected_send_time = update_time + min_period
        self.sensor.set_value(2, self.sensor.NOMINAL, update_time)
        # There should, however, be a wake-wait event
        self.wake_waits.get(timeout=1)

        self.assertEqual(len(self.calls), 0)
        # Timewarp less than min update period, should not result in an inform
        # callback
        self.timewarp(min_period*0.6)

        # Move time beyond minimum step
        self.timewarp(min_period*1.01, event_to_await=self.inform_called)

        self.assertEqual(len(self.calls), 1)
        self.assertEqual(self.calls,
                         [(expected_send_time,
                           (self.sensor.name, update_time, 'nominal', '2'))])
        # Should not be any outstanding wake-waits
        self.assertEqual(self.wake_waits.qsize(), 0)

        del self.calls[:]
        # Time we expect the next max-period sample
        expected_send_time += max_period
        # Timewarp past the next expected max-period sample time
        self.timewarp(max_period + min_period*0.01,
                      event_to_await=self.inform_called)
        self.assertEqual(len(self.calls), 1)
        self.assertEqual(self.calls[0][0], expected_send_time)
        self.reactor._debug_now = False
        self.reactor.remove_strategy(event_rate_strat)


    def test_differential_rate(self):
        max_period = 10.
        min_period = 1.
        difference = 2
        differential_rate_strat = sampling.SampleDifferentialRate(
            self.inform, self.sensor, difference, min_period, max_period)
        self._add_strategy(differential_rate_strat)

        no_max_periods = 3

        # Do some 'max period' updates where the sensor has not changed
        for i in range(no_max_periods):
            self.timewarp(max_period, event_to_await=self.inform_called)

        call_times = [t for t, vals in self.calls]
        self.assertEqual(len(self.calls), no_max_periods + 1)
        self.assertEqual(call_times,
                         [self.start_time + i*max_period
                          for i in range(no_max_periods + 1)])

        del self.calls[:]

        # Now do a sensor update by more than `difference` without moving time
        # along, should not result in any additional updates
        update_time = self.time()
        expected_send_time = update_time + min_period
        # Intial value = 3, difference = 2, 3-2 = 1, but sensor must differ by
        # _more_ than difference, so choose 0
        self.sensor.set_value(0, self.sensor.NOMINAL, update_time)
        # There should, however, be a wake-wait event
        self.wake_waits.get(timeout=1)

        self.assertEqual(len(self.calls), 0)
        # Timewarp less than min update period, should not result in an inform
        # callback
        self.timewarp(min_period*0.6)
        self.assertEqual(len(self.calls), 0)

        # Move time beyond minimum step
        self.timewarp(min_period*1.01, event_to_await=self.inform_called)

        self.assertEqual(len(self.calls), 1)
        self.assertEqual(self.calls,
                         [(expected_send_time,
                           (self.sensor.name, update_time, 'nominal', '0'))])
        # Should not be any outstanding wake-waits
        self.assertEqual(self.wake_waits.qsize(), 0)

        del self.calls[:]

        # Do a sensor update by less than `difference`
        self.sensor.set_value(1, self.sensor.NOMINAL, update_time)
        # Time we expect the next max-period sample
        expected_send_time += max_period
        update_time = self.time()

        # Move time beyond minimum step, should not send an update, since the
        # sensor changed by less than `difference`
        self.timewarp(min_period*1.1)
        # Timewarp past the next expected max-period sample time
        self.timewarp(max_period - min_period,
                      event_to_await=self.inform_called)

        self.assertEqual(len(self.calls), 1)
        self.assertEqual(self.calls[0][0], expected_send_time)
        self.reactor._debug_now = False
        self.reactor.remove_strategy(differential_rate_strat)


