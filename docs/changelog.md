# Changelog

## 0.1.2 (In Progress)
  * `repo` and `mount` keys in app specs are now optional

## 0.1.1 (June 18, 2015)
  * BREAKING CHANGE: We have changed the types of some of the values in app, lib, and test schema.  All commands to run in the container are now lists instead of single strings.

  * NEW: `dusty status` CLI command has been added.  This outputs a list of activated apps, libs, and services. It also informs if a container is associated with each.

  * FIXED: `dusty setup` now looks for your nginx config in all 3 default locations.


## 0.1.0 (June 15, 2015)
  * Initial release