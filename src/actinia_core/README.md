The module structure is currently under rework. See [according github issue](https://github.com/mundialis/actinia_core/issues/190) and [plugin dependencies](https://github.com/mundialis/actinia_core/pull/221) for more details.

This README should support restructuring and identify dependencies outside of this repository.
This mainly concerns the plugins:
* [actinia-module-plugin](https://github.com/mundialis/actinia-module-plugin) (amp)
* [actinia_statistic_plugin](https://github.com/mundialis/actinia_statistic_plugin) (statistic)
* [actinia_satallite_plugin](https://github.com/mundialis/actinia_satellite_plugin) (satellite)
* [actinia-metadata-plugin](https://github.com/mundialis/actinia-metadata-plugin) uses no sources of actinia_core
* [actinia-stac-plugin](https://github.com/mundialis/actinia-stac-plugin) (stac)
* [actinia-api](https://github.com/mundialis/actinia-api) (api)

The modules inside common folder are not only commonly used by actinia but also by actinia plugins.
Some other modules outside of core folder are concerned as well.

----------------
### Overview of modules used outside of actinia

| module | import|
| - | - |
| actinia_core.endpoints | create_endpoints |
| actinia_core.testsuite | ActiniaTestCaseBase, URL_PREFIX |
| actinia_core.health_check | health_check |
| actinia_core.version | version |
| actinia_core.rest.ephemeral_processing | EphemeralProcessing |
| actinia_core.rest.ephemeral_processing_with_export | start_job, SCHEMA_DOC, EphemeralProcessingWithExport |
| actinia_core.rest.persistent_processing | PersistentProcessing, start_job, SCHEMA_DOC |
| actinia_core.rest.resource_base | ResourceBase |
| actinia_core.core.common.api_logger | log_api_call |
| actinia_core.core.common.app | auth, flask_api, flask_app |
| actinia_core.core.common.aws_sentinel_interface | AWSSentinel2AInterface |
| actinia_core.core.common.config | global_config, Configuration, DEFAULT_CONFIG_PATH |
| actinia_core.core.common.exceptions | AsyncProcessError |
| actinia_core.core.common.google_satellite_bigquery_interface | GoogleSatelliteBigQueryInterface |
| actinia_core.core.common.landsat_processing_library | LandsatProcessing, SCENE_BANDS, extract_sensor_id_from_scene_id, RASTER_SUFFIXES |
| actinia_core.core.common.process_chain | GrassModule |
| actinia_core.core.common.process_object | Process |
| actinia_core.core.common.process_queue | create_process_queue |
| actinia_core.core.common.redis_base | RedisBaseInterface |
| actinia_core.core.common.redis_interface | full import! TODO check what is used. Else: connect, create_job_queues, enqueue_job |
| actinia_core.core.common.response_models | create_response_from_model, ProcessingErrorResponseModel, ProcessingResponseModel, SimpleResponseModel, StringListProcessingResultResponseModel, UnivarResultModel |
| actinia_core.core.common.sentinel_processing_library | Sentinel2Processing |
| actinia_core.core.common.user | ActiniaUser |
| actinia_core.core.redis_user | RedisUserInterface |

URL_PREFIX moved to actinia_api
------------

### Complete list of where modules are used and what exactly is imported

__amp, satellite, statistic__
actinia_core.endpoints import create_endpoints
actinia_core.rest.resource_base import ResourceBase
actinia_core.core.common.app import flask_app
actinia_core.core.common.config import global_config
actinia_core.core.common.redis_interface import enqueue_job
actinia_core.core.common.response_models import ProcessingResponseModel

__amp, statistic__
actinia_core.rest.ephemeral_processing import EphemeralProcessing

__actinia-module-plugin__
actinia_core.rest.ephemeral_processing_with_export import start_job
actinia_core.rest.ephemeral_processing_with_export import SCHEMA_DOC
actinia_core.rest.persistent_processing import start_job
actinia_core.rest.persistent_processing import SCHEMA_DOC
actinia_api import URL_PREFIX
actinia_core.core.common.config import Configuration
actinia_core.core.common.process_chain import GrassModule
/# from actinia_core.core.common.process_queue import create_process_queue
actinia_core.core.common.redis_base import RedisBaseInterface
actinia_core.core.common import redis_interface
actinia_core.core.common.response_models import create_response_from_model
actinia_core.core.common.response_models import StringListProcessingResultResponseModel
actinia_core.core.common.user import ActiniaUser
actinia_core.core.redis_user import RedisUserInterface

__satellite, statistic__
actinia_core.testsuite import ActiniaTestCaseBase, URL_PREFIX
actinia_core.core.common.api_logger import log_api_call
actinia_core.core.common.app import flask_api
actinia_core.core.common.app import auth
actinia_core.core.common.exceptions import AsyncProcessError
actinia_core.core.common.response_models import ProcessingErrorResponseModel

__satellite__
actinia_core.health_check import health_check
actinia_core.version import version
actinia_core.rest.ephemeral_processing_with_export import EphemeralProcessingWithExport
actinia_core.rest.persistent_processing import PersistentProcessing
actinia_core.core.common.aws_sentinel_interface import AWSSentinel2AInterface
actinia_core.core.common.config import DEFAULT_CONFIG_PATH
actinia_core.core.common.google_satellite_bigquery_interface import GoogleSatelliteBigQueryInterface
actinia_core.core.common.landsat_processing_library import LandsatProcessing, SCENE_BANDS, extract_sensor_id_from_scene_id, RASTER_SUFFIXES
actinia_core.core.common.process_object import Process
actinia_core.core.common.process_queue import create_process_queue
actinia_core.core.common.redis_interface import connect, create_job_queues
actinia_core.core.common.response_models import SimpleResponseModel
actinia_core.core.common.response_models import UnivarResultModel
actinia_core.core.common.sentinel_processing_library import Sentinel2Processing

__stac__
actinia_core.rest.resource_base import ResourceBase
actinia_core.core.common.redis_base import RedisBaseInterface
actinia_core.core.common.config import Configuration

__api__
actinia_core.models.response_models import ProcessingResponseModel
