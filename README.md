# The omnidator

Conceptually, omnidator takes whatever kind of data format that uses [Schema.org](http://schema.org) terms and turns it into any other kind of data format:

![omnidator concept](https://github.com/mhausenblas/omnidator/raw/master/img/omnidator-concept.png "omnidator concept")

Technically, omnidator is a web application written in Python, using the [Schema Gateway](https://github.com/mhausenblas/schema-org-rdf/tree/master/tools/schema-gateway) and deployed on [Google App Engine](http://code.google.com/appengine/): see [http://omnidator.appspot.com/](http://omnidator.appspot.com/) for the live instance.

## Ack

This software wouldn't be possible without an number of people that wrote a lot of stuff that I simply happen to glue together - big thanks go out to: Ed Summers for his awesome [rdflib-microdata](https://github.com/edsu/rdflib-microdata) plug-in, William Waites for his permanent first-level Python support via [IRC](http://chatlogs.planetrdf.com/swig/), and Richard Cyganiak for the idea re the CSV parser.

## License

This software is Public Domain.