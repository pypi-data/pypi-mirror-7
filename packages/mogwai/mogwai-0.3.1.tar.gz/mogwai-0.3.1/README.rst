mogwai
======

mogwai in an object-graph mapper (OGM) designed specifically for use with Titan
(http://thinkaurelius.github.io/titan/) via RexPro (https://github.com/tinkerpop/rexster/wiki/RexPro).
Mogwai supports easily integrating Gremlin graph-traversals with vertex and edge models. For those
already familiar with Blueprints (https://github.com/tinkerpop/blueprints/wiki) there is is a
simple example.

Documentation
=============

mogwai documentation can be found at http://mogwai.readthedocs.org/

Installation
============

``$ pip install mogwai``

Testing
=======

To get mogwai unit tests running you'll need a titan installation with rexster server configured with a mogwai graph::

    <graph>
        <graph-name>mogwai</graph-name>
        <graph-type>com.thinkaurelius.titan.tinkerpop.rexster.TitanGraphConfiguration</graph-type>
        <graph-read-only>false</graph-read-only>
        <graph-location>/tmp/mogwai</graph-location>
        <properties>
              <storage.backend>local</storage.backend>
              <storage.directory>/tmp/mogwai</storage.directory>
              <buffer-size>100</buffer-size>
        </properties>

        <extensions>
          <allows>
            <allow>tp:gremlin</allow>
          </allows>
        </extensions>
    </graph>

