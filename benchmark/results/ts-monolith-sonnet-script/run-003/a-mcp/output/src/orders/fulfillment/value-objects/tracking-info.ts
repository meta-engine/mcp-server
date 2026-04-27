import { Carrier } from '../enums/carrier.enum';

export interface TrackingInfo {
  carrier: Carrier;
  trackingNumber: string;
}
