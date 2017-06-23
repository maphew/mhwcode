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





[0]: https://github.com/davidpiesse/leaflet.w3w