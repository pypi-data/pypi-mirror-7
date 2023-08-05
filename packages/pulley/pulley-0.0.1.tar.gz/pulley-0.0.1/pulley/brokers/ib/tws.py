
import os
import posixpath

IB_HOME = posixpath.join(os.path.expanduser('~'), 'tws')

cmd_install = """\
IB_HOME=%(IB_HOME)s
rm -rf $IB_HOME
mkdir $IB_HOME
cd $IB_HOME
wget https://download2.interactivebrokers.com/download/unixmacosx_latest.jar
jar xf unixmacosx_latest.jar
"""

cmd_run = """\
IB_HOME=%(IB_HOME)s
cd $IB_HOME/IBJts
java -cp jts.jar:total.2013.jar -Xmx512M -XX:MaxPermSize=128M jclient.LoginFrame .
"""

def install():
    cmd = cmd_install % {'IB_HOME': IB_HOME}
    os.system(cmd)

def run():
    cmd = cmd_run % {'IB_HOME': IB_HOME}
    os.system(cmd)
