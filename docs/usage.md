# Dusty CLI Usage

## Options

#### -d
```
Listen for user commands to Dusty

Usage:
  dusty -d [--suppress-warnings] [--preflight-only]

Options:
  --suppress-warnings  Do not display run time warnings to the client
  --preflight-only  Only run the preflight_check, then exit
```

Runs the Dusty daemon.  This action must be performed as root.
If you use Dusty's install script, a plist will be setup to run
this daemon automatically for you.

## Commands

To get more usage information, including arguments and options,
about any of these commands, use `dusty <command> -h`.

#### bundles
```
Manage application bundles known to Dusty.

A bundle represents a set of applications that are
run together. Dusty uses your activated bundles as
an entrypoint to resolve which apps and services it
needs to run as part of your environment.

You can choose which bundles are activated to customize
your environment to what you're working on at the moment.
You don't need to run your entire stack all the time!

Usage:
  bundles activate <bundle_names>...
  bundles deactivate <bundle_names>...
  bundles list

Commands:
  activate     Activate one or more bundles.
  deactivate   Deactivate one or more bundles.
  list         List all bundles and whether they are currently active.
```

#### config
```
Configure Dusty.

For a description of all available config keys,
run `config list`.

Usage:
  config list
  config listvalues
  config set <key> <value>

Commands:
  list          List all config keys with descriptions and current values.
  listvalues    List all config keys in machine-readable format.
  set           Set a string config key to a new value.
```
Used to edit Dusty's configuration values. These are stored in a configuration file
at `/etc/dusty/config.yml`, but you should **always** use `dusty config` to change
the configuration.

#### cp
```
Copy files between your local filesystem and Dusty-managed containers.
This tool also supports copying files directly between two containers.

To specify a file or directory location, either give just a path to
indicate a location on your local filesystem, or prefix a path with
`<service>:` to indicate a location inside a running container.

Usage:
  cp <source> <destination>

Examples:
  To copy a file from your local filesystem to the container of an app called `website`:
    cp /tmp/my-local-file.txt website:/tmp/file-inside-website-container.txt

  To copy a file from that same `website` container back to your local filesystem:
    cp website:/tmp/file-inside-website-container.txt /tmp/my-local-file.txt

  To copy a file from the `website` container to a different container called `api`:
    cp website:/tmp/website-file.txt api:/different/location/api-file.txt
```
To move files to containers, Dusty mounts a `/cp` directory to all containers that
it runs.  It can then move files into and from containers by moving them into and
out of the mounted directory.  Files are moved to and from the exact path specified
using a `docker exec mv` command.

#### disk
```
Basic tools for managing disk usage in the boot2docker VM

Usage:
  disk inspect
  disk cleanup_containers
  disk cleanup_images

Commands:
  inspect             Prints VM disk usage information
  cleanup_containers  Cleans docker containers that have exited
  cleanup_images      Removes docker images that can be removed without the --force flag
```
Used to manage the disk usage of Dusty's docker images and containers.  These can end
up taking up a lot of space on boot2docker's virtual disk, which is 20G max (dynamically
allocated by Virtualbox).

#### dump
```
Output diagnostic data, useful for filing bug reports.

Usage:
  dump

Commands:
  dump    Output diagnostic data from your system.
```
Used to dump state of Dusty and your system.  This is used for debugging.

#### logs
```
Tail out Docker logs for a container running a Dusty application
or service.

Usage:
  logs [-f] [--tail=NUM] <service>

Options:
  -f          follow log output
  --tail=NUM  show NUM lines from end of file
```
This is just a wrapper around the `docker logs` command.

#### repos
```
Manage repos referenced in the current Dusty specs.

By default, Dusty automatically manages the repos referenced
in your app and lib specs. This includes cloning the repo and
pulling updates from master to keep the Dusty-managed copy up-to-date.

Alternatively, you can override a repo to manage it yourself. This
is useful for actively developing apps and libs that depend on that
repo. To override a repo, use the `override` or `from` commands.

Usage:
  repos from <source_path>
  repos list
  repos manage <repo_name>
  repos override <repo_name> <source_path>
  repos update

Commands:
  from        Override all repos from a given directory
  list        Show state of all repos referenced in specs
  manage      Tell Dusty to manage a repo, removing any overrides
  override    Override a repo with a local copy that you manage
  update      Pull latest master on Dusty-managed repos
```

#### restart
```
Restart containers associated with Dusty apps or services.

Upon restart, an app container will execute the command specified
in its `commands.always` spec key. Restarting app containers will
also perform a sync of any local repos needed inside the container
prior to restarting.

Usage:
  restart [--no-sync] [<services>...]

Options:
  --no-sync    If provided, Dusty will not sync repos used by
               services being restarted prior to the restart.
  <services>   If provided, Dusty will only restart the given
               services. Otherwise, all currently running
               services are restarted.
```
Restarts active containers associated with Dusty.  The following actions are performed:
* Sync repositories on your mac to boot2docker (using rsyinc)
* Use the `docker restart` command for each active container
* Since containers are not recreated, specified `once` commands will not be run

#### scripts
```
Execute scripts defined in an app's spec inside a running app container.

Usage:
  scripts <app_name> [<script_name>] [<args>...]

Options:
  <args>  Arguments to pass to the script

Examples:
  To get information on all scripts available for an app called `website`:
    dusty scripts website

  To run the `rebuild` script defined inside the `website` app spec:
    dusty scripts website rebuild
```

#### setup
```
Run this command once after installation to set up
configuration values tailored to your system.

Usage:
  setup [--mac_username=<mac_username>] [--default_specs_repo=<specs_repo>] [--nginx_includes_dir=<nginx_dir>]

Options:
  --mac_username=<mac_username>         User name of the primary Dusty client user. This user
                                        will own all Docker-related processes.
  --default_specs_repo=<specs_repo>     Repo where your Dusty specs are located. Dusty manages this
                                        repo for you just like other repos.
  --nginx_includes_dir=<nginx_dir>      Directory in which Dusty will write its nginx config. Your
                                        nginx master config should source files from this directory
                                        using an `includes` directive.
```

#### shell
```
Open a shell inside a running container. Works with Dusty
apps and services.

Usage:
  shell <service>

Example:
  To start a shell inside a container for a service named `website`:
    dusty shell website
```

#### status
```
Give information on activated apps, services and
libs. Will present which ones are running in a
container and name to use when calling addressing them.

Usage:
  status
```
Lists active apps, libs, and services, and whether not there is a docker container currently
running associated with each.  Note that libs will never have an active container, since
they are just loaded inside app containers.  If an app or service is listed without an active
container, that means the container has exited since launch.  You can use `dusty logs` to
figure out why.

#### stop
```
Stop containers associated with Dusty apps and services.

This does not remove the containers unless run with --rm

Usage:
  stop [--rm] [<services>...]

Options:
  --rm  remove containers
```

#### sync
```
Sync repos from the local filesystem to the boot2docker VM.

Sync uses rsync under the hood to quickly sync files between
your local filesystem and the boot2docker VM. Sync will use
either the Dusty-managed version of a repo or your overridden
version, depending on the current repo settings.

Usage:
  sync <repos>...
```

#### test
```
Allow you to run tests in an isolated container for an app or a lib.
If args are passed, default arguments are dropped

Usage:
  test <app_or_lib_name> [<suite_name>] [<args>...] [--recreate]

Options:
  <suite_name>  Name of the test suite you would like to run
  <args>        A list of arguments to be passed to the test script
  --recreate    Ensures that the testing image will be recreated

Examples:
  To call test suite frontend with default arguments:
    dusty test web frontend
  To call test suite frontend with arguments in place of the defaults:
    dusty test web frontend /web/javascript
```
By default, old test containers
that exists on your machine are re-used when you run `dusty test` - this keeps tests speedy.
Pass the `--recreate` flag to `dusty test` in order to recreate your docker container.

#### up
```
Fully initialize all components of the Dusty system.

Up compiles your specs (subject to your activated bundles),
configures local port forwarding through your hosts file and
nginx, initializes your boot2docker VM and prepares it for
use by Dusty, and starts any containers specified by your
currently activated bundles.

Usage:
  up [--no-recreate] [--no-pull]

Options:
  --no-recreate   If a container already exists, do not recreate
                  it from scratch. This is faster, but containers
                  may get out of sync over time.
  --no-pull       Do not pull dusty managed repos from remotes
```
Launches active bundles, and all apps and services that they depend on.  This command is
optimized to successfully launch your system from any state, and not for speed.  The steps
that `dusty up` takes are:

 * Ensure your boot2docker VM is up
 * Pull your Dusty-managed repos
 * Assemble your specs, based on active bundles, into configuration for your hosts file, nginx,
and Docker Compose
 * Stops running Dusty containers
 * Sync repos from your mac to boot2docker
 * Re-create and launch your docker containers

#### validate
```
Validates specs to ensure that they're consistent with specifications

Usage:
  validate [<specs-path>]
```
Validates your Dusty specs.  This will:

 * Check that your specs contain required fields
 * Check that apps, libs, and services referenced inside your specs are all defined in your specs
 * Check that your dependency graph (of apps and libs) is cycle-free
You can optionally specify a directory to look for specs in; the default is to use whatever
directory is set to your Dusty specs repository, whether managed or overriden.