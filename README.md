This utility works as a proxy for Jackett and is designed to filter the final results (by torrent volume and/or number
of seeds)

The following console arguments are used to start the utility:

--util_port - Port on which the proxy web server will start / Optional param / Type - int / Default value - 9118

--jackett_host - Host\Port Jackett / Required param / Type - str
--jackett_protocol - Jacket protocol / Optional param / Type - str / Default value - http
--jackett_api_key - Jackett apikey / Optional param / Type - str

--min_seeds - Minimum seeds in result / Optional param / Type - int / Default value - 2
--min_size_of_torrent - Minimum size of torrent in Gb / Optional param / Type - float
--max_size_of_torrent - Maximum size of torrent in Gb / Optional param / Type - float