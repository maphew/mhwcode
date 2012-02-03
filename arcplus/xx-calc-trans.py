#@+leo-ver=5-thin
#@+node:maphew.20120203103945.1813: * @file xx-calc-trans.py
''' scratchpad file: test out ideas for how to calculate transparency percentage of each ring buffer given approximate start and end values.
'''
ring_width = 1000   # width of each buffer ring
num_rings = 7   # total number of rings to create
darkest = 50    # uppermost layer transparency %
lightest = 80    # lowermost layer transparency %

first_ring = ring_width                 # 1000


def get_transparency_dict(darkest, lightest, steps):
    '''build dictionary of transparency percentages with specified number of steps
    Returns {0:50, 1:55, 2:60 ...}'''
    transparency_dict = {}
    stepsize = (lightest - darkest) / steps     # percent to lighten/darken each ring
    for e,i in enumerate(range(darkest, lightest, stepsize)):
        print "Ring #",e+1, "transparency is", i
        transparency_dict[e + 1] = i
    return transparency_dict
    
transparency_dict = get_transparency_dict(darkest, lightest, num_rings)

buffers = range(1,8)
for buffer in buffers:
    print "Buffer", buffer, transparency_dict[buffer]
    
    
#def get_buffer_transparencies(first_ring, last_ring, ring_width)

#The plus 1 is to counteract range() which stops *at* the last number
last_ring = ring_width * (num_rings + 1)  # 1000 * 8. 

for step,ring in enumerate(range(first_ring, last_ring, ring_width)):
    #calc transparency for this ring (step)
    my_transparency = transparency_dict[step+1]

    print step,"Buffer_{0} at width -{1} and transparency {2}".format(step+1, ring, my_transparency)
    
#@-leo
