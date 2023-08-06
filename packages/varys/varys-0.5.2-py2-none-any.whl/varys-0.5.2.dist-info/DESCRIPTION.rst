Varys
=====

Varys is a python package for anyone who has to work with behavioral data
logs.

Chances are, you need that data in another format before you can work with it.
If you're like most of us, you have some collection of scripts around
somewhere that can parse format A, other scripts that write format B, and
somewhere in the middle you'll sandwich some logic that actually has something
to do with your experiment.

Our goal is to reduce the load down to this last bit.

Varys breaks its work into three segments: LogParser, EventBuilder, and
FileWriter. Of these, only EventBuilder needs to be customized per experiment.

LogParser is meant to grow with time to be able to parse an increasingly
diverse list of input types. At the moment we support simple TDF and CSV
formats, as well as the FIDL format used by the eponymous software package
from Washington University in St Louis. But we're willing and interested to
work with users to expand that list.

EventBuilder takes input from a LogParser, and turns it into a list of "event"
dictionaries. These can contain arbitrary values, but at a minimum must
contain "name," "onset" and "duration."

FileWriter takes these ordered dictionaries, then writes files consumable by
analysis packages. At the time of this writing, we support SPM, FIDL, tab
delimited .txt, and python's Pickle, but here again we're willing and eager to
expand the list of supported formats.

We've thrown in some special options for working with neuroimaging data, for
concatenating runs, and other fun stuff too.

So please, take a look at the examples list, see if any of them sound like
your situation, and feel free to use them as a starting point for your own
work.

Installation
============

Varys uses scipy, which in turn uses numpy, and as of yet we're too lazy to do
the fancy dancing needed to auto-install numpy as a dependency. So it'll take
two steps:

```
pip install numpy
pip install varys
```

Or grab the latest development version from https://github.com/beOn/varys, and
install using setup.py.

Supported Formats
=================

Currently supported formats are:

Input: .txt, .tdf, .csv, .fidl

Output: spm, fidl, pickle, txt (tab delimited)

Examples
========

Varys provides several EventBuilder subclasses for handling data in different
ways - in short, you can either have your data handed to you as a list of rows
(as dicts), or you can have it handed to you one row at a time. Usually the
latter approach is the most helpful.

There are several EventBuilder subclasses you can dive into, but here we'll
cover the kinds you're most likely to use: RowWise_EventBuilder,
RowWise_fMRI_EventBuilder, and FixedDuration_EventBuilder. Please forgive the
long names. Names were never my strong suit.

Using either of the two RowWise classes involves creating your own subclass,
whereas FixedDuration_EventBuilder is meant to be configured and used without
subclassing, making it easier to write very simple EventBuilders.

Enough chit chat. Let's look at some examples.

Mise en Scène
-------------

For the following examples, we'll pretend that a few things are the case:

- Subject data is in /data/sub_N/run_M.txt, where 'N' and 'M' are two-digit
subject and run numbers, respectively (ie 01, 02, etc.).
- The event name is whatever value is stored in the column named "trial_type"
- All trials have a duration of 10.0
- Trial onset time is in a column named 'cue_onset'
- Answer accuracy is in a column named "acc", and is either '1' or '0'.
- The first trial's onset time is to be used as time = 0
- For the fMRI subclass, the TR is .7, because your scanner is awesome (written
circa 2014)
- For the sake of clarity, we're going to be sloppy about not catching
exceptions.
- Each run's data is in its own file
- You have three subjects, 1, 2, and 3
- You want to save the resulting files into "/data/output"
- Your source files fall into the correct order if sorted alphabetically
- You want to use the events in SPM, and save a pickled version as well for
later use in python

RowWise_EventBuilder
--------------------

This is probably the most useful subclass, and is pretty simple. Let's take a
look.

```python
from varys.EventBuilder import RowWise_EventBuilder
class basic_EventBuilder(RowWise_EventBuilder):
    def __init__(self):
        super(basic_EventBuilder, self).__init__()
        self.trial_onset = 0
        self.data_glob_templates = ["/data/sub_%02d/run_*.txt"]
        self.subjects = [1,2,3]
        self.output_dir = "/data/output"
        self.output_formats = ["spm", "pickle"]
    def events_for_row(self, row_dict):
        events = []
        name = row["trial_type"]
        onset = float(row["cue_onset"]) - self.trial_onset
        acc = row["acc"]
        if name and onset:
            events.append(["name":name,
                           "onset":onset,
                           "duration":10.0,
                           "acc":acc,
                           "set":"all_events"])
        return events
    def handle_run_start(self, run_idx, run_data, file_name):
        self.trial_onset = float(run_data[0]["cue_onset"])

eb = basic_EventBuilder()
eb.run()
```

To get the details on this and the other subclasses, check out the noted in the
related code. But since we're here, let's take this apart a little bit.

```handle_run_start``` gets called at the start of every run, and as such is a
great place to find and set aside any run-wide variables, like run onset time.
That's exactly what we do in this example.

```events_for_row``` gets called once per row of data in your original file,
and is expected to return a list of dicts (one dict per event). You might be
wondering what this set entry is all about, and why we return a list of
events, instead of just one. From time to time, analysis will require that you
create several different event sets - one including all trials, and one
including only those trials which were answered correctly, for example.
Suppose we wanted to do exactly this for the current example. Then we'd change
the if block of events_for_row to read as follows:

```python
    if name and onset:
        events.append(["name":name,
                       "onset":onset,
                       "duration":10.0,
                       "acc":acc,
                       "set":"all_events"])
        if acc == "1":
            events.append(["name":name,
                           "onset":onset,
                           "duration":10.0,
                           "acc":acc,
                           "set":"acc_events"])
```

Note that we used a different ```set``` for the second event. This will cause
EventBuilder to write two sets of files for the two event sets. You might not
need this, but if you do, it sure is nice not to have to write a whole 'nother
subclass!

The ```init``` method just presets a few values specific to this experiment.
Note that you can override these. If you moved the script to another machine,
where the data was instead in ```/my_data/subjects/sN/run_M.txt``` (remembering
that N and M are two-digit subject and run numbers, respectively), and you
wanted to save the results to ```/analyses/new_data```, you don't have to modify
the subclass. You can just change a couple of values, then call ```run()```:

```python
eb = basic_EventBuilder()
eb.data_glob_templates = ["/my_data/subjects/s%02d/run_*.txt"]
eb.output_dir = "/analyses/new_data"
eb.run()
```

```subjects``` can be similarly changed.

RowWise_fMRI_EventBuilder
-------------------------

This class is pretty much the same as RowWise_EventBuilder, but has a few extra
features specific to fMRI. Let's take a look, and go through it afterwards. I'll
omit everything that would be identical, but do remember to include it in your
own subclasses.

```python
from varys.EventBuilder import RowWise_EventBuilder
class basic_fMRI_EventBuilder(RowWise_EventBuilder):
    def __init__(self):
        super(basic_fMRI_EventBuilder, self).__init__()
        # same as RowWise_EventBuilder, with one extra property:
        self.TR = .7

    # events_for_row same as RowWise_EventBuilder
    # handle_run_start same as RowWise_EventBuilder

    def tr_count_for_run(self, run_idx, file_name, raw_rows, events):
        """ return the TR count for the given run. """
        if run_idx < 2:
            return 130
        else:
            return 200
```

So, there are really only two differences here, and their utility might not be
immediately apparent (we'll get there): the property ```TR```, and the method
```tr_count_for_run```. In this example, we set the TR to .7, and return one of
two values for ```tr_count_for_run``` depending on the run number.

So, who gives a flying leap at a rolling doughnut about TRs and how many there
are per run? Anyone who needs to concatenate their runs, that's who. We use
these two properties to figure out how much time to add to the onset of all
events for each run. So if you have 100 TRs of length .7 each in run 1, every
event in run 2 will have 70.0 added to its onset time. But take note, *this will
only happen if you set the ```concat_sets``` property to a list of the sets
whose runs you'd like to concatenate*. We do it this way because you may not
want to concatenate runs for every event set. So, if we wanted to concatenate
runs, but only for the event set that contains accurate response events
(acc_events), we'd change the init method like so:

```python
    def __init__(self):
        super(basic_fMRI_EventBuilder, self).__init__()
        # same as RowWise_EventBuilder, with one extra property:
        self.TR = .7
        self.concat_sets = ["acc_events"]
```

Take note, some output formats, such as fidl, absolutely require concatenated
runs. If you specify one of these output formats, *all runs in all sets will be
automatically concatenated*, even if you don't set concat_sets.

Skipping Output
---------------

Sometimes, you don't actually want to write the event set out to any file. You
just want to parse the events, then keep working with them in your code.

To do this, set the ```skip_output``` property to True, then retrieve the values
for the subject you're interested in. Working with our ```basic_EventBuilder```,
if we wanted to get the list of lists of event dicts for subject 1, we'd do as
follows:

```python
eb = basic_EventBuilder()
eb.skip_output = True
eb.run()
sub_num = 1
s1_events = eb.sub_data[sub_num]["acc_events"]
```

One Giant Input File
--------------------

It may be the case that, instead of having one input file per run, everything's
in one big table, and there's some column whose value changes every time a new
run's data begins. To handle this, just set the ```run_field``` property to the
name of that column. If this were the case for our example, and the name of the
column was "run_number", we'd just make a slight modificaiton to the init
method:

```python
class basic_EventBuilder(RowWise_EventBuilder):
    def __init__(self):
        super(basic_EventBuilder, self).__init__()
        # everything is the same as before, but add:
        self.run_field = "run_number"
    # everything else is the same as before
```

Not so bad, eh?

TODO
----
- FixedDuration_EventBuilder, once it's ready

Reporting Bugs, Requesting Features
===================================

Submit all bug reports and feature requests using the github ticketing system:
https://github.com/beOn/cili/issues

Please make an effort to provide high quality bug reports. If we get one that
just says, "sample range extraction is broken," we'll probably trash it without
a second look, because the submitter is probably the kind of person who saps
energy from everything they touch.

A good bug report should include three things:

1. Steps to reproduce the bug
2. Expected result
3. Actual result

The goal is to give the developers the ability to recreate the bug before
their own eyes. If you can give us that, we'll take a very close look.

Why Varys?
==========

Because it manipulates events: http://gameofthrones.wikia.com/wiki/Varys

TODO: Thanks, credit to CCP Lab


