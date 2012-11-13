2001 November 30 * matt.wilkie@gov.yk.ca

The central "brain" script is out2anudem.aml. It is an "all-in-one" synthesis of the other ANUDEM scripts.

Conceptual Model, For each tile do: (- done, + todo)

   - export contours, streams, boundary poly, etc. to ungenerate files
   - calc stats (min/max elev, bounds) [optimal tolerances?]
   - write anudem.cmd file
   - run anudem
   + convert anudem outputs (dem and diagnostic files) to Arc
   + delete intermediate files(?)


| * out2anudem * | all in one script |
| cover2generate | convert Arc coverage to generate file |
| build_cmd      | build ANUDEM command file |
| build_dem      | calculate the dem |
| adem2grid      | convert ANUDEM dem to Arc Grid |
