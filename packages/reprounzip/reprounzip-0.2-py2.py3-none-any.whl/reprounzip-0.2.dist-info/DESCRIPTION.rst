ReproZip is a tool aimed at scientists using Linux distributions, that
simplifies the process of creating reproducible experiments from programs.

It uses the ptrace facilities of Linux to trace the processes and files that
are part of the experiment and build a comprehensive provenance graph for the
user to review.

Then, it can pack these files in a package to allow for easy reproducibility
elsewhere, either by unpacking and running on a compatible machine or by
creating a virtual machine through Vagrant.

This package holds the unpacker components (and the 'reprounzip' command-line
utility).


