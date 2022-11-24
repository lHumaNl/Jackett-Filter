# Jackett-Filter

This utility works as a proxy for Jackett (https://github.com/Jackett/Jackett) 
and is designed to filter the final results (by torrent size and/or number of seeds)

## Console arguments

Arg | Required | Default value | Description
-|-|-|-
`--util_port` | False | 9118 |Port on which the proxy web server will start
`--config_file` | False | `config.json` | File name with configs. File must be placed in `config` folder near `main.py`

## Instruction for JSON config file

First of all, you need to create `config` folder near `main.py` file.
Then create inside this folder blank new file. Strongly recommended to create file with name `config.json`, 
because in the future it is not expected to enter a console argument `--config_file`.

### JSON config keys

Key | Required | Default value | Type | Description | Example
-|-|-|-|-|-
`link` | True | Null | String | Link to Jackett | `"link": "http://<host>:9117"`
`min_seeds` | False | 2 | Integer | Minimum seeds in result | `"min_seeds": 2`
`min_size` | False | 1 | Float | Minimum size of torrent in Gb | `"min_size": 1.5`
`max_size` | False | Null | Float | Maximum size of torrent in Gb | `"max_size": 145`

### JSON config Example

```
{
  "link": "http://10.10.0.21:9117",
  "min_seeds": 2,
  "min_size": 1
}
```

## Installation using Docker

1. Build image `docker build -t jackett-filter .`
2. Run container ```docker run -d
    --restart always
    -p 9118:9118
    -v <path-to-config-folder>:/app/config
    -it
    --name jackett-filter
    jackett-filter```