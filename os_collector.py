import psutil

def collect_os_metrics():
    # Get CPU utilization

    res = {}
    res['cpu'] = psutil.cpu_percent()

    memory_info = psutil.virtual_memory()
    res['mem'] = {}
    res['mem']['total'] = memory_info.total
    res['mem']['available'] = memory_info.available
    res['mem']['percent'] = memory_info.percent
    res['mem']['used'] = memory_info.used
    res['mem']['free'] = memory_info.free
    res['mem']['active'] = memory_info.active
    res['mem']['inactive'] = memory_info.inactive
    res['mem']['buffers'] = memory_info.buffers
    res['mem']['cached'] = memory_info.cached
    res['mem']['shared'] = memory_info.shared
    res['mem']['slab'] = memory_info.slab
    
    disk_io = psutil.disk_io_counters()

    res['disk'] = {}
    res['disk']['read_count'] = disk_io.read_count
    res['disk']['write_count'] = disk_io.write_count
    res['disk']['read_bytes'] = disk_io.read_bytes
    res['disk']['write_bytes'] = disk_io.write_bytes

    return res

