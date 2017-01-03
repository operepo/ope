
Open Prison Education - Canvas Server


Tech Notes - 
SHARDING CHANGES
The gem for switchman (/opt/canvas/.gems/gems/switchman-1.8.0/app/models/switchman/shard_internal.rb) sets
10 trillion to seperate shard ids and local ids. We move this 10_000_000_000_000 ==> 1_000_000_000_000_000_000

We push shard ids to the last digit in a 64bit int. We use the next 7 digits for our facility id.

Max Value -		9_223_372_036_854_775_807  ( 64 bit integer max possible value )
Shard Range - 	*_000_000_000_000_000_000  (normally set at 10trillion, but that interfered
											with our range so we bump it up, this still
											allows for 10 shards)
School Range - 	0_***_***_*00_000_000_000 ( this gives 99 billion ids for each table and
											9,999,999 facilities )
Local ID Range -0_000_000_0**_***_***_*** ( Leaves 99 billion for local ids )

FACILITY ID

Generate a facility ID based on the current minute. We then subtract 12/1/16 from it so that is
the start of our range. This should give us about 19.5 years before the range rolls over. The code
will roll over automatically at that time.

These ids are generated when a new canvas server boots the FIRST time
 (saved in volumes/canvas/tmp/db_sequence_range). Delete this file and restart the canvas server to generate
 a new range.

Conflict Danger - If you start up 2 canvas servers at the exact same minute they could potentially end up
with the same facility ID. Otherwise the odds of 2 servers ending up with the same ID are miniscule.

 
EFFECTS ON SHARD DATABASES
Unknown - You should be able to have 9 or 10 shard servers with these changes in place. In the prison
environment we have less issue with student volume and more issues with connectivity - hence the
changes to allow for offline sync capabilities.
