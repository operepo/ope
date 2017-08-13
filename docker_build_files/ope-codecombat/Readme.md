
-- To force DB to do an import, delte the volumes/codecombat/data/.db_updated file. Next time the container starts it will do a full db import.

-- First startup (or after forcing a db import) will import the mongodb data. This will take a couple of minutes and crank your cpu for the duration.
During this time, the website will not be up. 

-- Meant to be run with the OPE project with docker compose. To run witout docker-compose, use the -P option to expose ports and mount the volume
(see docker-compose-include file)

