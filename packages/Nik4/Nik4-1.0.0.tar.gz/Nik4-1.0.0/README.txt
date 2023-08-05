Nik4
====

This is a mapnik-to-image exporting script. It requires only
``mapnik-python`` bindings. Install it with ``pip install nik4`` or
``easy_install nik4`` and run with ``-h`` option to see available
options and their descriptions.

Why is it better
----------------

Nik4 takes great care to preserve values you feed it. If you say you
need a 800×600 image, it won't take a pixel less or more. It won't
shrink a bounding box or distort lines when specifying so called "scale
factor". When you need a 300 dpi image, you tell it ``--ppi 300`` and
can be sure you will get what you intended.

For example, this is a sample rendering of an area in Tallinn on zoom
17, by Nik4, Nik2img and as seen on the default layer on osm.org:

.. figure:: img/demo-zoom-levels.png
   :alt: nik4 - osm.org - nik2img

   nik4 - osm.org - nik2img
Also it can use real-world units, that is, millimeters (and prefers to).
Specify dimensions for printing, choose bounding box and ppi scale — and
the result won't disappoint. Options are intuitive and plenty, and you
will be amazed how much tasks became simpler with Nik4.

How to use it
-------------

Again, run ``nik4.py -h`` to see the list of all available options. Here
are some examples.

Watch a mapping party area
~~~~~~~~~~~~~~~~~~~~~~~~~~

First, if you haven't already, install PostgreSQL+PostGIS and Mapnik,
and use osm2pgsql to populate the database with a planet extract. For
instructions see `here <http://switch2osm.org/loading-osm-data/>`__ or
`here <http://wiki.openstreetmap.org/wiki/User:Zverik/Tile_Server_on_Fedora_20>`__.
Get bounds by visiting `osm.org <http://openstreetmap.org>`__: click
"Export" and "Choose another region". Then:

::

    nik4.py -b -0.009 51.47 0.013 51.484 -z 17 openstreetmap-carto/osm.xml party-before.png

Here ``osm.xml`` is the compiled Mapnik style. Then you can
`update <http://wiki.openstreetmap.org/wiki/Minutely_Mapnik>`__ you
database and generate snapshots of an area as it is being mapped.
Alternatively, you can specify an area with its center and desired image
size in pixels:

::

    nik4.py -c 0 51.477 --size-px 800 600 -z 17 openstreetmap-carto/osm.xml party-before.png

Make a georeferenced raster image
~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~

Some people prefer planning routes with OziExplorer or similar programs.
Or want to take a big raster map with them on the road. For that a very
big image is needed. Usually they turn to downloading and stitching
hundreds of tiles, but with Nik4 you can make Mapnik produce a better
looking map, faster and without bothering tile server administrators.

Since you are not bound to any tile provider, you should employ
`TileMill <https://www.mapbox.com/tilemill/>`__ for customizing your map
style: for example, remove forest on low zooms, add contrast to road
lines, render more villages, highlight useful POI and cycling routes.

::

    nik4.py -b 25 61.6 30.6 63.3 -z 13 custom.xml kuopio.png --ozi kuopio.map

This will render 16311×10709 image with a georeferencing file ready to
open in OziExplorer. For a ``.wld`` file, which can be used in desktop
GIS applications or for creating a GeoTIFF file, use ``--wld`` option.
You can convert png+wld to geotiff with GDAL:

::

    gdal_translate -of GTiff -a_srs epsg:4326 image.png image.tif

Make a BIG raster image
~~~~~~~~~~~~~~~~~~~~~~~

You would likely encounter out of memory error while trying to generate
16311×10709 image from the last chapter. Despair not:

::

    nik4.py -b 25 61.6 30.6 63.3 -z 13 custom.xml kuopio.png --ozi kuopio.map --tiles 4

Voilà — now Mapnik has to generate 16 images of a manageable size
4078×2678. After that Nik4 will call ``montage`` from the Imagemagick
package to stitch all tiles together.

What if ``montage`` cannot fit images into memory? There is a way, but
you would need quite a lot of disk space, several gigabytes:

::

    for i in *_kuopio.png; do convert $i `basename $i .png`.mpc; done
    montage -geometry +0+0 -tile 4x4 *_kuopio.mpc kuopio.png
    rm *_kuopio.{png,mpc,cache}

These lines will convert all images to Imagemagick's internal MPC
format, from which ``montage`` reads directly. You would need more space
for a similar MPC cache of the output file. Note that most software will
have trouble opening an image surpassing 200 megapixels.

Get an image for printing
~~~~~~~~~~~~~~~~~~~~~~~~~

.. figure:: img/paper-options.png
   :alt: A4 options

   A4 options
Let's say you need a 1:5000 image of a city center for printing on a A4
sheet with margins.

::

    nik4.py -s 5000 --ppi 300 -a 4 -c 24.1094 56.9488 --margin 10 ~/osm/krym/carto/osm.xml 4print.png

What you get is a raster image, which when printed on an A4 with 300 dpi
resolution, would have 10 mm margins and scale of exactly 50 m in a cm.
See the picture above for explanation of margins and other options. By
default paper is in landscape, horizontal orientation. To turn it
portrait, use negative values for ``-a`` option. Or enter numbers by
hand: ``-d 150 100`` will export a 15×10 postcard map.

Print a route
~~~~~~~~~~~~~

On the image above there is a route. Nik4 cannot parse GPX files or draw
anything on top of exported images, but it can manage layers in Mapnik
style file. And Mapnik (via OGR plugin) can draw `a lot of
things <http://www.gdal.org/ogr/ogr_formats.html>`__, including GPX,
GeoJSON, CSV, KML. Just add your route to the style like this:

.. code:: xml

    <Style name="route" filter-mode="first">
      <Rule>
        <LineSymbolizer stroke-width="5" stroke="#012d64" stroke-linejoin="round" stroke-linecap="round" />
      </Rule>
    </Style>
    <Layer name="route" status="off" srs="+proj=longlat +ellps=WGS84 +datum=WGS84 +no_defs">
        <StyleName>route</StyleName>
        <Datasource>
           <Parameter name="type">ogr></Parameter>
           <Parameter name="file"><![CDATA[/home/user/route.gpx]]></Parameter>
           <Parameter name="layer">tracks></Parameter>
           <Parameter name="all_layers">route_points,routes,track_points,waypoints></Parameter>
        </Datasource>
      </Layer>

Note that you can add it in any place: for example, between road and
label layers, so the route does not obscure any text. Also note
``status="off"``: this layer won't be drawn by default. So if you want
to export a clean map for the extent of your route (or any other) layer,
use those options:

::

    nik4.py --fit route --size-px 400 700 osm.xml route_area.png

To enable drawing of the layer, use ``--add-layers`` option:

::

    nik4.py --fit route --add-layers route,stops --ppi 150 -a -6 osm.xml route.png

You can list many layers, separating them with commas. And you can hide
some layers: ``--hide-layers contours,shields``. Obviously you can fit
several layers at once, as well as specify a bounding box to include on
a map. All layer names are case-sensitive, so if something does not
appear, check your style file for exact layer names.

Generate a vector drawing from a map
~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~

It's as easy as adding an ``.svg`` extension to the output file name.

::

    nik4.py --fit route -a -5 --factor 4 osm.xml map.svg

Why did I use ``--factor`` (it's the same as using ``--ppi 362.8``,
which is 90.7 \* 4)? Shouldn't vector images be independent of the
resolution? Well, the problem is in label kerning:

.. figure:: img/svg-factor.png
   :alt: SVG labels quality

   SVG labels quality
Left image was exported with ``--factor 1``. You can see in "ali",
"sis", "Uus" that distance between letters is varying unpredictably, not
like the font instructs. That's because Mapnik rounds letter widths to
nearest integers, that is, to pixels. By increasing the resolution, you
make that granularity finer, so rounding errors are much less prominent.
Labels would become slightly longer, that's why they are different in
the second image.

You can export a map to PDF and be done with it, but often you'd want to
do some postprocessing: move labels away from roads, highlight features,
draw additional labels and arrows. For that I recommend processing the
SVG file with
`mapnik-group-text <https://github.com/Zverik/mapnik-group-text>`__,
which would allow for easier label movement.

See also
--------

-  `mapnik/demo/python <https://github.com/mapnik/mapnik/tree/master/demo/python>`__
-  `generate\_image.py <http://svn.openstreetmap.org/applications/rendering/mapnik/generate_image.py>`__
-  `mapnik-render-image <https://github.com/plepe/mapnik-render-image>`__
-  `osm.org/export <https://trac.openstreetmap.org/browser/sites/tile.openstreetmap.org/cgi-bin/export>`__
-  `nik2img <http://code.google.com/p/mapnik-utils/wiki/Nik2Img>`__

For generating tiles, see
`polytiles.py <https://github.com/Zverik/polytiles>`__.

Author and license
------------------

The script was written by Ilya Zverev and published under WTFPL.
