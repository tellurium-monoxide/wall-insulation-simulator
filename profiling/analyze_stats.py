import os

import cProfile
import pstats
from pstats import SortKey
try:
    current_dir=(os.path.dirname(os.path.realpath(__file__)))
    main_script=current_dir+'/../src/main.py'
    
    # cProfile.__main__.run([        
        # '-o','output',
        # '-s', 'time',
        # main_script
    # ])
    
    profile_result_file=current_dir+"/wis.pstats"
    
    p = pstats.Stats(profile_result_file)
    p.sort_stats(SortKey.CUMULATIVE).print_stats(20)
    
    p.sort_stats(SortKey.TIME).print_stats(20)

except Exception:
    print(Exception.what())
    print("Failed profiling")
