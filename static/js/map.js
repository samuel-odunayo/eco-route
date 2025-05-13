
class RouteMap {
    constructor(mapElementId) {
        this.mapElement = document.getElementById(mapElementId);
        this.map = null;
        this.routeLines = {};
        this.markers = [];
        this.selectedRoute = null;
    }
    
    initialize(center = [51.505, -0.09], zoom = 13) {
        this.map = L.map(this.mapElement).setView(center, zoom);
        
        L.tileLayer('https://{s}.tile.openstreetmap.org/{z}/{x}/{y}.png', {
            attribution: '&copy; <a href="https://www.openstreetmap.org/copyright">OpenStreetMap</a> contributors'
        }).addTo(this.map);
        
        return this;
    }
    
    addMarkers(startLocation, endLocation) {
        this.clearMarkers();
        
        const startMarker = L.marker(startLocation).addTo(this.map);
        startMarker.bindPopup('Start: ' + startLocation.join(', ')).openPopup();
        this.markers.push(startMarker);
        
        const endMarker = L.marker(endLocation).addTo(this.map);
        endMarker.bindPopup('End: ' + endLocation.join(', '));
        this.markers.push(endMarker);
        
        this.fitBounds();
        
        return this;
    }
    
    clearMarkers() {
        this.markers.forEach(marker => this.map.removeLayer(marker));
        this.markers = [];
        return this;
    }
    
    addRoute(routeName, coordinates, options = {}) {
        const defaultOptions = {
            color: '#3388ff',
            weight: 5,
            opacity: 0.7
        };
        
        const routeOptions = {...defaultOptions, ...options};
        
        const routeLine = L.polyline(coordinates, routeOptions).addTo(this.map);
        
        this.routeLines[routeName] = routeLine;
        
        this.fitBounds();
        
        return this;
    }
    
    showRoute(routeName) {
        if (this.selectedRoute && this.routeLines[this.selectedRoute]) {
            this.routeLines[this.selectedRoute].setStyle({opacity: 0.3});
        }
        
        if (this.routeLines[routeName]) {
            this.routeLines[routeName].setStyle({opacity: 1.0});
            this.selectedRoute = routeName;
        }
        
        return this;
    }
    
    removeRoute(routeName) {
        if (this.routeLines[routeName]) {
            this.map.removeLayer(this.routeLines[routeName]);
            delete this.routeLines[routeName];
        }
        
        return this;
    }
    
    clearRoutes() {
        Object.keys(this.routeLines).forEach(routeName => {
            this.map.removeLayer(this.routeLines[routeName]);
        });
        
        this.routeLines = {};
        this.selectedRoute = null;
        
        return this;
    }
    
    fitBounds() {
        const allPoints = [];
        
        this.markers.forEach(marker => {
            allPoints.push(marker.getLatLng());
        });
        
        Object.values(this.routeLines).forEach(route => {
            route.getLatLngs().forEach(latLng => {
                if (Array.isArray(latLng)) {
                    latLng.forEach(point => allPoints.push(point));
                } else {
                    allPoints.push(latLng);
                }
            });
        });
        
        if (allPoints.length > 0) {
            this.map.fitBounds(L.latLngBounds(allPoints), {
                padding: [50, 50],
                maxZoom: 15
            });
        }
        
        return this;
    }
}

function generateDemoRoutes(start, end, transportModes) {
    const routes = {};
    
    transportModes.forEach((mode) => {
        let waypoints = [];
        
        switch(mode) {
            case 'walking':
                waypoints = getWalkingWaypoints(start, end, 5);
                break;
            case 'biking':
                waypoints = getBikingWaypoints(start, end, 3);
                break;
            case 'bus':
                waypoints = getBusWaypoints(start, end);
                break;
            case 'train':
                waypoints = getTrainWaypoints(start, end);
                break;
            case 'car':

                waypoints = [
                    [start[0] + (end[0] - start[0]) * 0.33, start[1] + (end[1] - start[1]) * 0.33],
                    [start[0] + (end[0] - start[0]) * 0.66, start[1] + (end[1] - start[1]) * 0.66]
                ];
                break;
            case 'rideshare':
                waypoints = [
                    [start[0] + (end[0] - start[0]) * 0.4, start[1] + (end[1] - start[1]) * 0.35],
                    [start[0] + (end[0] - start[0]) * 0.7, start[1] + (end[1] - start[1]) * 0.65]
                ];
                break;
        }
        
        routes[mode] = [start, ...waypoints, end];
    });
    
    return routes;
}

function getWalkingWaypoints(start, end, count) {
    const waypoints = [];
    const jitterFactor = 0.005;
    
    for (let i = 1; i <= count; i++) {
        const ratio = i / (count + 1);
        waypoints.push([
            start[0] + (end[0] - start[0]) * ratio + (Math.random() - 0.5) * jitterFactor,
            start[1] + (end[1] - start[1]) * ratio + (Math.random() - 0.5) * jitterFactor
        ]);
    }
    
    return waypoints;
}

function getBikingWaypoints(start, end, count) {
    const waypoints = [];
    const jitterFactor = 0.003;
    
    for (let i = 1; i <= count; i++) {
        const ratio = i / (count + 1);
        waypoints.push([
            start[0] + (end[0] - start[0]) * ratio + (Math.random() - 0.5) * jitterFactor,
            start[1] + (end[1] - start[1]) * ratio + (Math.random() - 0.5) * jitterFactor
        ]);
    }
    
    return waypoints;
}

function getBusWaypoints(start, end) {
    return [
        [start[0] + (end[0] - start[0]) * 0.2, start[1] + (end[1] - start[1]) * 0.2],
        [start[0] + (end[0] - start[0]) * 0.4, start[1] + (end[1] - start[1]) * 0.35],
        [start[0] + (end[0] - start[0]) * 0.6, start[1] + (end[1] - start[1]) * 0.5],
        [start[0] + (end[0] - start[0]) * 0.8, start[1] + (end[1] - start[1]) * 0.75]
    ];
}

function getTrainWaypoints(start, end) {
    return [
        [start[0] + (end[0] - start[0]) * 0.3, start[1] + (end[1] - start[1]) * 0.25],
        [start[0] + (end[0] - start[0]) * 0.7, start[1] + (end[1] - start[1]) * 0.75]
    ];
}

window.RouteMap = RouteMap;
window.generateDemoRoutes = generateDemoRoutes;