#@+leo-ver=5-thin
#@+node:maphew.20120203103945.1813: * @file xx-calc-trans.py
''' scratchpad file: test out ideas for how to calculate transparency percentage of each ring buffer given approximate start and end values.
'''
ring_width = 1000   # width of single buffer ring
num_rings = 7   # total number of rings to create
upper_t = 50    # uppermost layer transparency %
lower_t = 80    # lowermost layer transparency %

transparency_step = (lower_t - upper_t) / num_rings # percent to lighten/darken each ring

first_ring = ring_width                 # 1000


# build dictionary of transparency percentages tied to ring number
transparency_dict = {}
for e,i in enumerate(range(upper_t, lower_t, transparency_step)):
    print "Ring #",e, "transparency :", i
    transparency_dict[e] = i


#The plus 1 is to counteract range() which stops *at* the last number
last_ring = ring_width * (num_rings + 1)  # 1000 * 8. 

for step,ring in enumerate(range(first_ring, last_ring, ring_width)):
    #calc transparency for this ring (step)
    my_transparency = transparency_dict[step]

    print step,"Buffer_{0} at width -{1} and transparency {2}".format(step, ring, my_transparency)
    
#@-leo
