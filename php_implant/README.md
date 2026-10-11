# PHP SCA implant

`sca_prepand.php` implements support for coverage and parameter usage collection in PHP web-application.

## Usage

### XDebug config

[__XDebug__](https://github.com/xdebug/xdebug) extension should be installed and configured with coverage mode:

```ini
[xdebug]
zend_extension=/path/to/xdebug/extension/xdebug.so

xdebug.mode = debug,coverage

xdebug.start_with_request = yes

xdebug.client_host = DEBUG_CLIENT_HOST
xdebug.client_port = 9003

```

### uopz config

[__uopz__](https://github.com/krakjoe/uopz) extension should be installed and configured with propper `exit` operation handling:

```ini
[uopz]
uopz.exit = 1
```

### Implant integration

In order to use PHP SCA implant it should be placed in a directory that is reachable by the target PHP application.

The following config should be added into PHP configuration (config.d/):

```ini
auto_prepend_file = "/path/to/sca_prepand.php"

coverage_report_path = "/path/to/reports/output/dir/"
coverage_dump_path = "/path/to/coverage/output/dir/"
```

_NOTE:_ `coverage_rpeort_path` and `coverage_dump_path` directgories should be reachable by SCA python app if local report access configuration of SCA is used.