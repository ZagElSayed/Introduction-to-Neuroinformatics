# Chapter 23: a local distributed-platform slice

Use Python 3.11 or later with SQLite support. The reference uses only the Python
standard library. Open `01_event_ledger.ipynb`, predict the counts, and run its
cells in order. It creates a fresh temporary database and exports a JSON report.

The roles are producer, ingress policy, durable archive and volatile monitor in
one local process. Events contain synthetic quality flags, not EEG, diagnoses or
device commands. All event times use one assigned virtual clock. No clock
synchronization, network timing or patient outcome is measured.

The fixed experiment has ten expected opportunities and twelve delivery
attempts. It should archive nine unique events and admit seven to the monitor:
sequence 2 expires, sequence 4 fails quality, and sequence 7 never arrives.
Duplicate, conflicting and unauthorized attempts have their own records.
Coverage denominators remain ten opportunities, rather than twelve attempts.

Receipt and archive insertion share one SQLite transaction. A receiver restart
reopens the same database and recognizes a duplicate. The monitor is volatile;
the experiment does not demonstrate monitor recovery, process crashes,
concurrent delivery, authenticated identity, a network/broker, or a sender spool.
The trusted fixture principal exercises authorization only. The implementation
also restricts that principal to the declared stream and epoch. An accepted
status means the last accepted event remains within its synthetic lifetime;
it does not establish the present physiological condition of a person.

From the repository root, run the boundary tests with:

```sh
python -m unittest discover -s tests -p 'test_chapter23_lab.py' -v
```

Before extending the reference, preserve its baseline evidence. Implement a
bounded sender spool, then separately demonstrate disconnection and a lost
acknowledgement. Keep event identity and source time unchanged. Define overflow,
retry and recovery policies before claiming a transport guarantee. Add a broker
or independent process only after the local contract is understood.

Submit your predictions, report, actual versions, a fault-by-fault explanation,
and limitations. The chapter's five equal assessment categories are contract,
authorization/conflicts, durable duplicate handling, freshness/recovery
accounting, and reconstructable evidence. Repository-wide execution evidence is
in [the execution review](../../verification/later-studio-execution.md).
