==================
NEWS about uci-vms
==================

Overview of changes to uci-vms in reverse chronological order.

0.1.2
=====

 * Add 'vm.final_message' so VM daughter classes with specific needs can
   override (LP: #1328170).

0.1.1
=====

 * Add debian packaging (ubuntu native for now).

 * Makes 'vm.vms_dir' a PathOption to get '~' support.

 * Add 'vm.poweroff' as a config option defaulting to True so new VM classes
   (or users) can override if/when needed.

 * Fix test issue uncovered in trusty/utopic.

 * Fix minor compatibility changes with uci-tests.

0.1.0
=====

 * Add uci-vms config command.

0.0.1
=====

First release.
