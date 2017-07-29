# Leaflet and What3Words
_can we get this to work?_

Starting point:
[https://github.com/davidpiesse/leaflet.w3w][0]


Changes made:

- Put control.w3w.\* files in `/public`.
- Src css and js with prefix `/`

The web page is empty (https://palm-fish.glitch.me/)

- Add dotted box styling on map div so we can see where things are supposed to be

There is error in Web console about mixed mode content. Fixed by calling Leaflet cdn files with http**s**.

Next console error is "ReferenceError: L is not defined" in control.w3w.js. Changing to Leaflet v1.0.3 makes that go away.

Now we have "401 unauthorized" from api.tiles.mapbox.com. I'd wondered about that when I saw the `accesstoken` parameter.

 - added my Mapbox API token
 
Now we see a partial map. Console reports missing .png files. Oh yeah, we need to update the Leaflet css file too.

**YAY! it works! :)**

-----
## 2017-07-28  
Added `serve-index` module so don't have to keep editing the index page. See `server.js`

As of this writing only template-map and turf pages are working.

...

Added serve-index module so don't have to keep editing the index page. See `server.js`

Created basic template-map.html. Does nothing but show a map zoomed in on Schwatka boat launch.

Cleaned cruft from turf.html.  Learned how to add a point and buffer it.


### Tech Notes

	var point = turf.point([y,x]);
	var buffered = turf.buffer(point, 15, 'meters');
	
_turf.min.js:14 Uncaught TypeError: Cannot read property 'getEdge' of null_
	
Why? because 'point' coordinates are reversed!
	
See https://chat.stackexchange.com/rooms/939/gis




[0]: https://github.com/davidpiesse/leaflet.w3w