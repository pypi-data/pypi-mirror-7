from osgeo import gdal, osr, ogr
import os
import subprocess
import glob
import math
import json
from pgeo.utils import log
from pgeo.utils import filesystem
from pgeo.error.custom_exceptions import PGeoException, errors

log = log.logger(__name__)

# example of statistics
stats_config = {
    "descriptive_stats": {
        "force": True
    },
    "histogram": {
        "buckets": 256,
        "include_out_of_range": 0,
        "force": True
    }
}


def get_nodata_value(file_path, band=1):
    ds = gdal.Open(file_path)
    return ds.GetRasterBand(band).GetNoDataValue()


def crop_by_vector_database_olod(input_file, minlat, minlon, maxlat, maxlon, wkt, srcnodata='nodata', dstnodata='nodata'):
    # [[[1371670.86187088, 5713124.13469331], [1371670.86187088, 5885247.87691568], [1548365.06134181, 5885247.87691568], [1548365.06134181, 5713124.13469331], [1371670.86187088, 5713124.13469331]]]

    output_file_gdal_translate = filesystem.create_tmp_filename('output_', '.geotiff')
    output_file_gdal_warp = filesystem.create_tmp_filename('output_', '.geotiff')
    output_file = filesystem.create_tmp_filename('output_', '.geotiff')
    args = [
        'gdal_translate',
        '-projwin',
        str(minlat),
        str(minlon),
        str(maxlat),
        str(maxlon),
        input_file,
        output_file_gdal_translate
    ]
    try:
        print args
        #TODO: handle subprocess Error (like that is not taken)
        proc = subprocess.call(args, stdout=subprocess.PIPE, stderr=None)
    except:
        stdout_value = proc.communicate()[0]
        raise PGeoException(stdout_value, 500)

    args = [
        'gdalwarp',
        "-q",
        "-multi",
        "-of",
        "GTiff",
        "-cutline",
        wkt,
        "-srcnodata",
        str(srcnodata),
        "-dstnodata",
        str(dstnodata),
        # -crop_to_cutline is needed otherwise the layer is not cropped
        # TODO: resolve shifting problem
        # "-crop_to_cutline",
        # "-dstalpha",
        output_file_gdal_translate,
        output_file_gdal_warp
    ]
    try:
        print args
        #TODO: handle subprocess Error (like that is not taken)
        proc = subprocess.call(args, stdout=subprocess.PIPE, stderr=None)
    except:
        stdout_value = proc.communicate()[0]
        raise PGeoException(stdout_value, 500)

    # TODO: is it useful the third opetation?
    args = [
        'gdal_translate',
        "-a_nodata",
        str(dstnodata),
        output_file_gdal_warp,
        output_file
    ]
    try:
        print args
        #TODO: handle subprocess Error (like that is not taken)
        proc = subprocess.call(args, stdout=subprocess.PIPE, stderr=None)
    except:
        stdout_value = proc.communicate()[0]
        raise PGeoException(stdout_value, 500)


    filesystem.remove(output_file_gdal_warp)
    filesystem.remove(output_file_gdal_translate)

    if os.path.isfile(output_file):
        return output_file
    return None


def crop_by_vector_database(raster_path, db_spatial, query_extent, query_layer):
    srcnodatavalue = get_nodata_value(raster_path)
    extent = db_spatial.query(query_extent)
    log.info(extent)
    geom = json.dumps(extent)
    g = json.loads(geom)
    log.info(g)
    obj = g[0][0]
    log.info(obj)
    obj = json.loads(obj)
    # TODO: this is hardcoded because the returning bbox is different from the one used by GDAL processing
    log.info(obj["coordinates"])
    minlat = obj["coordinates"][0][0][0]
    minlon = obj["coordinates"][0][1][1]
    maxlat = obj["coordinates"][0][2][0]
    maxlon = obj["coordinates"][0][0][1]
    db_connection_string = db_spatial.get_connection_string(True);
    return _crop_by_vector_database(raster_path, query_layer, db_connection_string, minlat, minlon, maxlat, maxlon, srcnodatavalue, srcnodatavalue)


# TODO: instead of the connection string pass the geometry
def _crop_by_vector_database(input_file, query, db_connection_string, minlat, minlon, maxlat, maxlon, srcnodata='nodata', dstnodata='nodata'):
   # [[[1371670.86187088, 5713124.13469331], [1371670.86187088, 5885247.87691568], [1548365.06134181, 5885247.87691568], [1548365.06134181, 5713124.13469331], [1371670.86187088, 5713124.13469331]]]


    # From ST_Extent it's needed to get 1,4,3,2 of the values
    # BBOX(1371670.86187088
    # 5713124.13469331
    # 1548365.06134181
    # 5885247.87691568)
    #
    # bounding box to pass to the layer
    #1371670.86187088 5885247.87691568 1548365.06134181 5713124.13469331
    #
    # gdal_translate -projwin 1371670.86187088 5885247.87691568 1548365.06134181 5713124.1346933 /home/vortex/Desktop/LAYERS/earthstat/output/rice_area1.tif /home/vortex/Desktop/LAYERS/tmp/test3.tif

    # gdal_rasterize -b 1 -b 2 -b 3 -burn 255 -burn 255 -burn 255 -l VETOR_SHP D:/GDAL/VETOR_SHP.shp D:/GDAL/LS_SCALE.tif
    # print db_connection_string
    #
    # query = "SELECT geom from spatial.gaul1_3857_test where adm1_code = '1620'"

    #log.info(query)

    output_file_gdal_translate = filesystem.create_tmp_filename('output_', '.geotiff')
    output_file_gdal_warp = filesystem.create_tmp_filename('output_', '.geotiff')
    output_file = filesystem.create_tmp_filename('output_', '.geotiff')
    args = [
        'gdal_translate',
        '-projwin',
        str(minlat),
        str(minlon),
        str(maxlat),
        str(maxlon),
        input_file,
        output_file_gdal_translate
    ]
    try:
        print args
        #TODO: handle subprocess Error (like that is not taken)
        proc = subprocess.call(args, stdout=subprocess.PIPE, stderr=None)
    except:
        stdout_value = proc.communicate()[0]
        raise PGeoException(stdout_value, 500)


    args = [
        'gdalwarp',
        "-q",
        "-multi",
        "-of",
        "GTiff",
        "-cutline",
        db_connection_string,
        "-csql",
        query,
        "-srcnodata",
        str(srcnodata),
        "-dstnodata",
        str(dstnodata),
        # -crop_to_cutline is needed otherwise the layer is not cropped
        # TODO: resolve shifting problem
        # "-crop_to_cutline",
        # "-dstalpha",
        output_file_gdal_translate,
        output_file_gdal_warp
    ]
    try:
        print args
        #TODO: handle subprocess Error (like that is not taken)
        proc = subprocess.call(args, stdout=subprocess.PIPE, stderr=None)
    except:
        stdout_value = proc.communicate()[0]
        raise PGeoException(stdout_value, 500)

    # TODO: is it useful the third opetation?
    args = [
        'gdal_translate',
        "-a_nodata",
        str(dstnodata),
        output_file_gdal_warp,
        output_file
    ]
    try:
        print args
        #TODO: handle subprocess Error (like that is not taken)
        proc = subprocess.call(args, stdout=subprocess.PIPE, stderr=None)
    except:
        stdout_value = proc.communicate()[0]
        raise PGeoException(stdout_value, 500)


    filesystem.remove(output_file_gdal_warp)
    filesystem.remove(output_file_gdal_translate)

    if os.path.isfile(output_file):
        return output_file
    return None


def crop_by_vector_database_ok(input_file, query=None, db_connection_string=None, srcnodata='nodata', dstnodata='nodata'):
    """
    :param input_file: file to be cropped
    :param query: query that has to be passed to the db
    :param db_connection_string: connection string to the db
    :param dstnodata: set nodata on the nodata value
    :return: the output file path that has been processed, or None if there is any problem on the processing
    """
    output_file_gdal_warp = filesystem.create_tmp_filename('output_', '.geotiff')
    output_file = filesystem.create_tmp_filename('output_', '.geotiff')
    args = [
        'gdalwarp',
        "-q",
        "-multi",
        "-of",
        "GTiff",
        "-cutline",
        db_connection_string,
        "-csql",
        query,
        "-srcnodata",
        str(srcnodata),
        "-dstnodata",
        str(dstnodata),
        # -crop_to_cutline is needed otherwise the layer is not cropped
        # TODO: resolve shifting problem
        # "-crop_to_cutline",
        #"-dstalpha",
        input_file,
        output_file_gdal_warp
    ]
    try:
        print args
        #TODO: handle subprocess Error (like that is not taken)
        proc = subprocess.call(args, stdout=subprocess.PIPE, stderr=None)
    except:
        stdout_value = proc.communicate()[0]
        raise PGeoException(stdout_value, 500)

    args = [
        'gdal_translate',
        "-a_nodata",
        str(dstnodata),
        output_file_gdal_warp,
        output_file
    ]
    try:
        print args
        #TODO: handle subprocess Error (like that is not taken)
        proc = subprocess.call(args, stdout=subprocess.PIPE, stderr=None)
    except:
        stdout_value = proc.communicate()[0]
        raise PGeoException(stdout_value, 500)


    if os.path.isfile(output_file):
        return output_file
    return None


def get_statistics(input_file, config=stats_config):
    """
    :param input_file: file to be processed
    :param config: json config file to be passed
    :return: computed statistics
    """
    log.info("get_statistics: %s" % input_file)

    if config is None:
        config = stats_config

    stats = {}
    try:
        if os.path.isfile(input_file):
            ds = gdal.Open(input_file)
            if "descriptive_stats" in config:
                stats["stats"] = _get_descriptive_statistics(ds, config["descriptive_stats"])
            if "histogram" in config:
                stats["hist"] = _get_histogram(ds, config["histogram"])
        else:
            raise PGeoException(errors[522], 404)
    except PGeoException, e:
        raise PGeoException(e.get_message(), e.get_status_code())
    return stats


def get_descriptive_statistics(input_file, config):
    """
    :param input_file: file to be processed
    :param config: json config file to be passed
    :return: return and array with the min, max, mean, sd statistics per band i.e. [{"band": 1, "max": 549.0, "mean": 2.8398871527778, "sd": 17.103028971129, "min": 0.0}]
    """
    try:
        if os.path.isfile(input_file):
            ds = gdal.Open(input_file)
            return _get_descriptive_statistics(ds, config)
        else:
            raise PGeoException(errors[522], 404)
    except PGeoException, e:
        raise PGeoException(e.get_message(), e.get_status_code())


def get_histogram(input_file, config):
    """
    :param input_file: file to be processed
    :type string
    :param config: json config file to be passed
    :type json
    :return: return and array with the min, max, mean, sd statistics per band i.e. [{"band": 1, "buckets": 256, "values": [43256, 357, ...], "max": 998.0, "min": 0.0}]
    """
    try:
        if os.path.isfile(input_file):
            ds = gdal.Open(input_file)
            return _get_histogram(ds, config)
        else:
            raise PGeoException(errors[522], 404)
    except PGeoException, e:
        raise PGeoException(e.get_message(), e.get_status_code())



def location_values(input_files, x, y, band=None):
    """
    Get the value of a (x, y) location

    # TODO:
    1) pass a json, instead of [files] pass file and id
    2) pass as well the projection used i.e. EPSG:4326
    3) for now it's used x, y as lat lon (it's not used the projection)

    :param input_files: files to be processed
    :type array
    :param x: x value (for now it's used LatLon)
    :type float
    :param y: y value (for now it's used LatLon)
    :type float
    :param band: band default=None (not yet used)
    :return: and array with the values of the (x, y) location
    """
    values = []
    for input_file in input_files:
        values.append(_location_value(input_file, x, y, band))
    return values


def _location_value(input_file, x, y, band=None):
    """
    Get the value of a (x, y) location
    :param input_file: file to be processed
    :type string
    :param x: x value
    :type float
    :param y: y value
    :type float
    :param band: band default=None (not yet used)
    :return: the value of the (x, y) location
    """
    # TODO: check with -wgs84 values instead of -geoloc that is the reference system of the image
    #cmd = "gdallocationinfo -valonly " + input_file + " -l_srs EPSG:3857 -geoloc " + str(x) + " " + str(y)
    #cmd = "gdallocationinfo -valonly " + input_file + " -geoloc " + str(x) + " " + str(y)
    cmd = "gdallocationinfo -valonly " + input_file + " -wgs84 " + str(x) + " " + str(y)

    process = subprocess.Popen(cmd, stdout=subprocess.PIPE, stderr=subprocess.PIPE, shell=True)
    output, error = process.communicate()
    return output.strip()


def _get_descriptive_statistics(ds, config):
    # variables
    force = True if "force" not in config else bool(config["force"])

    # stats
    stats = []
    for band in range(ds.RasterCount):
        band += 1
        srcband = ds.GetRasterBand(band)
        if srcband is None:
            continue
        # TODO: check why the "force" doesn't work on GetStatistics but the ComputeStatistics works
        if force:
            s = srcband.ComputeStatistics(0)
            #s = srcband.ComputeRasterMinMax(False)
        else:
            s = srcband.GetStatistics(False, force)
        if stats is None:
            continue
        #srcband.SetStatistics(float(s[0]), float(s[1]), float(s[2]), float(s[3]))
        # if math.isnan(s[2]):
        #     s[2] = "null"
        # if math.isnan(s[2]):
        #     s[3] = "null"
        if math.isnan(s[2]):
            log.warn("polygon is empty! %s " % s)
        else:
            stats.append({"band": band, "min": s[0], "max": s[1], "mean": s[2], "sd": s[3]})


    return stats


def _get_histogram(ds, config):
    #log.info("config %s " % config)
    # variables
    # TODO boolean of config value
    force = True if "force" not in config else bool(config["force"])
    buckets = 256 if "buckets" not in config else int(config["buckets"])
    include_out_of_range = 0 if "include_out_of_range" not in config else int(config["include_out_of_range"])

    # stats
    stats = []
    for band in range(ds.RasterCount):
        band += 1
        if force:
            (min, max) = ds.GetRasterBand(band).ComputeRasterMinMax(0)
        else:
            min = ds.GetRasterBand(band).GetMinimum()
            max = ds.GetRasterBand(band).GetMaximum()

        #hist = ds.GetRasterBand(band).GetDefaultHistogram( force = 0 )
        #stats.append({"band": band, "buckets": hist[2], "min": hist[0], "max": hist[1], "values": hist[3]})
        hist = ds.GetRasterBand(band).GetHistogram(buckets=buckets, min=min, max=max, include_out_of_range=include_out_of_range)
        stats.append({"band": band, "buckets": buckets, "min": min, "max": max, "values": hist})
    return stats


def get_authority(file_path):
    """
    @param file_path: path to the file
    @type file_path: string
    @return: AuthorityName, AuthorityCode
    """
    ds = gdal.Open( file_path )
    prj = ds.GetProjection()
    srs=osr.SpatialReference(wkt=prj)
    return srs.GetAttrValue("AUTHORITY", 0),  srs.GetAttrValue("AUTHORITY", 1)


# Process HDFs
def process_hdfs(obj):
    log.info(obj)

    # extract bands
    hdfs = extract_files_and_band_names(obj["source_path"], obj["band"])

    # extract hdf bands
    single_hdfs = create_hdf_files(obj["output_path"], hdfs)

    # merge tiles
    hdf_merged = merge_hdf_files(obj["output_path"], obj["output_path"], obj["gdal_merge"])

    # do stats?
    #TODO: do stats

    # translate
    tiff = warp_hdf_file(hdf_merged, obj["output_path"], obj["output_file_name"], obj["gdalwarp"])

    #add overviews
    if obj.has_key("gdaladdo"):
        tiff = overviews_tif_file(tiff, obj["gdaladdo"]["parameters"], obj["gdaladdo"]["overviews_levels"])

    return tiff


def extract_files_and_band_names(path, band):
    bands = []
    hdfs = glob.glob(path + "/*.hdf")
    for f in hdfs:
        gtif = gdal.Open(f)
        sds = gtif.GetSubDatasets()
        bands.append(sds[int(band) - 1][0])
    return bands


def create_hdf_files(output_path, files):
    log.info("Create HDF Files")
    i = 0;
    for f in files:
        cmd = "gdal_translate '" + f + "' " + output_path + "/" + str(i) + ".hdf"
        log.info(cmd)
        process = subprocess.Popen(cmd, stdout=subprocess.PIPE, stderr=subprocess.PIPE, shell=True)
        output, error = process.communicate()
        i += 1;
        #TODO catch the error
        log.info(output)
        log.warn(error)


def merge_hdf_files(source_path, output_path, parameters=None):
    log.info("Merge HDF Merge")
    output_file = output_path + "/output.hdf"

    # creating the cmd
    cmd = "gdal_merge.py "
    for key in parameters.keys():
        cmd += " " + key + " " + str(parameters[key])
    cmd += " " + source_path + "/*.hdf -o " + output_file

    log.info(cmd)
    process = subprocess.Popen(cmd, stdout=subprocess.PIPE, stderr=subprocess.PIPE, shell=True)
    output, error = process.communicate()
    log.info(output)
    log.warn(error)
    return output_file


def warp_hdf_file(source_file, output_path, output_file_name, parameters=None ):
    log.info("Warp HDF File to Ti")
    output_file = output_path + "/" + output_file_name

    cmd = "gdalwarp "
    for key in parameters.keys():
        cmd += " " + key + " " + str(parameters[key])
    cmd += " " + source_file + " " + output_file

    log.info(cmd)
    process = subprocess.Popen(cmd, stdout=subprocess.PIPE, stderr=subprocess.PIPE, shell=True)
    output, error = process.communicate()
    log.info(output)
    log.warn(error)
    return output_file


def overviews_tif_file(output_file, parameters=None, overviews_levels=None):
    log.info("Create overviews")

    cmd = "gdaladdo "
    for key in parameters.keys():
        cmd += " " + key + " " + str(parameters[key])
    cmd += " " + output_file
    cmd += " " + overviews_levels

    log.info(cmd)
    process = subprocess.Popen(cmd, stdout=subprocess.PIPE, stderr=subprocess.PIPE, shell=True)
    output, error = process.communicate()
    log.info(output)
    log.warn(error)
    return output_file