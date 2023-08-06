# Qiniufops

------
Qiniu bucket image persistent operations


> * `qiniufops.cfg`  Configure file,in /etc/qiniu/
> * `qiniufops`      python scripts,in /usr/local/bin/

------
## Usage

### set qiniufops.cfg configure file, then run qiniufops.

```conf

[qiniu]
`accesskey:`           Your qiniu access key
`secretkey:`           Your qiniu access secret key
`bucket:`              Qiniu bucket name

[fops]
One or more image stylename:style,one per line
example:
`stylename1:style1`
`stylename2:style2`
`!qsmalllow:imageView2/1/w/320/h/320/q/60`

```

