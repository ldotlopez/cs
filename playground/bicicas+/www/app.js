"use strict";

class Point {
	constructor(latitude, longitude) {
		this.latitude = latitude;
		this.longitude = longitude;
	}

	distanceTo(point) {
		return Math.sqrt(
			Math.pow(Math.abs(this.latitude - point.latitude), 2) + 
			Math.pow(Math.abs(this.longitude - point.longitude), 2));
	}

	asLatLng(point) {
		return {
			lat: this.latitude,
			lng: this.longitude
		};
	}

	asString() {
		return "("+this.latitude+", "+this.longitude+")";
	}
}


class Station extends Point {
	constructor(id, name, latitude, longitude, available, capacity) {
		super(latitude, longitude);
		this.id = id;
		this.name = name;
		this.available = available;
		this.capacity = capacity;
	}

	asString() {
		return super.asString()+"("+this.name+")";
	}
}


class RouteManager {
	constructor(map, route, titles, fn) {
		this.route = route;
		this.directionsService = new google.maps.DirectionsService();
		this.markers = new Array(route.length);
		this.renderers = [];

		console.log("Route "+route.map((x) => {
			return x.asString()
		}).join(' => '));

		// Create markers
		this.markers = route.map((x, idx) => {
			var marker = this.createMarker({
				point: x,
				map: map,
				label: titles[idx],
				title: titles[idx],
				isEndPoint: (idx == 0 || idx == route.length - 1)
			});

			if (marker.getDraggable()) {
				marker.addListener('dragend', (marker) => {
					this.route[idx] = new Point(marker.latLng.lat(), marker.latLng.lng());
					fn(this.route);
				});
			}

			return marker;
		});

		var modes = [
			google.maps.TravelMode.WALKING,
			google.maps.TravelMode.BICYCLING,
			google.maps.TravelMode.WALKING,
		];
		for (var idx = 0; idx < route.length - 1; idx++) {
			var a = route[idx];
			var b = route[idx+1];
			var mode = modes[idx];

			var request = {
				origin: a.asLatLng(),
				destination: b.asLatLng(),
				unitSystem: google.maps.UnitSystem.METRIC,
				travelMode: mode, // See WALKING
			};

			this.directionsService.route(request, (directionResults, status) => {
				this.renderers.push(new google.maps.DirectionsRenderer({
					map: map,
					directions: directionResults,
					suppressMarkers: true,
				}));
			});
		}

		// Bounds
		var bounds = new google.maps.LatLngBounds(route[0].asLatLng(), route[1].asLatLng())
			.extend(route[2].asLatLng())
			.extend(route[3].asLatLng());
		map.panToBounds(bounds);
	}

	release() {
		// Remove previous Google Maps objects
		this.markers.concat(this.renderers).forEach((x) => {
			if (!x) {
				return;
			}
			x.setMap(null);
		});
		this.markers = null;
		this.renderers = null;
	}

	// opts: {map: google.maps.Map, label: Str, isStation: Bool, point: Point}
	createMarker(opts) {
		var opts = {
			map: opts.map,
			animation: google.maps.Animation.DROP,
			draggable: opts.isEndPoint,
			position: opts.point.asLatLng(),
			title: opts.title,
			label: opts.label
		};
		return new google.maps.Marker(opts);
	}
}


class App {
	constructor(element, mapOptions) {
		this.map = new google.maps.Map(element, mapOptions);
		this.routeManager = null;
		// this.geolocate();
	}

	calculateRouteFromMarkers(a, b) {
		this.calculateRoute(
			new Point(a.position.lat(), a.position.lng()),
			new Point(b.position.lat(), b.position.lng())
		);
	}

	calculateRoute(start, end) {
		if (!(start !== null && end !== null)) {
			return;
		}

		this.getStations()
			.then((stations) => {
				if (this.routeManager) {
					this.routeManager.release();
				}

				var startStation = this.getNearestStation(stations, start);
				var endStation = this.getNearestStation(stations, end);
				this.routeManager = new RouteManager(
					this.map,
					[start, startStation, endStation, end],
					['start', 'startStation', 'endStation', 'end'],
					(route) => {
						this.routeManager.release();
						this.calculateRoute(route[0], route[route.length-1])
					}); // FIX: use a Proxy
			});
	}

	getStations() {
		return fetch('stations.json')
			.then((response) => {
				return response.json();
			})
			.then((response) => {
				return response[0].ocupacion.map((x) => {
					return new Station(
						parseInt(x.id), x.punto,
						parseFloat(x.latitud), parseFloat(x.longitud),
						parseInt(x.ocupados), parseInt(x.puestos));
					});
			})
			.catch((error) => {
				console.log("Error:", error);
				throw error;
			});
	}

	getNearestStation(stations, point) {
		var nearest = null;
		var minDist = Infinity;
		
		stations.forEach((x) => {
			if (x.available === 0) {
				console.log("Discarting "+x.name+" because has not available slots");
				return;
			}

			var dist = point.distanceTo(x);
			// console.log("Distance to " + x.name + " is " + dist);

			if (dist < minDist) {
				nearest = x;
				minDist = dist;
				// console.log(x.name + " is nearest");
			}
		});

		return nearest;
	}

	displayRouteSegment(idx, directions) {
		return this.renderers[idx] = new google.maps.DirectionsRenderer({
			map: this.map,
			directions: directions,
			suppressMarkers: true,
		});
	}

	geolocate() {
		var self = this;
		if (!navigator.geolocation) {
			throw "Geolocation not available";
		}

		navigator.geolocation.getCurrentPosition(function (position) {
			self.setStart(new Point(
				position.coords.latitude,
				position.coords.longitude));

			self.setEnd(new Point(
				39.993963,
				-0.02809));
		});
	}
}

class AddressCompletion {
	// https://developers.google.com/maps/documentation/javascript/examples/places-autocomplete-addressform?hl=es-419

	constructor(element, callback, point, radius) {
		var self = this;

		self.callback = callback;

		var circle = new google.maps.Circle({
			center: point.asLatLng(),
			radius: radius
		});
		
		this.api = new google.maps.places.Autocomplete(element, {
			bounds: circle.getBounds(),
			types: ['geocode']
		});	
		
		this.api.addListener('place_changed', () => {
			this.callback(this.api.getPlace());
		});
	}
}
