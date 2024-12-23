###########################
#### MODULES ####
###########################
$MaxMessageSize 64k

module(load="imfile")

template(name="SingleLineJSONFormat" type="string" string="%msg%\n")

###########################
#### INPUTS ####
###########################

input(type="imfile"
      File="/var/log/logstash/anomalyhunter/*.syslog"
      Tag="anomalyhunter"
      Severity="info"
      Facility="local6"
      readMode="0"
      escapeLF="off"
)

###########################
#### OUTPUTS ####
###########################

if $syslogtag == 'anomalyhunter' then @@172.16.0.52:514;SingleLineJSONFormat
