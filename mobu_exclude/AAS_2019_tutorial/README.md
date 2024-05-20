# LSST Stack Tutorial at AAS 233

Thank you for joining us today! There are two sections for this tutorial:
Tuesday 9am - 12pm and 2pm - 5pm.

The only prerequisite is a computer with an internet connection in a modern
browser. You should have received instructions to make an account through NCSA
via email, and there are helpers circulating to assist with any technical
problems that come up.


These notebooks are designed to analyze an image that was processed with the
LSST stack. The raw data is available on the LSST Science Platform at
`/project/shared/data/ci_hsc_small`. Users should copy this to their home
directory to work on.

After copying, users will need to run `processCcd.py` at a terminal to process
the raw data into a finished, calibrated exposure and associated source catalog.
You can access a terminal inside the JupyterLab environment.  

To setup the terminal environment for running LSST stack commands, run:
```
source /opt/lsst/software/stack/loadLSST.bash
setup lsst_distrib
```
This configures paths and environment variables to select the software you want
to use.

To run the initial LSST processing stages, use the command: 
```
processCcd.py /PATH/TO/YOUR/REPO --rerun RERUN_NAME --id visit=903334 ccd=16
```
where `RERUN_NAME` is a name of your choosing; each time you process data, you
should give it a new rerun name (we'll talk more about this during the
tutorial). 

## Resources

- https://pipelines.lsst.io/getting-started/
  - Tutorial and helpful reference on similar topics we’re covering today. 
- https://pipelines.lsst.io/v/daily/
  - In-progress documentation on all of the Tasks and functions in the Stack
- https://community.lsst.org/
  - Q&A about LSST; someone might have already answered your question here.
- https://github.com/LSSTScienceCollaborations/StackClub/
  - “Stack Club” is a group of science users exploring the LSST Stack. Many helpful
notebooks, all on github.



