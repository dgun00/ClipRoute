export interface Region {
  regionId: number;
  regionName: string;
  imageUrl: string;
}

export interface RegionListResult {
  regions: Region[];
}

