# system-test

Jupyter Notebooks curated by SQuaRE for testing

***Note** there is a special branch called 'prod' in this repo that is continuously deployed into production.
Do not update this branch unless you know what you are doing. (Better instructions than "know what you are doing" will be forthcoming once the workflow settles down).

## General setup

The most common workflow is to work in an https://data.lsst.cloud JupyterLab session.
If you're working on these, you almost certainly don't want to check in any outputs.
There is a [pre-commit](https://pre-commit.com) config that will prevent this, but in order to use it, you must clone this repo manually so that you have write access to it.
Once you have started your jupyterlab session, start a terminal and:

```
mkdir ~/mynotebooks  # Or wherever you want to check this repo out
cd ~/mynotebooks
git clone https://github.com/lsst-sqre/system-test.git
make init
```