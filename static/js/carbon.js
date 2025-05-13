class CarbonCalculator {
    constructor(emissionsData) {     
        this.emissionsData = emissionsData || {
            'walking': 0,
            'biking': 0,
            'bus': 68,
            'train': 41,
            'car_small': 120,
            'car_medium': 170,
            'car_large': 220,
            'rideshare': 180
        };
    }
    
    calculateEmissions(mode, distance) {
        const emissionsPerKm = this.emissionsData[mode] || 0;
        return emissionsPerKm * distance;
    }
    
    calculateSavings(chosenMode, referenceMode, distance) {
        const chosenEmissions = this.calculateEmissions(chosenMode, distance);
        const referenceEmissions = this.calculateEmissions(referenceMode, distance);
        
        return Math.max(0, referenceEmissions - chosenEmissions);
    }
    
    getEnvironmentalImpact(carbonSaved) {
        const TREE_ABSORPTION_YEARLY = 21000;
        const DRIVING_EMISSIONS_PER_KM = 170;

        const carbonSavedKg = carbonSaved / 1000;
        
        return {
            treeDays: carbonSaved / (TREE_ABSORPTION_YEARLY / 365),
            carKmEquivalent: carbonSaved / DRIVING_EMISSIONS_PER_KM,
            carbonKg: carbonSavedKg
        };
    }
    
    getImpactDescription(carbonSaved) {
        const impact = this.getEnvironmentalImpact(carbonSaved);
        
        let description = '';
        
        if (impact.treeDays >= 1) {
            description += `Equivalent to a tree absorbing CO₂ for ${Math.round(impact.treeDays)} day(s). `;
        }
        
        if (impact.carKmEquivalent >= 1) {
            description += `You've saved as much CO₂ as driving a car for ${Math.round(impact.carKmEquivalent)} km. `;
        }
        
        return description || 'Every bit of CO₂ reduction helps the environment!';
    }
    
    getEmissionsColor(emissions, maxEmissions = 2000) {
        const ratio = Math.min(emissions / maxEmissions, 1);
        
        if (ratio < 0.33) {
            return '#28a745';
        } else if (ratio < 0.66) {
            return '#ffc107';
        } else {
            return '#dc3545';
        }
    }
    
    rankTransportationOptions(options) {
        const ranked = Object.keys(options).map(mode => ({
            mode: mode,
            emissions: this.calculateEmissions(mode, options[mode].distance),
            distance: options[mode].distance,
            duration: options[mode].duration
        }));
        
        return ranked.sort((a, b) => a.emissions - b.emissions);
    }
    
    calculateLifetimeImpact(savedRoutes) {
        let totalSaved = 0;
        
        savedRoutes.forEach(route => {
            totalSaved += route.carbonSaved;
        });
        
        return {
            totalSaved: totalSaved,
            kgSaved: totalSaved / 1000,
            treeDays: totalSaved / (21000 / 365),
            carKm: totalSaved / 170
        };
    }
}

window.carbonCalculator = new CarbonCalculator();