"""Chapter 23: local synthetic event ledger, not a network or clinical service.

One serialized SQLite connection; one virtual clock; trusted fixture principals.
The monitor is volatile and separate from the durable archive. Restart recovery
of a monitor, sender spool, authenticated transport and broker are extensions.
"""
from __future__ import annotations
import json
from pathlib import Path
import platform
import sqlite3

FIELDS = {'schema', 'stream', 'epoch', 'seq', 'source_ms', 'expires_ms',
          'quality_ok', 'transform'}
PRINCIPAL = 'fixture-publisher'


def validate(event):
    if type(event) is not dict or set(event) != FIELDS:
        raise ValueError('exact quality.v1 fields required')
    for key in ('schema', 'stream', 'epoch', 'transform'):
        value = event[key]
        if type(value) is not str or not value.strip() or len(value) > 64:
            raise ValueError('bounded nonempty identifiers required')
    if event['schema'] != 'quality.v1' or event['transform'] != 'toy-quality-v1':
        raise ValueError('unsupported schema or transformation')
    for key in ('seq', 'source_ms', 'expires_ms'):
        if type(event[key]) is not int or not 0 <= event[key] <= 2**63-1:
            raise ValueError('nonnegative SQLite-range integer required')
    if event['expires_ms'] < event['source_ms'] or type(event['quality_ok']) is not bool:
        raise ValueError('invalid lifetime or quality type')
    return event


def make_event(seq):
    return validate(dict(schema='quality.v1', stream='eeg-demo', epoch='session-001',
                         seq=seq, source_ms=400+20*seq, expires_ms=500+20*seq,
                         quality_ok=seq != 4, transform='toy-quality-v1'))


def open_store(path):
    # Explicit legacy transaction behavior is shared by Python 3.11 and later.
    db = sqlite3.connect(path, isolation_level='DEFERRED')
    for table in ('receipts', 'archive'):
        db.execute(f'''CREATE TABLE IF NOT EXISTS {table} (
            principal TEXT NOT NULL, stream TEXT NOT NULL,
            epoch TEXT NOT NULL, seq INTEGER NOT NULL, body TEXT NOT NULL,
            PRIMARY KEY (principal, stream, epoch, seq))''')
    db.commit()
    return db


def receive_archive(db, principal, event):
    if principal != PRINCIPAL:
        raise PermissionError('publish denied')
    validate(event)
    # This fixture publisher is authorized for precisely one stream and epoch.
    if (event['stream'], event['epoch']) != ('eeg-demo', 'session-001'):
        raise PermissionError('stream or epoch denied')
    key = (principal, event['stream'], event['epoch'], event['seq'])
    body = json.dumps(event, sort_keys=True, separators=(',', ':'), allow_nan=False)
    with db:
        receipt = db.execute('INSERT OR IGNORE INTO receipts VALUES (?,?,?,?,?)', (*key, body))
        if receipt.rowcount == 0:
            previous = db.execute('SELECT body FROM receipts WHERE principal=? AND '
                                  'stream=? AND epoch=? AND seq=?', key).fetchone()[0]
            if previous != body:
                raise ValueError('event identity conflict')
            return 'duplicate'
        db.execute('INSERT INTO archive VALUES (?,?,?,?,?)', (*key, body))
    return 'stored'


class Monitor:
    """Volatile, single-stream monitor; only newly archived events are offered."""
    def __init__(self):
        self.last = None

    def offer(self, event, now_ms):
        validate(event)
        if (event['stream'], event['epoch']) != ('eeg-demo', 'session-001'):
            raise ValueError('monitor stream/epoch mismatch')
        if type(now_ms) is not int or now_ms < 0:
            raise ValueError('virtual evaluation time must be a nonnegative integer')
        if not event['quality_ok']:
            return 'quality_inhibited'
        if event['source_ms'] > now_ms:
            return 'future'
        if now_ms > event['expires_ms']:
            return 'expired'
        if self.last is not None and event['source_ms'] <= self.last['source_ms']:
            return 'not_newer'
        self.last = dict(event)
        return 'accepted'

    def status(self, now_ms):
        if type(now_ms) is not int or now_ms < 0:
            raise ValueError('virtual evaluation time must be a nonnegative integer')
        if self.last is None:
            return {'state': 'unknown', 'last_accepted': None, 'source_age_ms': None}
        age = now_ms-self.last['source_ms']
        state = 'unknown' if age < 0 else ('stale' if now_ms > self.last['expires_ms'] else 'current')
        return {'state': state, 'last_accepted': dict(self.last), 'source_age_ms': age}


def schedule():
    attempts = []
    for seq in range(10):
        if seq == 7:
            continue
        event = make_event(seq)
        attempts.append((event['source_ms']+(160 if seq == 2 else 5), PRINCIPAL, event))
    attempts.extend([(625, PRINCIPAL, make_event(1)),
                     (630, PRINCIPAL, dict(make_event(1), quality_ok=False)),
                     (410, 'unauthorized-fixture', make_event(0))])
    return sorted(attempts, key=lambda row: row[0])


def run_fixture(path):
    """Require a fresh database; never erase a previous experiment implicitly."""
    path = Path(path)
    if path.exists():
        raise FileExistsError('use a fresh experiment filename')
    db = open_store(path)
    monitor = Monitor()
    attempts, outcomes = [], {seq: 'missing' for seq in range(10)}
    try:
        for now, principal, event in schedule():
            row = dict(arrival_ms=now, principal=principal, event=event)
            try:
                row['archive_outcome'] = receive_archive(db, principal, event)
            except (ValueError, PermissionError) as exc:
                row['archive_outcome'] = 'conflict' if isinstance(exc, ValueError) else 'denied'
                row['reason'] = str(exc)
            if row['archive_outcome'] == 'stored':
                row['monitor_outcome'] = monitor.offer(event, now)
                outcomes[event['seq']] = row['monitor_outcome']
            attempts.append(row)
        archive = [json.loads(row[0]) for row in db.execute('SELECT body FROM archive ORDER BY seq')]
    finally:
        db.close()
    # Receiver restart retains receipts; retrying an event changes no archive row.
    db = open_store(path)
    try:
        restart_outcome = receive_archive(db, PRINCIPAL, make_event(1))
        restart_count = db.execute('SELECT COUNT(*) FROM archive').fetchone()[0]
    finally:
        db.close()
    return dict(schema='chapter23-evidence.v1', expected_opportunities=10,
                clock='one synthetic shared virtual millisecond clock',
                fault_schedule='delay seq2 +160; omit7; quality4 false; retry1; conflict1; denied0',
                attempts=attempts, archive=archive, monitor_outcomes=outcomes,
                archive_count=len(archive), monitor_accepted=sum(v == 'accepted' for v in outcomes.values()),
                archive_coverage=len(archive)/10, timely_valid_monitor_coverage=sum(v == 'accepted' for v in outcomes.values())/10,
                status_at_1000_ms=monitor.status(1000),
                restart=dict(retry_outcome=restart_outcome, archive_count=restart_count),
                versions=dict(python=platform.python_version(), sqlite=sqlite3.sqlite_version),
                limitations=['synthetic quality events, no EEG or clinical inference',
                             'no network, broker, spool, authentication, concurrent calls or crash injection',
                             'receiver restart tested; monitor state is volatile',
                             'coverage counts fixture outcomes, not patient benefit or transport reliability'])
