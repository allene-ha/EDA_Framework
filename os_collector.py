import psutil

# def collect_os_metrics():
#     # Get CPU utilization

#     res = {}
#     res['cpu'] = psutil.cpu_percent()

#     memory_info = psutil.virtual_memory()
#     res['mem'] = {}
#     res['mem']['total'] = memory_info.total
#     res['mem']['available'] = memory_info.available
#     res['mem']['percent'] = memory_info.percent
#     res['mem']['used'] = memory_info.used
#     res['mem']['free'] = memory_info.free
#     res['mem']['active'] = memory_info.active
#     res['mem']['inactive'] = memory_info.inactive
#     res['mem']['buffers'] = memory_info.buffers
#     res['mem']['cached'] = memory_info.cached
#     res['mem']['shared'] = memory_info.shared
#     res['mem']['slab'] = memory_info.slab
    
#     disk_io = psutil.disk_io_counters()

#     res['disk'] = {}
#     res['disk']['read_count'] = disk_io.read_count
#     res['disk']['write_count'] = disk_io.write_count
#     res['disk']['read_bytes'] = disk_io.read_bytes
#     res['disk']['write_bytes'] = disk_io.write_bytes

#     return res


def collect_os_metrics(): # influx
    
    res = {}
    res['table'] = 'os_metric'
    res['data'] = {}
    field = res['data']
    field['cpu_percent'] = psutil.cpu_percent()

    memory_info = psutil.virtual_memory()
    field['mem_total'] = memory_info.total
    field['mem_available'] = memory_info.available
    field['mem_percent'] = memory_info.percent
    field['mem_used'] = memory_info.used
    field['mem_free'] = memory_info.free
    field['mem_active'] = memory_info.active
    field['mem_inactive'] = memory_info.inactive
    field['mem_buffers'] = memory_info.buffers
    field['mem_cached'] = memory_info.cached
    field['mem_shared'] = memory_info.shared
    field['mem_slab'] = memory_info.slab
    
    # Get the disk usage information
    disk_usage = psutil.disk_usage("/")

    # Calculate the disk usage percentage
    field['disk_percent'] = disk_usage.percent

    disk_io = psutil.disk_io_counters()

    field['disk_read_count'] = disk_io.read_count
    field['disk_write_count'] = disk_io.write_count
    field['disk_read_bytes'] = disk_io.read_bytes
    field['disk_write_bytes'] = disk_io.write_bytes

    return res

