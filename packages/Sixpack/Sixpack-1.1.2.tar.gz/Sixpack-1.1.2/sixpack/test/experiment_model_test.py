import unittest
# from numbers import Number
# from sixpack.db import _key
from datetime import datetime

import fakeredis

from sixpack.models import Experiment, Alternative, Client


class TestExperimentModel(unittest.TestCase):

    unit = True

    def setUp(self):
        self.redis = fakeredis.FakeStrictRedis()
        self.alternatives = ['yes', 'no']

        self.exp_1 = Experiment('show-something-awesome', self.alternatives, self.redis)
        self.exp_2 = Experiment('dales-lagunitas', ['dales', 'lagunitas'], self.redis)
        self.exp_3 = Experiment('mgd-budheavy', ['mgd', 'bud-heavy'], self.redis)
        self.exp_1.save()
        self.exp_2.save()
        self.exp_3.save()

    def test_constructor(self):
        with self.assertRaises(ValueError):
            Experiment('not-enough-args', ['1'], self.redis)

    def test_save(self):
        pass

    def test_control(self):
        control = self.exp_1.control
        self.assertEqual(control.name, 'yes')

    def test_created_at(self):
        exp = Experiment('bench-press', ['joe', 'think'], self.redis)
        date = exp.created_at()
        self.assertIsNone(date)
        exp.save()
        date = exp.created_at()
        self.assertTrue(isinstance(date, datetime))

    def test_get_alternative_names(self):
        exp = Experiment('show-something', self.alternatives, self.redis)
        names = exp.get_alternative_names()
        self.assertEqual(sorted(self.alternatives), sorted(names))

    def test_is_new_record(self):
        exp = Experiment('show-something-is-new-record', self.alternatives, self.redis)
        self.assertTrue(exp.is_new_record())
        exp.save()
        self.assertFalse(exp.is_new_record())

    # fakeredis does not currently support bitcount
    # todo, fix fakeredis and
    def _test_total_participants(self):
        pass

    def _test_total_conversions(self):
        pass

    def test_description(self):
        exp = Experiment.find_or_create('never-gonna', ['give', 'you', 'up'], self.redis)
        self.assertEqual(exp.get_description(), None)

        exp.update_description('hallo')
        self.assertEqual(exp.get_description(), 'hallo')

    def test_change_alternatives(self):
        exp = Experiment.find_or_create('never-gonna-x', ['let', 'you', 'down'], self.redis)

        with self.assertRaises(ValueError):
            Experiment.find_or_create('never-gonna-x', ['let', 'you', 'down', 'give', 'you', 'up'], self.redis)

        exp.delete()

        Experiment.find_or_create('never-gonna-x', ['let', 'you', 'down', 'give', 'you', 'up'], self.redis)

    def test_delete(self):
        exp = Experiment('delete-me', self.alternatives, self.redis)
        exp.save()

        exp.delete()
        with self.assertRaises(ValueError):
            Experiment.find('delete-me', self.redis)

    def test_leaky_delete(self):
        exp = Experiment('delete-me-1', self.alternatives, self.redis)
        exp.save()

        exp2 = Experiment('delete', self.alternatives, self.redis)
        exp2.save()

        exp2.delete()
        exp3 = Experiment.find('delete-me-1', self.redis)
        self.assertEqual(exp3.get_alternative_names(), self.alternatives)

    def test_archive(self):
        self.assertFalse(self.exp_1.is_archived())
        self.exp_1.archive()
        self.assertTrue(self.exp_1.is_archived())
        self.exp_1.unarchive()
        self.assertFalse(self.exp_1.is_archived())

    def test_unarchive(self):
        self.exp_1.archive()
        self.assertTrue(self.exp_1.is_archived())
        self.exp_1.unarchive()
        self.assertFalse(self.exp_1.is_archived())

    def test_set_winner(self):
        exp = Experiment('test-winner', ['1', '2'], self.redis)
        exp.set_winner('1')
        self.assertTrue(exp.winner is not None)

        exp.set_winner('1')
        self.assertEqual(exp.winner, '1')

    def test_winner(self):
        exp = Experiment.find_or_create('test-get-winner', ['1', '2'], self.redis)
        self.assertIsNone(exp.winner)

        exp.set_winner('1')
        self.assertEqual(exp.winner, '1')

    def test_reset_winner(self):
        exp = Experiment('show-something-reset-winner', self.alternatives, self.redis)
        exp.save()
        exp.set_winner('yes')
        self.assertTrue(exp.winner is not None)
        self.assertEqual(exp.winner, 'yes')

        exp.reset_winner()
        self.assertIsNone(exp.winner)

    def test_winner_key(self):
        exp = Experiment.find_or_create('winner-key', ['win', 'lose'], self.redis)
        self.assertEqual(exp._winner_key, "{0}:winner".format(exp.key()))

    def test_get_alternative(self):
        client = Client(10, self.redis)

        exp = Experiment.find_or_create('archived-control', ['w', 'l'], self.redis)
        exp.archive()

        # should return control on archived test with no winner
        alt = exp.get_alternative(client)
        self.assertEqual(alt.name, 'w')

        # should return current participation
        exp.unarchive()
        ### HACK TO SKIP WHIPLASH TESTS
        exp.random_sample = 1
        ### HACK TO SKIP WHIPLASH TESTS

        selected_for_client = exp.get_alternative(client)
        self.assertIn(selected_for_client.name, ['w', 'l'])

        # should check to see if client is participating and only return the same alt
        # unsure how to currently test since fakeredis obviously doesn't parse lua
        # most likely integration tests

    # See above note for the next 5 tests
    def _test_existing_alternative(self):
        pass

    def _test_has_converted_by_client(self):
        pass

    def _test_choose_alternative(self):
        pass

    def _test_random_choice(self):
        pass

    def _test_whiplash(self):
        pass

    def test_key(self):
        key = self.exp_1.key()
        self.assertEqual(key, 'sxp:e:show-something-awesome')

        key_2 = self.exp_2.key()
        self.assertEqual(key_2, 'sxp:e:dales-lagunitas')

        exp = Experiment('brews', ['mgd', 'bud-heavy'], self.redis)
        key_3 = exp.key()
        self.assertEqual(key_3, 'sxp:e:brews')

    def test_find(self):
        exp = Experiment('crunches-situps', ['crunches', 'situps'], self.redis)
        exp.save()

        with self.assertRaises(ValueError):
            Experiment.find('this-does-not-exist', self.redis)

        try:
            Experiment.find('crunches-situps', self.redis)
        except:
            self.fail('known exp not found')

    def test_find_or_create(self):
        # should throw a ValueError if alters are invalid
        with self.assertRaises(ValueError):
            Experiment.find_or_create('party-time', ['1'], self.redis)

        with self.assertRaises(ValueError):
            Experiment.find_or_create('party-time', ['1', '*****'], self.redis)

        # should create a -NEW- experiment if experiment has never been used
        with self.assertRaises(ValueError):
            Experiment.find('dance-dance', self.redis)

    def test_all(self):
        # there are three created in setUp()
        all_of_them = Experiment.all(self.redis)
        self.assertEqual(len(all_of_them), 3)

        exp_1 = Experiment('archive-this', ['archived', 'unarchive'], self.redis)
        exp_1.save()

        all_again = Experiment.all(self.redis)
        self.assertEqual(len(all_again), 4)

        exp_1.archive()
        all_archived = Experiment.all(self.redis)
        self.assertEqual(len(all_archived), 3)

        all_with_archived = Experiment.all(self.redis, False)
        self.assertEqual(len(all_with_archived), 4)

        all_archived = Experiment.archived(self.redis)
        self.assertEqual(len(all_archived), 1)

    def test_load_alternatives(self):
        exp = Experiment.find_or_create('load-alts-test', ['yes', 'no', 'call-me-maybe'], self.redis)
        alts = Experiment.load_alternatives(exp.name, self.redis)
        self.assertEqual(sorted(alts), sorted(['yes', 'no', 'call-me-maybe']))

    def test_differing_alternatives_fails(self):
        exp = Experiment.find_or_create('load-differing-alts', ['yes', 'zack', 'PBR'], self.redis)
        alts = Experiment.load_alternatives(exp.name, self.redis)
        self.assertEqual(sorted(alts), sorted(['PBR', 'yes', 'zack']))

        with self.assertRaises(ValueError):
            exp = Experiment.find_or_create('load-differing-alts', ['kyle', 'zack', 'PBR'], self.redis)

    def _test_initialize_alternatives(self):
        # Should throw ValueError
        with self.assertRaises(ValueError):
            Experiment.initialize_alternatives('n', ['*'], self.redis)

        # each item in list should be Alternative Instance
        alt_objs = Experiment.initialize_alternatives('n', ['1', '2', '3'])
        for alt in alt_objs:
            self.assertTrue(isinstance(alt, Alternative))
            self.assertTrue(alt.name in ['1', '2', '3'])

    def test_is_not_valid(self):
        not_valid = Experiment.is_valid(1)
        self.assertFalse(not_valid)

        not_valid = Experiment.is_valid(':123:name')
        self.assertFalse(not_valid)

        not_valid = Experiment.is_valid('_123name')
        self.assertFalse(not_valid)

        not_valid = Experiment.is_valid('&123name')
        self.assertFalse(not_valid)

    def test_invalid_options(self):
        opts = {'derp': 'ington'}
        with self.assertRaises(ValueError):
            Experiment.find_or_create('jay-fi', ['jay', 'fi'], self.redis, opts)

    def test_valid_options(self):
        opts = {'traffic_fraction': 1}
        Experiment.find_or_create('red-white', ['red', 'white'], self.redis, opts)

        opts = {'traffic_fraction': 0}
        Experiment.find_or_create('red-white', ['red', 'white'], self.redis, opts)

        opts = {'traffic_fraction': 0.4}
        Experiment.find_or_create('red-white', ['red', 'white'], self.redis, opts)


    def test_invalid_traffic_fraction(self):
        opts = {'traffic_fraction': 2}
        with self.assertRaises(ValueError):
            Experiment.find_or_create('dist-2', ['dist', '2'], self.redis, opts)

        opts = {'traffic_fraction': 101}
        with self.assertRaises(ValueError):
            Experiment.find_or_create('dist-100', ['dist', '100'], self.redis, opts)

        opts = {'traffic_fraction': 'x'}
        with self.assertRaises(ValueError):
            Experiment.find_or_create('dist-100', ['dist', '100'], self.redis, opts)

    def test_valid_traffic_fractions_save(self):
        # test the hidden prop gets set
        opts = {'traffic_fraction': 0.02}
        exp = Experiment.find_or_create('dist-02', ['dist', '100'], self.redis, opts)
        self.assertEqual(exp._traffic_fraction, 0.02)

        opts = {'traffic_fraction': 0.4}
        exp = Experiment.find_or_create('dist-100', ['dist', '100'], self.redis, opts)
        self.assertEqual(exp._traffic_fraction, 0.40)

    # test is set in redis
    def test_traffic_fraction(self):
        opts = {'traffic_fraction': 0.10}
        exp = Experiment.find_or_create('d-test-10', ['d', 'c'], self.redis, opts)
        exp.save()
        self.assertEqual(exp.traffic_fraction, 0.1)

    def test_valid_kpi(self):
        ret = Experiment.validate_kpi('hello-jose')
        self.assertTrue(ret)
        ret = Experiment.validate_kpi('123')
        self.assertTrue(ret)
        ret = Experiment.validate_kpi('foreigner')
        self.assertTrue(ret)
        ret = Experiment.validate_kpi('boston')
        self.assertTrue(ret)
        ret = Experiment.validate_kpi('1_not-two-times-two-times')
        self.assertTrue(ret)

    def test_invalid_kpi(self):
        ret = Experiment.validate_kpi('!hello-jose')
        self.assertFalse(ret)
        ret = Experiment.validate_kpi('thunder storm')
        self.assertFalse(ret)
        ret = Experiment.validate_kpi('&!&&!&')
        self.assertFalse(ret)

    def test_set_kpi(self):
        exp = Experiment.find_or_create('multi-kpi', ['kpi', '123'], self.redis)
        # We shouldn't beable to manually set a KPI. Only via web request
        with self.assertRaises(ValueError):
            exp.set_kpi('bananza')

        # simulate conversion via webrequest
        client = Client(100, self.redis)
        # hack for disabling whiplash
        exp.random_sample = 1

        exp.get_alternative(client)
        exp.convert(client, None, 'bananza')

        exp2 = Experiment.find_or_create('multi-kpi', ['kpi', '123'], self.redis)
        self.assertEqual(exp2.kpi, None)
        exp2.set_kpi('bananza')
        self.assertEqual(exp2.kpi, 'bananza')

    def test_add_kpi(self):
        exp = Experiment.find_or_create('multi-kpi-add', ['asdf', '999'], self.redis)
        kpi = 'omg-pop'

        exp.add_kpi(kpi)
        key = "{0}:kpis".format(exp.key(include_kpi=False))
        self.assertIn(kpi, self.redis.smembers(key))
        exp.delete()

    def test_get_kpis(self):
        exp = Experiment.find_or_create('multi-kpi-add', ['asdf', '999'], self.redis)
        kpis = ['omg-pop', 'zynga']

        exp.add_kpi(kpis[0])
        exp.add_kpi(kpis[1])
        ekpi = exp.get_kpis()
        self.assertIn(kpis[0], ekpi)
        self.assertIn(kpis[1], ekpi)
        exp.delete()
