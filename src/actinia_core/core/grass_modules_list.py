module_list = {
    "raster": {
        "cost surface": {
            "r.cost": {
                "keywords": "raster,cost surface,cumulative costs,cost "
                "allocation",
                "description": "Creates a raster map showing the cumulative "
                "cost of  moving between different geographic projects on an "
                "input raster map whose cell category values represent"
                " cost.",
                "module": "r.cost",
            },
            "r.walk": {
                "keywords": "raster,cost surface,cumulative costs,cost "
                "allocation",
                "description": "Creates a raster map showing the anisotropic "
                "cumulative cost of moving between different geographic "
                "projects on an input raster map whose cell category values "
                "represent cost.",
                "module": "r.walk",
            },
        },
        "projection": {
            "r.proj": {
                "keywords": "raster,projection,transformation,import",
                "description": "Re-projects a raster map from given project "
                "to the current project.",
                "module": "r.proj",
            }
        },
        "transect": {
            "r.transect": {
                "keywords": "raster,transect",
                "description": "Outputs raster map layer values lying along "
                "user defined transect line(s).",
                "module": "r.transect",
            }
        },
        "series": {
            "r.series.interp": {
                "keywords": "raster,series,interpolation",
                "description": "Interpolates raster maps located (temporal or "
                "spatial) in between input raster maps at specific sampling "
                "positions.",
                "module": "r.series.interp",
            },
            "r.series.accumulate": {
                "keywords": "raster,series,accumulation",
                "description": "Makes each output cell value a "
                "accumulationfunction of the values assigned to the "
                "corresponding cells in the input raster map layers.",
                "module": "r.series.accumulate",
            },
        },
        "terrain": {
            "r.slope.aspect": {
                "keywords": "raster,terrain,aspect,slope,curvature",
                "description": "Generates raster maps of slope, aspect, "
                "curvatures and partial derivatives from an elevation raster "
                "map. Aspect is calculated counterclockwise from east.",
                "module": "r.slope.aspect",
            }
        },
        "surface": {
            "r.surf.area": {
                "keywords": "raster,surface,statistics,area estimation",
                "description": "Prints estimation of surface area for raster "
                "map.",
                "module": "r.surf.area",
            },
            "r.surf.fractal": {
                "keywords": "raster,surface,fractal",
                "description": "Creates a fractal surface of a given fractal "
                "dimension.",
                "module": "r.surf.fractal",
            },
            "r.surf.contour": {
                "keywords": "raster,surface,interpolation",
                "description": "Generates surface raster map from rasterized "
                "contours.",
                "module": "r.surf.contour",
            },
            "r.resamp.bspline": {
                "keywords": "raster,surface,resample,interpolation",
                "description": "Performs bilinear or bicubic spline "
                "interpolation with Tykhonov regularization.",
                "module": "r.resamp.bspline",
            },
            "r.surf.idw": {
                "keywords": "raster,surface,interpolation,IDW",
                "description": "Provides surface interpolation from raster "
                "point data by Inverse Distance Squared Weighting.",
                "module": "r.surf.idw",
            },
            "r.surf.gauss": {
                "keywords": "raster,surface,random",
                "description": "Generates a raster map using gaussian random "
                "number generator. Mean and standard deviation of gaussian "
                "deviates can be expressed by the user.",
                "module": "r.surf.gauss",
            },
            "r.random.surface": {
                "keywords": "raster,surface,random",
                "description": "Generates random surface(s) with spatial "
                "dependence.",
                "module": "r.random.surface",
            },
            "r.contour": {
                "keywords": "raster,surface,contours,vector",
                "description": "Produces a vector map of specified contours "
                "from a raster map.",
                "module": "r.contour",
            },
            "r.surf.random": {
                "keywords": "raster,surface,random",
                "description": "Produces a raster surface map of uniform "
                "random deviates with defined range.",
                "module": "r.surf.random",
            },
        },
        "sampling": {
            "r.random.cells": {
                "keywords": "raster,sampling,random,autocorrelation",
                "description": "Generates random cell values with spatial "
                "dependence.",
                "module": "r.random.cells",
            },
            "r.random": {
                "keywords": "raster,sampling,vector,random",
                "description": "Creates a raster map layer and vector point "
                "map containing randomly located points.",
                "module": "r.random",
            },
        },
        "RGB": {
            "r.rgb": {
                "keywords": "raster,RGB,separate,split",
                "description": "Splits a raster map into red, green and blue "
                "maps.",
                "module": "r.rgb",
            }
        },
        "recode categories": {
            "r.recode": {
                "keywords": "raster,recode categories,reclassification",
                "description": "Recodes categorical raster maps.",
                "module": "r.recode",
            }
        },
        "landscape structure analysis": {
            "r.li.dominance": {
                "keywords": "raster,landscape structure analysis,diversity "
                "index",
                "description": "Calculates dominance's diversity index on a "
                "raster map",
                "module": "r.li.dominance",
            },
            "r.li.mpa": {
                "keywords": "raster,landscape structure analysis,patch index",
                "description": "Calculates mean pixel attribute index on a "
                "raster map",
                "module": "r.li.mpa",
            },
            "r.li.padcv": {
                "keywords": "raster,landscape structure analysis,patch index",
                "description": "Calculates coefficient of variation of patch "
                "area on a raster map",
                "module": "r.li.padcv",
            },
            "r.li.patchnum": {
                "keywords": "raster,landscape structure analysis,patch index",
                "description": "Calculates patch number index on a raster map,"
                " using a 4 neighbour algorithm.",
                "module": "r.li.patchnum",
            },
            "r.li.padsd": {
                "keywords": "raster,landscape structure analysis,patch index",
                "description": "Calculates standard deviation of patch area a "
                "raster map",
                "module": "r.li.padsd",
            },
            "r.li.cwed": {
                "keywords": "raster,landscape structure analysis,patch index",
                "description": "Calculates contrast weighted edge density "
                "index on a raster map",
                "module": "r.li.cwed",
            },
            "r.li.edgedensity": {
                "keywords": "raster,landscape structure analysis,patch index",
                "description": "Calculates edge density index on a raster map,"
                " using a 4 neighbour algorithm",
                "module": "r.li.edgedensity",
            },
            "r.li.simpson": {
                "keywords": "raster,landscape structure analysis,diversity "
                "index",
                "description": "Calculates Simpson's diversity index on a "
                "raster map",
                "module": "r.li.simpson",
            },
            "r.li.renyi": {
                "keywords": "raster,landscape structure analysis,diversity "
                "index",
                "description": "Calculates Renyi's diversity index on a raster"
                " map",
                "module": "r.li.renyi",
            },
            "r.li.mps": {
                "keywords": "raster,landscape structure analysis,patch index",
                "description": "Calculates mean patch size index on a raster "
                "map, using a 4 neighbour algorithm",
                "module": "r.li.mps",
            },
            "r.li.shannon": {
                "keywords": "raster,landscape structure analysis,diversity "
                "index",
                "description": "Calculates Shannon's diversity index on a "
                "raster map",
                "module": "r.li.shannon",
            },
            "r.li.patchdensity": {
                "keywords": "raster,landscape structure analysis,patch index",
                "description": "Calculates patch density index on a raster "
                "map, using a 4 neighbour algorithm",
                "module": "r.li.patchdensity",
            },
            "r.li.richness": {
                "keywords": "raster,landscape structure analysis,diversity "
                "index",
                "description": "Calculates richness index on a raster map",
                "module": "r.li.richness",
            },
            "r.li.pielou": {
                "keywords": "raster,landscape structure analysis,diversity "
                "index",
                "description": "Calculates Pielou's diversity index on a "
                "raster map",
                "module": "r.li.pielou",
            },
            "r.li.shape": {
                "keywords": "raster,landscape structure analysis,patch index",
                "description": "Calculates shape index on a raster map",
                "module": "r.li.shape",
            },
            "r.li.padrange": {
                "keywords": "raster,landscape structure analysis,patch index",
                "description": "Calculates range of patch area size on a "
                "raster map",
                "module": "r.li.padrange",
            },
        },
        "tiling": {
            "r.tile": {
                "keywords": "raster,tiling",
                "description": "Splits a raster map into tiles.",
                "module": "r.tile",
            },
            "r.tileset": {
                "keywords": "raster,tiling",
                "description": "Produces tilings of the source projection for "
                "use in the destination region and projection.",
                "module": "r.tileset",
            },
        },
        "groundwater flow": {
            "r.gwflow": {
                "keywords": "raster,groundwater flow,hydrology",
                "description": "Numerical calculation program for transient, "
                "confined and unconfined groundwater flow in two dimensions.",
                "module": "r.gwflow",
            }
        },
        "reclassification": {
            "r.reclass": {
                "keywords": "raster,reclassification",
                "description": "Reclassify raster map based on category "
                "values. Creates a new raster map whose category values are "
                "based upon a reclassification of the categories in "
                "an existing raster map.",
                "module": "r.reclass",
            }
        },
        "category": {
            "r.category": {
                "keywords": "raster,category",
                "description": "Manages category values and labels associated "
                "with user-specified raster map layers.",
                "module": "r.category",
            }
        },
        "conversion": {
            "r.to.vect": {
                "keywords": "raster,conversion,geometry,vectorization",
                "description": "Converts a raster map into a vector map.",
                "module": "r.to.vect",
            },
            "r.to.rast3": {
                "keywords": "raster,conversion,voxel",
                "description": "Converts 2D raster map slices to one 3D raster"
                " volume map.",
                "module": "r.to.rast3",
            },
            "r.to.rast3elev": {
                "keywords": "raster,conversion,raster3d,voxel",
                "description": "Creates a 3D volume map based on 2D elevation "
                "and value raster maps.",
                "module": "r.to.rast3elev",
            },
        },
        "statistics": {
            "r.stats.zonal": {
                "keywords": "raster,statistics,zonal statistics",
                "description": "Calculates category or object oriented "
                "statistics (accumulator-based statistics).",
                "module": "r.stats.zonal",
            },
            "r.coin": {
                "keywords": "raster,statistics",
                "description": "Tabulates the mutual occurrence (coincidence) "
                "of categories for two raster map layers.",
                "module": "r.coin",
            },
            "r.support.stats": {
                "keywords": "raster,statistics",
                "description": "Update raster map statistics",
                "module": "r.support.stats",
            },
            "r.clump": {
                "keywords": "raster,statistics,reclass,clumps",
                "description": "Recategorizes data in a raster map by grouping"
                " cells that form physically discrete areas into unique "
                "categories.",
                "module": "r.clump",
            },
            "r.cross": {
                "keywords": "raster,statistics",
                "description": "Creates a cross product of the category values"
                " from multiple raster map layers.",
                "module": "r.cross",
            },
            "r.reclass.area": {
                "keywords": "raster,statistics,aggregation",
                "description": "Reclasses a raster map greater or less than "
                "user specified area size (in hectares).",
                "module": "r.reclass.area",
            },
            "r.univar": {
                "keywords": "raster,statistics,univariate statistics,zonal "
                "statistics",
                "description": "Calculates univariate statistics from the "
                "non-null cells of a raster map. Statistics include number of "
                "cells counted, minimum and maximum cell values, "
                "range, arithmetic mean, population variance, standard "
                "deviation, coefficient of variation, and sum.",
                "module": "r.univar",
            },
            "r.covar": {
                "keywords": "raster,statistics",
                "description": "Outputs a covariance/correlation matrix for "
                "user-specified raster map layer(s).",
                "module": "r.covar",
            },
            "r.statistics": {
                "keywords": "raster,statistics,zonal statistics",
                "description": "Calculates category or object oriented "
                "statistics.",
                "module": "r.statistics",
            },
            "r.report": {
                "keywords": "raster,statistics",
                "description": "Reports statistics for raster maps.",
                "module": "r.report",
            },
            "r.mode": {
                "keywords": "raster,statistics,algebra",
                "description": "Finds the mode of values in a cover map within"
                " areas assigned the same category value in a user-specified "
                "base map.",
                "module": "r.mode",
            },
            "r.regression.line": {
                "keywords": "raster,statistics,regression",
                "description": "Calculates linear regression from two raster "
                "maps: y = a + b*x.",
                "module": "r.regression.line",
            },
            "r.regression.multi": {
                "keywords": "raster,statistics,regression",
                "description": "Calculates multiple linear regression from "
                "raster maps.",
                "module": "r.regression.multi",
            },
            "r.quant": {
                "keywords": "raster,statistics,quantization",
                "description": "Produces the quantization file for a "
                "floating-point map.",
                "module": "r.quant",
            },
            "r.stats": {
                "keywords": "raster,statistics",
                "description": "Generates area statistics for raster map.",
                "module": "r.stats",
            },
            "r.stats.quantile": {
                "keywords": "raster,statistics",
                "description": "Compute category quantiles using two passes.",
                "module": "r.stats.quantile",
            },
            "r.kappa": {
                "keywords": "raster,statistics,classification",
                "description": "Calculates error matrix and kappa parameter "
                "for accuracy assessment of classification result.",
                "module": "r.kappa",
            },
        },
        "rescale": {
            "r.rescale.eq": {
                "keywords": "raster,rescale",
                "description": "Rescales histogram equalized the range of "
                "category values in a raster map layer.",
                "module": "r.rescale.eq",
            },
            "r.rescale": {
                "keywords": "raster,rescale",
                "description": "Rescales the range of category values in a "
                "raster map layer.",
                "module": "r.rescale",
            },
        },
        "map management": {
            "r.compress": {
                "keywords": "raster,map management,compression",
                "description": "Compresses and decompresses raster maps.",
                "module": "r.compress",
            }
        },
        "color table": {
            "r.colors": {
                "keywords": "raster,color table",
                "description": "Creates/modifies the color table associated "
                "with a raster map.",
                "module": "r.colors",
            }
        },
        "composite": {
            "r.composite": {
                "keywords": "raster,composite,RGB",
                "description": "Combines red, green and blue raster maps into"
                " a single composite raster map.",
                "module": "r.composite",
            },
            "r.blend": {
                "keywords": "raster,composite",
                "description": "Blends color components of two raster maps by"
                " a given ratio.",
                "module": "r.blend",
            },
        },
        "latitude": {
            "r.latlong": {
                "keywords": "raster,latitude,longitude,projection",
                "description": "Creates a latitude/longitude raster map.",
                "module": "r.latlong",
            }
        },
        "metadata": {
            "r.describe": {
                "keywords": "raster,metadata",
                "description": "Prints terse list of category values found in"
                " a raster map layer.",
                "module": "r.describe",
            },
            "r.info": {
                "keywords": "raster,metadata,extent,history",
                "description": "Outputs basic information about a raster map.",
                "module": "r.info",
            },
            "r.timestamp": {
                "keywords": "raster,metadata,timestamp,time",
                "description": "Modifies a timestamp for a raster map. "
                "Print/add/remove a timestamp for a raster map.",
                "module": "r.timestamp",
            },
            "r.support": {
                "keywords": "raster,metadata",
                "description": "Allows creation and/or modification of raster"
                " map layer support files.",
                "module": "r.support",
            },
            "r.region": {
                "keywords": "raster,metadata",
                "description": "Sets the boundary definitions for a raster "
                "map.",
                "module": "r.region",
            },
        },
        "profile": {
            "r.profile": {
                "keywords": "raster,profile",
                "description": "Outputs the raster map layer values lying on "
                "user-defined line(s).",
                "module": "r.profile",
            }
        },
        "elevation": {
            "r.fillnulls": {
                "keywords": "raster,elevation,interpolation",
                "description": "Fills no-data areas in raster maps using "
                "spline interpolation.",
                "module": "r.fillnulls",
            },
            "r.plane": {
                "keywords": "raster,elevation",
                "description": "Creates raster plane map given dip "
                "(inclination), aspect (azimuth) and one point.",
                "module": "r.plane",
            },
            "r.relief": {
                "keywords": "raster,elevation,relief,terrain,hillshade",
                "description": "Creates shaded relief map from an elevation "
                "map (DEM).",
                "module": "r.relief",
            },
            "r.shade": {
                "keywords": "raster,elevation,relief,hillshade,visualization",
                "description": "Drapes a color raster over an shaded relief or"
                " aspect map.",
                "module": "r.shade",
            },
        },
        "algebra": {
            "r.mapcalc": {
                "keywords": "raster,algebra",
                "description": "Raster map calculator.",
                "module": "r.mapcalc",
            },
            "r.quantile": {
                "keywords": "raster,algebra,statistics",
                "description": "Compute quantiles using two passes.",
                "module": "r.quantile",
            },
            "r.mfilter": {
                "keywords": "raster,algebra,statistics,filter",
                "description": "Performs raster map matrix filter.",
                "module": "r.mfilter",
            },
            "r.neighbors": {
                "keywords": "raster,algebra,statistics,aggregation,neighbor,"
                "focal statistics,filter",
                "description": "Makes each cell category value a function of "
                "the category values assigned to the cells around it, "
                "and stores new cell values in an output raster "
                "map layer.",
                "module": "r.neighbors",
            },
            "r.texture": {
                "keywords": "raster,algebra,statistics,texture",
                "description": "Generate images with textural features from a "
                "raster map.",
                "module": "r.texture",
            },
        },
        "fire": {
            "r.spreadpath": {
                "keywords": "raster,fire,cumulative costs",
                "description": "Recursively traces the least cost path "
                "backwards to cells from which the cumulative cost was "
                "determined.",
                "module": "r.spreadpath",
            },
            "r.spread": {
                "keywords": "raster,fire,spread,hazard,model",
                "description": "Simulates elliptically anisotropic spread. "
                "Generates a raster map of the cumulative time of spread, "
                "given raster maps containing the rates of spread (ROS), the "
                "ROS directions and the spread origins. It optionally "
                "produces raster maps to contain backlink UTM "
                "coordinates for tracing spread paths. Usable for "
                "fire spread simulations.",
                "module": "r.spread",
            },
            "r.ros": {
                "keywords": "raster,fire,spread,rate of spread,hazard,model",
                "description": "Generates rate of spread raster maps. "
                "Generates three, or four raster map layers showing the base "
                "(perpendicular) rate of spread (ROS), the maximum "
                "(forward) ROS, the direction of the maximum ROS, "
                "and optionally the maximum potential spotting "
                "distance for fire spread simulation.",
                "module": "r.ros",
            },
        },
        "resample": {
            "r.resamp.filter": {
                "keywords": "raster,resample,kernel filter",
                "description": "Resamples raster map layers using an analytic "
                "kernel.",
                "module": "r.resamp.filter",
            },
            "r.resamp.rst": {
                "keywords": "raster,resample",
                "description": "Reinterpolates and optionally computes "
                "topographic analysis from input raster map to a new raster "
                "map (possibly with different resolution) using "
                "regularized spline with tension and smoothing.",
                "module": "r.resamp.rst",
            },
            "r.resample": {
                "keywords": "raster,resample",
                "description": "GRASS raster map layer data resampling "
                "capability.",
                "module": "r.resample",
            },
            "r.resamp.stats": {
                "keywords": "raster,resample",
                "description": "Resamples raster map layers to a coarser grid "
                "using aggregation.",
                "module": "r.resamp.stats",
            },
            "r.resamp.interp": {
                "keywords": "raster,resample,interpolation",
                "description": "Resamples raster map to a finer grid using "
                "interpolation.",
                "module": "r.resamp.interp",
            },
        },
        "aggregation": {
            "r.series": {
                "keywords": "raster,aggregation,series",
                "description": "Makes each output cell value a function of the"
                " values assigned to the corresponding cells in "
                "the input raster map layers.",
                "module": "r.series",
            }
        },
        "volume": {
            "r.volume": {
                "keywords": "raster,volume,clumps",
                "description": 'Calculates the volume of data "clumps". '
                "Optionally produces a GRASS vector points map containing the "
                "calculated centroids of these clumps.",
                "module": "r.volume",
            }
        },
        "buffer": {
            "r.circle": {
                "keywords": "raster,buffer,geometry,circle",
                "description": "Creates a raster map containing concentric "
                "rings around a given point.",
                "module": "r.circle",
            },
            "r.buffer": {
                "keywords": "raster,buffer",
                "description": "Creates a raster map showing buffer zones "
                "surrounding cells that contain non-NULL category values.",
                "module": "r.buffer",
            },
            "r.buffer.lowmem": {
                "keywords": "raster,buffer",
                "description": "Creates a raster map showing buffer zones "
                "surrounding cells that contain non-NULL category values. "
                "This is the low-memory alternative to the classic r.buffer "
                "module.",
                "module": "r.buffer.lowmem",
            },
        },
        "solar": {
            "r.horizon": {
                "keywords": "raster,solar,sun position",
                "description": "Computes horizon angle height from a digital "
                "elevation model. The module has two different modes of "
                "operation: 1. Computes the entire horizon around a "
                "single point whose coordinates are given with the "
                "'coord' option. The horizon height (in radians). "
                "2. Computes one or more raster maps of the horizon "
                "height in a single direction. The input for this "
                "is the angle "
                "(in degrees), which is measured "
                "counterclockwise with east=0, north=90 etc. "
                "The output is the horizon height in radians.",
                "module": "r.horizon",
            },
            "r.sunmask": {
                "keywords": "raster,solar,sun position,shadow",
                "description": "Calculates cast shadow areas from sun position"
                " and elevation raster map. Either exact sun position (A) "
                "is specified, or date/time to calculate the sun "
                "position (B) by r.sunmask itself.",
                "module": "r.sunmask",
            },
            "r.sunhours": {
                "keywords": "raster,solar,sun energy,sun position",
                "description": "Calculates solar elevation, solar azimuth, and"
                " sun hours. Solar elevation: the angle between the "
                "direction of the geometric center of the sun's "
                "apparent disk and the (idealized) horizon. Solar "
                "azimuth: the angle from due north in clockwise "
                "direction.",
                "module": "r.sunhours",
            },
            "r.sun": {
                "keywords": "raster,solar,sun energy,shadow",
                "description": "Solar irradiance and irradiation model. "
                "Computes direct (beam), diffuse and reflected solar "
                "irradiation raster maps for given day, latitude, "
                "surface and atmospheric conditions. Solar parameters "
                "(e.g. sunrise, sunset times, declination, "
                "extraterrestrial irradiance, daylight length) are "
                "saved in the map history file. Alternatively, a local "
                "time can be specified to compute solar incidence angle "
                "and/or irradiance raster maps. The shadowing effect "
                "of the topography is optionally incorporated.",
                "module": "r.sun",
            },
        },
        "viewshed": {
            "r.viewshed": {
                "keywords": "raster,viewshed,line of sight,LOS",
                "description": "Computes the viewshed of a point on an "
                "elevation raster map. Default format: NULL (invisible), "
                "vertical angle wrt viewpoint (visible).",
                "module": "r.viewshed",
            }
        },
        "querying": {
            "r.what": {
                "keywords": "raster,querying,position",
                "description": "Queries raster maps on their category values "
                "and category labels.",
                "module": "r.what",
            },
            "r.what.color": {
                "keywords": "raster,querying,color table",
                "description": "Queries colors for a raster map layer.",
                "module": "r.what.color",
            },
        },
        "null data": {
            "r.null": {
                "keywords": "raster,null data",
                "description": "Manages NULL-values of given raster map.",
                "module": "r.null",
            }
        },
        "distance": {
            "r.grow.distance": {
                "keywords": "raster,distance,proximity",
                "description": "Generates a raster map containing distances "
                "to nearest raster features.",
                "module": "r.grow.distance",
            },
            "r.distance": {
                "keywords": "raster,distance",
                "description": "Locates the closest points between objects in "
                "two raster maps.",
                "module": "r.distance",
            },
            "r.grow": {
                "keywords": "raster,distance,proximity",
                "description": "Generates a raster map layer with contiguous "
                "areas grown by one cell.",
                "module": "r.grow",
            },
        },
        "hydrology": {
            "r.carve": {
                "keywords": "raster,hydrology",
                "description": "Generates stream channels. Takes vector stream"
                " data, transforms it to raster and subtracts depth from the "
                "output DEM.",
                "module": "r.carve",
            },
            "r.uslek": {
                "keywords": "raster,hydrology,soil,erosion",
                "description": "Computes USLE Soil Erodibility Factor (K).",
                "module": "r.uslek",
            },
            "r.topmodel": {
                "keywords": "raster,hydrology,model",
                "description": "Simulates TOPMODEL which is a physically based"
                " hydrologic model.",
                "module": "r.topmodel",
            },
            "r.flow": {
                "keywords": "raster,hydrology",
                "description": "Constructs flowlines. Computes flowlines, "
                "flowpath lengths, and flowaccumulation (contributing areas) "
                "from a elevation raster map.",
                "module": "r.flow",
            },
            "r.lake": {
                "keywords": "raster,hydrology,hazard,flood",
                "description": "Fills lake at given point to given level.",
                "module": "r.lake",
            },
            "r.drain": {
                "keywords": "raster,hydrology,cost surface",
                "description": "Traces a flow through an elevation model or "
                "cost surface on a raster map.",
                "module": "r.drain",
            },
            "r.sim.sediment": {
                "keywords": "raster,hydrology,soil,sediment flow,erosion,"
                "deposition,model",
                "description": "Sediment transport and erosion/deposition "
                "simulation using path sampling method (SIMWE).",
                "module": "r.sim.sediment",
            },
            "r.terraflow": {
                "keywords": "raster,hydrology,flow,accumulation,sink",
                "description": "Performs flow computation for massive grids. "
                "Float version.",
                "module": "r.terraflow",
            },
            "r.stream.extract": {
                "keywords": "raster,hydrology,stream network",
                "description": "Performs stream network extraction.",
                "module": "r.stream.extract",
            },
            "r.watershed": {
                "keywords": "raster,hydrology,watershed",
                "description": "Calculates hydrological parameters and RUSLE "
                "factors.",
                "module": "r.watershed",
            },
            "r.fill.dir": {
                "keywords": "raster,hydrology",
                "description": "Filters and generates a depressionless "
                "elevation map and a flow direction map from a given elevation"
                " raster map.",
                "module": "r.fill.dir",
            },
            "r.water.outlet": {
                "keywords": "raster,hydrology,watershed",
                "description": "Creates watershed basins from a drainage "
                "direction map.",
                "module": "r.water.outlet",
            },
            "r.solute.transport": {
                "keywords": "raster,hydrology,solute transport",
                "description": "Numerical calculation program for transient, "
                "confined and unconfined solute transport in two dimensions",
                "module": "r.solute.transport",
            },
            "r.usler": {
                "keywords": "raster,hydrology,rainfall,soil,erosion",
                "description": "Computes USLE R factor, Rainfall erosivity "
                "index.",
                "module": "r.usler",
            },
            "r.sim.water": {
                "keywords": "raster,hydrology,soil,flow,overland flow,model",
                "description": "Overland flow hydrologic simulation using path"
                " sampling method (SIMWE).",
                "module": "r.sim.water",
            },
            "r.topidx": {
                "keywords": "raster,hydrology,wetness",
                "description": "Creates a topographic index (wetness index) "
                "raster map from an elevation raster map.",
                "module": "r.topidx",
            },
        },
        "geometry": {
            "r.patch": {
                "keywords": "raster,geometry,mosaicking,merge,patching",
                "description": "Creates a composite raster map layer by using "
                "known category values from one (or more) map layer(s) to "
                'fill in areas of "no data" in another map layer.',
                "module": "r.patch",
            },
            "r.thin": {
                "keywords": "raster,geometry",
                "description": "Thins non-null cells that denote linear "
                "features in a raster map layer.",
                "module": "r.thin",
            },
        },
        "mask": {
            "r.mask": {
                "keywords": "raster,mask",
                "description": "Creates a MASK for limiting raster operation.",
                "module": "r.mask",
            }
        },
        "color transformation": {
            "r.his": {
                "keywords": "raster,color transformation,RGB,HIS,IHS",
                "description": "Generates red, green and blue (RGB) raster map"
                " layers combining hue, intensity and saturation (HIS) values "
                "from user-specified input raster map layers.",
                "module": "r.his",
            }
        },
        "geomorphology": {
            "r.param.scale": {
                "keywords": "raster,geomorphology,terrain,elevation,landform",
                "description": "Extracts terrain parameters from a DEM. Uses a"
                " multi-scale approach by taking fitting quadratic parameters "
                "to any size window (via least squares).",
                "module": "r.param.scale",
            }
        },
    },
    "general": {
        "support": {
            "g.version": {
                "keywords": "general,support,citing,copyright,version,license",
                "description": "Displays GRASS GIS version info. Optionally "
                "also prints build or copyright information.",
                "module": "g.version",
            }
        },
        "settings": {
            "g.mapset": {
                "keywords": "general,settings",
                "description": "Changes/reports current mapset. Optionally "
                "create new mapset or list available mapsets in given "
                "project.",
                "module": "g.mapset",
            },
            "g.region": {
                "keywords": "general,settings",
                "description": "Manages the boundary definitions for the "
                "geographic region.",
                "module": "g.region",
            },
            "g.gisenv": {
                "keywords": "general,settings,variables,scripts",
                "description": "Outputs and modifies the user's current GRASS "
                "variable settings. Prints all defined GRASS variables if no "
                "option is given.",
                "module": "g.gisenv",
            },
        },
        "projection": {
            "g.proj": {
                "keywords": "general,projection,create project",
                "description": "Prints or modifies GRASS projection "
                "information files (in various coordinate system descriptions"
                "). Can also be used to create new GRASS projects.",
                "module": "g.proj",
            }
        },
        "map management": {
            "g.list": {
                "keywords": "general,map management,list",
                "description": "Lists available GRASS data base files of the "
                "user-specified data type optionally using the search "
                "pattern.",
                "module": "g.list",
            },
            "g.findfile": {
                "keywords": "general,map management,scripts",
                "description": "Searches for GRASS data base files and sets "
                "variables for the shell.",
                "module": "g.findfile",
            },
            "g.remove": {
                "keywords": "general,map management,remove",
                "description": "Removes data base element files from the "
                "user's current mapset using the search pattern.",
                "module": "g.remove",
            },
            "g.rename": {
                "keywords": "general,map management,rename",
                "description": "Renames data base element files in the user's "
                "current mapset.",
                "module": "g.rename",
            },
        },
    },
}
