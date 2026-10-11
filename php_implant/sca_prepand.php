<?php

/**
 * PER FILE COV COLLECTION BEGIN
 */

define("COV_SUFFIX", ".covinfo");

function load_coverage_info($php_file_path) {
    $cov_file_path = $php_file_path . COV_SUFFIX;
    if (file_exists($cov_file_path)) {
        $data = file_get_contents($cov_file_path);
        return (array)json_decode($data);
    }
    return [];
}

function store_coverage_info($php_file_path, $cov_info) {
    $cov_file_path = $php_file_path . COV_SUFFIX;
    $encoded_cov_info = json_encode((object)$cov_info);
    file_put_contents($cov_file_path, $encoded_cov_info);
}

function update_coverage_info($php_file_path, $cov_info) {
    $cov_info_to_update = load_coverage_info($php_file_path);
    $timestamp = time();
    $new_cov = array_diff_key($cov_info, $cov_info_to_update);
    foreach ($new_cov as $line => $v) {
        $cov_info_to_update[$line] = $timestamp;
    }
    store_coverage_info($php_file_path, $cov_info_to_update);
}

/**
 * PER FILE COV COLLECTION END
 */

/**
 * Helper class that registers parameter usage througout PHP application codebase
 * 
 * In order to register paramter usage the following call should be made from application codebase:
 * 
 * \InputReporter::getInstance()->report("GET", "some_param_used");
 */
class InputReporter 
{
    private static ?InputReporter $instance = null;
    private array $usage = [];

    private function __construct() 
    {
    }

    private function __clone() 
    {
    }

    public function __wakeup() 
    {
        throw new \Exception("Cannot unserialize a singleton.");
    }

    public static function getInstance(): self 
    {
        if (self::$instance === null) {
            self::$instance = new self();
        }
        return self::$instance;
    }

    public function report(string $type, string $name): void 
    {
        if (!defined("INPUT_PARAMS_COLLECT"))
        {
            return;
        }
        if (!array_key_exists($type, $this->usage))
        {
            $this->usage[$type] = [];
        }
        if (!array_key_exists($name, $this->usage[$type]))
        {
            $this->usage[$type][$name] = [];
        }
        $backtrace = array_slice(debug_backtrace(0), 1);
        $clean_backtrace = [];

        foreach ($backtrace as $belem)
        {
            if (!isset($belem["line"]) || !isset($belem["file"])) {
                continue; // skip frames from call_user_function and similar
            }
            $elem = [
                "file" => $belem["file"],
                "line" => $belem["line"],
                "function" => $belem["function"]
            ];
            if (isset($belem["class"])) {
                $elem["php_class"] = $belem["class"];
            }
            if (isset($belem["type"])) {
                $elem["php_type"] = $belem["type"];
            }
            if (str_ends_with($elem["file"], basename(__FILE__)))
            {
                continue;
            }
            $clean_backtrace[] = $elem;
        }
        $hash = hash('sha256', json_encode($clean_backtrace));
        $this->usage[$type][$name][$hash] = $clean_backtrace;
    }

    public function dump(string $path): void
    {
        $encoded = json_encode($this->usage, JSON_PRETTY_PRINT);
        file_put_contents($path, $encoded);
    }

    public function get_usage(): array
    {
        return $this->usage;
    }
}

/**
 * Helper class that automates input usage from superglobal arrays by wrapping them:
 * 
 * $_GET = \DictWrapper::wrap("GET", $_GET);
 */
class DictWrapper implements \ArrayAccess, \Iterator
{
    private array $orig = [];
    private int $position = 0;
    private string $name = "";

    private array $prefix_list = [];
    private bool $use_prefix_list = false;

    public static function wrap(string $name, array $orig, array $prefix_list = []): mixed 
    {
        if (defined("INPUT_PARAMS_COLLECT")) {
            return new \DictWrapper($name, $orig, $prefix_list);
        }
        return $orig;
    }

    public function __construct(string $name, array $orig, array $prefix_list = [])
    {
        $this->name = $name;
        $this->orig = $orig;
        if (!empty($prefix_list))
        {
            $this->prefix_list = $prefix_list;
            $this->use_prefix_list = true;
        }
    }
    private function report($value): void
    {
        if (!$this->use_prefix_list)
        {
            \InputReporter::getInstance()->report($this->name, $value);
        }
        else
        {
            foreach ($this->prefix_list as $tag => $prefix)
            {
                if (str_starts_with($value, $prefix))
                {
                    \InputReporter::getInstance()->report($tag, $value);
                    break;
                }
            }
        }
    }
    public function getOrig(): array
    {
        return $this->orig;
    }
    public function getName(): string
    {
        return $this->name;
    }
    public function offsetExists(mixed $offset): bool
    {
        $this->report($offset);
        return isset($this->orig[$offset]);
    }
    public function offsetGet(mixed $offset): mixed
    {
        $this->report($offset);
        $value = $this->orig[$offset] ?? null;
        return $value;
    }
    public function offsetSet(mixed $offset, mixed $value): void 
    {
        if (is_null($offset)) {
            $this->orig[] = $value;
        } else {
            $this->orig[$offset] = $value;
        }
    }
    public function offsetUnset(mixed $offset): void 
    {
        unset($this->orig[$offset]);
    }
    public function rewind(): void
    {
        $this->position = 0;
    }
    public function current(): mixed
    {
        $currentKey = array_keys($this->orig)[$this->position];
        return $this->orig[$currentKey];
    }
    public function key(): mixed
    {
        return array_keys($this->orig)[$this->position];
    }
    public function next(): void
    {
        $this->position++;
    }
    public function valid(): bool
    {
        return isset(array_keys($this->orig)[$this->position]);
    }
}

function setup_input_id()
{
    $input_id_name = '__php_iid';
    // check if input id was provided
    if (!isset($_GET[$input_id_name]) || !is_string($_GET[$input_id_name]))
    {
        return;
    }
    
    define("INPUT_ID_GLOBAL_CONST", $_GET[$input_id_name]);
    define("__ORIG_REQUEST_URI", $_SERVER['REQUEST_URI']);

    // unset canary parameter
    unset($_GET[$input_id_name]);
    unset($_REQUEST[$input_id_name]);
}

function cov_collection_shutdown_callback()
{
    $reports_path = get_cfg_var("coverage_report_path");
    $coverage_path = get_cfg_var("coverage_dump_path");

    $to_exclude = [
        __DIR__ . DIRECTORY_SEPARATOR . basename(__FILE__)
    ];

    $coverage = xdebug_get_code_coverage();
    foreach ($to_exclude as $path) {
        unset($coverage[$path]);
    }

    // PER FILE COV COLLECTION BEGIN
    foreach ($coverage as $file => $cov_info) {
        update_coverage_info($file, $cov_info);
    }
    // PER FILE COV COLLECTION END

    $encoded_coverage = json_encode((object)$coverage);
    $hash = hash('sha256', $encoded_coverage);

    $report = [
        "URI" => __ORIG_REQUEST_URI,
        "coverage" => $hash,
        "id" => INPUT_ID_GLOBAL_CONST
    ];

    $encoded_report = json_encode($report, JSON_PRETTY_PRINT);
    file_put_contents($reports_path . DIRECTORY_SEPARATOR . INPUT_ID_GLOBAL_CONST . ".cov.json", $encoded_report);
    file_put_contents($coverage_path . DIRECTORY_SEPARATOR . "{$hash}.json", $encoded_coverage);
}

function setup_cov_collection()
{
    $cov_name = '__php_cov';
    // check if coverage analysis was requested via canary query param
    if (!defined("INPUT_ID_GLOBAL_CONST") || !isset($_GET[$cov_name]))
    {
        return;
    }

    define("INPUT_COV_COLLECT", true);
    
    // unset canary parameter
    unset($_GET[$cov_name]);
    unset($_REQUEST[$cov_name]);

    // set on exit callback in order to export coverage report
    register_shutdown_function('cov_collection_shutdown_callback');

    xdebug_start_code_coverage();
}

function paramcollect_shutdown_callback()
{
    $reports_path = get_cfg_var("coverage_report_path");

    $param_collect_report = [
        "URI" => __ORIG_REQUEST_URI,
        "id" => INPUT_ID_GLOBAL_CONST,
        "used_input" => (object)\InputReporter::getInstance()->get_usage()
    ];

    $encoded_report = json_encode($param_collect_report, JSON_PRETTY_PRINT);
    file_put_contents($reports_path . DIRECTORY_SEPARATOR . INPUT_ID_GLOBAL_CONST . ".params.json", $encoded_report);
}

function setup_param_collection()
{
    $param_collect_name = '__php_params';
    // check if param uasage analysis was requested via canary query param
    if (!defined("INPUT_ID_GLOBAL_CONST") || !isset($_GET[$param_collect_name]))
    {
        return;
    }

    define("INPUT_PARAMS_COLLECT", true);

    // unset canary parameter
    unset($_GET[$param_collect_name]);
    unset($_REQUEST[$param_collect_name]);

    // TAINT superglobals
    $_REQUEST = \DictWrapper::wrap("REQUEST", $_REQUEST);
    $_GET = \DictWrapper::wrap("GET", $_GET);
    $_POST = \DictWrapper::wrap("POST", $_POST);
    $_COOKIE = \DictWrapper::wrap("COOKIE", $_COOKIE);
    $_FILES = \DictWrapper::wrap("FILE", $_FILES);
    $_SERVER = \DictWrapper::wrap("HEADER", $_SERVER, [
        "HTTP_" => "HEADER",
        "REMOTE_ADDR" => "SOCKET_ADDR",
        "REMOTE_PORT" => "SOCKET_PORT",
        "REQUEST_URI" => "URI",
        "QUERY_STRING" => "QUERY_STRING",
        "PATH_INFO" => "PATH_INFO",
        "PHP_AUTH_DIGEST" => "AUTH_DIGEST",
        "PHP_AUTH_USER" => "HTTP_AUTH_USER",
        "PHP_AUTH_PW" => "HTTP_AUTH_PASSWORD"
    ]);

    uopz_set_return('is_array', function($arr) {
        $result = is_array($arr);
        if ($arr instanceof \DictWrapper)
            $result = true;
        return $result;
    }, true);

    uopz_set_return('array_key_exists', function($k, $arr) {
        if ($arr instanceof \DictWrapper) {
            return isset($arr[$k]);
        }
        return array_key_exists($k, $arr);
    }, true);

    uopz_set_return('session_start', function() {
        if ($_COOKIE instanceof \DictWrapper) {
            $wrapped_cookie = $_COOKIE;
            $_COOKIE = $_COOKIE->getOrig();
            session_start();
            $_COOKIE = $wrapped_cookie;
        } else {
            session_start();
        }
    }, true);

    uopz_set_return('array_merge', function( ...$args ) {
        $arr_name = "";
        $has_dict_wrappers = false;
        $all_dict_wrappers = true;

        $all_arrs = [];
        foreach ($args as $arr) {
            if ($arr instanceof \DictWrapper) {
                if (!$has_dict_wrappers) {
                    $has_dict_wrappers = true;
                    $arr_name = $arr->getName();
                }
                $all_arrs[] = $arr->getOrig();
            } else {
                $all_arrs[] = $arr;
                $all_dict_wrappers = false;
            }
        }
        if ($has_dict_wrappers && $all_dict_wrappers) {
            $merged = array_merge(...$all_arrs);
            return \DictWrapper::wrap($arr_name, $merged);
        } else {
            return array_merge(...$all_arrs);
        }
    }, true);

    register_shutdown_function('paramcollect_shutdown_callback');
}

function check_is_download_file() {
    $download_type_param_name = '__php_dl_id';
    $download_id_param_name = '__php_dl_id';
    if (!isset($_GET[$download_type_param_name])
        || !isset($_GET[$download_id_param_name]))
    {
        return false;
    }
    else
    {
        return true;
    }
}

function download_file() {
    $download_type_param_name = '__php_dl_type';
    $download_id_param_name = '__php_dl_id';

    $download_type = $_GET[$download_type_param_name];
    $download_id = $_GET[$download_id_param_name];

    $prefix = '';
    $suffix = '';
    $correct_type = true;

    if ($download_type === 'cov_report')
    {
        $prefix = get_cfg_var("coverage_report_path");
        $suffix = ".cov.json";
    }
    else if ($download_type == 'params_report')
    {
        $prefix = get_cfg_var("coverage_report_path");
        $suffix = '.params.json';
    }
    else if ($download_type == 'cov')
    {
        $prefix = get_cfg_var("coverage_dump_path");
        $suffix = '.json';
    }
    else
    {
        $correct_type = false;
    }

    $file_path = $prefix . DIRECTORY_SEPARATOR . basename($download_id) . $suffix;
    if (file_exists($file_path) && $correct_type) {
        if (ob_get_level()) {
            ob_end_clean();
        }

        header('Content-Type: application/octet-stream');
        header('Content-Disposition: attachment; filename="' . basename($file_path) . '"');
        header('Content-Length: ' . filesize($file_path));

        // Open file in binary read mode
        $file = fopen($file_path, 'rb');
        
        // Output file in 1MB chunks
        while (!feof($file)) {
            echo fread($file, 1024 * 1024);
            flush(); // Flush system output buffer to browser
        }
        
        fclose($file);
        unlink($file_path);
        exit;
    } else {
        http_response_code(404);
        echo "Error: File not found.";
        exit;
    }
}

uopz_allow_exit(true);
if (check_is_download_file()) {
    download_file();
    exit;
}
setup_input_id();
setup_cov_collection();
setup_param_collection();