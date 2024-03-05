





def format_time(t):
    if t>1:
        s=int(t)
        d=s//(24*3600)
        h=(s - d * 24 * 3600) // 3600
        m=(s - d * 24 * 3600 - h * 3600) // 60
        s=(s - d * 24 * 3600 - h * 3600 - m * 60)
        if d>0:
            return "%dd%dh%dm%ds" % (d,h,m,s)
        elif h>0:
            return "%dh%dm%ds" % (h,m,s)
        elif m>0:
            return "%dm%ds" % (m,s)
        else:
            return "%ds" % (s)
    else:
        return "%dms" % (t*1000)

def format_time_hms(t):

    ts=int(t)
    d=ts//(24*3600)
    h=(ts - d * 24 * 3600) // 3600
    m=(ts - d * 24 * 3600 - h * 3600) // 60
    s=(ts - d * 24 * 3600 - h * 3600 - m * 60)

    return "%02dh%02dm%02ds" % (h,m,s)
    
    
def format_time_hm(t):

    ts=int(t)
    d=ts//(24*3600)
    h=(ts - d * 24 * 3600) // 3600
    m=(ts - d * 24 * 3600 - h * 3600) // 60

    return "%02dh%02dm" % (h,m)
