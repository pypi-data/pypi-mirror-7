from ajenti.api import *
from ajenti.plugins import *


info = PluginInfo(
    title='Services',
    icon='play',
    dependencies=[
        PluginDependency('main'),
        PluginDependency('dashboard'),
    ],
)


def init():
    import api

    try:
        import dbus
        import sm_upstart
        import sm_systemd
    except ImportError:
        pass
        
    import sm_sysvinit
    import sm_centos
    import sm_freebsd
    import main
    import widget
    import sensor
