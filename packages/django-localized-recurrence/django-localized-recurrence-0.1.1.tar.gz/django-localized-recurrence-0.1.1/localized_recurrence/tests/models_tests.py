import unittest
from datetime import datetime, timedelta

import pytz

from ..models import LocalizedRecurrence, LocalizedRecurrenceQuerySet, replace_with_offset


class Test_LocalizedRecurrenceQuerySet(unittest.TestCase):
    """Simple test to ensure the custom query set is being used.
    """
    def setUp(self):
        self.lr_day = LocalizedRecurrence.objects.create(
            interval='DAY',
            offset=timedelta(hours=12),
            timezone=pytz.timezone('US/Eastern'),
        )

    def test_isinstance(self):
        recurrences = LocalizedRecurrence.objects.all()
        self.assertIsInstance(recurrences, LocalizedRecurrenceQuerySet)


class Test_LocalizedRecurrenceQuerySet_update_schedule(unittest.TestCase):
    """Test that updates to recurrences are reflected in the DB.
    """
    def setUp(self):
        self.lr_day = LocalizedRecurrence.objects.create(
            interval='DAY',
            offset=timedelta(hours=12),
            timezone=pytz.timezone('US/Eastern'),
        )
        self.lr_month = LocalizedRecurrence.objects.create(
            interval='MONTH',
            offset=timedelta(hours=15),
            timezone=pytz.timezone('US/Eastern'),
        )

    def test_update_from_1970(self):
        """Start with next_scheduled of 1970, after update should be new.
        """
        time = datetime(year=2013, month=5, day=20, hour=12, minute=3)
        LocalizedRecurrence.objects.filter(interval='DAY').update_schedule(time=time)
        lr_day = LocalizedRecurrence.objects.filter(interval='DAY').first()
        self.assertGreater(lr_day.next_scheduled, time)

    def test_update_all(self):
        """Calls to the model manager to update should be passed through.
        """
        time = datetime(year=2013, month=5, day=20, hour=15, minute=3)
        LocalizedRecurrence.objects.update_schedule(time=time)
        self.assertTrue(all(r.next_scheduled > time for r in LocalizedRecurrence.objects.all()))


class Test_LocalizedRecurrence(unittest.TestCase):
    """Test the creation and querying of LocalizedRecurrence records.
    """
    def setUp(self):
        self.lr = LocalizedRecurrence.objects.create(
            interval='DAY',
            offset=timedelta(hours=12),
            timezone=pytz.timezone('US/Eastern'),
        )

    def test_creation_works(self):
        """Create a single record and get it back in a queryset.

        The record is created in setUp, we just test the return here.
        """
        lr_count = LocalizedRecurrence.objects.all().count()
        self.assertEqual(lr_count, 1)

    def test_timedelta_returned(self):
        """Test that the Duration field is correctly returning timedeltas.
        """
        lr = LocalizedRecurrence.objects.first()
        self.assertTrue(isinstance(lr.offset, timedelta))


class Test_LocalizedRecurrence_utc_of_next_schedule(unittest.TestCase):
    def setUp(self):
        self.lr_day = LocalizedRecurrence.objects.create(
            interval='DAY',
            offset=timedelta(hours=12),
            timezone=pytz.timezone('US/Eastern'),
        )

        self.lr_week = LocalizedRecurrence.objects.create(
            interval='WEEK',
            offset=timedelta(days=3, hours=17, minutes=30),
            timezone=pytz.timezone('US/Central')
        )

        self.lr_month = LocalizedRecurrence.objects.create(
            interval='MONTH',
            offset=timedelta(days=21, hours=19, minutes=15, seconds=10),
            timezone=pytz.timezone('US/Central')
        )

    def test_basic_works(self):
        """Test a simple case of utc_of_next_schedule.

        - The given recurrence is scheduled daily for Eastern Time at noon.
        - The given current date in UTC is 2013/1/15::17:05:22
        - We then expect the next schedule in UTC to be 2013/1/16::17:0:0
        """
        current_time = datetime(2013, 1, 15, 17, 5, 22)
        expected_next_schedule = datetime(2013, 1, 16, 17)
        schedule_out = self.lr_day.utc_of_next_schedule(current_time)
        self.assertEqual(schedule_out, expected_next_schedule)

    def test_before_midnight(self):
        """The case when the scheduled and current time cross midnight.

        - The given recurrence is scheduled daily for Eastern Time at 11:59PM.
        - The given current date in UTC is 2013/1/15::05:05:22 -> 12:05AM EST
        - We then expect the next schedule in UTC to be 2013/1/16::05:0:0
        """
        self.lr_day.offset = timedelta(hours=23, minutes=59)
        self.lr_day.save()
        current_time = datetime(2013, 1, 15, 5, 5, 22)
        expected_next_schedule = datetime(2013, 1, 16, 4, 59)
        schedule_out = self.lr_day.utc_of_next_schedule(current_time)
        self.assertEqual(schedule_out, expected_next_schedule)

    def test_after_midnight(self):
        """The case when the scheduled and current time are after midnight.

        - The given recurrence is scheduled daily for Eastern Time at 12:01 AM.
        - The given current date in UTC is 2013/1/15::05:05:22 -> 12:05AM EST
        - We then expect the next schedule in UTC to be 2013/1/16::05:01:0
        """
        self.lr_day.offset = timedelta(minutes=1)
        self.lr_day.save()
        current_time = datetime(2013, 1, 15, 5, 5, 22)
        expected_next_schedule = datetime(2013, 1, 16, 5, 01)
        schedule_out = self.lr_day.utc_of_next_schedule(current_time)
        self.assertEqual(schedule_out, expected_next_schedule)

    def test_week_update(self):
        """Weekly Recurrences should work as expected.

        - Friday August 8th at 10:34 PM UTC is 5:34 PM CDT.
        - Scheduled for weekly, Friday at 5:30
        - Expect next schedule to be Friday August 15th at 10:30 PM UTC
        """
        current_time = datetime(2013, 8, 8, 22, 34)
        expected_next_schedule = datetime(2013, 8, 15, 22, 30)
        schedule_out = self.lr_week.utc_of_next_schedule(current_time)
        self.assertEqual(schedule_out, expected_next_schedule)

    def test_month_update(self):
        """Monthly Recurrences should work as expected.

        - Friday August 23rd at 12:34 AM UTC is Friday August 22nd at 7:34 PM CDT.
        - Scheduled for Monthly, on the 8th day at 7:15.10 PM CDT
        - Expect next schedule to be September 9 at 12:15.10 AM UTC
        """
        current_time = datetime(2013, 8, 23, 0, 34, 55)
        expected_next_schedule = datetime(2013, 9, 23, 0, 15, 10)
        schedule_out = self.lr_month.utc_of_next_schedule(current_time)
        self.assertEqual(schedule_out, expected_next_schedule)

    def test_into_dst_boundary(self):
        """Recurrences happen at the correct local time after going into DST.

        Going into daylight savings time should mean the UTC time is
        an hour less on the next recurrence.

        - 2013 US DST began: Sunday March 10th.
        - Weekly recurence, every Thursday at Noon EST.
        """
        self.lr_week.offset = timedelta(days=3, hours=12)
        self.lr_week.save()
        current_time = datetime(2013, 3, 7, 18)
        expected_next_schedule = datetime(2013, 3, 14, 17)
        schedule_out = self.lr_week.utc_of_next_schedule(current_time)
        self.assertEqual(schedule_out, expected_next_schedule)

    def test_out_of_dst_boundary(self):
        """Recurrences at the correct local time after going out of UTC.

        Going into daylight savings time should mean the UTC time is
        an hour greater on the next recurrence.

        - 2013 US DST ended: Sunday November 3rd.
        - Weekly recurence, every Thursday at Noon EST.
        """
        self.lr_week.offset = timedelta(days=3, hours=12)
        self.lr_week.save()
        current_time = datetime(2013, 10, 31, 17)
        expected_next_schedule = datetime(2013, 11, 7, 18)
        schedule_out = self.lr_week.utc_of_next_schedule(current_time)
        self.assertEqual(schedule_out, expected_next_schedule)

    def test_utc_plus(self):
        """Test a timezone that is UTC + 2.

        - Europe/Berlin DST is UTC + 2
        """
        self.lr_day.timezone = pytz.timezone('Europe/Berlin')
        self.lr_day.save()
        current_time = datetime(2013, 5, 5, 10, 10)
        expected_next_schedule = datetime(2013, 5, 6, 10)
        schedule_out = self.lr_day.utc_of_next_schedule(current_time)
        self.assertEqual(schedule_out, expected_next_schedule)


class Test_replace_with_offset(unittest.TestCase):
    def test_day(self):
        """replace_with_offset works as expected with a 'DAY' interval.
        """
        dt_in = datetime(2013, 1, 20, 12, 45, 48)
        td_in = timedelta(hours=3, minutes=3, seconds=3)
        interval_in = 'DAY'
        dt_expected = datetime(2013, 1, 20, 3, 3, 3)
        dt_out = replace_with_offset(dt_in, td_in, interval_in)
        self.assertEqual(dt_out, dt_expected)

    def test_week(self):
        """replace_with_offset works as expected with a 'WEEK' interval.
        """
        dt_in = datetime(2013, 1, 20, 12, 45, 48)
        td_in = timedelta(days=4, hours=3, minutes=3, seconds=3)
        interval_in = 'WEEK'
        dt_expected = datetime(2013, 1, 18, 3, 3, 3)
        dt_out = replace_with_offset(dt_in, td_in, interval_in)
        self.assertEqual(dt_out, dt_expected)

    def test_week_on_month_boundary(self):
        """replace_with_offset using interval 'WEEK' should roll over months
        correctly.
        """
        dt_in = datetime(2013, 7, 30, 12, 45, 48)
        td_in = timedelta(days=4, hours=3, minutes=3, seconds=3)
        interval_in = 'WEEK'
        dt_expected = datetime(2013, 8, 2, 3, 3, 3)
        dt_out = replace_with_offset(dt_in, td_in, interval_in)
        self.assertEqual(dt_out, dt_expected)

    def test_month(self):
        """replace_with_offset works as expected with a 'MONTH' interval.
        """
        dt_in = datetime(2013, 1, 20, 12, 45, 48)
        td_in = timedelta(days=15, hours=3, minutes=3, seconds=3)
        interval_in = 'MONTH'
        dt_expected = datetime(2013, 1, 16, 3, 3, 3)
        dt_out = replace_with_offset(dt_in, td_in, interval_in)
        self.assertEqual(dt_out, dt_expected)

    def test_bad_interval(self):
        """A missformed interval should raise a value error
        """
        dt_in = datetime(2013, 1, 20, 12, 45, 48)
        td_in = timedelta(days=15, hours=3, minutes=3, seconds=3)
        interval_in = 'blah'
        with self.assertRaises(ValueError):
            replace_with_offset(dt_in, td_in, interval_in)
