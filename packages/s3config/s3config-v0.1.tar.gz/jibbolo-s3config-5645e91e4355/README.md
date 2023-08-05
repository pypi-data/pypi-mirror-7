#Read config file from Amazon S3 url. 
###Parse data from json or yalm and convert to python dict.

Example:

    config = S3Config("s3://s3config/config.json").read()