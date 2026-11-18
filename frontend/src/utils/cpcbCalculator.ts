import { AqiCategory } from '../types/aqi';

/**
 * Official CPCB NAQI Breakpoints Table: [Blo, Bhi, Ilo, Ihi]
 */
export const CPCB_BREAKPOINTS: Record<string, [number, number, number, number][]> = {
  'PM2.5': [
    [0.0, 30.0, 0, 50],
    [30.0, 60.0, 51, 100],
    [60.0, 90.0, 101, 200],
    [90.0, 120.0, 201, 300],
    [120.0, 250.0, 301, 400],
    [250.0, 380.0, 401, 500],
  ],
  'PM10': [
    [0.0, 50.0, 0, 50],
    [50.0, 100.0, 51, 100],
    [100.0, 250.0, 101, 200],
    [250.0, 350.0, 201, 300],
    [350.0, 430.0, 301, 400],
    [430.0, 510.0, 401, 500],
  ],
  'NO2': [
    [0.0, 40.0, 0, 50],
    [40.0, 80.0, 51, 100],
    [80.0, 180.0, 101, 200],
    [180.0, 280.0, 201, 300],
    [280.0, 400.0, 301, 400],
    [400.0, 500.0, 401, 500],
  ],
  'SO2': [
    [0.0, 40.0, 0, 50],
    [40.0, 80.0, 51, 100],
    [80.0, 380.0, 101, 200],
    [380.0, 800.0, 201, 300],
    [800.0, 1600.0, 301, 400],
    [1600.0, 2000.0, 401, 500],
  ],
  'CO': [
    [0.0, 1.0, 0, 50],
    [1.0, 2.0, 51, 100],
    [2.0, 10.0, 101, 200],
    [10.0, 17.0, 201, 300],
    [17.0, 34.0, 301, 400],
    [34.0, 50.0, 401, 500],
  ],
  'O3': [
    [0.0, 50.0, 0, 50],
    [50.0, 100.0, 51, 100],
    [100.0, 168.0, 101, 200],
    [168.0, 208.0, 201, 300],
    [208.0, 748.0, 301, 400],
    [748.0, 1000.0, 401, 500],
  ],
};

export function getAqiCategory(aqi: number): AqiCategory {
  if (aqi <= 50) return 'Good';
  if (aqi <= 100) return 'Satisfactory';
  if (aqi <= 200) return 'Moderate';
  if (aqi <= 300) return 'Poor';
  if (aqi <= 400) return 'Very Poor';
  if (aqi <= 500) return 'Severe';
  return 'Severe+';
}

export function calculateSubindex(pollutant: string, concentration: number): number {
  if (concentration <= 0) return 0;
  const bands = CPCB_BREAKPOINTS[pollutant.toUpperCase()];
  if (!bands) return 0;

  for (const [bLo, bHi, iLo, iHi] of bands) {
    if (concentration >= bLo && concentration <= bHi) {
      const sub = iLo + ((iHi - iLo) / (bHi - bLo)) * (concentration - bLo);
      return Math.round(sub);
    }
  }

  const highest = bands[bands.length - 1];
  if (concentration > highest[1]) {
    const sub = highest[2] + ((highest[3] - highest[2]) / (highest[1] - highest[0])) * (concentration - highest[0]);
    return Math.min(999, Math.round(sub));
  }

  return 0;
}

export function concentrationFromSubindex(pollutant: string, targetSubindex: number): number {
  if (targetSubindex <= 0) return 0;
  const bands = CPCB_BREAKPOINTS[pollutant.toUpperCase()];
  if (!bands) return 0;

  for (const [bLo, bHi, iLo, iHi] of bands) {
    if (targetSubindex >= iLo && targetSubindex <= iHi) {
      const conc = bLo + ((bHi - bLo) / (iHi - iLo)) * (targetSubindex - iLo);
      return Number(conc.toFixed(1));
    }
  }

  const highest = bands[bands.length - 1];
  const conc = highest[0] + ((highest[1] - highest[0]) / (highest[3] - highest[2])) * (targetSubindex - highest[2]);
  return Number(conc.toFixed(1));
}
