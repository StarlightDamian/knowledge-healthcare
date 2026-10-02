import unittest
from datetime import date, datetime
from unittest.mock import patch

from src.guide.model import review_date
from src.guide.editorial import editorial_audit
from tests.test_editorial import fixture


class ReviewDateTests(unittest.TestCase):
    def clock(self, instant):
        return patch('src.guide.model.datetime', **{
            'now.side_effect': lambda zone: datetime.fromisoformat(instant).astimezone(zone)})

    def test_editorial_midnight_is_independent_of_host_timezone(self):
        for instant, expected in [('2026-10-02T15:59:59+00:00', date(2026, 10, 2)),
                                  ('2026-10-02T16:00:00+00:00', date(2026, 10, 3)),
                                  ('2026-10-02T09:00:00-07:00', date(2026, 10, 3))]:
            with self.subTest(instant=instant), self.clock(instant):
                self.assertEqual(review_date(), expected)

    def test_same_day_review_qualifies_but_future_and_explicit_past_do_not(self):
        data, records = fixture()
        for record in records:
            record['checked_at'] = '2026-10-03'
            record['adversarial_review']['checked_at'] = '2026-10-03'
        with self.clock('2026-10-02T15:59:59+00:00'):
            before = editorial_audit(data=data, records=records)
            self.assertEqual(before['qualified_condition_ids'], [])
            self.assertIn('invalid_check_date', {item['issue'] for item in before['issues']})
        with self.clock('2026-10-02T16:00:00+00:00'):
            current = editorial_audit(data=data, records=records)
            self.assertEqual(current['qualified_condition_ids'], ['test-condition'])
            self.assertEqual(current['issues'], [])
            past = editorial_audit(data=data, records=records, today=date(2026, 10, 2))
            self.assertEqual(past['qualified_condition_ids'], [])
