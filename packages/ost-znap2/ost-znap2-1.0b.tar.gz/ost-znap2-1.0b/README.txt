ost.znap2
=========

Znap2 is a universal ZoDB snapshotter. It allows making multiple snapshots of
ZoDB database(s) and restoring the database(s) to any past snapshot.

Usage
-----

Before we make any snapshots, we need to intialize the snapshot storage::

    znap2 init <db-file> [...]

This creates .znap2 directory that will contain the configuration and all
snapshots. Initially only configuration file is created and the length of all
database files is recorded there.

After the storage is initialized we can make snapshots::

    znap2 save <snapshot-id>

This will store the tail of each database file that the storage is tracking
and a copy of its index file. This information is sufficient to restore the
snapshot of ZoDB because all writing to the main database file always happens
at the end.

To list available snapshots use the following command::

    znap2 list

Some time later we can revert to an earlier stored snapshot::

    znap2 restore <snapshot-id>

This will truncate the databases to their size at the time of initialization,
then append the stored tails and replace the index files with stored copies of
the index files.

Finally the snapshots that are no longer needed can be deleted with::

    znap2 delete <snapshot-id>

Note that packing the database will invalidate all snapshots. If you need to
pack the database, delete the storage and start over.
