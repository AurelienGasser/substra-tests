"""Global settings for all tests environment."""
import dataclasses
import os
import typing
import yaml

CURRENT_DIR = os.path.dirname(__file__)

DEFAULT_NETWORK_CONFIGURATION_PATH = os.path.join(CURRENT_DIR, '../', 'values.yaml')
SUBSTRA_TESTS_CONFIG_FILEPATH = os.getenv('SUBSTRA_TESTS_CONFIG_FILEPATH', DEFAULT_NETWORK_CONFIGURATION_PATH)

DEFAULT_NETWORK_LOCAL_CONFIGURATION_PATH = os.path.join(CURRENT_DIR, '../', 'local-backend-values.yaml')

MIN_NODES = 2


@dataclasses.dataclass(frozen=True)
class NodeCfg:
    name: str
    msp_id: str
    address: str
    user: str = None
    password: str = None
    shared_path: str = None


@dataclasses.dataclass(frozen=True)
class Options:
    enable_intermediate_model_removal: bool
    enable_model_download: bool
    minikube: bool = False


@dataclasses.dataclass(frozen=True)
class Settings:
    path: str
    options: Options
    nodes: typing.List[NodeCfg] = dataclasses.field(default_factory=list)


_SETTINGS = None
_LOCAL_SETTINGS = None


def _load_yaml(path):
    """Load configuration from yaml file."""
    with open(path) as f:
        data = yaml.load(f, Loader=yaml.Loader)
    nodes = [NodeCfg(**kw) for kw in data['nodes']]
    return Settings(
        path=path,
        nodes=nodes,
        options=Options(**data['options'])
    )


def load():
    """Loads settings static configuration.

    As the configuration is static and immutable, it is loaded only once from the disk.

    Returns an instance of the `Settings` class.
    """
    global _SETTINGS
    if _SETTINGS is not None:
        return _SETTINGS

    s = _load_yaml(SUBSTRA_TESTS_CONFIG_FILEPATH)
    assert len(s.nodes) >= MIN_NODES, f'not enough nodes: {len(s.nodes)}'
    _SETTINGS = s
    return _SETTINGS


def load_local_backend():
    """Loads settings static configuration.

    As the configuration is static and immutable, it is loaded only once from the disk.

    Returns an instance of the `Settings` class.
    """
    global _LOCAL_SETTINGS
    if _LOCAL_SETTINGS is None:
        _LOCAL_SETTINGS = _load_yaml(DEFAULT_NETWORK_LOCAL_CONFIGURATION_PATH)
    return _LOCAL_SETTINGS


# TODO that's a bad idea to expose the static configuration, it has been done to allow
#      tests parametrization but this won't work for specific tests written with more
#      nodes

# load configuration at module load time to allow tests parametrization depending on
# network static configuration
load()


MSP_IDS = [n.msp_id for n in _SETTINGS.nodes]
HAS_SHARED_PATH = bool(_SETTINGS.nodes[0].shared_path)
IS_MINIKUBE = bool(_SETTINGS.options.minikube)
