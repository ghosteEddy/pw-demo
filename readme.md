# Overall
## Overall design is:
1.  Data received through Receiver (Ylive) which will save to questDB
2.  Aggregrator query periodically from questDB and send data to Ticker server
3.  Ticker server is a webserver that stored and received data through Http request

# Usage
- copy .env to the root folder (same location as docker compose file)
- run all containers `docker compose up -d --build`
  
# Notes
- These projects use python 3.12
- actually data shouldn't be kept or treat as float
- Production mode is not set because these shouldn't be on production yet
- For simple deployment, many implementations are simplified which could result as security risks.
- In aggregrator script, I don't want to mess the file system yet. Therefore, time input could be duplicate or inaccurate. This could be fixed by using a dedicate scheduler or store current progress somewhere. Actually, crontab is not good for this script purpose.