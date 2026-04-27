/** Value object representing the estimated delivery window for a shipment. */
export interface DeliveryWindow {
  id: string;
  createdAt: Date;
  updatedAt: Date;
  name: string;
  description: string;
}
