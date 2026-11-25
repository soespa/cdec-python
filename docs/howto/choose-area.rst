Choose the area
===============

Every download function takes the area as its second argument, ``spatial_extent``. There are
three ways to write it. All of them use longitude and latitude in degrees (WGS 84).

**A box.** Give the four edges. This is the usual way:

.. code-block:: python

    spatial_extent = {"west": 8.721771, "south": 53.025027, "east": 8.904419, "north": 53.114965}

**A Shapely geometry.** Useful if you have a polygon, or if you prefer ``box(west, south, east, north)``:

.. code-block:: python

    from shapely.geometry import box

    spatial_extent = box(8.721771, 53.025027, 8.904419, 53.114965)

**A GeoJSON file.** Give the path of the file:

.. code-block:: python

    spatial_extent = "areas/bremen.geojson"

Find your area on a map
-----------------------

You do not have to know coordinates by heart. Draw the area on a map and let a website give you the
numbers or a file. Both sites are free and need no account.

bboxfinder.com: four numbers for a box
~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~

1. Open `bboxfinder.com <https://bboxfinder.com/>`__ and zoom to your place.
2. Choose the rectangle tool of the map and drag a rectangle over your area.
3. Find **Box** in the list of coordinates. Set the format to **Lng / Lat**, then click the copy icon next to
   **Box**. You get four numbers in the order *west, south, east, north*, for example
   ``8.721771,53.025027,8.904419,53.114965``.
4. Paste them into your code and let Python split them:

.. code-block:: python

    box = "8.721771,53.025027,8.904419,53.114965"  # pasted from bboxfinder.com
    west, south, east, north = map(float, box.split(","))
    spatial_extent = {"west": west, "south": south, "east": east, "north": north}

The format **Lat / Lng** turns each pair around. The numbers would then go under the wrong names and the
area would be somewhere else on the globe, without an error message: check the first plot.

geojson.io: a file for your area
~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~

1. Open `geojson.io <https://geojson.io/>`__ and zoom to your place.
2. Choose the rectangle tool in the toolbar of the map and draw **one** rectangle. A polygon works too, but a
   rectangle is the easiest to check.
3. Open the **Save** menu at the top and choose **GeoJSON**. The browser downloads a file, for example
   ``map.geojson``.
4. Move the file into your project and give its path. The name has to end with ``.geojson`` or ``.json``:

.. code-block:: python

    spatial_extent = "areas/bremen.geojson"

The panel next to the map shows the same area as text. Its numbers are ``[longitude, latitude]`` pairs.

Which site? bboxfinder.com is quicker, and the numbers stay visible in your code. geojson.io gives you a file
that you can keep, share and use again for the next data type.

Tips
----

* ``west`` and ``east`` are longitudes, ``south`` and ``north`` are latitudes. They are easy to mix up
  (``box`` wants longitude first), so look at the first plot: is it the place you wanted?
* Some tools write the latitude first (Google Maps does). Put each number under its own name: ``west`` and
  ``east`` are the longitudes.
* Start small. A few kilometres and one month are quick to download; make the area and the period
  larger when everything works.
* The downloaded file is clipped to the area but it has the grid of the data, so its edges can differ
  a little from your box (see the ``extent`` line of the summary).
* The area must lie inside the coverage of the data type. :doc:`/data/soil-water-index` covers Europe only.
