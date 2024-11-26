#!/bin/sh
curl -s https://www.sudo.ws/releases/stable/ |grep "is version " |head -n1 |sed -e 's,.*is version ,,;s,\. .*,,'
