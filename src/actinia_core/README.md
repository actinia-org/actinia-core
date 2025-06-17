# Overview of used modules

## History
The module structure has had some changes and will have in the future. For more details, see
- [issue for first reordering](https://github.com/actinia-org/actinia-core/issues/190)
- [reordering for plugin dependencies imports](https://github.com/actinia-org/actinia-core/pull/221)
- new plugins / libs extracted from actinia-core
  - actinia-grassdata-management-plugin [#3](https://github.com/actinia-org/actinia-grassdata-management-plugin/pull/3) (actinia-core [#614](https://github.com/actinia-org/actinia-core/pull/614)) and [#5](https://github.com/actinia-org/actinia-grassdata-management-plugin/pull/5) (actinia-core [#627](https://github.com/actinia-org/actinia-core/pull/627))
  - actinia-processing-lib [#2](https://github.com/actinia-org/actinia-processing-lib/pull/2) (actinia-core [#627](https://github.com/actinia-org/actinia-core/pull/627))
  - actinia-rest-lib [#2](https://github.com/actinia-org/actinia-rest-lib/pull/2) (actinia-core [#627](https://github.com/actinia-org/actinia-core/pull/627))
- Other changes
  - URL_PREFIX moved to actinia_api
  - actinia_core.endpoints method "get_endpoint_class_name" now copied to plugins to remove imports


## Potentially connected modules
This README should support restructuring and identify dependencies outside of this repository.
This mainly concerns the libs:
- [actinia-api](https://github.com/actinia-org/actinia-api) (api)
- [actinia-processing-lib](https://github.com/actinia-org/actinia-processing-lib) (example)
- [actinia-rest-lib](https://github.com/actinia-org/actinia-rest-lib) (example)

And plugins:
- [actinia-cloudevent-plugin](https://github.com/actinia-org/actinia-cloudevent-plugin) (cloudevent)
- [actinia-example-plugin](https://github.com/actinia-org/actinia-example-plugin) (example)
- [actinia-grassdata-management-plugin](https://github.com/actinia-org/actinia-grassdata-management-plugin) (gdmp)
- [actinia-metadata-plugin](https://github.com/actinia-org/actinia-metadata-plugin) uses no sources of actinia_core
- [actinia-module-plugin](https://github.com/actinia-org/actinia-module-plugin) (amp)
- [actinia-parallel-plugin](https://github.com/actinia-org/actinia-parallel-plugin) (parallel)
- [actinia_satallite_plugin](https://github.com/actinia-org/actinia_satellite_plugin) (satellite)
- [actinia-stac-plugin](https://github.com/actinia-org/actinia-stac-plugin) (stac)
- [actinia_statistic_plugin](https://github.com/actinia-org/actinia_statistic_plugin) (statistic)
- [actinia-tiling-plugin](https://github.com/actinia-org/actinia-tiling-plugin) (tiling)

The modules inside common folder are not only commonly used by actinia but also by actinia plugins.
Some other modules outside of core folder are concerned as well.
______________________________________________________________________

## Overview of modules used outside of actinia-core

Change directory to the plugin you want to check imports from actinia_core from and run
`IFS=","; findimports -C | grep actinia_core | while read module import;do echo $import;done | sort -u`

Or to generate a list with all actinia_core imports, sorted by plugin/lib, run
```bash
for i in actinia-api actinia-processing-lib actinia-rest-lib actinia-cloudevent-plugin actinia-example-plugin actinia-grassdata-management-plugin actinia-metadata-plugin actinia-module-plugin actinia-parallel-plugin actinia-satellite-plugin actinia-stac-plugin actinia-statistic-plugin actinia-tiling-plugin
  do (cd $i; echo $i;IFS=","; findimports -C 2>/dev/null| grep actinia_core | while read module import;do echo $import;done | sort -u;echo); done
```

Or to generate this overview table, run
```bash
for i in actinia-api actinia-processing-lib actinia-rest-lib actinia-cloudevent-plugin actinia-example-plugin actinia-grassdata-management-plugin actinia-metadata-plugin actinia-module-plugin actinia-parallel-plugin actinia-satellite-plugin actinia-stac-plugin actinia-statistic-plugin actinia-tiling-plugin
  do (cd $i;IFS=","; findimports -C 2>/dev/null| grep actinia_core | while read module import;do echo "$import,$i" ;done); done | sort -u | grep actinia_core > imports.csv
IFS=",";cat imports.csv | while read import plugin;do echo $import;done | sort -u > imports_unique.csv
IFS=",";cat imports_unique.csv | while read i;do echo -n "| $i |"; cat imports.csv | while read import plugin;do if [ "$i" == "$import" ];then echo -n $plugin,;fi;done; echo -n "|";echo;done
```

| import | used by plugin / lib |
| - | - |
| actinia_core.core.common.api_logger.log_api_call |actinia-rest-lib,actinia-satellite-plugin,actinia-statistic-plugin,|
| actinia_core.core.common.app.auth |actinia-parallel-plugin,actinia-rest-lib,actinia-satellite-plugin,actinia-statistic-plugin,|
| actinia_core.core.common.app.flask_api |actinia-rest-lib,actinia-statistic-plugin,|
| actinia_core.core.common.app.flask_app |actinia-cloudevent-plugin,actinia-example-plugin,actinia-grassdata-management-plugin,actinia-module-plugin,actinia-processing-lib,actinia-rest-lib,actinia-satellite-plugin,actinia-stac-plugin,|
| actinia_core.core.common.app.URL_PREFIX |actinia-module-plugin,|
| actinia_core.core.common.aws_sentinel_interface.AWSSentinel2AInterface |actinia-satellite-plugin,|
| actinia_core.core.common.config.Configuration |actinia-module-plugin,actinia-stac-plugin,|
| actinia_core.core.common.config.DEFAULT_CONFIG_PATH |actinia-processing-lib,actinia-satellite-plugin,|
| actinia_core.core.common.config.global_config |actinia-cloudevent-plugin,actinia-example-plugin,actinia-grassdata-management-plugin,actinia-module-plugin,actinia-parallel-plugin,actinia-processing-lib,actinia-rest-lib,actinia-satellite-plugin,actinia-stac-plugin,actinia-statistic-plugin,actinia-tiling-plugin,|
| actinia_core.core.common.exceptions.RsyncError |actinia-processing-lib,|
| actinia_core.core.common.google_satellite_bigquery_interface.GoogleSatelliteBigQueryInterface |actinia-satellite-plugin,|
| actinia_core.core.common.kvdb_base.KvdbBaseInterface |actinia-module-plugin,actinia-stac-plugin,|
| actinia_core.core.common.kvdb_interface |actinia-cloudevent-plugin,actinia-example-plugin,actinia-grassdata-management-plugin,actinia-processing-lib,actinia-rest-lib,actinia-stac-plugin,|
| actinia_core.core.common.kvdb_interface.connect |actinia-module-plugin,actinia-satellite-plugin,|
| actinia_core.core.common.kvdb_interface.disconnect |actinia-module-plugin,|
| actinia_core.core.common.kvdb_interface.enqueue_job |actinia-grassdata-management-plugin,actinia-module-plugin,actinia-parallel-plugin,actinia-satellite-plugin,actinia-statistic-plugin,actinia-tiling-plugin,|
| actinia_core.core.common.landsat_processing_library.extract_sensor_id_from_scene_id |actinia-satellite-plugin,|
| actinia_core.core.common.landsat_processing_library.LandsatProcessing |actinia-satellite-plugin,|
| actinia_core.core.common.landsat_processing_library.RASTER_SUFFIXES |actinia-satellite-plugin,|
| actinia_core.core.common.landsat_processing_library.SCENE_BANDS |actinia-satellite-plugin,|
| actinia_core.core.common.process_chain.get_param_stdin_part |actinia-processing-lib,|
| actinia_core.core.common.process_chain.GrassModule |actinia-module-plugin,|
| actinia_core.core.common.process_chain.ProcessChainConverter |actinia-processing-lib,actinia-tiling-plugin,|
| actinia_core.core.common.process_chain.ProcessChainModel |actinia-api,|
| actinia_core.core.common.process_object.Process |actinia-processing-lib,actinia-satellite-plugin,|
| actinia_core.core.common.process_queue.create_process_queue |actinia-module-plugin,actinia-satellite-plugin,|
| actinia_core.core.common.sentinel_processing_library.Sentinel2Processing |actinia-satellite-plugin,|
| actinia_core.core.common.user.ActiniaUser |actinia-cloudevent-plugin,actinia-example-plugin,actinia-grassdata-management-plugin,actinia-module-plugin,actinia-parallel-plugin,actinia-processing-lib,actinia-rest-lib,actinia-stac-plugin,actinia-tiling-plugin,|
| actinia_core.core.grass_init.GrassInitializer |actinia-processing-lib,|
| actinia_core.core.interim_results.get_directory_size |actinia-processing-lib,|
| actinia_core.core.interim_results.InterimResult |actinia-processing-lib,|
| actinia_core.core.kvdb_lock.KvdbLockingInterface |actinia-processing-lib,|
| actinia_core.core.kvdb_user.KvdbUserInterface |actinia-module-plugin,|
| actinia_core.core.mapset_merge_utils.change_mapsetname |actinia-processing-lib,|
| actinia_core.core.messages_logger.MessageLogger |actinia-parallel-plugin,actinia-processing-lib,actinia-rest-lib,|
| actinia_core.core.resource_data_container.ResourceDataContainer |actinia-parallel-plugin,actinia-rest-lib,|
| actinia_core.core.resources_logger.ResourceLogger |actinia-parallel-plugin,actinia-processing-lib,actinia-rest-lib,|
| actinia_core.core.stac_exporter_interface.STACExporter |actinia-processing-lib,|
| actinia_core.endpoints.create_endpoints |actinia-cloudevent-plugin,actinia-example-plugin,actinia-grassdata-management-plugin,actinia-module-plugin,actinia-parallel-plugin,actinia-processing-lib,actinia-rest-lib,actinia-satellite-plugin,actinia-stac-plugin,actinia-statistic-plugin,actinia-tiling-plugin,|
| actinia_core.models.process_chain.IOParameterBase |actinia-tiling-plugin,|
| actinia_core.models.process_chain.ProcessChainModel |actinia-parallel-plugin,|
| actinia_core.models.response_models.ApiInfoModel |actinia-parallel-plugin,actinia-rest-lib,|
| actinia_core.models.response_models.create_response_from_model |actinia-module-plugin,actinia-parallel-plugin,actinia-processing-lib,actinia-rest-lib,|
| actinia_core.models.response_models.ExceptionTracebackModel |actinia-processing-lib,|
| actinia_core.models.response_models.LockedMapsetListResponseModel |actinia-api,|
| actinia_core.models.response_models.MapsetInfoResponseModel |actinia-api,|
| actinia_core.models.response_models.ProcessingErrorResponseModel |actinia-api,actinia-satellite-plugin,actinia-statistic-plugin,actinia-tiling-plugin,|
| actinia_core.models.response_models.ProcessingResponseListModel |actinia-api,|
| actinia_core.models.response_models.ProcessingResponseModel |actinia-api,actinia-module-plugin,actinia-parallel-plugin,actinia-processing-lib,actinia-rest-lib,actinia-satellite-plugin,actinia-statistic-plugin,actinia-tiling-plugin,|
| actinia_core.models.response_models.ProcessLogModel |actinia-processing-lib,|
| actinia_core.models.response_models.ProgressInfoModel |actinia-processing-lib,|
| actinia_core.models.response_models.SimpleResponseModel |actinia-api,actinia-cloudevent-plugin,actinia-example-plugin,actinia-grassdata-management-plugin,actinia-parallel-plugin,actinia-rest-lib,actinia-satellite-plugin,|
| actinia_core.models.response_models.StorageResponseModel |actinia-api,|
| actinia_core.models.response_models.StringListProcessingResultResponseModel |actinia-api,actinia-grassdata-management-plugin,actinia-module-plugin,|
| actinia_core.models.response_models.UnivarResultModel |actinia-satellite-plugin,|
| actinia_core.models.response_models.UrlModel |actinia-parallel-plugin,|
| actinia_core.models.response_models.UserInfoResponseModel |actinia-api,|
| actinia_core.models.response_models.UserListResponseModel |actinia-api,|
| actinia_core.processing.actinia_processing.persistent.mapset_management.PersistentMapsetDeleter |actinia-tiling-plugin,|
| actinia_core.processing.actinia_processing.persistent.mapset_management.PersistentMapsetUnlocker |actinia-tiling-plugin,|
| actinia_core.processing.common.ephemeral_processing_with_export.start_job |actinia-module-plugin,|
| actinia_core.processing.common.persistent_processing.start_job |actinia-module-plugin,|
| actinia_core.rest.base.user_auth.check_project_mapset_module_access |actinia-processing-lib,|
| actinia_core.rest.base.user_auth.check_user_permissions |actinia-rest-lib,|
| actinia_core.rest.base.user_auth.create_dummy_user |actinia-parallel-plugin,actinia-rest-lib,|
| actinia_core.rest.resource_management.ResourceManager |actinia-rest-lib,|
| actinia_core.rest.resource_management.ResourceManagerBase |actinia-parallel-plugin,|
| actinia_core.rest.resource_streamer.RequestStreamerResource |actinia-rest-lib,|
| actinia_core.testsuite.ActiniaTestCaseBase |actinia-cloudevent-plugin,actinia-example-plugin,actinia-grassdata-management-plugin,actinia-parallel-plugin,actinia-processing-lib,actinia-rest-lib,actinia-satellite-plugin,actinia-statistic-plugin,actinia-tiling-plugin,|
| actinia_core.testsuite.URL_PREFIX |actinia-grassdata-management-plugin,actinia-parallel-plugin,actinia-satellite-plugin,actinia-statistic-plugin,actinia-tiling-plugin,|
| actinia_core.version.G_VERSION |actinia-api,actinia-cloudevent-plugin,actinia-example-plugin,actinia-grassdata-management-plugin,actinia-module-plugin,actinia-parallel-plugin,actinia-processing-lib,actinia-rest-lib,actinia-satellite-plugin,actinia-statistic-plugin,actinia-tiling-plugin,|
| actinia_core.version.init_versions |actinia-api,actinia-cloudevent-plugin,actinia-example-plugin,actinia-grassdata-management-plugin,actinia-module-plugin,actinia-parallel-plugin,actinia-processing-lib,actinia-rest-lib,actinia-satellite-plugin,actinia-statistic-plugin,actinia-tiling-plugin,|

| import | used by plugin / lib |
| - | - |
| actinia_processing_lib.ephemeral_processing_with_export.EphemeralProcessingWithExport |actinia-satellite-plugin,|
| actinia_processing_lib.ephemeral_processing.EphemeralProcessing |actinia_grassdata_management_plugin,actinia-module-plugin,actinia-parallel-plugin,actinia-statistic-plugin,|
| actinia_processing_lib.exceptions.AsyncProcessError |actinia_grassdata_management_plugin,actinia-satellite-plugin,actinia-statistic-plugin,|
| actinia_processing_lib.persistent_processing.PersistentProcessing |actinia_grassdata_management_plugin,actinia-satellite-plugin,actinia-tiling-plugin,|
| actinia_processing_lib.utils |  actinia_grassdata_management_plugin |
| actinia_rest_lib.deprecated_locations.location_deprecated_decorator |actinia-cloudevent-plugin,actinia-example-plugin,|
| actinia_rest_lib.endpoint_config | actinia_grassdata_management_plugin |
| actinia_rest_lib.resource_base.ResourceBase |actinia_grassdata_management_plugin,actinia-module-plugin,actinia-parallel-plugin,actinia-satellite-plugin,actinia-stac-plugin,actinia-statistic-plugin,actinia-tiling-plugin,|
