"""Independent boundary checks of the local Chapter 23 teaching ledger."""
import importlib.util
import json
from pathlib import Path
import sqlite3
import tempfile
import unittest

HELPER = Path(__file__).resolve().parents[1]/'chapters/ch23-distributed-platform/distributed_platform.py'
spec = importlib.util.spec_from_file_location('chapter23_lab', HELPER)
lab = importlib.util.module_from_spec(spec)
spec.loader.exec_module(lab)


class DistributedPlatformTests(unittest.TestCase):
    def test_fixture_counts_and_denominators(self):
        with tempfile.TemporaryDirectory() as td:
            path = Path(td)/'ledger.sqlite'
            report = lab.run_fixture(path)
            self.assertEqual(len(report['attempts']), 12)
            self.assertEqual([r['seq'] for r in report['archive']], [0,1,2,3,4,5,6,8,9])
            self.assertEqual((report['archive_count'], report['monitor_accepted']), (9,7))
            self.assertEqual((report['archive_coverage'], report['timely_valid_monitor_coverage']), (.9,.7))
            self.assertEqual({k:v for k,v in report['monitor_outcomes'].items() if v != 'accepted'},
                             {2:'expired',4:'quality_inhibited',7:'missing'})
            self.assertEqual(report['restart'], {'retry_outcome':'duplicate','archive_count':9})
            self.assertEqual(report['status_at_1000_ms']['state'], 'stale')
            with self.assertRaises(FileExistsError): lab.run_fixture(path)
            json.dumps(report, allow_nan=False)

    def test_schema_boundary(self):
        for changes in ({'seq':True}, {'seq':-1}, {'seq':2**63}, {'source_ms':1.2},
                        {'quality_ok':1}, {'expires_ms':399}, {'stream':''},
                        {'epoch':'x'*65}, {'schema':'quality.v2'}, {'transform':'unknown'}):
            with self.subTest(changes=changes), self.assertRaises(ValueError):
                lab.validate(dict(lab.make_event(0), **changes))
        with self.assertRaises(ValueError): lab.validate(dict(lab.make_event(0), extra=1))
        missing = lab.make_event(0); del missing['seq']
        with self.assertRaises(ValueError): lab.validate(missing)

    def test_duplicate_conflict_and_authorization(self):
        db = lab.open_store(':memory:')
        try:
            event = lab.make_event(0)
            self.assertEqual(lab.receive_archive(db, lab.PRINCIPAL, event), 'stored')
            reordered = dict(reversed(list(event.items())))
            self.assertEqual(lab.receive_archive(db, lab.PRINCIPAL, reordered), 'duplicate')
            with self.assertRaisesRegex(ValueError, 'conflict'):
                lab.receive_archive(db, lab.PRINCIPAL, dict(event, quality_ok=False))
            for principal, payload in [('other', event), (lab.PRINCIPAL, dict(event, stream='other')),
                                       (lab.PRINCIPAL, dict(event, epoch='other'))]:
                with self.assertRaises(PermissionError): lab.receive_archive(db, principal, payload)
            for table in ('receipts','archive'):
                self.assertEqual(db.execute(f'SELECT COUNT(*) FROM {table}').fetchone()[0],1)
            self.assertTrue(json.loads(db.execute('SELECT body FROM archive').fetchone()[0])['quality_ok'])
        finally:
            db.close()

    def test_archive_failure_rolls_back_receipt(self):
        db = lab.open_store(':memory:')
        try:
            db.execute("CREATE TRIGGER fail_archive BEFORE INSERT ON archive BEGIN SELECT RAISE(ABORT, 'injected failure'); END")
            with self.assertRaises(sqlite3.IntegrityError):
                lab.receive_archive(db, lab.PRINCIPAL, lab.make_event(0))
            self.assertEqual(db.execute('SELECT COUNT(*) FROM receipts').fetchone()[0],0)
            db.execute('DROP TRIGGER fail_archive')
            self.assertEqual(lab.receive_archive(db,lab.PRINCIPAL,lab.make_event(0)),'stored')
        finally:
            db.close()

    def test_monitor_clock_quality_and_order(self):
        monitor = lab.Monitor()
        self.assertEqual(monitor.status(0)['state'],'unknown')
        self.assertEqual(monitor.offer(lab.make_event(1),419),'future')
        self.assertEqual(monitor.offer(lab.make_event(1),520),'accepted')  # expiry equality
        self.assertEqual(monitor.offer(lab.make_event(0),500),'not_newer')
        self.assertEqual(monitor.offer(lab.make_event(2),541),'expired')
        self.assertEqual(monitor.offer(lab.make_event(4),485),'quality_inhibited')
        self.assertEqual(monitor.last['seq'],1)
        self.assertEqual(monitor.status(521)['state'],'stale')
        self.assertEqual(monitor.status(419)['state'],'unknown')
        copy = monitor.status(500); copy['last_accepted']['source_ms']=0
        self.assertEqual(monitor.last['source_ms'],420)
        with self.assertRaises(ValueError): monitor.offer(lab.make_event(2),True)
        with self.assertRaises(ValueError): monitor.offer(dict(lab.make_event(2),epoch='new-session'),445)


if __name__ == '__main__': unittest.main()
